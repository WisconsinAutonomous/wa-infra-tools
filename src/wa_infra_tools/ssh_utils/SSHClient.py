"""
This file contains a SSH tunneler that works with CAE 2FA
"""
import paramiko
import socketserver
import select
import threading

class ForwardServer(socketserver.ThreadingTCPServer):
    """
    Server that manages the ssh tunnel
    """
    daemon_threads = True
    allow_reuse_address = True

class Handler(socketserver.BaseRequestHandler):
    """
    Class to manage initial tunneling request
    """
    @property
    def chan_host(self):
        return self.chan_host

    @property
    def chan_port(self):
        return self.chan_port

    @property
    def transport(self):
        return self.transport

    def handle(self):
        channel = None
        try:
            channel = self.transport.open_channel(
                "direct-tcpip", 
                (self.chan_host, self.chan_port), 
                self.request.getpeername()
            )
        except Exception as e:
            print("Request to {}:{} failed".format(self.chan_host, self.chan_port)) 
            return

        if channel is None:
            print("Request to {}:{} was rejected by the server".format(self.chan_host, self.chan_port)) 
            return

        print("Connected! Tunnel open {} -> {} -> {}".format(self.request.getpeername(), channel.getpeername(), (self.chan_host, self.chan_port)))

        while True:
            read_list = select.select([self.request, channel], [], [])[0]
            if self.request in read_list:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                channel.send(data)
            if channel in read_list:
                data = channel.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        peername = self.request.getpeername()
        channel.close()
        self.request.close()
        print("Tunnel closed from {}".format(peername))

class SSHTunnel:
    """
    This class creates a single ssh tunnel in the background

    @param username - username to login to the ssh server
    @param local_port - port on this machine you want to connect to the remote port
    @param hostname - name or ip address of the remote server
    @param remote_host - host we want to tunnel to within the remote server
    @param remote_port - port of the remote host we want to tunnel to 
    """
    def __init__(self, transport, local_port, remote_host, remote_port=22):
        self.transport = transport

        # initialize the fields of the handler using this subhandler class (we need to pass a class name into the forward server)
        class SubHandler(Handler):
            chan_host = remote_host
            chan_port = remote_port
            transport = self.transport

        self.forward_server = ForwardServer(("", local_port), SubHandler)
        self.is_active = False

    def _serve_forever_wrap(self, server):
        """ Wraps the serve_forever function to be run in a thread """
        server.serve_forever() 

    def start(self):
        """ Start the tunnel """
        if not self.is_active:
            thread = threading.Thread(
                target=self._serve_forever_wrap,
                args=(self.forward_server,),
                name='server'
            )
            
            self.is_active = True
            thread.daemon = True
            thread.start()

    def stop(self):
        """ Kill the tunnel """
        if self.is_active:
            self.forward_server.shutdown()
            self.forward_server.server_close()
            self.is_active = False

class SSHClient:
    def __init__(self, username, hostname):
        self.transport = paramiko.Transport(hostname)
        self.transport.connect(username=username)
        self.transport.auth_interactive_dumb(username)

        # create dict for forward servers
        self.forward_servers = {}

        # create sftp client
        self.sftp_client = paramiko.SFTPClient.from_transport(self.transport)

    def exec_command(self, command):
        channel = self.transport.open_session()
        channel.exec_command(command)
        stdin = channel.makefile_stdin("wb", -1) 
        stdout = channel.makefile("r", -1) 
        stderr = channel.makefile_stderr("r", -1) 
        return stdin, stdout, stderr

    def get_sftp_client(self):
        return self.sftp_client

    def start_tunnels(self):
        # start all tunnels
        for tunnel in self.forward_servers.values():
            tunnel.start()

    def stop_tunnels(self):
        # stop all tunnels
        for tunnel in self.forward_servers.values():
            tunnel.stop()

    def start_tunnel(self, local_port, remote_host, remote_port):
        if (local_port, remote_host, remote_port) not in self.forward_servers:
            self.create_tunnel(local_port, remote_host, remote_port)
        self.forward_servers[(local_port, remote_host, remote_port)].start()

    def stop_tunnel(self, local_port, remote_host, remote_port):
        if (local_port, remote_host, remote_port) in self.forward_servers:
            self.forward_servers[(local_port, remote_host, remote_port)].stop()

    def remove_tunnel(self, local_port, remote_host, remote_port):
        # stop tunnel, then remove from dict
        self.stop_tunnel(local_port, remote_host, remote_port)
        del self.forward_servers[(local_port, remote_host, remote_port)]

    def create_tunnel(self, local_port, remote_host, remote_port):
        self.forward_servers[(local_port, remote_host, remote_port)] = SSHTunnel(self.transport, local_port, remote_host, remote_port)

    @property
    def tunnels(self):
        return list(self.forward_servers.keys())


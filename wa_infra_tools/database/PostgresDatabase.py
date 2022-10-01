import psycopg2
from wa_infra_tools.ssh_utils.SSHTunnel import SSHTunnel

class PostgresDatabase:
    def __init__(self, cae_username, db_username='wa_admin', db_password='wa', dbname='wa', hostname='tux-133.cae.wisc.edu', remote_port=5432):
        local_port = 1234
        tunnel= SSHTunnel(username=cae_username, local_port=local_port, hostname=hostname, remote_host='localhost', remote_port=remote_port)
        tunnel.start()

        conn_string = "host='localhost' port='{}' dbname='{}' user='{}' password='{}'".format(local_port, dbname, db_username, db_password)
        print("Connecting to", conn_string)
        self.connection = psycopg2.connect(conn_string)

    

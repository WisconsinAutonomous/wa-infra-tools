from wa_infra_tools.ssh_utils import SSHClient
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", type=str)
    parser.add_argument("--hostname", type=str, default="tux-144.cae.wisc.edu")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    client = SSHClient(args.username, args.hostname)
    stdin, stdout, stderr = client.exec_command("cd /groupspace/studentorgs/wiautonomous/pgsql;chmod 0750 data;bin/pg_ctl start -D data -l logs/serverlog;tail logs/serverlog")
    print("Logs:\n")
    print("\n".join(stdout.readlines()))

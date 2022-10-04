# wa_infra_tools
This package contains tooling for Wisconsin Autonomous infra.

## Motivation and Goals
This package is meant to house any tools to assist in development for subteams. The initial motivation was to create a package to help manage data for the perception team. We've accomplished this by establishing a database on the CAE network and providing a python api (wa_infra_tools.database.PostgresDatabase) to interface with the database, allowing basic commands such as directly executing sql, inserting rows with images and downloading data.

In the future, we aim to continue improving on the database api by improving performance and adding more functionality (how do we sample data, asynchronous sending of files, etc). We also want to add a package to help the perception team optimize their GPU-trained models to be run on Intel CPUs using OpenVino. Finally, want to create an interface for recording and managing rosbags.

## How To Use
### Install
You can install the package locally by running `pip install .` in the root directory.
### Components and Examples
We have two main classes in the package right now, PostgresDatabase and SSHClient. SSHClient was built to support PostgresDatabase and manage the SSH connection to the CAE machine/port forwarding, but it can also be used independently for other projects that require SSH utility.
#### PostgresDatabase
```python3
from wa_infra_tools.database import PostgresDatabase

# create a connection to the remote database
db = PostgresDatabase('your_cae_username')

# view what tables are on the database
tables = db.tables

# get schema of a table
schema = db.get_schema('table_name')

# preview table
records = db.preview_table('table_name')

# execute a sql command and get the results
# NOTE: if you execute a mutation (insertion, creation, deletion, update) it will not be committed to the database until you call db.commit()
records = db.sql("some sql string")

# insert a row into a table
db.insert_row('table_name', {'col_name': col_val, ...})

# insert a row that contains an image
db.insert_row_with_image('table_name', {'col_name': col_val, ..., 'filepath': local_filepath_to_image})

# download data from a table (assumed you are downloading data in image/label pairs)
db.download_data('table_name', ['label_col_name_1', 'label_col_name_2', ...], 'output_path', 'format_type (only yolo so far)')

# if you want to join two tables and download the result (as it is common that images/labels are stored separately)
db.join_and_download_data('images_table_name', 'labels_table_name', ['label_col_name_1', 'label_col_name_2', ...], 'output_path', 'format_type (only yolo so far)')
```

#### SSHClient
```python3
from wa_infra_tools.ssh_utils import SSHClient

# create connection to a host
client = SSHClient('username', 'hostname')

# execute command via SSH on the remote machine
stdin, stdout, stderr = client.exec_command('command')

# get SFTP client to transfer  files
sftp = client.get_sftp_client()

# start a tunnel
client.start_tunnel(local_port, remote_host, remote_port)

# stop a tunnel
client.stop_tunnel(local_port, remote_host, remote_port)

# remove a tunnel
client.remove_tunnel(local_port, remote_host, remote_port)

# start all tunnels
client.start_tunnels()

# stop all tunnels
client.stop_tunnels()

# see what tunnels exist
tunnels = client.tunnels
```

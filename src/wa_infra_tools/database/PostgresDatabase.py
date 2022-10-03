"""
This file contains the PostgresDatabase class which connects the 
user to the database on CAE storage
"""
import psycopg2
import os
import time
import hashlib
from collections import defaultdict
from wa_infra_tools.ssh_utils.SSHClient import SSHClient

class PostgresDatabase:
    def __init__(self, cae_username, dbname='wa', db_username='wa_admin', db_password='wa', hostname='tux-133.cae.wisc.edu', local_port=1234, remote_port=5432):
        """
        Constructs a PostgresDatabase object by setting up SSH tunnel
        Note: the database runs on tux-133.cae.wisc.edu so hostname must be that machine (for now)

        @param cae_username : str   - username on cae network
        @param db_name : str        - database to connect to (default: wa)
        @param db_username : str    - username on database (default: wa_admin)
        @param db_password : str    - password on database (default: wa)
        @param hostname : str       - ip address or alias of host (default: tux-133.cae.wisc.edu)
        @param local_port : int     - port to use for tunneling on this machine (default: 1234)
        @param remote_port : int    - port of the database on the remote machine (default: 5432)
        """
        self.client = SSHClient(username=cae_username, hostname=hostname)
        self.client.start_tunnel(local_port=local_port, remote_host='localhost', remote_port=remote_port)

        self.uncomitted_image_paths = []

        conn_string = "host='localhost' port='{}' dbname='{}' user='{}' password='{}'".format(local_port, dbname, db_username, db_password)
        print("Connecting to", conn_string)
        try:
            self.connection = psycopg2.connect(conn_string)
            self.cursor = self.connection.cursor() 
        except:
            print("Failed to connect")
            self.client.stop_tunnels()

    def sql(self, sql_string):
        """
        Executes any sql command on the database

        @param sql_string : str     - string containing sql command
        @return List[Tuple[any...]] - list of the result of the query (if there is a response)
        """
        self.cursor.execute(sql_string)
        return self.cursor.fetchall() if self.cursor.pgresult_ptr is not None else []

    def commit(self):
        """
        Commits transaction on the sql database AND sends all images that were inserted into
        the database to the remote machine
        """
        self.connection.commit()
        for (local_filepath, remote_filepath, remote_filename) in self.uncomitted_image_paths:
            self._upload_image(local_filepath, remote_filepath, remote_filename)
        self.uncomitted_image_paths = []

    def get_schema(self, table_name):
        """
        Gets schema of any table in the database

        @param table_name : str - table name 
        """
        assert table_name in self.tables, f"Table {table_name} is not in the database"
        return self.sql(
            f"""
            SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
            """)

    def preview_table(self, table_name, limit=10):
        """
        Previews the data of any table in the database

        @param table_name : str - table name 
        @param limit : int      - number of rows to be shown (default: 10)
        """
        assert table_name in self.tables, f"Table {table_name} is not in the database"
        return self.sql(
            f"""
            SELECT * 
                FROM {table_name} 
                LIMIT {limit}
            """)

    def insert_row(self, table_name, value_dict):
        """
        Insert row into the database. Does not commit the insertion into the database until commit is called
        Note: This function will NOT prepare to send any images you want to insert
        upon commiting the transaction

        @param table_name : str             - table to insert into
        @param value_dict : Dict[str, any]  - dictionary of column name, value pairs to insert
        """
        self._check_schema(table_name, value_dict)
        col_names = []
        col_values = []
        for name, val in value_dict.items():
            col_names.append(name)
            col_values.append(str(val))

        self.sql(
            """
            INSERT INTO {} ({})
            VALUES ({})
            """.format(
                table_name,
                ", ".join(col_names),
                ", ".join(col_values)
            )
        )

    def insert_row_with_image(self, table_name, value_dict, image_id_col="image_id"):
        """
        Insert row into the database with image. Does not commit the insertion into the database or send the 
        image until commit is called

        @param table_name : str             - table to insert into
        @param value_dict : Dict[str, any]  - dictionary of column name, value pairs to insert
        @param image_id_col: str            - name of the id (primary key) column in the table (default: image_id)
        """
        assert "filepath" in value_dict, "The values you insert must contain a filepath attribute with the local filepath of the image"

        # get local filepath from values
        local_filepath = value_dict["filepath"]
        assert os.path.isfile(local_filepath), f"The path {local_filepath} to the image is invalid"

        # get image_id of the row we are going to insert
        image_id = self.sql(f"SELECT max({image_id_col}) FROM {table_name}")[0][0] or 0
        image_id += 1
        hash_val = str(hashlib.md5(repr(image_id).encode()).hexdigest())

        # generate filepath for the image to be stored
        image_extension = "." + value_dict["filepath"].split(".")[-1]
        cae_filepath = f"/groupspace/studentorgs/wiautonomous/pgsql/{table_name}/"
        for i in range(0, 26, 2): # md5 hashes are 32 hex digits long, we only want part of it to create the filepath
            cae_filepath += hash_val[i] + hash_val[i + 1] + "/"
        cae_filename = hash_val[26:] + image_extension

        # insert row into the database
        value_dict["filepath"] = "'" + cae_filepath + cae_filename + "'"
        self.insert_row(table_name, value_dict)
        self.uncomitted_image_paths.append((local_filepath, cae_filepath, cae_filename))

        return image_id 

    def download_data(self, table_name, label_column_names, output_path, format_type, image_id="image_id", filter_sql=[]):
        """
        Downloads data from existing table on the database. Executes and commits any filters from filter_sql 
        before downloading. Download format can be specified by format_type. Images and labels will be downloaded 
        to output_path/images and output_path/labels respectively.

        @param table_name : str                 - table name
        @param label_column_names : List[str]   - list containing the columns to be in the label file in order
        @param output_path : str                - path to save images/labels in
        @param format_type : str                - download format
        @param image_id : str                   - column that the two tables will be joined on
        @param filter_sql : List[str]           - list of sql queries to execute before joining the tables
        """
        for sql_op in filter_sql:
            self.sql(sql_op)
        self.commit()

        records = self.sql(f"SELECT * FROM {table_name}")

        column_names = {self.cursor.description[i][0] : i for i in range(len(self.cursor.description))}
        assert all([name in column_names for name in label_column_names]), "Invalid column name in label column names"

        if format_type == "yolo":
            self._download_data_yolo(records, label_column_names, column_names, output_path, image_id)

    def join_and_download_data(self, images_table_name, labels_table_name, label_column_names, output_path, format_type, image_id="image_id", filter_sql=[]):
        """
        Downloads data from the join of two tables (image table and labels table). Executes and commits
        any filters from filter_sql onto the table before the join. Download format can be specified
        by format_type. Images and labels will be downloaded to output_path/images and output_path/labels
        respectively.

        @param images_table_name : str          - table that contains the images
        @param labels_table_name : str          - table that contains the labels
        @param label_column_names : List[str]   - list containing the columns to be in the label file in order
        @param output_path : str                - path to save images/labels in
        @param format_type : str                - download format
        @param image_id : str                   - column that the two tables will be joined on
        @param filter_sql : List[str]           - list of sql queries to execute before joining the tables
        """
        temp_table_name = images_table_name + "_" + labels_table_name + "_tmp"
        filter_sql.append(
            f"""
            DROP TABLE IF EXISTS {temp_table_name};
            SELECT *
                INTO {temp_table_name}
                FROM {images_table_name}
                JOIN {labels_table_name}
                USING ({image_id})
            """
        )
        self.download_data(temp_table_name, label_column_names, output_path, format_type, image_id, filter_sql)
        self.sql(f"DROP TABLE {temp_table_name}")
        self.commit()

    def _download_data_yolo(self, records, label_column_names, column_names, output_path, image_id):
        """
        Data download specifically for yolo format

        @param records : List[Tuple[any...]]    - contents of a sql table containing a filepath column and all the label_column_names
        @param label_column_names : List[str]   - list containing the columns to be in the label file in order
        @param column_names: Dict[str, int]     - maps column names to their index in a row of the table
        @param output_path : str                - path to save images/labels in
        @param image_id : str                   - column that the two tables will be joined on
        """
        image_remote_filepaths = {}
        label_dict = defaultdict(str)
        for row in records:
            image_id_val = row[column_names[image_id]]
            if image_id_val not in image_remote_filepaths:
                image_remote_filepaths[image_id_val] = row[column_names["filepath"]]

            label = " ".join([str(row[column_names[name]]) for name in label_column_names])
            label_dict[image_id_val] += label + "\n"

        if output_path[-1] != "/":
            output_path += "/"
        if not os.path.exists(output_path + "images"):
            os.mkdir(output_path + "images")
        if not os.path.exists(output_path + "labels"):
            os.mkdir(output_path + "labels")

        print("Downloading images")
        for image_id_val, path in image_remote_filepaths.items():
            image_extension = "." + path.split(".")[-1]
            self._download_image(output_path + "images/" + str(image_id_val) + image_extension, path)

        print("Writing labels")
        for image_id_val, label_str in label_dict.items():
            with open(output_path + "labels/" + str(image_id_val) + ".txt", "w") as f:
                f.write(label_str)

    def _check_schema(self, table_name, value_dict):
        """
        Checks that the keys of the value dict are in the table schema

        @table_name : str - table name
        """
        assert table_name in self.tables, "Table name is not in the database"
        schema = self.get_schema(table_name)
        schema_dict = {col[0]: col[1] for col in schema}
        for col_name in value_dict.keys(): # iterate through columns in the val dict
            assert col_name in schema_dict, "Invalid column name in the value dictionary"
            if schema_dict[col_name] == "character varying": # if column is string type
                # make sure that the value is contained in ''
                new_val = value_dict[col_name]
                if new_val[0] != "'":
                    new_val = "'" + new_val
                if new_val[-1] != "'":
                    new_val += "'"
                value_dict[col_name] = new_val

    def _upload_image(self, local_filepath, remote_filepath, remote_filename):
        """ 
        Uploads image to the remote machine using SFTP

        @local_filepath : str   - path to image on local machine
        @remote_filepath : str  - where to store image on remote machine
        @remote_filename : str  - what to call file on remote machine
        """
        sftp = self.client.getSFTPClient()
        self.client.exec_command(f"mkdir -p '{remote_filepath}'")
        while True:
            try:
                sftp.put(local_filepath, remote_filepath + remote_filename)
                break
            except:
                time.sleep(0.1)

    def _download_image(self, local_filepath, remote_filepath):
        """ 
        Downloads image to the remote machine using SFTP

        @local_filepath : str   - where to store image on local machine
        @remote_filepath : str  - path to image on remote machine
        """
        sftp = self.client.getSFTPClient()
        sftp.stat(remote_filepath)
        while True:
            try:
                sftp.get(remote_filepath, local_filepath)
                break
            except:
                time.sleep(0.1)


    @property
    def tables(self):
        """
        Lists all the tables in the database
        """
        records = self.sql("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        return [record[0] for record in records]

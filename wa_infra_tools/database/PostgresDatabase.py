import psycopg2
import os
import hashlib
from wa_infra_tools.ssh_utils.SSHClient import SSHClient

class PostgresDatabase:
    def __init__(self, cae_username, db_username='wa_admin', db_password='wa', dbname='wa', hostname='tux-133.cae.wisc.edu', local_port=1234, remote_port=5432):
        self.client = SSHClient(username=cae_username, hostname=hostname)
        self.client.start_tunnel(local_port=local_port, remote_host='localhost', remote_port=remote_port)

        conn_string = "host='localhost' port='{}' dbname='{}' user='{}' password='{}'".format(local_port, dbname, db_username, db_password)
        print("Connecting to", conn_string)
        try:
            self.connection = psycopg2.connect(conn_string)
            self.cursor = self.connection.cursor() 
        except:
            self.client.stop_tunnels()

    def sql(self, sql_string):
        self.cursor.execute(sql_string)
        return self.cursor.fetchall()

    def get_schema(self, table_name):
        return self.sql(
            f"""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            """)

    def preview_table(self, table_name, limit=10):
        return self.sql(
            f"""
            SELECT * 
            FROM {table_name} 
            LIMIT {limit}
            """)

    def insert_row(self, table_name, values):
        self._check_schema(table_name, values)
        col_names = []
        col_values = []
        for name, val in values.items():
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
        self.connection.commit()

    def insert_row_with_image(self, table_name, values):
        self._check_schema(table_name, values)
        assert "filepath" in values, "The values you insert must contain a filepath attribute with the local filepath of the image"

        # get local filepath from values
        local_filepath = values["filepath"]
        assert os.path.isfile(local_filepath), f"The path {local_filepath} to the image is invalid"

        # get image_id of the row we are going to insert
        image_id = self.sql(f"SELECT COUNT(*) FROM {table_name}")[0][0] + 1
        hash_val = str(hashlib.md5(repr(image_id).encode()).hexdigest())

        # generate filepath for the image to be stored
        image_extension = "." + values["filepath"].split(".")[-1]
        cae_filepath = f"/groupspace/studentorgs/wiautonomous/pgsql/{table_name}/"
        for i in range(0, 26, 2): # md5 hashes are 32 hex digits long, we only want part of it to create the filepath
            cae_filepath += hash_val[i] + hash_val[i + 1] + "/"
        cae_filename = hash_val[26:] + image_extension

        # insert row into the database
        values["filepath"] = cae_filepath + cae_filename
        self.insert_row(table_name, values)

        # copy the image to the database
        self.client.exec_command(f"mkdir -p {cae_filepath}")
        sftp = self.client.createSFTPClient()
        sftp.put(local_filepath, cae_filepath + cae_filename)
        sftp.close()

        return image_id 

    def download_data(self, images_table_name, labels_table_name, output_path, format_type, filter_labels_sql=None):
        pass

    def _check_schema(self, table_name, value_dict):
        assert(table_name in self.tables)
        schema = self.get_schema(table_name)
        schema_col_names = {col[0] for col in schema}
        for name in set(value_dict.keys()):
            assert(name in schema_col_names)

    @property
    def tables(self):
        records = self.sql("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        return [record[0] for record in records]

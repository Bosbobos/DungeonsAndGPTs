import psycopg2
from psycopg2 import sql

class DbContext:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connect(self):
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    def create_record(self, table_name, record_data):
        conn = self.connect()
        cursor = conn.cursor()
        columns = ', '.join(record_data.keys())
        values = ', '.join(['%s' for _ in record_data.values()])
        query = sql.SQL(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")
        cursor.execute(query, tuple(record_data.values()))
        conn.commit()
        cursor.close()
        conn.close()

    def read_record(self, table_name, record_id):
        conn = self.connect()
        cursor = conn.cursor()
        query = sql.SQL(f"SELECT * FROM {table_name} WHERE id = %s")
        cursor.execute(query, (record_id,))
        record = cursor.fetchone()
        cursor.close()
        conn.close()
        return record

    def update_record(self, table_name, record_id, updates):
        conn = self.connect()
        cursor = conn.cursor()
        set_clause = ', '.join([f"{key} = %s" for key in updates.keys()])
        query = sql.SQL(f"UPDATE {table_name} SET {set_clause} WHERE id = %s")
        cursor.execute(query, tuple(updates.values()) + (record_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def delete_record(self, table_name, record_id):
        conn = self.connect()
        cursor = conn.cursor()
        query = sql.SQL(f"DELETE FROM {table_name} WHERE id = %s")
        cursor.execute(query, (record_id,))
        conn.commit()
        cursor.close()
        conn.close()

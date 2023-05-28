import sqlite3
import threading
# import datetime
from datetime import datetime

class Database:
    def __init__(self, dbname):
        self.lock = threading.Lock()
        self.dbname = dbname

    def execute_query(self, query, parameters=None):
        conn = sqlite3.connect(self.dbname, check_same_thread=False)
        cursor = conn.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        conn.commit()
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def create_table(self, table_name, columns):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.execute_query(query)

    def delete_all_records(self, table_name):
        query = f"DELETE FROM {table_name}"
        self.execute_query(query)

    def insert_record(self, table_name, values):
        placeholders = ",".join(["?" for _ in values])
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        self.execute_query(query, values)

    def update_record(self, table_name, set_column, set_value, where_column, where_value):
        query = f"UPDATE {table_name} SET {set_column} = ? WHERE {where_column} = ?"
        parameters = (set_value, where_value)
        self.execute_query(query, parameters)

    def delete_record(self, table_name, where_column, where_value):
        query = f"DELETE FROM {table_name} WHERE {where_column} = ?"
        parameters = (where_value,)
        self.execute_query(query, parameters)

    def select_table(self, table_name, filter_column=None, filter_value=None):
        if filter_column is not None and filter_value is not None:
            query = f"SELECT * FROM {table_name} WHERE {filter_column} = ?"
            parameters = (filter_value,)
        else:
            query = f"SELECT * FROM {table_name}"
            parameters = None
        rows = self.execute_query(query, parameters)
        return rows

    def search_record(self, table_name, search_column, search_value):
        query = f"SELECT * FROM {table_name} WHERE {search_column} LIKE ?"
        parameters = (f"%{search_value}%",)
        rows = self.execute_query(query, parameters)
        return rows

    def update_records(self, table_name, set_columns, set_values, where_column, where_value):
        set_clause = ", ".join([f"{col} = ?" for col in set_columns])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_column} = ?"
        parameters = [*set_values, where_value]
        self.execute_query(query, parameters)

    def get_last_record(self, table_name):
        query = f"SELECT * FROM {table_name} WHERE id = (SELECT MAX(id) FROM {table_name})"
        rows = self.execute_query(query)
        return rows[0] if rows else None

    def get_record_by_id(self, table_name, id_value):
        query = f"SELECT * FROM {table_name} WHERE id = ?"
        parameters = (id_value,)
        rows = self.execute_query(query, parameters)
        return rows[0] if rows else None

    def select_table_with_filters(self, table_name, filters={}, date_columns=None, from_dates=None, to_dates=None):
        filter_columns = []
        filter_values = []
        for column, value in filters.items():
            if isinstance (value, list):
                filter_columns.append(f"{column} IN ({','.join(['?' for _ in value])})")
                filter_values.extend(value)
            else:
                filter_columns.append(f"{column} = ?")
                filter_values.append(value)
        date_filters = []
        if date_columns is not None and from_dates is not None and to_dates is not None:
            for i in range(len(date_columns)):
                date_column = date_columns[i]
                from_date = from_dates[i]
                to_date = to_dates[i]
                date_filter = f"{date_column} BETWEEN ? AND ?"
                date_filters.append(date_filter)
                filter_values.append(from_date)
                filter_values.append(to_date)

        if len(filter_columns) > 0 and len(date_filters) > 0:
            where_clause = " WHERE " + " AND ".join(filter_columns) + " AND (" + " OR ".join(date_filters) + ")"
        elif len(filter_columns) > 0:
            where_clause = " WHERE " + " AND ".join(filter_columns)
        elif len(date_filters) > 0:
            where_clause = " WHERE " + " OR ".join(date_filters)
        else:
            where_clause = ""

        query = f"SELECT * FROM {table_name}" + where_clause
        rows = self.execute_query(query, filter_values)
        return rows

    def add_column_to_table(self, table_name, column_name, column_type):
        try:
            query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            self.execute_query(query)
            print(f"Column '{column_name}' added to table '{table_name}'")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column '{column_name}' already exists in table '{table_name}'. Skipping column creation.")
            else:
                raise e


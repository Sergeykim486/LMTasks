import sqlite3
import threading
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
   
    def get_column_names(self, table_name):
        conn = sqlite3.connect(self.dbname, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        conn.close()
        column_names = [column[1] for column in columns]
        return column_names
    
    def select_table_with_filters(self, table_name, filters={}, date_columns=None, from_dates=None, to_dates=None):
        if not filters:
            return self.select_table(table_name)

        filter_conditions = []
        parameters = []

        col_indexes = []

        for column, value in filters.items():
            filter_conditions.append(f"{column} = ?")
            parameters.append(value)

        if date_columns:
            column_names = self.get_column_names(table_name)
            for column in date_columns:
                if column in column_names:
                    col_indexes.append(column_names.index(column))

        query = f"SELECT * FROM {table_name} WHERE {' AND '.join(filter_conditions)}"
        rows = self.execute_query(query, parameters)
        
        result_rows = []

        if date_columns is not None and from_dates is not None and to_dates is not None:
            for row in rows:
                include_row = True
                ind = 0
                for i in col_indexes:
                    date_value = datetime.strptime(row[i], "%d.%m.%Y %H:%M")
                    from_date = datetime.strptime(from_dates[ind], "%d.%m.%Y %H:%M")
                    to_date = datetime.strptime(to_dates[ind], "%d.%m.%Y %H:%M")
                    ind = ind + 1
                    if not (from_date <= date_value <= to_date):
                        include_row = False
                        break
                if include_row:
                    result_rows.append(row)
        else:
            result_rows = rows

        return result_rows
import sqlite3
import threading
from datetime import datetime

class Database:
    def __init__(self, dbname):
        self.lock = threading.Lock()
        self.conn = None
        self.cur = None
        self.dbname = dbname
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
        self.cur = self.conn.cursor()

    def create_table(self, table_name, columns):
        with self.lock:
            self.cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")
            self.conn.commit()

    def delete_all_records(self, table_name):
        with self.lock:
            self.cur.execute(f"DELETE FROM {table_name}")
            self.conn.commit()

    def insert_record(self, table_name, values):
        with self.lock:
            vals = ",".join(["?" for _ in values])
            self.cur.execute(f"INSERT INTO {table_name} VALUES ({vals})", values)
            self.conn.commit()

    def update_record(self, table_name, set_column, set_value, where_column, where_value):
        with self.lock:
            self.cur.execute(
                f"UPDATE {table_name} SET {set_column} = ? WHERE {where_column} = ?",
                (set_value, where_value),
            )
            self.conn.commit()

    def delete_record(self, table_name, where_column, where_value):
        with self.lock:
            self.cur.execute(
                f"DELETE FROM {table_name} WHERE {where_column} = ?", (where_value,)
            )
            self.conn.commit()

    def select_table(self, table_name, filter_column=None, filter_value=None):
        with self.lock:
            if filter_column is not None and filter_value is not None:
                self.cur.execute(
                    f"SELECT * FROM {table_name} WHERE {filter_column} = ?", (filter_value,)
                )
            else:
                self.cur.execute(f"SELECT * FROM {table_name}")
            rows = self.cur.fetchall()
            return rows

    def search_record(self, table_name, search_column, search_value):
        with self.lock:
            self.cur.execute(
                f"SELECT * FROM {table_name} WHERE {search_column} LIKE ?",
                (f"%{search_value}%",),
            )
            rows = self.cur.fetchall()
            return rows

    def update_records(self, table_name, set_columns, set_values, where_column, where_value):
        with self.lock:
            set_clause = ", ".join([f"{col} = ?" for col in set_columns])
            self.cur.execute(
                f"UPDATE {table_name} SET {set_clause} WHERE {where_column} = ?",
                (*set_values, where_value),
            )
            self.conn.commit()

    def get_last_record(self, table_name):
        with self.lock:
            self.cur.execute(f"SELECT * FROM {table_name} WHERE id = (SELECT MAX(id) FROM {table_name})")
            row = self.cur.fetchone()
            return row

    def get_record_by_id(self, table_name, id_value):
        with self.lock:
            self.cur.execute(f"SELECT * FROM {table_name} WHERE id=?", (id_value,))
            row = self.cur.fetchone()
            return row
    
    def select_table_with_filters(self, table_name, filters={}, date_columns=None, from_dates=None, to_dates=None):
        with self.lock:
            filter_columns = []
            filter_values = []
            for column, value in filters.items():
                if isinstance(value, list):
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
            self.cur.execute(query, filter_values)
            rows = self.cur.fetchall()
            return rows
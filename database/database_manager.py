import sqlite3


class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name

    def commit_query(self, query):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()

    def select_query(self, query):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def select_single_return(self, query):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            return cursor.fetchone()

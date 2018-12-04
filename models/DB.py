import os
import sqlite3
from config import database_settings


class DB(object):
    def __init__(self):
        path = os.path.abspath(os.path.join(database_settings['location'], database_settings['database_name']))
        self.database_connection = sqlite3.connect(path, isolation_level=None)
        self.cursor = self.database_connection.cursor()

    def fetch_all(self, query, params=None):
        self.cursor.execute(query, params if params else [])
        return self.cursor.fetchall()

    def fetch_many(self, query, params):
        self.cursor.executemany(query, params if params else [])
        return self.cursor.fetchall()

    def fetch_one(self, query, params=None):
        self.cursor.execute(query, params if params else [])
        return self.cursor.fetchone()

    def insert_multiple(self, query, params):
        self.cursor.executemany(query, params)

    def insert_return_id(self, query, params):
        self.cursor.execute(query, params)
        return self.cursor.lastrowid

    def execute(self, query, params=None):
        """LEGACY USE OTHER METHODS"""
        self.cursor.execute(query, params if params else [])

    def execute_many(self, query, params=None):
        """LEGACY USE OTHER METHODS"""
        self.cursor.executemany(query, params if params else [])



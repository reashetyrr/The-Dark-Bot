import os
import sqlite3
import mysql.connector
from config import database_settings


class DB(object):
    def __init__(self):
        if database_settings['type'] == 'sqlite3':
            path = os.path.abspath(os.path.join(database_settings['location'], database_settings['database_name']))
            self.database_connection = sqlite3.connect(path, isolation_level=None)
            self.cursor = self.database_connection.cursor()
        elif database_settings['type'] == 'mysql':
            self.database_connection = mysql.connector.connect(user=database_settings['username'], password=database_settings['password'], host=database_settings['location'], database=database_settings['database'], autocommit=True)
            self.database_connection.set_charset_collation(charset='utf8mb4')
            self.cursor = self.database_connection.cursor()

    def fetch_all(self, query, params=None):
        self.cursor.execute(query, params if params else [])
        results = self.cursor.fetchall()
        return results

    def fetch_many(self, query, params):
        self.cursor.executemany(query, params if params else [])
        results = self.cursor.fetchall()
        return results

    def fetch_one(self, query, params=None):
        self.cursor.execute(query, params if params else [])
        results = self.cursor.fetchone()
        return results

    def insert_multiple(self, query, params):
        self.cursor.executemany(query, params)

    def insert_return_id(self, query, params):
        self.cursor.execute(query, params)
        result = self.cursor.lastrowid
        return result

    def execute(self, query, params=None):
        """LEGACY USE OTHER METHODS"""
        self.cursor.execute(query, params if params else [])

    def execute_many(self, query, params=None):
        """LEGACY USE OTHER METHODS"""
        self.cursor.executemany(query, params if params else [])

    def ping(self):
        return self.database_connection.ping()

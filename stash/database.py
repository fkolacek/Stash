#
# Author: Frantisek Kolacek <work@kolacek.it
# Version: 1.0
#

import logging
import sqlite3
from datetime import datetime

from .exception import StashDatabaseException


class StashDatabase:

    config = None
    connection = None
    cursor = None

    def __init__(self, **config):
        try:
            self.config = config
            self.connection = sqlite3.connect(self.config['name'])
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()

            self.create_schema()
        except sqlite3.Error as e:
            raise StashDatabaseException(e) from None

    def close(self):
        if self.connection:
            self.connection.commit()
            self.cursor.close()
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create_schema(self):
        logging.info('Checking/creating DB schema')

        self.query("""CREATE TABLE IF NOT EXISTS repos (
                      id INTEGER PRIMARY KEY,
                      name TEXT NOT NULL,
                      type TEXT NOT NULL,
                      remote TEXT NOT NULL,
                      description TEXT,
                      created TEXT,
                      updated TEXT,
                      score INTEGER DEFAULT 0);""")

        self.query("""CREATE TABLE IF NOT EXISTS tokens (
                      id INTEGER PRIMARY KEY,
                      token TEXT NOT NULL UNIQUE);""")

        token = self.config.get('token')
        if token and not self.is_token(token):
            self.query('INSERT INTO tokens (token) VALUES (?)', [token])

    def is_token(self, token):
        return self.query_exists('SELECT COUNT(*) FROM tokens WHERE token = ?', [token])

    def is_repo(self, id):
        return self.query_exists('SELECT COUNT(*) FROM repos WHERE id = ?', [id])

    def add_repo(self, name, type, remote, description):
        sql = 'INSERT INTO repos (name, type, remote, description, created, score) VALUES (?, ?, ?, ?, ?, ?)'

        self.query(sql, [name, type, remote, description, self.get_now(), 0])

    def del_repo(self, id):
        self.query('DELETE FROM repos WHERE id = ?', [id])

    def get_repo(self, id):
        if not self.is_repo(id):
            return None

        result = self.query('SELECT id, name, type, remote, description, created, updated, score FROM repos WHERE id = ?', [id])

        return self.dict_from_row(result.fetchone())

    def get_repos(self):
        repos = []
        result = self.query('SELECT id, name, type, remote, description, created, updated, score FROM repos')
        for repo in result.fetchall():
            repos.append(self.dict_from_row(repo))

        return repos

    def query(self, sql, args=None):
        args = [] if args is None else args
        logging.debug('Executing: {} [{}]'.format(sql, ','.join(str(v) for v in args)))

        data = self.cursor.execute(sql, args)

        self.connection.commit()

        return data

    def query_exists(self, sql, args=None):
        args = [] if args is None else args

        return self.query(sql, args).fetchone()[0] > 0

    @staticmethod
    def get_now():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def dict_from_row(row):
        return dict(zip(row.keys(), row))

""" 
Created by
@author: tao.zhan
@time: 15/3/22 8:03 PM
"""

import pymysql
from config import conf


class DB(object):

    def __init__(self):
        self.host = conf.get_config('DB', 'host')
        self.user = conf.get_config('DB', 'user')
        self.password = conf.get_config('DB', 'password')
        self.db = conf.get_config('DB', 'database')
        self.port = int(conf.get_config('DB', 'port'))
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        if self.conn is None:
            self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db,
                                        port=self.port, charset='utf8mb4')
            self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def execute_one(self, sql, args=None):
        self.connect()
        effect_count = self.cursor.execute(sql, args)
        self.conn.commit()
        return effect_count, self.cursor.fetchall()

    def execute_many(self, sql, args=None):
        self.connect()
        effect_count = self.cursor.executemany(sql, args)
        self.conn.commit()
        return effect_count, self.cursor.fetchall()


db = DB()

""" 
Created by
@author: tao.zhan
@time: 15/3/22 3:59 PM
"""

import configparser
import os


BASE_PATH = os.path.abspath(os.path.join(os.getcwd(), "../.."))


class Config(object):

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(BASE_PATH + "/conf/config.ini")

    def get_config(self, section, key):
        return self.config[section][key]

    def get(self, section, key):
        return self.config.get(section, key, fallback=None)


conf = Config()

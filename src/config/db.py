import threading
import sqlite3
import os
import time
import traceback
import ujson as json

import constants
from common import variable
from .utils.logger import logger


DB_DIR = os.path.join(variable.dir_data, "db")

if not os.path.exists(DB_DIR):
    try:
        os.makedirs(DB_DIR)
    except:
        pass


class Cache:
    def __init__(self):
        # 创建线程本地存储对象
        self.LocalTreading = threading.local()
        self.DataBaseFilePath = os.path.join(DB_DIR, constants.FILE_NAMES.DB.CACHE)
        return

    def init(self):
        connection = sqlite3.connect(self.DataBaseFilePath)
        # 创建一个游标对象
        cursor = connection.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS cache
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,
    key TEXT NOT NULL,
    data TEXT NOT NULL)"""
        )

        connection.close()

    def handleGetConnection(self):
        # 检查线程本地存储对象是否存在连接对象，如果不存在则创建一个新的连接对象
        if not hasattr(self.LocalTreading, "connection"):
            self.LocalTreading.connection = sqlite3.connect(self.DataBaseFilePath)
        return self.LocalTreading.connection

    def handleGetCache(self, module, key):
        try:
            # 连接到数据库（如果数据库不存在，则会自动创建）
            connection = self.handleGetConnection()
            # 创建一个游标对象
            cursor = connection.cursor()

            cursor.execute(
                "SELECT data FROM cache WHERE module=? AND key=?", (module, key)
            )

            result = cursor.fetchone()
            if result:
                cache_data = json.loads(result[0])
                if not cache_data["expire"]:
                    return cache_data
                if int(time.time()) < cache_data["time"]:
                    return cache_data
        except:
            pass
        return False

    def handleUpdateCache(self, module, key, data):
        try:
            # 连接到数据库（如果数据库不存在，则会自动创建）
            connection = self.handleGetConnection()
            # 创建一个游标对象
            cursor = connection.cursor()

            cursor.execute(
                "SELECT data FROM cache WHERE module=? AND key=?", (module, key)
            )

            result = cursor.fetchone()
            if result:
                cache_data = json.loads(result[0])
                if isinstance(cache_data, dict):
                    cache_data.update(data)
                else:
                    logger.error(
                        f"Cache data for module '{module}' and key '{key}' is not a dictionary."
                    )
            else:
                cursor.execute(
                    "INSERT INTO cache (module, key, data) VALUES (?, ?, ?)",
                    (module, key, json.dumps(data)),
                )

            connection.commit()
        except:
            logger.error("缓存写入遇到错误…")
            logger.error(traceback.format_exc())


class Data:
    def __init__(self):
        # 创建线程本地存储对象
        self.LocalTreading = threading.local()
        self.DataBaseFilePath = os.path.join(DB_DIR, constants.FILE_NAMES.DB.DATA)
        return

    def init(self):
        connection = sqlite3.connect(self.DataBaseFilePath)
        # 创建一个游标对象
        cursor = connection.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS data
    (key TEXT PRIMARY KEY,
    value TEXT)"""
        )

        connection.close()

    def handleGetConnection(self):
        # 检查线程本地存储对象是否存在连接对象，如果不存在则创建一个新的连接对象
        if not hasattr(self.LocalTreading, "connection"):
            self.LocalTreading.connection = sqlite3.connect(self.DataBaseFilePath)
        return self.LocalTreading.connection

    def handleLoadData(self):
        config_data = {}
        try:
            # Connect to the database
            connection = self.handleGetConnection()
            cursor = connection.cursor()

            # Retrieve all configuration data from the 'config' table
            cursor.execute("SELECT key, value FROM data")
            rows = cursor.fetchall()

            for row in rows:
                key, value = row
                config_data[key] = json.loads(value)

        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            logger.error(traceback.format_exc())

        return config_data

    def handleSaveData(self, config_data):
        try:
            # Connect to the database
            connection = self.handleGetConnection()
            cursor = connection.cursor()

            # Clear existing data in the 'data' table
            cursor.execute("DELETE FROM data")

            # Insert the new configuration data into the 'data' table
            for key, value in config_data.items():
                cursor.execute(
                    "INSERT INTO data (key, value) VALUES (?, ?)",
                    (key, json.dumps(value)),
                )

            connection.commit()

        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            logger.error(traceback.format_exc())

    def readData(self, key):
        config = self.handleLoadData()
        keys = key.split(".")
        value = config
        for k in keys:
            if k not in value and keys.index(k) != len(keys) - 1:
                value[k] = {}
            elif k not in value and keys.index(k) == len(keys) - 1:
                value = None
            value = value[k]

        return value

    def writeData(self, key, value):
        config = self.handleLoadData()

        keys = key.split(".")
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

        self.handleSaveData(config)

    def pushToList(self, key, obj):
        config = self.handleLoadData()

        keys = key.split(".")
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        if keys[-1] not in current:
            current[keys[-1]] = []

        current[keys[-1]].append(obj)

        self.handleSaveData(config)

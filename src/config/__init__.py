# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: config.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you know what you are doing.

import time
import os
import traceback

from common import variable
from .utils.logger import logger
from .default import DefaultConfig
from .user import UserConfig
from .db import Cache, Data


class ConfigReadException(Exception):
    pass


config_user = UserConfig()
config_default = DefaultConfig()

db_cache = Cache()
db_data = Data()


def resetRequestTime(ip):
    config_data = db_data.handleLoadData()
    try:
        try:
            config_data["requestTime"][ip] = 0
        except KeyError:
            config_data["requestTime"] = {}
            config_data["requestTime"][ip] = 0
        db_data.handleSaveData(config_data)
    except:
        logger.error("配置写入遇到错误…")
        logger.error(traceback.format_exc())


def updateRequestTime(ip):
    try:
        config_data = db_data.handleLoadData()
        try:
            config_data["requestTime"][ip] = time.time()
        except KeyError:
            config_data["requestTime"] = {}
            config_data["requestTime"][ip] = time.time()
        db_data.handleSaveData(config_data)
    except:
        logger.error("配置写入遇到错误...")
        logger.error(traceback.format_exc())


def getRequestTime(ip):
    config_data = db_data.handleLoadData()
    try:
        value = config_data["requestTime"][ip]
    except:
        value = 0
    return value


def handleInit():
    # 加载配置
    config_default.init()
    config_user.init(config_default.readRawConfig())

    variable.log_length_limit = (
        config_user.handleGetConfig("common.log_length_limit") or 500
    )
    variable.debug_mode = config_user.handleGetConfig("common.debug_mode") or False
    logger.debug("配置文件加载成功")

    # 加载数据库
    db_cache.init()
    db_data.init()
    logger.debug("数据库初始化成功")

    if db_data.handleLoadData() == {}:
        db_data.writeData("banList", [])
        db_data.writeData("requestTime", {})
        logger.info("数据库内容为空，已写入默认值")

    # 处理代理配置
    if config_user.handleGetConfig("common.proxy.enable"):
        if config_user.handleGetConfig("common.proxy.http_value"):
            os.environ["http_proxy"] = config_user.handleGetConfig(
                "common.proxy.http_value"
            )
            logger.info(
                "HTTP协议代理地址: " + config_user.handleGetConfig("common.proxy.http_value")
            )

        if config_user.handleGetConfig("common.proxy.https_value"):
            os.environ["https_proxy"] = config_user.handleGetConfig(
                "common.proxy.https_value"
            )
            logger.info(
                "HTTPS协议代理地址: "
                + config_user.handleGetConfig("common.proxy.https_value")
            )

        logger.info("代理功能已开启，请确保代理地址正确，否则无法连接网络")


def ban_ip(ip_addr, ban_time=-1):
    if config_user.handleGetConfig("security.banlist.enable"):
        banList = db_data.readData("banList")
        banList.append(
            {
                "ip": ip_addr,
                "expire": config_user.handleGetConfig("security.banlist.expire.enable"),
                "expire_time": config_user.handleGetConfig(
                    "security.banlist.expire.length"
                )
                if (ban_time == -1)
                else ban_time,
            }
        )
        db_data.writeData("banList", banList)
    else:
        if variable.banList_suggest < 10:
            variable.banList_suggest += 1
            logger.warning("黑名单功能已被关闭，我们墙裂建议你开启这个功能以防止恶意请求")


def check_ip_banned(ip_addr):
    if config_user.handleGetConfig("security.banlist.enable"):
        banList = db_data.readData("banList")
        for ban in banList:
            if ban["ip"] == ip_addr:
                if ban["expire"]:
                    if ban["expire_time"] > int(time.time()):
                        return True
                    else:
                        banList.remove(ban)
                        db_data.writeData("banList", banList)
                        return False
                else:
                    return True
            else:
                return False
        return False
    else:
        if variable.banList_suggest <= 10:
            variable.banList_suggest += 1
            logger.warning("黑名单功能已被关闭，我们墙裂建议你开启这个功能以防止恶意请求")
        return False


handleInit()

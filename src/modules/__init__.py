# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: __init__.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you konw what you are doing.

from common.exceptions import FailedException
from common.utils import require, CreateObject
from common import log
import config
import traceback
import time

from . import kg
from . import kw
from . import tx
from . import wy
from . import mg

logger = log.log("api_handler")

sourceExpirationTime = {
    "tx": {
        "expire": True,
        "time": 15 * 60 * 60,  # 15 hours
    },
    "kg": {
        "expire": True,
        "time": 15 * 60 * 60,  # 15 hours
    },
    "kw": {"expire": True, "time": 30 * 60},  # 30 minutes
    "wy": {
        "expire": True,
        "time": 10 * 60,  # 10 minutes
    },
    "mg": {
        # no expiration
        "expire": False,
        "time": 0,
    },
}


async def handleApiRequest(command, source, songId, quality):
    id = f"{source}_{songId}_{quality}"

    try:
        func = require("modules." + source + "." + command)
    except:
        return {
            "code": 1,
            "msg": "未知的源或命令",
            "data": None,
            "extra": None,
        }

    try:
        cache = config.db_cache.handleGetCache("urls", id)
        if cache:
            result = CreateObject(cache)
            logger.debug(f"使用缓存 [{source}_{songId}_{quality}]\nURL: {result.url}")
            return {
                "code": 0,
                "msg": "success",
                "data": result.url,
                "extra": {
                    "cache": True,
                    "quality": {
                        "target": quality,
                        "result": quality,
                    },
                },
            }
    except:
        logger.error(traceback.format_exc())

    try:
        raw = await func(songId, quality)
        result = CreateObject(raw)

        print(config.config_user.handleGetConfig("common.reject_unmatched_quality"))
        if config.config_user.handleGetConfig("common.reject_unmatched_quality"):
            print(result.quality, quality)
            if result.quality != quality:
                return {
                    "code": 7,
                    "msg": f"获取目标音质[{quality}]失败",
                    "data": None,
                    "extra": None,
                }

        logger.debug(f"获取URL成功 [{id}]\nURL: {result.url}")

        canExpire = sourceExpirationTime[source]["expire"]
        expireTime = sourceExpirationTime[source]["time"] + int(time.time())
        config.db_cache.handleUpdateCache(
            "urls",
            id,
            {
                "expire": canExpire,
                "time": expireTime,
                "url": result.url,
            },
        )
        logger.debug(f"缓存更新 [{id}]\nURL: {result.url}\nexpire: {expireTime}")

        return {
            "code": 0,
            "msg": "success",
            "data": result.url,
            "extra": {
                "cache": False,
                "quality": {
                    "target": quality,
                    "result": result["quality"],
                },
                "expire": {
                    "time": expireTime,
                    "canExpire": canExpire,
                },
            },
        }
    except FailedException as e:
        return {"code": 2, "msg": e.args[0], "data": None, "extra": None}

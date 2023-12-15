import os
import yaml
import constants

from common import variable
from ..utils.logger import logger


USER_CONFIG_FILE_PATH = os.path.join(
    variable.dir_work, constants.CONFIG.FILE_NAMES.USER
)


class UserConfig:
    # 初始化
    def init(self, rawDefaultConfig):
        config = self.handleReadConfig()

        if config is None:
            print("读取配置文件失败，使用默认配置文件")
            config = variable.config_default
            self.handleWriteDefaultConfig(rawDefaultConfig)

        variable.config_user = config
        return

    def handleWriteDefaultConfig(self, rawConfig):
        with open(USER_CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(rawConfig)
            f.close()

        if not os.getenv("build"):
            logger.info("首次启动或配置文件被删除，已创建默认配置文件")
            logger.info(
                f"\n建议您到{variable.dir_work + os.path.sep}config.yaml修改配置后重新启动服务器"
            )

    def handleWriteConfig(self, config):
        with open(USER_CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=None)
            f.close()

    def handleReadConfig(self):
        config = None

        try:
            with open(USER_CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                f.close()
        except FileNotFoundError:
            config = None
            pass

        return config

    def handleGetConfig(self, key):
        try:
            keys = key.split(".")
            value = variable.config_user

            for k in keys:
                if isinstance(value, dict):
                    if k not in value and keys.index(k) != len(keys) - 1:
                        value[k] = {}
                    elif k not in value and keys.index(k) == len(keys) - 1:
                        value = None
                    value = value[k]
                else:
                    value = None
                    break

            return value
        except:
            logger.warning(f"配置文件{key}不存在")
            return None

    def handleUpdateConfig(self, key, value):
        config = self.handleReadConfig()

        keys = key.split(".")
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        variable.config = config

        self.handleWriteConfig(config)


# def read_config(key):
#     try:
#         config = variable.config
#         keys = key.split(".")
#         value = config
#         for k in keys:
#             if isinstance(value, dict):
#                 if k not in value and keys.index(k) != len(keys) - 1:
#                     value[k] = {}
#                 elif k not in value and keys.index(k) == len(keys) - 1:
#                     value = None
#                 value = value[k]
#             else:
#                 value = None
#                 break

#         return value
#     except:
#         default_value = default.handleGetDefaultConfig(key)
#         if isinstance(default_value, type(None)):
#             logger.warning(f"配置文件{key}不存在")
#         else:
#             for i in range(len(keys)):
#                 tk = ".".join(keys[: (i + 1)])
#                 tkvalue = _read_config(tk)
#                 logger.debug(f"configfix: 读取配置文件{tk}的值：{tkvalue}")
#                 if (tkvalue is None) or (tkvalue == {}):
#                     write_config(tk, default.handleGetDefaultConfig(tk))
#                     logger.info(f"配置文件{tk}不存在，已创建")
#                     return default_value

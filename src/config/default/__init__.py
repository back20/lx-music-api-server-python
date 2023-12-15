import os
import yaml
import constants

from common import variable
from common import utils
from ..utils.logger import logger


DEFAULT_CONFIG_FILE_PATH = os.path.join(
    os.path.dirname(__file__), constants.CONFIG.FILE_NAMES.DEFAULT
)


class DefaultConfig:
    def init(self):
        config = self.readConfig()
        variable.config_default = config

    # 检查配置文件是否加载
    def _checkConfigInit(self):
        if variable.config_default is None:
            return

    # 读取配置文件
    def readConfig(self):
        config = None

        try:
            with open(DEFAULT_CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                f.close()
        except FileNotFoundError:
            logger.error("默认配置文件丢失，请检查项目完整性")
            utils.handleExit()

        return config

    # 读取原始配置文件
    def readRawConfig(self):
        config = None

        try:
            with open(DEFAULT_CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                config = f.read()
                f.close()
        except FileNotFoundError:
            logger.error("默认配置文件丢失，请检查项目完整性")
            utils.handleExit()

        return config

    # 读取配置
    def getConfigByKey(self, key):
        self._checkConfigInit()
        try:
            keys = key.split(".")
            value = variable.default_config

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


# def handleWriteDefaultConfig(path="./config.yaml"):
#     defaultFilePath = os.path.abspath(
#         os.path.dirname(os.path.abspath(__file__)) + "./default.yaml"
#     )
#     defaultConfig = None

#     with open(defaultFilePath, "r", encoding="utf-8") as f:
#         defaultConfig = f.read()
#         f.close()

#     with open(path, "w", encoding="utf-8") as f:
#         f.write(defaultConfig)
#         f.close()

#     if not os.getenv("build"):
#         logger.info("首次启动或配置文件被删除，已创建默认配置文件")
#         logger.info(f"\n建议您到{variable.workdir + os.path.sep}config.yaml修改配置后重新启动服务器")

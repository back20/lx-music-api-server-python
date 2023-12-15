from common import utils


CONFIG = utils.CreateObject(
    {
        "FILE_NAMES": {
            "DEFAULT": "default.yaml",
            "USER": "config.yaml",
        }
    }
)

FILE_NAMES = utils.CreateObject(
    {
        "CONFIG": {
            "DEFAULT": "default.yaml",
            "USER": "config.yaml",
        },
        "DB": {
            "CACHE": "cache.db",
            "DATA": "data.db",
        },
    }
)

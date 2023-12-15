# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: variable.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you know what you are doing.

import os


debug_mode = False
log_length_limit = 500
running = True
config = {}
default_config = None
workdir = os.getcwd()
banList_suggest = 0
iscn = True
fake_ip = None

config_default = None
config_user = None

dir_work = os.getcwd()
dir_data = os.path.join(dir_work, "data")

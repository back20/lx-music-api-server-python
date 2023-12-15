#!/usr/bin/env python3

# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: main.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import sys
import argparse

# 设置根目录
sys.path.insert(0, "./src")


parser = argparse.ArgumentParser()
parser.add_argument("--env", type=str, help="环境 (会决定使用Flask还是AioHttp)")
args = parser.parse_args()

if __name__ == "__main__":
    if args.env == "development":
        import src.dev
    else:
        import src.prod

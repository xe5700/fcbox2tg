# -*- coding:utf-8 -*-
from typing import List

import requests
from dataclasses_json import dataclass_json
from dataclasses import dataclass, field
import logging
from os import path
import os
import uuid
import myrandom
from appcfg import *


cfg_data: Config


def main():
    print("""
.########..######..########...#######..##.....##..#######..########..######..
.##.......##....##.##.....##.##.....##..##...##..##.....##....##....##....##.
.##.......##.......##.....##.##.....##...##.##..........##....##....##.......
.######...##.......########..##.....##....###.....#######.....##....##...####
.##.......##.......##.....##.##.....##...##.##...##...........##....##....##.
.##.......##....##.##.....##.##.....##..##...##..##...........##....##....##.
.##........######..########...#######..##.....##.#########....##.....######..
    """)
    logging.basicConfig(level=logging.INFO)
    logging.info("丰巢推送机器人")
    global cfg_data
    cfg_data = Config(device=str(uuid.uuid4()).replace("-", "")[:16],
                      ip=myrandom.生成随机内网地址(),
                      token=""
                      )
    logging.info("正在载入配置文件")
    if path.exists("config.json"):
        with open("config.json", mode="r", encoding="utf-8") as f:
            cfg_data = Config.from_json(f.read())
    else:
        with open("config.json", mode="w+", encoding="utf-8") as f:
            f.write(cfg_data.to_json(indent=4, ensure_ascii=False))
    if cfg_data.token == "":
        logging.error("未设置丰巢的token,无法运行此程序。")
        return -1
    return 0


if __name__ == "__main__":
    exit(main())

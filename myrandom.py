# -*- coding:utf-8 -*-
import random

rd_1 = range(1, 255)
rd_2 = range(1, 256)
rd_3 = range(1, 1000)


def 生成随机内网地址():
    return "192.168.{}.{}".format(random.choice(rd_2), random.choice(rd_1))


def 生成随机毫秒():
    return random.choice(rd_3)
# -*- coding:utf-8 -*-
from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class TG丰巢推送:
    chatids: List[str] = field(default_factory=list)
    token: str = ""
    enabled: bool = False


@dataclass_json
@dataclass
class SMTP丰巢推送:
    server: str = "smtp.qq.com"
    port: int = 553
    ssl: bool = True
    sender: str = "who@email.com"
    recivers: List[str] = field(default_factory=list)
    enabled: bool = False


@dataclass_json
@dataclass
class Config:
    device: str
    ip: str
    token: str
    fc_ver_code: str = "2029000"
    fc_ver_name: str = "2.29.0"
    user_agent: str = "channel=yingyongbao,deviceId={device_id},ip={ip},mac=02:00:00:00:00:00," \
                      "os=7.1.2,platform=Android,resolution=1080*1920,versionCode={fc_code},versionName={fc_ver}"
    telegram: TG丰巢推送 = TG丰巢推送()
    smtp: SMTP丰巢推送 = SMTP丰巢推送()


__all__ = ["Config", "SMTP丰巢推送", "TG丰巢推送"]

# -*- coding:utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Union

from dataclasses_json import dataclass_json, DataClassJsonMixin


@dataclass
class TG丰巢推送(DataClassJsonMixin):
    recivers: List[Union[str, int]] = field(default_factory=list)  # 允许接收消息和使用指令到会话名单
    commanders: List[Union[str, int]] = field(default_factory=list)  # 允许使用指令的聊天会话名单，这些邮箱只允许使用指令但不发送消息。
    token: str = ""
    enabled: bool = False
    extra_push_blacklist: List[Union[str, int]] = field(default_factory=list)  # 额外推送黑名单，将不会发送额外推送消息。
    timing_push_blacklist: List[Union[str, int]] = field(default_factory=list)  # 定期推送黑名单，将不会发送定期推送消息。
    expire_push_blacklist: List[Union[str, int]] = field(default_factory=list)  # 超时推送黑名单，将不会发送超时推送消息。


@dataclass
class SMTP丰巢推送(DataClassJsonMixin):
    # 邮箱推送功能不支持指令
    server: str = "smtp.qq.com"
    port: int = 553
    ssl: bool = True
    sender: str = "who@qq.com"
    username: str = "who@qq.com"
    password: str = "123456"
    recivers: List[str] = field(default_factory=list)
    short_push_list: List[str] = field(default_factory=list)
    short_title_only_push_list: List[str] = field(default_factory=list)
    enabled: bool = False
    extra_push_blacklist: List[str] = field(default_factory=list)  # 额外推送黑名单，将不会发送额外推送消息。
    timing_push_blacklist: List[str] = field(default_factory=list)  # 定期推送黑名单，将不会发送定期推送消息。
    expire_push_blacklist: List[str] = field(default_factory=list)  # 超时推送黑名单，将不会发送超时推送消息。


@dataclass
class Config(DataClassJsonMixin):
    device: str
    ip: str
    token: str
    fc_ver_code: str = "2029000"
    fc_ver_name: str = "2.29.0"
    user_agent: str = "channel=yingyongbao,deviceId={device_id},ip={ip},mac=02:00:00:00:00:00," \
                      "os=7.1.2,platform=Android,resolution=1080*1920,versionCode={fc_code},versionName={fc_ver}"
    timing_push: bool = True  # 定时推送，免费每剩一半时间将会提示你去取出，最高半小时提示一次，防止为超时付费。
    expire_push: bool = True  # 到期推送，每隔12小时涨价都会提示你。
    telegram: TG丰巢推送 = TG丰巢推送()
    smtp: SMTP丰巢推送 = SMTP丰巢推送()
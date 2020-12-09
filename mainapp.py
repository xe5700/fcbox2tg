# -*- coding:utf-8 -*-
import asyncio
import signal
from asyncio.tasks import Task
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union

import logging
from os import path
import os
import uuid

import telegram

import myrandom
import fcbox
from appcfg import *
import fcboxjson
from threading import Lock

from emailhelper import SmtpPush
from mytgbot import TgBot
from utils import *

包裹信息读取任务: asyncio.Task
包裹定时提醒任务: asyncio.Task

main_task: Task


def stop_me(_signo, _stack):
    print("Docker container has stoped....")
    main_task.cancel("Container or application stoped")


def 格式化时间间隔(td: timedelta, s: bool = False):
    mm, ss = divmod(td.total_seconds(), 60)
    hh, mm = divmod(mm, 60)
    if hh > 0:
        if mm > 0:
            if s:
                return "%d小时 %d分钟" % (hh, mm)
            else:
                return "%d时%d分" % (hh, mm)
        else:
            if s:
                return "%d小时" % hh
            else:
                return "%d时" % hh
    if hh == 0 and mm > 0:
        if s:
            return "%d分钟 %d秒" % (mm, ss)
        else:
            return "%d分%d秒" % (mm, ss)
    else:
        return "%d秒" % ss


def 短格式化时间间隔(td: timedelta):
    格式化时间间隔(td, True)


@dataclass
class Application:
    smtp: Optional[SmtpPush] = None
    t1: Optional[Task] = None
    t2: Optional[Task] = None
    t3: Optional[Task] = None
    t4: Optional[Task] = None
    cfg: Optional[Config] = None
    tg_bot: Optional[TgBot] = None
    loop: Optional[asyncio.AbstractEventLoop] = None
    _sent_packages: Dict[str, '未取包裹'] = field(default_factory=dict)
    _last_error: datetime = datetime.now()

    async def _包裹定时提醒处理(self):
        try:
            while True:
                await asyncio.sleep(60)
                logging.info("开始处理定时处理包裹，一分钟后再次处理。")
                for wqbg in self._sent_packages.values():
                    self.t4 = asyncio.create_task(wqbg.检查(), name="检查包裹任务")
                    await self.t4
        except asyncio.CancelledError as e:
            logging.exception(e)

    async def 读取包裹信息(self):
        try:
            packages = fcbox.获取快件列表(self.cfg)
            if packages.success:
                kj_id: int = 0
                for kj in packages.data:
                    kj_id += 1
                    logging.debug(f"快件{kj_id}")
                    logging.debug("丰巢终端代码：" + kj.ed_code)
                    logging.debug("快递公司：" + kj.staff_company_name)
                    logging.debug("单号；" + kj.expressid)
                    # logging.debug("手机号：" + kj.picker_phone)
                    logging.debug("取件码：" + kj.code)
                    logging.debug("快件柜地址：" + kj.ed_adress)
                    if kj.pick_tm:
                        logging.debug("取件日期：" + kj.pick_tm.isoformat())
                    if fcbox.检查包裹是否取出(kj):
                        logging.debug(f"快件{kj.expressid}已经被领取，将不再提示。")
                        if kj.postid in self._sent_packages:
                            self._sent_packages[kj.postid].已取出()
                            self._sent_packages.pop(kj.postid)
                    else:
                        logging.debug(f"检测到快件{kj.expressid}未取出，将会根据设置提示你。")
                        if kj.postid not in self._sent_packages.keys():
                            logging.debug("提醒未取包裹")
                            wqbg = 未取包裹(package=kj, app=self)
                            self._sent_packages[kj.postid] = wqbg
                            if self.t4 and not self.t4.done():
                                await self.t4
                            self.t4 = asyncio.create_task(wqbg.检查(), name="检查包裹任务")
                            await self.t4
                        else:
                            self._sent_packages[kj.postid].package = kj

            else:
                logging.warning(f"操作失败！你可能需要重新获取TOKEN，错误消息：{packages.msg}，错误代码：{packages.code}")
                if self._last_error + timedelta(minutes=120) < datetime.now():
                    logging.warning("每120分钟将推送这个消息")
        except BaseException as e:
            logging.exception(e)

    async def _包裹信息定时读取(self):
        while True:
            self.t3 = asyncio.create_task(self.读取包裹信息(), name="读取包裹信息")
            logging.info("10分钟后再次处理丰巢快递包裹")
            await asyncio.sleep(600)

    async def main(self):
        try:
            self._last_error = datetime.now()
            env = os.environ
            signal.signal(signal.SIGINT, stop_me)
            print("""
        .########..######..########...#######..##.....##..#######..########..######..
        .##.......##....##.##.....##.##.....##..##...##..##.....##....##....##....##.
        .##.......##.......##.....##.##.....##...##.##..........##....##....##.......
        .######...##.......########..##.....##....###.....#######.....##....##...####
        .##.......##.......##.....##.##.....##...##.##...##...........##....##....##.
        .##.......##....##.##.....##.##.....##..##...##..##...........##....##....##.
        .##........######..########...#######..##.....##.#########....##.....######..
            """)
            if str2bool(env.get("DEBUG", "False")):
                logging.basicConfig(level=logging.DEBUG)
            else:
                logging.basicConfig(level=logging.INFO)
            logging.info("丰巢推送姬")
            self.cfg = Config(device=str(uuid.uuid4()).replace("-", "")[:16],
                              ip=myrandom.生成随机内网地址(),
                              token=""
                              )
            logging.info("正在载入配置文件")
            config_path = env.get("CONFIG_PATH", "config.json")
            if path.exists(config_path):
                with open(config_path, mode="r", encoding="utf-8") as f:
                    self.cfg = Config.from_json(f.read())
            with open(config_path, mode="w+", encoding="utf-8") as f:
                f.write(self.cfg.to_json(indent=4, ensure_ascii=False))
            if self.cfg.token == "":
                logging.error("未设置丰巢的token,无法运行此程序。")
                return -2
            self.t1 = asyncio.create_task(self._包裹信息定时读取(), name="包裹信息读取任务")
            self.t2 = asyncio.create_task(self._包裹定时提醒处理(), name="包裹定时提醒任务")
            self.loop = asyncio.get_running_loop()
            if self.cfg.telegram.enabled:
                self.tg_bot = TgBot(self)
                logging.info("正在启动telegram推送机器人")
                self.tg_bot.load()
                self.tg_bot.sendMessage(text=f"成功在{datetime.now().isoformat()}启动了丰巢推送助手")
            if self.cfg.smtp.enabled:
                self.smtp = SmtpPush(self)
                if len(self.cfg.smtp.recivers) > 0:
                    self.smtp.send(self.cfg.smtp.recivers, "丰巢推送助手", f"成功在{datetime.now().isoformat()}启动了丰巢推送助手")
                if len(self.cfg.smtp.short_push_list) > 0:
                    self.smtp.send(self.cfg.smtp.short_push_list, "丰巢推送助手", "启动成功")
                if len(self.cfg.smtp.short_title_only_push_list) > 0:
                    self.smtp.send(self.cfg.smtp.short_title_only_push_list, "丰巢推送助手已经启动成功",
                                   f"成功在{datetime.now().isoformat()}启动了丰巢推送助手")
                    
            await self.t1
            await self.t2
        except asyncio.CancelledError as e:
            logging.exception(e)
        except BaseException as e:
            logging.exception(e)
        finally:
            return 0


@dataclass
class 未取包裹:
    package: fcboxjson.FcBoxPackage
    app: Application
    tg_messages: List[telegram.Message] = field(default_factory=list)
    notice_time: Optional[datetime] = None
    next_pay_time: Optional[datetime] = None
    需要氪金 = False

    @staticmethod
    def _获得过滤过期推送的邮箱列表(original: List[str]) -> Optional[List[str]]:
        nl = original.copy()
        for i in app.cfg.smtp.timing_push_blacklist:
            nl.remove(i)
        for i in app.cfg.smtp.expire_push_blacklist:
            nl.remove(i)
        if len(nl) == 0:
            return None
        return nl

    @staticmethod
    def _获得过滤定期推送的邮箱列表(original: List[str]) -> Optional[List[str]]:
        nl = original.copy()
        for i in app.cfg.smtp.timing_push_blacklist:
            nl.remove(i)
        if len(nl) == 0:
            return None
        return nl

    async def 检查(self) -> None:
        kj = self.package
        if self.notice_time is None:
            if kj.retention_tm <= datetime.now():
                self.notice_time = datetime.now()
                return await self.检查()
            print(f"丰巢推送：你的{kj.staff_company_name} [{kj.expressid}] 已经到柜了！到{kj.ed_adress}领取 取件码:{kj.code}")
            if self.app.cfg.telegram.enabled:
                msgs = self.app.tg_bot.sendMessage(text=f"{kj.expressid} [{kj.staff_company_name}] 已到柜 \n"
                                                        f"到{kj.ed_adress}领取 \n"
                                                        f"取件码:{kj.code}\n"
                                                        f"到柜时间:{kj.send_tm.isoformat()}\n"
                                                        f"收费开始时间:{kj.retention_tm.isoformat()}")
                for msg in msgs:
                    self.tg_messages.append(msg)
            if self.app.cfg.smtp.enabled:
                msg = f"{kj.expressid} [{kj.staff_company_name}] 已到柜 \n" \
                      f"到{kj.ed_adress}领取 \n" \
                      f"取件码:{kj.code}\n" \
                      f"到柜时间:{kj.send_tm.isoformat()}\n" \
                      f"收费开始时间:{kj.retention_tm.isoformat()}"
                shortmsg = f"{kj.comp_simple_name} 取件码:{kj.code} " \
                           f"到 {kj.ed_adress[len(kj.ed_adress) - 4:4]}{kj.ed_adress[:len(kj.ed_adress) - 4]} 领"
                if len(self.app.cfg.smtp.recivers) > 0:
                    self.app.smtp.send(self.app.smtp.cfg.recivers, "丰巢推送姬", msg)
                if len(self.app.cfg.smtp.short_push_list) > 0:
                    self.app.smtp.send(self.app.smtp.cfg.recivers, "丰巢", shortmsg)
                if len(self.app.cfg.smtp.short_title_only_push_list) > 0:
                    self.app.smtp.send(self.app.smtp.cfg.recivers, shortmsg, "丰巢")
            self.notice_time = datetime.now() + (kj.send_tm - kj.retention_tm) / 2
        elif self.notice_time <= datetime.now():
            if datetime.now() <= kj.retention_tm:
                放柜里的时间 = datetime.now() - kj.send_tm
                收费剩余时间 = kj.retention_tm - datetime.now()
                print(f"丰巢推送姬：你的{kj.staff_company_name} [{kj.expressid}] 已经到柜 {格式化时间间隔(放柜里的时间)} 在"
                      f"{短格式化时间间隔(收费剩余时间)}后将会收费 请尽快领取 取件码:{kj.code}")
                if self.app.cfg.timing_push:
                    if self.app.cfg.telegram.enabled:
                        msgs = self.app.tg_bot.sendMessage(text=f"{kj.expressid} [{kj.staff_company_name}] 已到柜 \n"
                                                                f"到{kj.ed_adress}领取 \n"
                                                                f"取件码:{kj.code}\n"
                                                                f"这个快递已经放丰巢里{格式化时间间隔(放柜里的时间)}了\n"
                                                                f"{格式化时间间隔(收费剩余时间)}后这个快递要开始收费领取")
                        for msg in msgs:
                            self.tg_messages.append(msg)
                    if self.app.cfg.smtp.enabled:
                        msg = f"{kj.expressid} [{kj.staff_company_name}] 已到柜 \n" \
                              f"到{kj.ed_adress}领取 \n" \
                              f"取件码:{kj.code}\n" \
                              f"这个快递已经放丰巢里{格式化时间间隔(放柜里的时间)}了\n" \
                              f"{格式化时间间隔(收费剩余时间)}后这个快递要开始收费领取"
                        shortmsg = f"{kj.comp_simple_name} 取件码:{kj.code} {短格式化时间间隔(收费剩余时间)}后收费"
                        sendlist = self._获得过滤过期推送的邮箱列表(self.app.cfg.smtp.recivers)
                        if sendlist:
                            self.app.smtp.send(sendlist, "丰巢推送姬", msg)
                        sendlist = self._获得过滤过期推送的邮箱列表(self.app.cfg.smtp.short_title_only_push_list)
                        if sendlist:
                            self.app.smtp.send(sendlist, shortmsg, "请注意将会收费")
                        sendlist = self._获得过滤过期推送的邮箱列表(self.app.cfg.smtp.short_push_list)
                        if sendlist:
                            self.app.smtp.send(sendlist, "丰巢", msg)
                    self.notice_time = datetime.now() + min(max(timedelta(minutes=10), 收费剩余时间 / 2), timedelta(
                        hours=6), 收费剩余时间)
            else:
                if self.next_pay_time is None:
                    self.next_pay_time = self.package.retention_tm + timedelta(hours=12)
                elif self.next_pay_time <= datetime.now():
                    self.next_pay_time = self.next_pay_time + timedelta(hours=12)
                放柜里的时间 = datetime.now() - kj.send_tm
                下一个收费周期间隔 = self.next_pay_time - datetime.now()
                if kj.custody_pay_info.custody_money < (
                        (datetime.now() - kj.retention_tm) / timedelta(hours=12) + 1) \
                        * 50:
                    logging.info("检测到可能价格不正确，刷新获取新包裹价格中。")
                    await self.app.读取包裹信息()
                    kj = self.package
                if self.app.cfg.expire_push:
                    if self.app.cfg.telegram.enabled:
                        money = "%.2f" % (kj.custody_pay_info.custody_money / 100.0)
                        msgs = self.app.tg_bot.sendMessage(text=f"{kj.expressid} [{kj.staff_company_name}] 已到柜 \n"
                                                                f"到{kj.ed_adress}领取 \n"
                                                                f"取件码:{kj.code}\n"
                                                                f"这个快递已经放丰巢里{格式化时间间隔(放柜里的时间)}了\n"
                                                                f"需要收费{money}¥ 下次请尽早领取\n"
                                                                f"{格式化时间间隔(下一个收费周期间隔)}后将会涨价，上限是3元。")
                        for msg in msgs:
                            self.tg_messages.append(msg.message_id)
                    if self.app.cfg.smtp.enabled:
                        money = "%.2f" % (kj.custody_pay_info.custody_money / 100.0)
                        msg = f"{kj.expressid} [{kj.staff_company_name}] 已到柜 \n到{kj.ed_adress}领取 \n" \
                              f'取件码:{kj.code}\n' \
                              f'这个快递已经放丰巢里{格式化时间间隔(放柜里的时间)}了\n' \
                              f'需要收费{money}¥ 下次请尽早领取\n' \
                              f'{格式化时间间隔(下一个收费周期间隔)}后将会涨价，上限是3元。'
                        shortmsg = f"{kj.comp_simple_name} 取件码:{kj.code} 收费{money}¥ {短格式化时间间隔(下一个收费周期间隔)}后涨价"
                        sendlist = self._获得过滤过期推送的邮箱列表(self.app.cfg.smtp.recivers)
                        if sendlist:
                            self.app.smtp.send(sendlist, "丰巢推送姬", msg)
                        sendlist = self._获得过滤过期推送的邮箱列表(self.app.cfg.smtp.short_push_list)
                        if sendlist:
                            self.app.smtp.send(sendlist, "丰巢", shortmsg)
                        sendlist = self._获得过滤过期推送的邮箱列表(self.app.cfg.smtp.short_title_only_push_list)
                        if sendlist:
                            self.app.smtp.send(sendlist, shortmsg, "请看标题注意收费")
                self.notice_time = datetime.now() + min(max(timedelta(minutes=10), 下一个收费周期间隔 / 2), timedelta(
                    hours=6), 下一个收费周期间隔)

    def 已取出(self):
        if self.app.cfg.telegram.enabled:
            for msg in self.tg_messages:
                msg.delete()


if __name__ == "__main__":
    app = Application()
    exit(asyncio.run(app.main()))

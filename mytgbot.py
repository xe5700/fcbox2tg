# -*- coding:utf-8 -*-
import asyncio
import logging
from io import StringIO
import time
from typing import List
import telegram
import telegram.ext
from telegram import Update

from functools import wraps
from telegram.ext import CallbackContext, CommandHandler
import appcfg

import fcboxjson
import fcbox


def tg_cmd(func=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self: TgBot = args[0]
        update: telegram.Update = args[1]
        context: telegram.ext.CallbackContext = args[2]
        if update.message.chat_id in self.cfg.telegram.recivers or update.message.from_user.username in \
                self.cfg.telegram.recivers:
            return func(*args, **kwargs)
        else:
            return

    return wrapper


class TgBot:
    bot: telegram.Bot
    cfg: appcfg.Config

    def __init__(self, app):
        from mainapp import Application
        app: Application
        self.app = app
        self.cfg = app.cfg
        self.bot = telegram.Bot(token=self.cfg.telegram.token)
        self.updater = telegram.ext.Updater(token=self.cfg.telegram.token)
        self.dispatcher = self.updater.dispatcher

    @tg_cmd
    def list(self, update: Update, context: CallbackContext):
        result = fcbox.获取快件列表(self.cfg)
        未取包裹: List[fcboxjson.FcBoxPackage] = list()
        if result.success:
            for kj in result.data:
                if not fcbox.检查包裹是否取出(kj):
                    未取包裹.append(kj)
            sb = StringIO()
            i = 0
            for kj in 未取包裹:
                i += 1
                sb.write(f"{i}.单号{kj.expressid}[{kj.staff_company_name}] ")
                if kj.custody_pay_info.need_pay_flag:
                    money = "%.2f" % (kj.custody_pay_info.custody_money / 100.0)
                    sb.write(f"已超时需要支付{money} ")
                sb.write(f"在{kj.ed_adress}领取 取件码:{kj.code}\n")
            update.message.reply_text(text=f"你有{len(未取包裹)}个未取包裹\n{sb.getvalue()}")

        else:
            update.message.reply_text(text="获取失败！\n" + result.msg)
        update.message.delete()

    @tg_cmd
    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text(text="丰巢推送机器人已启动\n输入 /list 显示所有你未取的快递")
        update.message.delete()

    @tg_cmd
    def refresh(self, update: Update, context: CallbackContext):
        update.message.delete()
        msg1 = update.message.reply_text(text="已经开始进行刷新处理...")

        async def asyncrefresh():
            try:
                s_time = time.time_ns()
                await self.app.读取包裹信息()
                msg1.edit_text("刷新完成 用时 %.2fms" % ((time.time_ns()-s_time)/(1000*1000)))
                await asyncio.sleep(60)
                msg1.delete()
            except BaseException as e:
                logging.exception(e)
        asyncio.run_coroutine_threadsafe(asyncrefresh(), self.app.t1.get_loop())

    @tg_cmd
    def setToken(self, update: Update, context: CallbackContext):
        t = update.message.text.split(" ")
        if len(t) < 2:
            update.message.reply_text(text="参数错误！请输入/settoken <新的丰巢token>")
        else:
            async def asyncSetToken():
                self.app.cfg.token = t[1]
                update.message.reply_text(text=f"将你的Token设置为{t:1}， 并且将会进行刷新包裹操作。")
                self.app.saveCfg()
                await self.app.读取包裹信息()
            asyncio.run_coroutine_threadsafe(asyncSetToken(), self.app.t1.get_loop())
        update.message.delete()

    @tg_cmd
    def setToken(self, update: Update, context: CallbackContext):
        update.message.delete()

        update.message.reply_text(text='''
/list 列出全部未取出的快递
/refresh 刷新包裹信息
/setToken <丰巢Token> 重新设置丰巢Token值

        ''')

    def sendMessage(self, **kwargs) -> List[telegram.message.Message]:
        msgs = list()
        for i in self.cfg.telegram.recivers:
            chat = self.bot.get_chat(chat_id=i)
            msgs.append(chat.send_message(**kwargs))
        return msgs

    def load(self):
        BotCmd = telegram.BotCommand
        cmd_list = BotCmd(command="list", description="列出全部未取出的快递")
        cmd_start = BotCmd(command="start", description="启动")
        cmd_refresh = BotCmd(command="refresh", description="重新获取包裹")
        cmd_set_token = BotCmd(command="setToken", description="重新设置丰巢Token值")
        cmds = self.bot.commands
        cmds.extend([cmd_start, cmd_list, cmd_refresh, cmd_set_token])
        handler_list = CommandHandler('list', self.list)
        handler_start = CommandHandler('start', self.start)
        handler_refresh = CommandHandler('refresh', self.refresh)
        handler_stoken = CommandHandler('saveToken', self.setToken)
        self.dispatcher.add_handler(handler_list)
        self.dispatcher.add_handler(handler_start)
        self.dispatcher.add_handler(handler_refresh)
        self.dispatcher.add_handler(handler_stoken)

        self.updater.start_polling()

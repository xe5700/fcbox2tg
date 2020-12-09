# -*- coding:utf-8 -*-
# 丰巢盒子

from appcfg import Config
import time
import requests
import fcboxjson
import myrandom


def 获取快件列表(cfg: Config) -> fcboxjson.FcBoxPackageReponse:
    user_agent = cfg.user_agent.format(ip=cfg.ip, device_id=cfg.device, fc_code=cfg.fc_ver_code,
                                       fc_ver=cfg.fc_ver_name, timestamp=time.time() * 1000 + myrandom.生成随机毫秒())
    headers = {
        'User-Agent': user_agent,
        'FC_USER_FLAG': '',
        'Authorization': cfg.token,
        'Host': 'consumer.fcbox.com',
        'Accept-Encoding': 'gzip'
    }
    rep = requests.get("https://consumer.fcbox.com/post/express/getReceive?pageNo=1&queryType=3"
                       "&isShowAssociateExpress=1", headers=headers)
    nrep = fcboxjson.FcBoxPackageReponse.from_json(rep.text)
    if nrep.success:
        for i in range(0, len(nrep.data)):
            ii = nrep.data[i]
            if type(ii) == dict:
                nrep.data[i] = fcboxjson.FcBoxPackage.from_dict(ii)
    return nrep


def 检查包裹是否取出(pack: fcboxjson.FcBoxPackage) -> bool:
    if pack.pick_tm is None:
        return False
    else:
        return True

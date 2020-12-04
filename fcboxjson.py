r"""
generated by json2python-models v0.2.1 at Thu Dec  3 21:22:38 2020
command: json2models -m FcBoxReponse .\fcdata.json --no-unidecode -f dataclasses --max-strings-literal=0 -o fcboxjson.py
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from dataclasses_json import dataclass_json, LetterCase, config
from datetime import datetime


def timeformat1(self: datetime):
    if self is None:
        return None
    return self.isoformat(sep=" ")


def fromisoformat1(t_str):
    if t_str is not None:
        return datetime.fromisoformat(t_str)
    else:
        return None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FcBoxReponse:
    success: bool
    code: str
    msg: str
    data: Any


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FcBoxPackageReponse:
    success: bool
    code: str
    msg: str
    data: Optional[List['FcBoxPackage']]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FcBoxPackage:
    postid: str
    expressid: str
    ed_code: str
    client_mobile: str
    picker_phone: str
    staff_company: str
    staff_company_name: str
    staff_mobile: str
    company_logo_url: str
    code: str
    ed_adress: str
    ed_buildname: str
    longtitude: str
    latitude: str
    pick_type: int
    express_type: int
    operate_time: datetime = field(metadata=config(encoder=timeformat1, decoder=fromisoformat1))
    send_tm: datetime = field(metadata=config(encoder=timeformat1, decoder=fromisoformat1))
    pick_tm: Optional[datetime] = field(metadata=config(encoder=timeformat1, decoder=fromisoformat1))
    retention_tm: datetime = field(metadata=config(encoder=timeformat1, decoder=fromisoformat1))
    retention_period: Optional[str]
    express_status: int
    cell_location_desc: str
    comp_simple_name: str
    staff_icon_url: Optional[str]
    money: float
    is_face_auth: Optional[str]
    post_tips: str
    staff_name: Optional[str]
    belong_org: Optional[str]
    service_fee: float
    verify_applied: Optional[str]
    status: Optional[str]
    stored_hours: Optional[str]
    stored_ms: Optional[str]
    user_mobile: str
    sdy_transition: bool
    tag: Optional[str]
    routes: Optional[str]
    custody: 'Custody'
    custody_pay_info: 'CustodyPayInfo'


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Custody:
    agreement_url: Optional[str]
    free_hour: Optional[str]
    per_hour: Optional[str]
    free_minute: Optional[str]
    per_minute: Optional[str]
    max_money: Optional[str]
    money: Optional[str]
    agree_custody_flag: Optional[str]
    promote_contents: Optional[str]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CustodyPayInfo:
    custody_day: Optional[str]
    custody_min: int
    custody_hours: int
    custody_min_secs: int
    order_no: Optional[str]
    pay_money: int
    pay_type: Optional[str]
    pay_time: Optional[datetime] = field(metadata=config(encoder=timeformat1, decoder=fromisoformat1))
    custody_money: int
    pay_mobile: Optional[str]
    custody_member_flag: bool
    pick_rights_expired_tm: Optional[str]
    custody_charge_flag: bool
    need_pay_flag: bool
    custody_pay_status: int
    insurance_money: int

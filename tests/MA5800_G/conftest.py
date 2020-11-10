#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client_MA5800 import *
from src.MA5800_G.ont_auth import *

from src.config.Cdata_loggers import *
from src.config.initialization_config import *
from renix_py_api import renix
import pytest


@pytest.fixture(scope='function')
def login_gpon():
    tn = telnet_host(host_ip=Gpon_olt_mgt_ip , username=Gpon_olt_username, password=Gpon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    logout_host(tn)

@pytest.fixture(scope='function')
def login_epon():
    tn = telnet_host(host_ip=Epon_olt_mgt_ip , username=Epon_olt_username, password=Epon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    logout_host(tn)


@pytest.fixture(scope='function')
def login():
    tn = telnet_host(host_ip=Gpon_olt_mgt_ip , username=Gpon_olt_username, password=Gpon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    del_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID)
    ont_del(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    logout_host(tn)

@pytest.fixture(scope='function')
def login2():
    tn = telnet_host(host_ip=Gpon_olt_mgt_ip , username=Gpon_olt_username, password=Gpon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    check_telnet(host_ip=olt_mgt_ip)


@pytest.fixture(scope='function')
def login_1():
    # host_ip = '192.168.5.164'
    # username = 'root'
    # password = 'admin'
    tn = telnet_host(host_ip=Gpon_olt_mgt_ip , username=Gpon_olt_username, password=Gpon_olt_password)[0]
    yield tn
    ont_del_1(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    logout_host(tn)






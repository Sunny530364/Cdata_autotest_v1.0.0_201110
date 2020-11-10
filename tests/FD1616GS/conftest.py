#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
from tests.FD1616GS.initialization_config import *
from src.FD1616GS.ont_auth import *
from src.FD1616GS.vlan_func import *
from src.config.Cdata_loggers import *
from renix_py_api import renix
from src.FD1616GS.olt_opera import *
from src.FD1616GS.olt_opera import *
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
    # no_shutdown_gpon(tn, Gpon_PonID)
    yield tn
    ont_del(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    # shutdown_epon(tn, Gpon_PonID)
    logout_host(tn)


@pytest.fixture(scope='function')
def login2():

    tn = telnet_host(host_ip=Gpon_olt_mgt_ip , username=Gpon_olt_username, password=Gpon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    check_telnet(host_ip=Gpon_olt_mgt_ip)


@pytest.fixture(scope='function')
def login_1():
    # host_ip = '192.168.5.164'
    # username = 'root'
    # password = 'admin'
    tn = telnet_host(host_ip=Gpon_olt_mgt_ip, username=Gpon_olt_username, password=Gpon_olt_password)[0]
    yield tn
    ont_del_1(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    logout_host(tn)







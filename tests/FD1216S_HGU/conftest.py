#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
from src.Epon_HGU.ont_auth import *
# from src.Epon.vlan_func import *
from src.config.Cdata_loggers import *
from tests.FD1216S_HGU.initialization_config import *
from renix_py_api import renix
from src.FD1216S.olt_opera import *
import pytest


@pytest.fixture(scope='function')
def login():
    tn = telnet_host(host_ip=Epon_olt_mgt_ip, username=Epon_olt_username, password=Epon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    ont_del(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    logout_host(tn)

@pytest.fixture(scope='function')
def login_gpon():
    tn = telnet_host(host_ip=Gpon_olt_mgt_ip, username=Gpon_olt_username, password=Gpon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    logout_host(tn)

@pytest.fixture(scope='function')
def login_epon():

    tn = telnet_host(host_ip=Epon_olt_mgt_ip, username=Epon_olt_username, password=Epon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    logout_host(tn)

@pytest.fixture(scope='function')
def login1():
    tn = telnet_host(host_ip=Epon_olt_mgt_ip, username=Epon_olt_username, password=Epon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    add_pon_native_vlan(tn, Epon_PonID, '1')
    ont_del(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    logout_host(tn)


@pytest.fixture(scope='function')
def login2():
    tn = telnet_host(host_ip=Epon_olt_mgt_ip, username=Epon_olt_username, password=Epon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    #check_telnet(host_ip=Epon_olt_mgt_ip)

@pytest.fixture(scope='function')
def login2():
    tn = telnet_host(host_ip=Epon_olt_mgt_ip, username=Epon_olt_username, password=Epon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    check_telnet(host_ip=Epon_olt_mgt_ip)


@pytest.fixture(scope='function')
def login_1():
    tn = telnet_host(host_ip=Epon_olt_mgt_ip, username=Epon_olt_username, password=Epon_olt_password)[0]
    yield tn
    ont_del_1(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    logout_host(tn)





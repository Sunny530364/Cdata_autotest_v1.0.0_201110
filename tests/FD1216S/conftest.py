#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
from src.FD1216S.ont_auth import *
from src.FD1216S.olt_opera import *
from src.FD1216S import ont_auth
import pytest
from tests.FD1216S.initialization_config import *

# @pytest.fixture(scope='session')
# def login_init():
#     tn1 = telnet_host(host_ip=Epon_olt_mgt_ip, username=Epon_olt_username, password=Epon_olt_password)[0]
#     noshutdown_pon(tn1, Epon_PonID)
#     yield
#     shutdown_pon(tn1, Epon_PonID)
#     logout_host(tn1)

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
    tn = telnet_host(host_ip=Epon_olt_mgt_ip, username=Epon_olt_username, password=Epon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    # noshutdown_pon(tn, Epon_PonID)
    yield tn
    ont_del(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    # shutdown_pon(tn, Epon_PonID)
    logout_host(tn)

@pytest.fixture(scope='function')
def login2():
    tn = telnet_host(host_ip=Epon_olt_mgt_ip, username=Epon_olt_username, password=Epon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    check_telnet(host_ip=Epon_olt_mgt_ip)

# @pytest.fixture(scope='function')
# def login3():
#     tn = telnet_host(host_ip=Epon_olt_mgt_ip, username=Epon_olt_username, password=Epon_olt_password)[0]
#     if tn == False:
#         raise Exception("设备登录失败")
#     yield tn
#     logout_host(tn)

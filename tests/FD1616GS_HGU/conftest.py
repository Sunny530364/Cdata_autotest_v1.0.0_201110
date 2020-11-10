#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI
from src.Gpon_HGU.gemport import *
from src.config.telnet_client import *
from src.Gpon_HGU.ont_auth import *
from src.Gpon_HGU.vlan_func import *
from src.config.Cdata_loggers import *
from renix_py_api import renix
from src.Gpon_HGU.olt_opera import *
import pytest
from src.Gpon_HGU.internet_type import *
from tests.FD1616GS_HGU.initialization_config import  *


@pytest.fixture(scope='function')
def login():

    tn = telnet_host(host_ip=Gpon_olt_mgt_ip, username=Gpon_olt_username, password=Gpon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    ont_del(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
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
def login_1():
    tn = telnet_host(host_ip=Gpon_olt_mgt_ip, username=Gpon_olt_username, password=Gpon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    wifi_disconnect()
    ont_del(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    enable_interface(interface_name)
    logout_host(tn)


@pytest.fixture(scope='function')
def login_2():
    tn = telnet_host(host_ip=Gpon_olt_mgt_ip, username=Gpon_olt_username, password=Gpon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    ont_del(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    logout_host(tn)


@pytest.fixture(scope='function')
def login_gemport():
    tn = telnet_host(host_ip=Gpon_olt_mgt_ip, username=Gpon_olt_username, password=Gpon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    gemport_transparent(tn, ont_lineprofile_id=Ont_Lineprofile_ID)
    ont_del(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    logout_host(tn)

@pytest.fixture(scope='function')
def login2():

    tn = telnet_host(host_ip=Gpon_olt_mgt_ip , username=Gpon_olt_username, password=Gpon_olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    yield tn
    check_telnet(host_ip=Gpon_olt_mgt_ip)


# @pytest.fixture(scope='session')
# def ont_auth_suit(login):
#     tn=login
#     PonID=16
#     OnuID=2
#     Ont_Lineprofile_ID=200
#     Ont_Srvprofile_ID=200
#     SN= 'ZTE171200033'
#     Onu_port_ID=1
#     User_vlan_1 = 2000
#     User_vlan_2 = 4001
#     Vlan_list=[2000]
#     Gemport_ID=1
#     #onu自动发现
#     autofind_onu(tn,PonID, SN)
#     #onu基于sn认证
#     auth_by_sn(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, SN)
#     #配置onu端口1native-vlan
#     ont_native_vlan(tn, PonID, OnuID, Onu_port_ID, User_vlan_1)
#     # # 配置onu端口2native-vlan
#     # ont_native_vlan(tn, PonID, OnuID, Onu_port_ID, User_vlan_2)
#     #配置虚端口
#     # add_service_port(tn, PonID, OnuID, Gemport_ID, Vlan_list)
#     return tn





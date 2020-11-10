#!/usr/bin/python
# -*- coding UTF-8 -*-

import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.Gpon_HGU.internet_type import *
# from page.telnet_client import *
from src.Gpon_HGU.ont_auth import *
from tests.FD1616GS_HGU.initialization_config import *
from src.xinertel.renix_test import *
from src.Gpon_HGU.omci_wan import *
import allure


@allure.feature("ONU远程管理")
@allure.story("远程管理ONU")
@allure.title("去激活ONU")
@pytest.mark.run(order=1015)
def test_deactive_onu(login):
    '''
    用例描述：
    再OLT上将ONU去激活后，再重新激活。
    例如：
    ont deactivate 1 1
    ont activate 1 1
    '''
    cdata_info("=========去激活ONU=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0',  ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:测试仪发送双向10000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name = sys._getframe().f_code.co_name)
    with allure.step('步骤6:在OLT上将ONU去激活后，重新激活。'):
        assert deactive_onu(tn, Gpon_PonID, Gpon_OnuID)
    with allure.step('步骤7:测试仪发送双向10000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name = sys._getframe().f_code.co_name)
    with allure.step('步骤8:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)


@allure.feature("ONU远程管理")
@allure.story("远程管理ONU")
@allure.title("远程重启ONU")
@pytest.mark.run(order=1016)
def test_reboot_onu(login):
    '''
    用例描述：
    在OLT上远程重启ONU。
    例如：
    ont reboot 1 1
    '''
    cdata_info("=========远程重启ONU=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0',  ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:测试仪发送双向10000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤6:在OLT上重启ONU。'):
        assert reboot_onu(tn, Gpon_PonID, Gpon_OnuID)
    with allure.step('步骤7:测试仪发送双向10000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤8:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    # with allure.step('步骤6:删除omci_wan配置'):
    #     assert ont_del(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)


@allure.feature("ONU远程管理")
@allure.story("远程管理ONU")
@allure.title("OMCI升级ONU")
# @pytest.mark.skip("暂时不执行")
@pytest.mark.run(order=1002)
def test_upgrade_onu(login_2):
    '''
    用例描述：
    通过OMCI升级ONU。
    例如：
    load file tftp 192.168.5.100 FD514GB-G_V1.0.1_190909_1158_X000.bin
    ont load select 0/0 1 1
    ont load start 0/0 FD514GB-G_V1.0.1_190909_1158_X000.bin activemode immediate
    '''
    cdata_info("=========OMCI升级ONU=========")
    tn = login_2
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    # with allure.step('步骤4:添加omci_wan配置'):
    #     assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0',  ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:测试仪发送双向10000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name = sys._getframe().f_code.co_name)
    with allure.step('步骤6:将ONU通过OMCI升级'):
        assert upgrade_onu(tn, Gpon_PonID, Gpon_OnuID, tftp_server_ip, file_name)
    with allure.step('步骤7:测试仪发送双向10000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name = sys._getframe().f_code.co_name)
    # with allure.step('步骤8:删除omci_wan配置'):
    #     assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤6:删除omci_wan配置'):
        assert ont_del_1(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)

if __name__ == '__main__':
    # case_1()
    pytest.main(["-s","-x","test_onu_mgt.py::test_deactive_onu"])





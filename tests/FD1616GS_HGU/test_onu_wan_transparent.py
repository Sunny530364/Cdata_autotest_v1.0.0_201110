#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI
from src.Gpon_HGU.gemport import *
from src.xinertel.unicast66 import *
from src.Gpon_HGU.ont_auth import *
from tests.FD1616GS_HGU.initialization_config import *
from src.Gpon_HGU.omci_wan import *
from src.xinertel.renix_test import *
import pytest
import allure


@allure.feature("WAN连接测试")
@allure.story("透传模式WAN连接测试")
@allure.title("gemport mapping优先级为透传")
@pytest.mark.run(order=1031)
def test_mapping_transparent(login):

    cdata_info("=========WAN连接模式为透传，gemport mapping模式为透传=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, range(2000, 2008))
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_bridge_transparent(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, User_Vlan, WAN_pri, ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:测试仪发送双向10000个报文,报文VLAN为2000'):
        assert stream_test_vlan(stream_rate, "10000",  port_location, "2000", '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤6:测试仪发送双向70000个报文，报文VLAN为2001到2007'):
        assert stream_test_vlan_1(stream_rate, "7000", port_location, '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤7:删除当前的serpocr-port'):
        assert del_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID)
    with allure.step('步骤8:添加可以让untag报文向上转发的service-port'):
        assert add_service_port_1(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    with allure.step('步骤9:测试仪发送双向10000个报文,上下行都为untag报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤10:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)



@allure.feature("WAN连接测试")
@allure.story("透传模式WAN连接测试")
@allure.title("gemport mapping优先级为untag")
@pytest.mark.run(order=1032)
def test_mapping_untag(login_gemport):

    cdata_info("=========WAN连接模式为透传，gemport mapping模式为untag=========")
    tn = login_gemport
    with allure.step('步骤1:修改gemport的mapping的模式为untag'):
        assert gemport_untag(tn, ont_lineprofile_id=200, mapping_mode='vlan')
    with allure.step('步骤2:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤3:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤4:添加可以让untag报文向上转发的service-port'):
        assert add_service_port_1(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    with allure.step('步骤5:添加omci_wan配置'):
        assert add_omci_wan_bridge_transparent(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, User_Vlan, WAN_pri, ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤6:测试仪发送双向10000个报文,上下行均为untag报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤7:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)

@allure.feature("WAN连接测试")
@allure.story("透传模式WAN连接测试")
@allure.title("gemport mapping优先级为vlan")
@pytest.mark.run(order=1033)
def test_mapping_vlan(login_gemport):

    cdata_info("=========WAN连接模式为透传，gemport mapping模式为vlan=========")
    tn = login_gemport
    with allure.step("步骤1:修改gemport的mapping的模式为vlan"):
        assert gemport_vlan(tn,ont_lineprofile_id=Ont_Lineprofile_ID)
    with allure.step('步骤2:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤3:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤4:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, range(2000, 2008))
    with allure.step('步骤5:添加omci_wan配置'):
        assert add_omci_wan_bridge_transparent(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, User_Vlan, WAN_pri, ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤6:测试仪发送双向10000个报文，报文的VLAN为2000'):
        assert stream_test_vlan(stream_rate, "10000",  port_location, "2000", '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤7:测试仪发送双向7000个报文，报文的VLAN为2001到2007'):
        assert stream_test_vlan_4(stream_rate, "7000",  port_location, '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤8:删除当前的service-port'):
        assert del_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID)
    with allure.step('步骤9:添加可以让untag报文向上转发的service-port'):
        assert add_service_port_1(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    with allure.step('步骤10:测试仪发送双向10000个报文,报文为untag报文'):
        assert stream_test_1(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤11:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
#
@allure.feature("WAN连接测试")
@allure.story("透传模式WAN连接测试")
@allure.title("gemport mapping优先级为pri")
@pytest.mark.run(order=1034)
def test_mapping_pri(login_gemport):

    cdata_info("=========WAN连接模式为透传，gemport mapping模式为pri=========")
    tn = login_gemport
    with allure.step("步骤1:修改gemport的mapping的模式为pri"):
        assert gemport_pri(tn, ont_lineprofile_id=Ont_Lineprofile_ID)
    with allure.step('步骤2:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤3:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤4:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, range(2000, 2008))
    with allure.step('步骤5:添加omci_wan配置'):
        assert add_omci_wan_bridge_transparent(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, User_Vlan, '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤6:测试仪发送双向100000个报文，报文的VLAN为2001到2007，优先级为0到6'):
        assert stream_test_vlan_5(stream_rate, "7000",  port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤7:测试仪发送双向100000个报文，报文的VLAN为2000，优先级为0到6'):
        assert stream_test_vlan_6(stream_rate, "7000",  port_location, "2000", packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤8:测试仪发送双向100000个报文，报文的VLAN为2000，VLAN优先级为7'):
        assert stream_test_vlan_pri(stream_rate, "10000",  port_location, "2000", "7", packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤9:测试仪发送双向70000个报文，报文的VLAN为2001到2007，VLAN优先级为7', ):
        assert stream_test_vlan_1_pri(stream_rate, "7000", port_location,  "7", packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤10:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
#
@allure.feature("WAN连接测试")
@allure.story("透传模式WAN连接测试")
@allure.title("gemport mapping优先级为vlan+pri")
@pytest.mark.run(order=1035)
def test_mapping_vlan_pri(login_gemport):

    cdata_info("=========WAN连接模式为透传，gemport mapping模式为vlan+pri=========")
    tn = login_gemport
    with allure.step("步骤1:修改gemport的mapping的模式为pri+vlan"):
        assert gemport_vlan_pri(tn,ont_lineprofile_id=200,mapping_mode='vlan-priority ')
    with allure.step('步骤2:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤3:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤4:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, range(2000, 2008))
    with allure.step('步骤5:添加omci_wan配置'):
        assert add_omci_wan_bridge_transparent(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, User_Vlan, WAN_pri, ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤7:测试仪发送双向7000个报文，报文的VLAN为2001到2007，VLAN优先级为7'):
        assert stream_test_vlan_4_pri(stream_rate, "7000", port_location,  "7", packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤8:测试仪发送双向7000个报文，报文的VLAN为2001到2007，优先级为1到7'):
        assert stream_test_vlan_5(stream_rate, "7000", port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤9:测试仪发送双向7000个报文，报文的VLAN为2000，优先级为1到7'):
        assert stream_test_vlan_6(stream_rate, "7000", port_location, "2000", packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤6:测试仪发送双向10000个报文，报文的VLAN为2000，VLAN优先级为7'):
        assert stream_test_vlan_pri(stream_rate, "10000", port_location, "2000", "7", packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤10:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
#
#
#
#
# # def test_test():
# #     assert stream_test_vlan_5(stream_rate, "7000", download_capture_num, port_location)
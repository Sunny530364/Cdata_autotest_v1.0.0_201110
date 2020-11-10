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


@allure.feature("gemport测试")
@allure.story("gemport测试")
@allure.title("测试mapping为transaprent")
@pytest.mark.run(order=1009)
def test_gemport_transparent(login):
    cdata_info("=========gemport为tranparent测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, range(2000, 2008))
    with allure.step('步骤4:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2000', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤6:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤7:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2001'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2001', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤8:测试仪发送双向10000个报文，下行为vlan是2001的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000',port_location, '2001', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤9:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤10:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2002'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2002', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤11:测试仪发送双向10000个报文，下行为vlan是2002的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2002', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤12:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤13:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2003'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2003', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤14:测试仪发送双向10000个报文，下行为vlan是2003的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2003', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤15:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤16:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2004'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2004', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤17:测试仪发送双向10000个报文，下行为vlan是2004的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2004', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤18:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤19：添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2005'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2005', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤20:测试仪发送双向10000个报文，下行为vlan是2005的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2005', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤21:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤22:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2006'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2006', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤23:测试仪发送双向10000个报文，下行为vlan是2006的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2006', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤24:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤25:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2007'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2007', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤26:测试仪发送双向10000个报文，下行为vlan是2007的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2007', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤27:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)

@allure.feature("gemport测试")
@allure.story("gemport测试")
@allure.title("测试mapping为untag")
@pytest.mark.run(order=1010)
def test_gemport_untag(login_gemport):

    cdata_info("=========gemport为untag测试=========")
    tn = login_gemport
    with allure.step('步骤1:修改gemport的mapping的模式为untag。'):
        assert gemport_untag(tn, ont_lineprofile_id=200, mapping_mode='vlan')
    with allure.step('步骤2:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤3:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤4:添加service-port'):
        assert add_service_port_1(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    with allure.step('步骤5:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000'):
        assert add_omci_wan_bridge_untag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤6:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2000', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤7:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
#
@allure.feature("gemport测试")
@allure.story("gemport测试")
@allure.title("测试mapping为vlan")
@pytest.mark.run(order=1011)
def test_gemport_vlan(login_gemport):
    cdata_info("=========gemport为vlan测试=========")
    tn = login_gemport
    with allure.step("步骤1:修改gemport的mapping的模式为vlan"):
        assert gemport_vlan(tn,ont_lineprofile_id=Ont_Lineprofile_ID)
    with allure.step('步骤2:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤3:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤4:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, range(2000, 2008))
    with allure.step('步骤5:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤6:测试仪发送双向100000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2000', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤7:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤8:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2001'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2001', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤9:测试仪发送双向10000个报文，下行为vlan是2001的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2001', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤10:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤11:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2002'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2002', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤12:测试仪发送双向10000个报文，下行为vlan是2002的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2002', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤13:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤14:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2003'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2003', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤15:测试仪发送双向10000个报文，下行为vlan是2003的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2003', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤16:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤17:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2004'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2004', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤18:测试仪发送双向10000个报文，下行为vlan是2004的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2004', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤19:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤20:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2005'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2005', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤21:测试仪发送双向10000个报文，下行为vlan是2005的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2005', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤22:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤23:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2006'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2006', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤24:测试仪发送双向10000个报文，下行为vlan是2006的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2006', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤25:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤26:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2007'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2007', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤27:测试仪发送双向10000个报文，下行为vlan是2007的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2007', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤28:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
#
@allure.feature("gemport测试")
@allure.story("gemport测试")
@allure.title("测试mapping为pri")
@pytest.mark.run(order=1012)
def test_gemport_pri(login_gemport):
    cdata_info("=========gemport为pri测试=========")
    tn = login_gemport
    with allure.step("步骤1:修改gemport的mapping的模式为pri"):
        assert gemport_pri(tn,ont_lineprofile_id=Ont_Lineprofile_ID)
    with allure.step('步骤2:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤3:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤4:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, range(2000, 2008))
    with allure.step('步骤5:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤6:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2000', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤7:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤8:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2001，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2001', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤9:测试仪发送双向10000个报文，下行为vlan是2001的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2001', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤10:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤11:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2002，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2002', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤12:测试仪发送双向10000个报文，下行为vlan是2002的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2002', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤13:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤14:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2003，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2003', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤15:测试仪发送双向10000个报文，下行为vlan是2003的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2003', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤16:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤17:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2004，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2004', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤18:测试仪发送双向10000个报文，下行为vlan是2004的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2004', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤19:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤20:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2005，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2005', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤21:测试仪发送双向10000个报文，下行为vlan是2005的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2005', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤22:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤23:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2006，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2006', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤24:测试仪发送双向10000个报文，下行为vlan是2006的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2006', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤25:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤26:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2007，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2007', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤27:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2007', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤28:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤29:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为1'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '1', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤30:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '1', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤31:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤32:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为2'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '2', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤33:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '2', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤34:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤35:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为3'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '3', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤36:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '3', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤37:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤38:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为4'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '4', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤39:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '4', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤40:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤41:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为5'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '5', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤42:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '5', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤43:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤44:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为6'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '6', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤45:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '6', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤46:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤47:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为0'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤48:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤49:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
#
@allure.feature("gemport测试")
@allure.story("gemport测试")
@allure.title("测试mapping为vlan+pri")
@pytest.mark.run(order=1013)
def test_gemport_vlan_pri(login_gemport):
    cdata_info("=========gemport为vlan+pri测试=========")
    tn = login_gemport
    with allure.step("步骤1:修改gemport的mapping的模式为vlan+pri"):
        assert gemport_vlan_pri(tn,ont_lineprofile_id=200,mapping_mode='vlan-priority ')
    with allure.step('步骤2:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤3:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤4:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, range(2000, 2008))
    with allure.step('步骤5:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤6:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_1(stream_rate, '10000', port_location, '2000', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤7:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤8:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2001，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2001', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤9:测试仪发送双向10000个报文，下行为vlan是2001的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2001', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤10:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤11:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2002，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2002', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤12:测试仪发送双向10000个报文，下行为vlan是2002的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2002', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤13:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤14:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2003，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2003', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤15:测试仪发送双向10000个报文，下行为vlan是2003的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2003', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤16:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤17:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2004，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2004', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤18:测试仪发送双向10000个报文，下行为vlan是2004的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2004', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤19:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤20:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2005，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2005', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤21:测试仪发送双向10000个报文，下行为vlan是2005的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2005', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤22:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤23:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2006，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2006', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤24:测试仪发送双向10000个报文，下行为vlan是2006的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2006', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤25:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤26:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2007，优先级为7'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2007', '7', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤27:测试仪发送双向10000个报文，下行为vlan是2007的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2007', '7', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤28:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤29:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为1'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '1', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤30:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000',  port_location, '2000', '1', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤31:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤32:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为2'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '2', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤33:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '2', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤34:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤35:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为3'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '3', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤36:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '3', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤37:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤38:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为4'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '4', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤39:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '4', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤40:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤41:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为5'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '5', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤42:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '5', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤43:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤44:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为6'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '6', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤45:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '6', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤46:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤47:添加omci_wan配置,WAN连接的模式为桥接，WAN连接的vlan为2000，优先级为0'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤48:测试仪发送双向10000个报文，下行为vlan是2000的报文，上行为untag的报文'):
        assert stream_test_vlan_gemport_2(stream_rate, '10000', port_location, '2000', '0', packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤49:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)


if __name__ == '__main__':
    pytest.main(['-v',"-s" ,'-x', 'test_onu_gemport.py::test_gemport_vlan'] )
import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.Gpon_HGU.internet_type import *
# from page.telnet_client import *
from src.Gpon_HGU.omci_wan import *
from src.Gpon_HGU.ont_auth import *
from tests.FD1616GS_HGU.initialization_config import *
# from src.xinertel.renix_test import *
import allure


@allure.feature("WAN连接测试")
@allure.story("WAN连接绑定测试")
@allure.title("桥接的WAN连接测试")
@pytest.mark.run(order=1025)
# @pytest.mark.skip("暂时不执行")
def test_binding_bridge(login):
    '''
    用例描述：
    测试PC是否可以通过DHCP方式上网。
    '''
    cdata_info("=========桥接的WAN连接的绑定测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [4001])
    with allure.step('步骤4:添加omci_wan配置,不绑定任何端口'):
        assert add_omci_wan_bridge_tag_1(tn, Gpon_PonID, Gpon_OnuID, '0', WAN_service_type, '4001',  WAN_pri)
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping_false(Ping_test_addr)
    with allure.step('步骤7:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)



@allure.feature("WAN连接测试")
@allure.story("WAN连接绑定测试")
@allure.title("DHCP的WAN连接")
@pytest.mark.run(order=1026)
# @pytest.mark.skip("暂时不执行")
def test_binding_dhcp(login):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========dhcp的WAN连接的绑定测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [4001])
    with allure.step('步骤4:添加omci_wan配置，不绑定任何端口'):
        assert add_omci_wan_route_dhcp_tag_1(tn, Gpon_PonID, Gpon_OnuID, '0', 'internet', '4001', '0')
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤7:添加omci_wan配置，绑定所有端口'):
        assert add_omci_wan_route_dhcp_tag(tn, Gpon_PonID, Gpon_OnuID, '1', 'internet', '1234', '0',  '1-4', SSID_list, SSID_5g_list)
    with allure.step('步骤8:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤9:PC进行PING测试'):
        assert ping_false(Ping_test_addr)
    with allure.step('步骤10:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, '1')
    with allure.step('步骤11:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, '2')

@allure.feature("WAN连接测试")
@allure.story("WAN连接绑定测试")
@allure.title("static的WAN连接")
@pytest.mark.run(order=1027)
# @pytest.mark.skip("暂时不执行")
def test_binding_static(login):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========static的WAN连接的绑定测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [4001])
    with allure.step('步骤4:添加omci_wan配置，不绑定任何端口'):
        assert add_omci_wan_route_static_tag_1(tn, Gpon_PonID, Gpon_OnuID, '0', 'internet', IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, '4001', '0')
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤7:添加omci_wan配置，绑定所有端口'):
        assert add_omci_wan_route_static_tag(tn, Gpon_PonID, Gpon_OnuID, '1', 'internet', '1.1.1.10', Net_mask, '1.1.1.1', DNS1, DNS2, '1234', '0', '1-4', SSID_list, SSID_5g_list)
    with allure.step('步骤8:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤9:PC进行PING测试'):
        assert ping_false(Ping_test_addr)
    with allure.step('步骤10:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, '0')
    with allure.step('步骤11:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, '1')

@allure.feature("WAN连接测试")
@allure.story("WAN连接绑定测试")
@allure.title("pppoe的WAN连接")
@pytest.mark.run(order=1028)
# @pytest.mark.skip("暂时不执行")
def test_binding_pppoe(login):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========pppoe的WAN连接的绑定测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [4001])
    with allure.step('步骤4:添加omci_wan配置，不绑定任何端口'):
        assert add_omci_wan_route_pppoe_tag_1(tn, Gpon_PonID, Gpon_OnuID, '0', 'internet', '4001', pppoe_name, pppoe_password, '0')
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤7:添加omci_wan配置，绑定所有端口'):
        assert add_omci_wan_route_pppoe_tag(tn, Gpon_PonID, Gpon_OnuID, '1', 'internet', '1234', pppoe_name, pppoe_password, '0', '1-4', SSID_list, SSID_5g_list)
    with allure.step('步骤8:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤9:PC进行PING测试'):
        assert ping_false(Ping_test_addr)
    with allure.step('步骤10:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤11:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, '1')


if __name__ == '__main__':
    # case_1()
    pytest.main(["-s",'-v',"test_onu_wan_binding.py"])





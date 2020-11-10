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
@allure.story("TAG模式WAN连接测试")
@allure.title("桥接的WAN连接测试")
@pytest.mark.run(order=1017)
# @pytest.mark.skip("暂时不执行")
def test_tag_bridge(login):
    '''
    用例描述：
    测试PC是否可以通过DHCP方式上网。
    '''
    cdata_info("=========桥接的WAN连接TAG模式测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [4001])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '4001', '0',  ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:检测PC是否获取到了公司DHCP服务器分配的IP地址'):
        assert check_ip(Network_car_name)
    with allure.step('步骤7:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤8:PC进行SPEEDTEST测试'):
        assert speedtest_test()
    with allure.step('步骤9:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)
    with allure.step('步骤10:检测PC是否获取到了LAN接口分配的IP地址'):
        assert check_ip_1(Network_car_name)

@allure.feature("WAN连接测试")
@allure.story("TAG模式WAN连接测试")
@allure.title("dhcp的WAN连接测试")
@pytest.mark.run(order=1018)
# @pytest.mark.skip("暂时不执行")
def test_tag_dhcp(login):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========dhcp的WAN连接TAG模式测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [4001])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_route_dhcp_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, 'internet', '4001', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤7:PC进行SPEEDTEST测试'):
        assert speedtest_test()
    with allure.step('步骤8:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)

@allure.feature("WAN连接测试")
@allure.story("TAG模式WAN连接测试")
@allure.title("static的WAN连接测试")
@pytest.mark.run(order=1019)
# @pytest.mark.skip("暂时不执行")
def test_tag_static(login):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========static的WAN连接TAG模式测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [4001])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_route_static_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, 'internet', IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, '4001', '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤7:PC进行SPEEDTEST测试'):
        assert speedtest_test()
    with allure.step('步骤8:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)

@allure.feature("WAN连接测试")
@allure.story("TAG模式WAN连接测试")
@allure.title("pppoe的WAN连接测试")
@pytest.mark.run(order=1020)
# @pytest.mark.skip("暂时不执行")
def test_tag_pppoe(login):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========pppoe的WAN连接TAG模式测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [4001])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_route_pppoe_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, 'internet', '4001', pppoe_name, pppoe_password, '0', ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤7:PC进行SPEEDTEST测试'):
        assert speedtest_test()
    with allure.step('步骤8:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)

if __name__ == '__main__':
    # case_1()
    pytest.main(["-v",'-s',"test_onu_wan_tag.py"])





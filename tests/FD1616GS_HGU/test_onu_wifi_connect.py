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






@allure.feature("WIFI测试")
@allure.story("WIFI连接测试")
@allure.title("2.4G的WIFI连接测试")
@pytest.mark.run(order=1029)
# @pytest.mark.skip("暂时不执行")
def test_wifi_connect_2_4g(login_1):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========2.4G的WIFI连接测试=========")
    tn = login_1
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [4001])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_route_dhcp_tag(tn, Gpon_PonID, Gpon_OnuID, '0', 'internet', '4001', '0',  ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:将电脑连接ONU的LAN口disable。'):
        assert disable_interface(interface_name)
    with allure.step('步骤6:连接2.4G的无线。'):
        assert wifi_connect(wifi_2_4g_ssid, wifi_2_4g_password)
    with allure.step('步骤7:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤8:PC进行SPEEDTEST测试'):
        assert speedtest_test_wifi()


@allure.feature("ONU业务测试")
@allure.story("ONU上网方式测试")
@allure.title("静态IP测试")
@pytest.mark.run(order=1030)
# @pytest.mark.skip("暂时不执行")
def test_wifi_connect_5g(login_1):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========5G的WIFI连接测试=========")
    tn = login_1
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [4001])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_route_dhcp_tag(tn, Gpon_PonID, Gpon_OnuID, '0', 'internet', '4001', '0',  ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:将电脑连接ONU的LAN口disable。'):
        assert disable_interface(interface_name)
    with allure.step('步骤6:连接5G的无线。'):
        assert wifi_connect(wifi_5g_ssid, wifi_5g_password)
    with allure.step('步骤7:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤8:PC进行SPEEDTEST测试'):
        assert speedtest_test_wifi()


if __name__ == '__main__':
    # case_1()
    pytest.main(["-v","test_onu_internet_type.py::test_static_ip"])





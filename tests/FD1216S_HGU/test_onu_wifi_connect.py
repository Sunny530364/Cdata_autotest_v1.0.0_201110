import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.Epon_HGU.internet_type import *
# from page.telnet_client import *
from src.Epon_HGU.oam_wan import *
from src.Epon_HGU.ont_auth import *
from tests.FD1216S_HGU.initialization_config import *
# from src.xinertel.renix_test import *
import allure






@allure.feature("WIFI测试")
@allure.story("WIFI连接测试")
@allure.title("2.4G的WIFI连接测试")
@pytest.mark.run(order=2022)
# @pytest.mark.skip("暂时不执行")
def test_wifi_connect_2_4g(login_1):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========2.4G的WIFI连接测试=========")
    tn = login_1
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        assert add_pon_vlan(tn, Epon_PonID, '4001')
    with allure.step('步骤4:添加oam_wan配置'):
        assert add_oam_wan_dhcp_vlan_enable(tn, Epon_PonID, Epon_OnuID, 'cdata_test', 'enable', '4001' , '0', 'internet', '1-8')
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
@pytest.mark.run(order=2023)
# @pytest.mark.skip("暂时不执行")
def test_wifi_connect_5g(login_1):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========5G的WIFI连接测试=========")
    tn = login_1
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        assert add_pon_vlan(tn, Epon_PonID, '4001')
    with allure.step('步骤4:添加oam_wan配置'):
        assert add_oam_wan_dhcp_vlan_enable(tn, Epon_PonID, Epon_OnuID, 'cdata_test', 'enable', '4001' , '0', 'internet', '1-8')
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





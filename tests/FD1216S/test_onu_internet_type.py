import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.FD1216S.internet_type import *
# from page.telnet_client import *
from src.FD1216S.ont_auth import *
from tests.FD1216S.initialization_config import *
# from src.xinertel.renix_test import *
import allure


@allure.feature("ONU业务测试")
@allure.story("ONU上网方式测试")
@allure.title("DHCP测试")
@pytest.mark.run(order=1207)
# @pytest.mark.skip("暂时不执行")
def test_dhcp(login):
    '''
    用例描述：
    测试PC是否可以通过DHCP方式上网。
    '''
    cdata_info("=========ONU业务测试：DHCP测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过Epon_LOID+PASSWORD的方式将ONU注册上线。'):
        assert auth_by_loid_password(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_LOID, Epon_LOID_PASSWORD, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        Vlan_list=Internet_Vlan
        assert add_pon_vlan(tn, Epon_PonID, Vlan_list)
    with allure.step('步骤4:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Onu_port_ID='2', User_vlan=Internet_Vlan)
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤7:PC进行SPEEDTEST测试'):
        assert speedtest_test()


@allure.feature("ONU业务测试")
@allure.story("ONU上网方式测试")
@allure.title("静态IP测试")
@pytest.mark.run(order=1208)
# @pytest.mark.skip("暂时不执行")
def test_static_ip(login):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========ONU业务测试：static ip测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过Epon_LOID+PASSWORD的方式将ONU注册上线。'):
        assert auth_by_loid_password(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_LOID, Epon_LOID_PASSWORD, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        Vlan_list=Internet_Vlan
        assert add_pon_vlan(tn, Epon_PonID, Vlan_list)
    with allure.step('步骤4:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Onu_port_ID='2', User_vlan=Internet_Vlan)
    with allure.step('步骤5:PC设置静态IP地址'):
        assert static_ip_test(Network_car_name)
        time.sleep(5)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤7:PC进行SPEEDTEST测试'):
        assert speedtest_test()
    with allure.step('步骤8:将PC恢复DHCP方式获取IP地址'):
        assert static_turn_to_dhcp(Network_car_name)


@allure.feature("ONU业务测试")
@allure.story("ONU上网方式测试")
@allure.title("PPPoE拨号测试")
@pytest.mark.run(order=1209)
# @pytest.mark.skip("暂时不执行")
def test_pppoe_connect(login):
    '''
    用例描述：
    测试PC是否可以通过PPPoE方式上网。
    '''
    cdata_info("=========ONU业务测试：PPPOE拨号测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过Epon_LOID+PASSWORD的方式将ONU注册上线。'):
        assert auth_by_loid_password(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_LOID, Epon_LOID_PASSWORD, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        Vlan_list=Internet_Vlan
        assert add_pon_vlan(tn, Epon_PonID, Vlan_list)
    with allure.step('步骤4:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Onu_port_ID='2', User_vlan=Internet_Vlan)
    with allure.step('步骤5:PC进行宽带拨号上网'):
        assert pppoe_connect(pppoe_client, pppoe_name, pppoe_password)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤7:PC进行SPEEDTEST测试'):
        assert speedtest_test()
    with allure.step('步骤8:断开PC的PPPoE拨号'):
        assert pppoe_disconnect(pppoe_client)


if __name__ == '__main__':
    # case_1()
    pytest.main(["-v","test_onu_internet_type.py::test_static_ip"])





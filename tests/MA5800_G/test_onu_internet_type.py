import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.MA5800_G.internet_type import *
from src.MA5800_G.ont_auth import *
from src.MA5800_G.gemport import *
from src.config.initialization_config import *
import allure


@allure.feature("ONU业务测试")
@allure.story("ONU上网方式测试")
@allure.title("DHCP测试")
@pytest.mark.run(order=5808)
# @pytest.mark.skip("暂时不执行")
def test_dhcp(login):
    '''
    用例描述：
    测试PC是否可以通过DHCP方式上网。
    '''
    cdata_info("=========ONU业务测试：DHCP测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:修改gemport配置为vlan"):
        assert gemport_vlan(tn, Ont_Lineprofile_ID,[4001],Gemport_ID)
    with allure.step('步骤4:在OLT配置ONU的service-port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID,Gemport_ID,[4001])
    with allure.step('步骤5:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, '2', '4001')
    with allure.step('步骤6:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤7:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤8:PC进行SPEEDTEST测试'):
        assert speedtest_test()


@allure.feature("ONU业务测试")
@allure.story("ONU上网方式测试")
@allure.title("静态IP测试")
@pytest.mark.run(order=5809)
# @pytest.mark.skip("暂时不执行")
def test_static_ip(login):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========ONU业务测试：static ip测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:修改gemport配置为vlan"):
        assert gemport_vlan(tn, Ont_Lineprofile_ID,[4001],Gemport_ID)
    with allure.step('步骤4:在OLT配置ONU的service-port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID,Gemport_ID,[4001])
    with allure.step('步骤5:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, '2', '4001')
    with allure.step('步骤6:PC设置静态IP地址'):
        assert static_ip_test(Network_car_name)
        time.sleep(5)
    with allure.step('步骤7:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤8:PC进行SPEEDTEST测试'):
        assert speedtest_test()
    with allure.step('步骤8:将PC恢复DHCP方式获取IP地址'):
        assert static_turn_to_dhcp(Network_car_name)


@allure.feature("ONU业务测试")
@allure.story("ONU上网方式测试")
@allure.title("PPPoE拨号测试")
@pytest.mark.run(order=5810)
# @pytest.mark.skip("暂时不执行")
def test_pppoe_connect(login):
    '''
    用例描述：
    测试PC是否可以通过PPPoE方式上网。
    '''
    cdata_info("=========ONU业务测试：PPPOE拨号测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:修改gemport配置为vlan"):
        assert gemport_vlan(tn, Ont_Lineprofile_ID,[4001],Gemport_ID)
    with allure.step('步骤4:在OLT配置ONU的service-port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID,Gemport_ID,[4001])
    with allure.step('步骤5:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, '2', '4001')
    with allure.step('步骤6:PC进行宽带拨号上网'):
        assert pppoe_connect(pppoe_client, pppoe_name, pppoe_password)
    with allure.step('步骤7:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤8:PC进行SPEEDTEST测试'):
        assert speedtest_test()
    with allure.step('步骤9:断开PC的PPPoE拨号'):
        assert pppoe_disconnect(pppoe_client)


if __name__ == '__main__':
    # case_1()
    pytest.main(["-v","test_onu_internet_type.py::test_static_ip"])





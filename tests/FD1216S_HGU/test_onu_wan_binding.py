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


@allure.feature("WAN连接测试")
@allure.story("WAN连接绑定测试")
@allure.title("桥接的WAN连接测试")
@pytest.mark.run(order=2018)
# @pytest.mark.skip("暂时不执行")
def test_binding_bridge(login):
    '''
    用例描述：
    测试PC是否可以通过DHCP方式上网。
    '''
    cdata_info("=========桥接的WAN连接的绑定测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        assert add_pon_vlan(tn, Epon_PonID, '4001')
    with allure.step('步骤4:添加oam_wan配置'):
        assert add_oam_wan_bridge_not_bind(tn, Epon_PonID, Epon_OnuID, 'cdata_test', 'enable', '4001', '0', 'vod')
    with allure.step('步骤6:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤7:PC进行PING测试'):
        assert ping_false(Ping_test_addr)
    with allure.step('步骤9:删除oam_wan配置'):
        assert del_oam_wan(tn, Epon_PonID, Epon_OnuID)




@allure.feature("WAN连接测试")
@allure.story("WAN连接绑定测试")
@allure.title("DHCP的WAN连接")
@pytest.mark.run(order=2019)
# @pytest.mark.skip("暂时不执行")
def test_binding_dhcp(login):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========dhcp的WAN连接的绑定测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        assert add_pon_vlan(tn, Epon_PonID, '4001')
    with allure.step('步骤4:添加oam_wan配置'):
        assert add_oam_wan_dhcp_not_bind(tn, Epon_PonID, Epon_OnuID, 'cdata_test', 'enable', '4001', '0', 'internet')
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤4:添加oam_wan配置'):
        assert add_oam_wan_dhcp_vlan_enable(tn, Epon_PonID, Epon_OnuID, 'cdata_test1', 'enable', '1234', '0', 'internet', '1-8')
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping_false(Ping_test_addr)
    with allure.step('步骤9:删除oam_wan配置'):
        assert del_oam_wan(tn, Epon_PonID, Epon_OnuID)

@allure.feature("WAN连接测试")
@allure.story("WAN连接绑定测试")
@allure.title("static的WAN连接")
@pytest.mark.run(order=2020)
# @pytest.mark.skip("暂时不执行")
def test_binding_static(login):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========static的WAN连接的绑定测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        assert add_pon_vlan(tn, Epon_PonID, '4001')
    with allure.step('步骤4:添加oam_wan配置'):
        assert add_oam_wan_static_not_bind(tn, Epon_PonID, Epon_OnuID, 'cdata_test', 'enable', '4001', '0', 'internet', IP_addr, Net_mask, IP_default_gw, DNS1, DNS2)
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤7:添加oam_wan配置'):
        assert add_oam_wan_static_vlan_enable(tn, Epon_PonID, Epon_OnuID, 'cdata_test1', 'enable', '1234', '0', 'internet', '1.1.1.10', Net_mask, '1.1.1.1', DNS1, DNS2, '1-8')
    with allure.step('步骤8:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤9:PC进行PING测试'):
        assert ping_false(Ping_test_addr)
    with allure.step('步骤10:删除oam_wan配置'):
        assert del_oam_wan(tn, Epon_PonID, Epon_OnuID)

@allure.feature("WAN连接测试")
@allure.story("WAN连接绑定测试")
@allure.title("pppoe的WAN连接")
@pytest.mark.run(order=2021)
# @pytest.mark.skip("暂时不执行")
def test_binding_pppoe(login):
    '''
    用例描述：
    测试PC是否可以通过静态IP的方式上网。
    '''
    cdata_info("=========pppoe的WAN连接的绑定测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        assert add_pon_vlan(tn, Epon_PonID, '4001')
    with allure.step('步骤4:添加oam_wan配置'):
        assert add_oam_wan_pppoe_not_bind(tn, Epon_PonID, Epon_OnuID, 'cdata_test', 'enable', '4001' , '0', 'internet', pppoe_name, pppoe_password)
    with allure.step('步骤5:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤6:PC进行PING测试'):
        assert ping(Ping_test_addr)
    with allure.step('步骤7:添加oam_wan配置'):
        assert add_oam_wan_pppoe_vlan_enable(tn, Epon_PonID, Epon_OnuID, 'cdata_test1', 'enable', '1234' , '0', 'internet', pppoe_name, pppoe_password, '1-8')
    with allure.step('步骤8:PC重新获取IP地址'):
        assert dhcp_test(Network_car_name)
    with allure.step('步骤9:PC进行PING测试'):
        assert ping_false(Ping_test_addr)
    with allure.step('步骤10:删除oam_wan配置'):
        assert del_oam_wan(tn, Epon_PonID, Epon_OnuID)


if __name__ == '__main__':
    # case_1()
    pytest.main(["-v",'-s',"test_onu_wan_binding.py"])





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
from src.xinertel.renix_test import *
import allure


@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("MAC认证")
@pytest.mark.run(order=2004)
def test_auth_by_mac(login):
    '''
    用例描述：
    ONU通过SN的方式认证。
    例如：
    ont add 1 1 sn-auth TEST12345678 ont-lineprofile-id 1 ont-srvprofile-id 1
    '''
    cdata_info("=========ONT SN认证测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        assert add_pon_vlan(tn, Epon_PonID, '2000')
    with allure.step('步骤4:添加桥接模式的oam_wan,VLAN为2000，业务类型为OTHE'):
        assert add_oam_wan_bridge_vlan_enable(tn, Epon_PonID, Epon_OnuID, 'cdata_test', 'enable', '2000', '0', 'vod', '1-8')
    with allure.step('步骤5:测试仪发送双向100000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name = sys._getframe().f_code.co_name)
    with allure.step('步骤6:删除oam_wan配置'):
        assert del_oam_wan(tn, Epon_PonID, Epon_OnuID)




@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("LOID认证")
@pytest.mark.run(order=2005)
def test_auth_by_loid(login):
    '''
    用例描述：
    ONU通过LOID的方式认证。
    例如：
    ont add 1 1 loid-auth 12345678 ont-lineprofile-id 1 ont-srvprofile-id 1
    '''
    cdata_info("=========ONT LOID认证测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过LOID的方式将ONU注册上线。'):
        assert auth_by_loid(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_LOID, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        assert add_pon_vlan(tn, Epon_PonID, '2000')
    with allure.step('步骤4:添加桥接模式的oam_wan,VLAN为2000，业务类型为OTHER'):
        assert add_oam_wan_bridge_vlan_enable(tn, Epon_PonID, Epon_OnuID, 'cdata_test', 'enable', '2000', '0', 'vod', '1-8')
    with allure.step('步骤5:测试仪发送双向100000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name = sys._getframe().f_code.co_name)
    with allure.step('步骤6:删除oam_wan配置'):
        assert del_oam_wan(tn, Epon_PonID, Epon_OnuID)


@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("LOID+PASSWORD认证")
@pytest.mark.run(order=2006)
def test_auth_by_loid_password(login):
    '''
    用例描述：
    ONU通过SN的方式认证。
    例如：
    ont add 1 1 loid-auth 12345678 password-auth 12345678 ont-lineprofile-id 1 ont-srvprofile-id 1
    '''
    cdata_info("=========ONT LOID+PASSWORD认证测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过LOID+PASSWORD的方式将ONU注册上线。'):
        assert auth_by_loid_password(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID,Epon_LOID, Epon_LOID_PASSWORD, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        assert add_pon_vlan(tn, Epon_PonID, '2000')
    with allure.step('步骤4:添加桥接模式的oam_wan,VLAN为2000，业务类型为OTHER'):
        assert add_oam_wan_bridge_vlan_enable(tn, Epon_PonID, Epon_OnuID, 'cdata_test', 'enable', '2000', '0', 'vod', '1-8')
    with allure.step('步骤5:测试仪发送双向100000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name = sys._getframe().f_code.co_name)
    with allure.step('步骤6:删除oam_wan配置'):
        assert del_oam_wan(tn, Epon_PonID, Epon_OnuID)

if __name__ == '__main__':
    # case_1()
    pytest.main(["-v",'-s', "-x", "test_onu_auth_type.py::test_auth_by_mac"])





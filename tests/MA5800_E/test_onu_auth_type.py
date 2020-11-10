import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.MA5800_E.internet_type import *
from src.MA5800_E.ont_auth import *
from tests.MA5800_E.initialization_config import *
from src.xinertel.renix_test import *
import allure


@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("SN认证")
@pytest.mark.run(order=15803)
def test_auth_by_mac(login):
    '''
    用例描述：
    ONU通过SN的方式认证。
    例如：
    ont add 1 1 sn-auth TEST12345678 ont-lineprofile-id 1 ont-srvprofile-id 1
    '''
    cdata_info("=========ONT MAC认证测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置ONU的service-port'):
        assert add_service_port(tn, Epon_PonID, Epon_OnuID,[2000])
    with allure.step('步骤4:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID, User_Vlan)
    # import time
    # time.sleep(3600)
    with allure.step('步骤5:测试仪发送双向100000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)


@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("LOID认证")
@pytest.mark.run(order=15804)
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
    with allure.step('步骤3:在OLT配置ONU的service-port'):
        assert add_service_port(tn, Epon_PonID, Epon_OnuID,[2000])
    with allure.step('步骤4:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step('步骤5:测试仪发送双向100000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)


@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("LOID+PASSWORD认证")
@pytest.mark.run(order=15805)
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
        assert auth_by_loid_password(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_LOID, Epon_LOID_PASSWORD, Epon_ONU_MAC)
    with allure.step('步骤3:在OLT配置ONU的service-port'):
        assert add_service_port(tn, Epon_PonID, Epon_OnuID,[2000])
    with allure.step('步骤4:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step('步骤5:测试仪发送双向100000个报文。'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)


if __name__ == '__main__':
    # case_1()
    pytest.main(["-v",'-s',"-x","test_onu_auth_type.py"])





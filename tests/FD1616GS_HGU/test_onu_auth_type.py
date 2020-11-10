import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.Gpon_HGU.internet_type import *
# from page.telnet_client import *
from src.Gpon_HGU.ont_auth import *
from src.Gpon_HGU.omci_wan import *
from tests.FD1616GS_HGU.initialization_config import  *
from src.xinertel.renix_test import *
import allure


@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("SN认证")
@pytest.mark.run(order=1004)
def test_auth_by_sn(login):
    '''
    用例描述：
    ONU通过SN的方式认证。
    例如：
    ont add 1 1 sn-auth TEST12345678 ont-lineprofile-id 1 ont-srvprofile-id 1
    '''
    cdata_info("=========ONT SN认证测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):

        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0',  ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:测试仪发送双向10000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name = sys._getframe().f_code.co_name)
    with allure.step('步骤6:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)



@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("SN的PASSWORD认证")
@pytest.mark.run(order=1005)
def test_auth_by_snpassword(login):
    '''
    用例描述：
    SN的PASSWORD认证。
    例如：
    ont add 1 1 password-auth 12345678 ont-lineprofile-id 1 ont-srvprofile-id 1
    '''
    cdata_info("=========ONT SNPASSWORD认证测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的PASSWORD的方式将ONU注册上线。'):
        assert auth_by_snpassword(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN, Gpon_SN_PASSWORD)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0',  ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:测试仪发送双向10000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤6:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)



@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("SN+PASSWORD认证")
@pytest.mark.run(order=1006)
def test_auth_by_sn_password(login):
    '''
    用例描述：
    ONU通过SN+PASSWORD的方式认证。
    例如：
    ont add 1 1 sn-auth TEST12345678 password-auth 12345678 ont-lineprofile-id 1 ont-srvprofile-id 1
    '''
    cdata_info("=========ONT SN+PASSWORD认证测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN+PASSWORD的方式将ONU注册上线。'):
        assert auth_by_sn_password(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID,Gpon_SN,Gpon_SN_PASSWORD)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0',  ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:测试仪发送双向10000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name = sys._getframe().f_code.co_name)
    with allure.step('步骤6:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)


@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("LOID认证")
@pytest.mark.run(order=1007)
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
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过LOID的方式将ONU注册上线。'):
        assert auth_by_loid(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_LOID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0',  ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:测试仪发送双向10000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name = sys._getframe().f_code.co_name)
    with allure.step('步骤6:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)


@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("LOID+PASSWORD认证")
@pytest.mark.run(order=1008)
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
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过LOID+PASSWORD的方式将ONU注册上线。'):
        assert auth_by_loid_password(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_LOID,Gpon_LOID_PASSWORD, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000])
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0',  ETH_list, SSID_list, SSID_5g_list)
    with allure.step('步骤5:测试仪发送双向10000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name = sys._getframe().f_code.co_name)
    with allure.step('步骤6:删除omci_wan配置'):
        assert del_omci_wan(tn, Gpon_PonID, Gpon_OnuID, WAN_ID)


if __name__ == '__main__':
    pytest.main(["-s","-x","test_onu_auth_type.py::test_auth_by_loid"])








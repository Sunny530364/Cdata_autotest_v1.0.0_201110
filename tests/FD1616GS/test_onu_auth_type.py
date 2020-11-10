#!/usr/bin/python
# -*- coding UTF-8 -*-

import sys
import time
import pytest
from os.path import dirname, abspath

# import sys
# # reload(sys)
# sys.setdefaultencoding('utf-8')

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.FD1616GS.internet_type import *
# from page.telnet_client import *
from src.FD1616GS.ont_auth import *
from tests.FD1616GS.initialization_config import *
from src.xinertel.renix_test import *
import allure
from src.xinertel.unicast66 import *

@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("Gpon_SN认证")
@pytest.mark.run(order=1604)
def test_auth_by_sn(login):
    '''
    用例描述：
    ONU通过Gpon_SN的方式认证。
    例如：
    ont add 1 1 sn-auth TEST12345678 ont-lineprofile-id 1 ont-srvprofile-id 1
    '''
    cdata_info("=========ONT Gpon_SN认证测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000, 4001])
    with allure.step('步骤4:ONU的以太网口1添加NATIVE-VLAN'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID,User_vlan= '2000')
    with allure.step('步骤5:ONU的以太网口2添加NATIVE-VLAN'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID='2',User_vlan= '4001')

    with allure.step('步骤6:测试仪发送双向10000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)




@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("Gpon_SN的PASSWORD认证")
@pytest.mark.run(order=1605)
def test_auth_by_snpassword(login):
    '''
    用例描述：
    Gpon_SN的PASSWORD认证。
    例如：
    ont add 1 1 password-auth 12345678 ont-lineprofile-id 1 ont-srvprofile-id 1
    '''
    cdata_info("=========ONT Gpon_SNPASSWORD认证测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的PASSWORD的方式将ONU注册上线。'):
        assert auth_by_snpassword(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN, Gpon_SN_PASSWORD)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000, 4001])
    with allure.step('步骤4:ONU的以太网口1添加NATIVE-VLAN'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID,User_vlan= '2000')
    with allure.step('步骤5:ONU的以太网口2添加NATIVE-VLAN'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID='2',User_vlan= '4001')
    with allure.step('步骤6:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)



@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("Gpon_SN+PASSWORD认证")
@pytest.mark.run(order=1606)
def test_auth_by_sn_password(login):
    '''
    用例描述：
    ONU通过Gpon_SN+PASSWORD的方式认证。
    例如：
    ont add 1 1 sn-auth TEST12345678 password-auth 12345678 ont-lineprofile-id 1 ont-srvprofile-id 1
    '''
    cdata_info("=========ONT Gpon_SN+PASSWORD认证测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN+PASSWORD的方式将ONU注册上线。'):
        assert auth_by_sn_password(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN, Gpon_SN_PASSWORD)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000, 4001])
    with allure.step('步骤4:ONU的以太网口1添加NATIVE-VLAN'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID,User_vlan= '2000')
    with allure.step('步骤5:ONU的以太网口2添加NATIVE-VLAN'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID='2',User_vlan= '4001')
    with allure.step('步骤6:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)


@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("LOID认证")
@pytest.mark.run(order=1607)
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
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000, 4001])
    with allure.step('步骤4:ONU的以太网口1添加NATIVE-VLAN'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID,User_vlan= '2000')
    with allure.step('步骤5:ONU的以太网口2添加NATIVE-VLAN'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID='2',User_vlan= '4001')
    with allure.step('步骤6:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)


@allure.feature("ONU认证")
@allure.story("ONU认证方式")
@allure.title("LOID+PASSWORD认证")
@pytest.mark.run(order=1608)
def test_auth_by_loid_password(login):
    '''
    用例描述：
    ONU通过Gpon_SN的方式认证。
    例如：
    ont add 1 1 loid-auth 12345678 password-auth 12345678 ont-lineprofile-id 1 ont-srvprofile-id 1
    '''
    cdata_info("=========ONT LOID+PASSWORD认证测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过LOID+PASSWORD的方式将ONU注册上线。'):
        assert auth_by_loid_password(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_LOID, Gpon_LOID_PASSWORD, Gpon_SN)
    with allure.step('步骤3:添加service_port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, [2000, 4001])
    with allure.step('步骤4:ONU的以太网口1添加NATIVE-VLAN'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID,User_vlan= '2000')
    with allure.step('步骤5:ONU的以太网口2添加NATIVE-VLAN'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID='2',User_vlan= '4001')
    with allure.step('步骤6:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)


if __name__ == '__main__':
    # case_1()
    pytest.main(["-v",'-s',"test_onu_auth_type.py::test_auth_by_sn"])





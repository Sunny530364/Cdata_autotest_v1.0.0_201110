import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.FD1216S.internet_type import *
from src.FD1216S.ont_auth import *
from tests.FD1216S.initialization_config import *
from src.xinertel.renix_test import *
import allure


@allure.feature("ONU远程管理")
@allure.story("远程管理ONU")
@allure.title("去激活ONU")
@pytest.mark.run(order=1221)
def test_deactive_onu(login):
    '''
    用例描述：
    再OLT上将ONU去激活后，再重新激活。
    例如：
    ont deactivate 1 1
    ont activate 1 1
    '''
    cdata_info("=========去激活ONU=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:在olt上配置ge口trunk 2000。'):
        Vlan_list = User_Vlan
        assert add_pon_vlan(tn, Epon_PonID, Vlan_list)
    with allure.step('步骤4:在OLT上通过SN的方式将ONU注册上线。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step('步骤5:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤6:在OLT上通过SN的方式将ONU注册上线。'):
        assert deactive_onu(tn, Epon_PonID, Epon_OnuID)
    with allure.step('步骤7:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)


@allure.feature("ONU远程管理")
@allure.story("远程管理ONU")
@allure.title("远程重启ONU")
@pytest.mark.run(order=1222)
def test_reboot_onu(login):
    '''
    用例描述：
    在OLT上远程重启ONU。
    例如：
    ont reboot 1 1
    '''
    cdata_info("=========远程重启ONU=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    # with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
    #     assert add_pon_vlan(tn, Epon_PonID, Vlan_list)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step('步骤2:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert reboot_onu(tn, Epon_PonID, Epon_OnuID)
    with allure.step('步骤2:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)


@allure.feature("ONU远程管理")
@allure.story("远程管理ONU")
@allure.title("OMCI升级ONU")
#@pytest.mark.skip("暂时不执行")
@pytest.mark.run(order=1202)
def test_upgrade_onu(login):
    '''
    用例描述：
    通过OMCI升级ONU。
    例如：
    load file tftp 192.168.5.100 FD514GB-G_V1.0.1_190909_1158_X000.bin
    ont load select 0/0 1 1
    ont load start 0/0 FD514GB-G_V1.0.1_190909_1158_X000.bin activemode immediate
    '''
    cdata_info("=========OMCI升级ONU=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    # with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
    #     assert add_pon_vlan(tn, Epon_PonID, Vlan_list)
    with allure.step('步骤2:配置onu的native-vlan。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step('步骤2:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert upgrade_onu(tn, Epon_PonID, Epon_OnuID, tftp_server_ip, file_name)
    with allure.step('步骤2:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)


if __name__ == '__main__':
    # case_1()
    pytest.main(["-s","-x","test_onu_mgt.py::test_deactive_onu"])





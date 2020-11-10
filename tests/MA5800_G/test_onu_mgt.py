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
from src.xinertel.renix_test import *
import allure


@allure.feature("ONU远程管理")
@allure.story("远程管理ONU")
@allure.title("去激活ONU")
@pytest.mark.run(order=5825)
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
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:修改gemport配置为vlan"):
        assert gemport_vlan(tn, Ont_Lineprofile_ID,[2000],Gemport_ID)
    with allure.step('步骤4:在OLT配置ONU的service-port。'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID,Gemport_ID,[2000])
    with allure.step('步骤5:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step('步骤6:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤7:去激活ONU后，重新激活ONU。'):
        assert deactive_onu(tn, Gpon_PonID, Gpon_OnuID)
    with allure.step('步骤8:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)


@allure.feature("ONU远程管理")
@allure.story("远程管理ONU")
@allure.title("远程重启ONU")
@pytest.mark.run(order=5826)
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
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:修改gemport配置为vlan"):
        assert gemport_vlan(tn, Ont_Lineprofile_ID,[2000],Gemport_ID)
    with allure.step('步骤4:在OLT配置ONU的service-port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID,Gemport_ID,[2000])
    with allure.step('步骤5:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step('步骤6:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤7:在OLT上远程重启ONU。'):
        assert reboot_onu(tn, Gpon_PonID, Gpon_OnuID)
    with allure.step('步骤8:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)

@allure.feature("ONU远程管理")
@allure.story("远程管理ONU")
@allure.title("OMCI升级ONU")
@pytest.mark.run(order=5801)
def test_upgrade_onu(login):
    '''
    用例描述：test
    通过OMCI升级ONU。
    例如：
    load file tftp 192.168.5.100 FD514GB-G_V1.0.1_190909_1158_X000.bin
    ont load select 0/0 1 1
    ont load start 0/0 FD514GB-G_V1.0.1_190909_1158_X000.bin activemode immediate
    '''
    cdata_info("=========OMCI升级ONU=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:修改gemport配置为vlan"):
        assert gemport_vlan(tn, Ont_Lineprofile_ID,[2000],Gemport_ID)
    with allure.step('步骤4:在OLT配置ONU的service-port'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID,Gemport_ID,[2000])
    with allure.step('步骤5:ONU的以太网口4添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step('步骤6:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)
    with allure.step('步骤7:在OLT上通过OAM升级ONU。'):
        assert upgrade_onu(tn, Gpon_PonID, Gpon_OnuID, tftp_server_ip, file_name)
    with allure.step('步骤8:测试仪发送双向100000个报文'):
        assert stream_test(stream_rate, stream_num, port_location, packet_name=sys._getframe().f_code.co_name)


if __name__ == '__main__':
    # case_1()
    pytest.main(["-v","-x","test_onu_mgt.py::test_upgrade_onu"])





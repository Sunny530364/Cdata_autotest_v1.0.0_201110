import sys
import time
import pytest
from os.path import dirname, abspath
base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.MA5800_G.internet_type import *
from src.MA5800_G.ont_auth import *
from src.config.initialization_config import *
import allure


@allure.feature("信息上报")
@allure.story("ONU信息上报")
@allure.title("查看ONU的信息上报")
@pytest.mark.run(order=5802)
def test_get_info(login):
    '''
    用例描述：
    查看ONU上报的基本信息。
    例如：
    show ont info 1 1
    show ont version 1 1
    show ont capability 1 1
    show ont optical-info 1 1
    '''
    cdata_info("=========查看onu的信息上报=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3:获取ONU的基本信息。'):
        assert get_onu_info(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)

if __name__ == '__main__':
    # case_1()
    pytest.main(["-v",'-s',"test_get_ont_info.py"])





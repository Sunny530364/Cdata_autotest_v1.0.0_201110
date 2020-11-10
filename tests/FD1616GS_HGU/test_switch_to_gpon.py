import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.Gpon_HGU.internet_type import *
# from page.telnet_client import *
from src.Gpon_HGU.ont_auth import *
from src.Gpon_HGU.switch_to_gpon import *
from tests.FD1616GS_HGU.initialization_config import *
# from src.Gpon_HGU.renix_test import *
import allure


@allure.feature("切换OLT")
@allure.story("切换OLT为GPON")
@allure.title("切换成GPON的OLT")
@pytest.mark.run(order=1001)
def test_switch_to_gpon(login_gpon,login_epon):
    '''
    用例描述：
    查看ONU上报的基本信息。
    例如：
    show ont info 1 1
    show ont version 1 1
    show ont capability 1 1
    show ont optical-info 1 1
    '''
    cdata_info("=========切换成GPON的OLT=========")
    tn_gpon = login_gpon
    tn_epon = login_epon
    with allure.step('步骤1:关闭EPON OLT上相应PON口的TX。'):
        assert shutdown_epon(login_epon, Epon_PonID)
    with allure.step('步骤2:开启GPON OLT上相应PON口的TX。'):
        assert no_shutdown_gpon(login_gpon, Gpon_PonID)
        time.sleep(60)
    with allure.step('步骤3:发现未注册的ONU。'):
        assert autofind_onu(login_gpon, Gpon_PonID, Gpon_OnuID, Gpon_SN)



if __name__ == '__main__':
    # case_1()
    pytest.main(["-v",'-s',"test_switch_to_gpon.py"])





import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.FD1216S.olt_opera import *
from src.FD1616GS.olt_opera import *
from src.FD1216S.ont_auth import *
from tests.FD1216S.initialization_config import *

import allure


@allure.feature("切换OLT")
@allure.story("切换OLT为EPON")
@allure.title("切换成EPON的OLT")
@pytest.mark.run(order=1201)
def test_switch_to_epon(login_gpon,login_epon):

    cdata_info("=========将OLT切换成EPON=========")
    tn_gpon = login_gpon
    tn_epon = login_epon
    with allure.step('步骤1:关闭GPON OLT上相应PON口的TX。'):
        assert shutdown_gpon(tn_gpon, Gpon_PonID)
    with allure.step('步骤2:开启EPON OLT上相应PON口的TX。'):
        assert no_shutdown_epon(tn_epon,Epon_PonID)
        time.sleep(60)
    with allure.step('步骤3:发现未注册的ONU。'):
        assert autofind_onu(tn_epon,Epon_PonID,Epon_OnuID,Epon_ONU_MAC)



if __name__ == '__main__':
    # case_1()
    pytest.main(["-s","test_switch_to_epon.py"])





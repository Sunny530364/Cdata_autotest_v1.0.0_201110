import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.MA5800_E.olt_opera import *
from src.MA5800_G.olt_opera import *
from src.MA5800_G.ont_auth import *
# from src.MA5800_G.limitrate import *
from src.config.initialization_config import *

import allure


@allure.feature("切换OLT")
@allure.story("切换OLT为EPON")
@allure.title("切换成EPON的OLT")
@pytest.mark.run(order=5800)
def test_switch_to_gpon(login_gpon,login_epon):

    cdata_info("=========将OLT切换成GPON=========")
    tn_gpon = login_gpon
    # tn_epon = login_epon
    # with allure.step('步骤1:关闭GPON OLT上相应PON口的TX。'):
    #     assert shutdown_epon(tn_epon, Epon_PonID)
    # with allure.step('步骤2:开启EPON OLT上相应PON口的TX。'):
    #     assert no_shutdown_gpon(tn_gpon,Gpon_PonID)
    with allure.step('步骤3:创建epon的线路模板和服务模板'):
        assert create_gpon_ontlineprofile(tn_gpon ,Ont_Lineprofile_ID, Dba_Profile_ID)
    with allure.step('步骤4:创建epon的线路模板和服务模板'):
        assert create_gpon_ontsrvprofile(tn_gpon, Ont_Srvprofile_ID)

    with allure.step('步骤5:发现未注册的ONU。'):
        time.sleep(50)
        assert autofind_onu(tn_gpon,Gpon_PonID,Gpon_OnuID,Gpon_SN)



if __name__ == '__main__':
    # case_1()
    pytest.main(["-s","test_switch_to_gpon.py"])





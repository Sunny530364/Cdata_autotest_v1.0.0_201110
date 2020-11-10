#!/usr/bin/python
# -*- coding UTF-8 -*-


import sys
import time
import pytest
from os.path import dirname, abspath

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)
from src.FD1616GS.internet_type import *
# from page.telnet_client import *
from src.FD1616GS.olt_opera import *
from tests.FD1616GS.initialization_config import *
# from src.Gpon.renix_test import *
import allure



@allure.feature("olt初始化配置")
@allure.story("olt初始化配置")
@allure.title("olt初始化配置")
@pytest.mark.run(order=1600)
def test_load_oltconfig(login2):

    cdata_info("=========olt初始化配置=========")
    tn = login2
    with allure.step('步骤1:olt初始化配置，重启设备'):
        assert load_config(tn,tftp_server_ip,olt_config_file='FD1616GS_init_config.txt ')
    time.sleep(10)





# dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# print(dir)
# dir_data = (os.path.join(dir,'data'))
if __name__ == '__main__':
    pytest.main(['-s','test_olt_loadconfig.py'])

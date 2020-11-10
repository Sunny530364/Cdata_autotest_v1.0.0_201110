#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.FD1616GS.vlan_func import *
from src.FD1616GS.ont_auth import *
from tests.FD1616GS.initialization_config import *
import pytest
import allure
from src.scenes.ont_port_vlan_scene import *


current_dir_name = 'FD1616GS'

@pytest.fixture(scope='function')
def vlan_trunk_suit(login):
    tn=login
    yield tn
    with allure.step("步骤6:onu端口vlan恢复为transparent"):
        Vlan_list = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]
        assert ont_port_vlan_del_profile(tn,Ont_Srvprofile_ID,Ont_Port_ID,Vlan_list)

@pytest.fixture(scope='function')
def vlan_translate_suit(login):
    tn=login
    yield tn
    with allure.step("步骤6:onu端口vlan恢复为transparent"):
        Vlan_list = [100,101,102,103,104,105,106,107]
        assert ont_port_vlan_del_profile(tn,Ont_Srvprofile_ID,Ont_Port_ID,Vlan_list)

# class TestVlan():

@allure.feature("onu端口vlan测试")
@allure.story("onu端口vlan测试")
@allure.title("测试onu端口vlan为transparent")
@pytest.mark.run(order=1617)
def test_onu_transparent(login):
    '''
    用例描述
    测试目的： 测试onu端口为transparent，测试上下行流vlan2000-2001是否正常
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3: 配置onu端口vlan为transparent
    步骤4: 添加虚端口vlan透传2000,2001
    步骤5：打流测试
    1）上下行发vlan2000和2001的流两条
    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.1.11 ipv4_1.destination=192.168.1.21',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.1.12 ipv4_1.destination=192.168.1.22',)
    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.1.21 ipv4_1.destination=192.168.1.11',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.1.22 ipv4_1.destination=192.168.1.12',)
    预期结果: 上下行vlan2000-2001的流量正常通,下行流带tag 2000,2001
    步骤6：删除onu
    '''

    cdata_info("=========测试ONU端口vlan为transaprent=========")

    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:配置onu端口vlan为transparent"):
        assert ont_port_transparent_profile(tn, Ont_Srvprofile_ID)
    with allure.step("步骤4:添加虚端口vlan透传2000,2001"):
        Vlan_list = [2000, 2001]
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step("步骤5:打流测试"):
        assert streamstest_ont_port_vlan_transparent_G(port_location=port_location, packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name)


@allure.feature("onu端口vlan测试")
@allure.story("onu端口vlan测试")
@allure.title("测试onu端口vlan为trunk")
@pytest.mark.run(order=1618)
def test_onu_trunk(vlan_trunk_suit):
    '''
    用例描述
    测试目的： 测试onu端口为trunk，测试上下行流vlan2000-2007是否正常
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3：配置onu端口vlan为trunk 2000-2006
    步骤4：添加虚端口vlan透传2000,2001,2002,2003,2004,2005,2006,2007
    步骤5：打流测试
    1）上下行发vlan2000-2007的流8条
     down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.0.12 ipv4_1.destination=192.168.0.22',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:13 vlan_1.id=2002  ethernetII_1.destMacAdd=00:00:00:22:22:23 ipv4_1.source=192.168.0.13 ipv4_1.destination=192.168.0.23',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:14 vlan_1.id=2003  ethernetII_1.destMacAdd=00:00:00:22:22:24 ipv4_1.source=192.168.0.14 ipv4_1.destination=192.168.0.24',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:15 vlan_1.id=2004  ethernetII_1.destMacAdd=00:00:00:22:22:25 ipv4_1.source=192.168.0.15 ipv4_1.destination=192.168.0.25',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:16 vlan_1.id=2005  ethernetII_1.destMacAdd=00:00:00:22:22:26 ipv4_1.source=192.168.0.16 ipv4_1.destination=192.168.0.26',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:17 vlan_1.id=2006  ethernetII_1.destMacAdd=00:00:00:22:22:27 ipv4_1.source=192.168.0.17 ipv4_1.destination=192.168.0.27',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:18 vlan_1.id=2007  ethernetII_1.destMacAdd=00:00:00:22:22:28 ipv4_1.source=192.168.0.18 ipv4_1.destination=192.168.0.28',
            )
        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.0.22 ipv4_1.destination=192.168.0.12',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:23 vlan_1.id=2002  ethernetII_1.destMacAdd=00:00:00:11:11:13 ipv4_1.source=192.168.0.23 ipv4_1.destination=192.168.0.13',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:24 vlan_1.id=2003  ethernetII_1.destMacAdd=00:00:00:11:11:14 ipv4_1.source=192.168.0.24 ipv4_1.destination=192.168.0.14',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:25 vlan_1.id=2004  ethernetII_1.destMacAdd=00:00:00:11:11:15 ipv4_1.source=192.168.0.25 ipv4_1.destination=192.168.0.15',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:26 vlan_1.id=2005  ethernetII_1.destMacAdd=00:00:00:11:11:16 ipv4_1.source=192.168.0.26 ipv4_1.destination=192.168.0.16',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:27 vlan_1.id=2006  ethernetII_1.destMacAdd=00:00:00:11:11:17 ipv4_1.source=192.168.0.27 ipv4_1.destination=192.168.0.17',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:28 vlan_1.id=2007  ethernetII_1.destMacAdd=00:00:00:11:11:18 ipv4_1.source=192.168.0.28 ipv4_1.destination=192.168.0.18',
            )
    预期结果: 上下行vlan2000-2007的流量正常通,2008流上下行不通
    步骤6：模板onu端口vlan恢复为transparent
    步骤7：删除onu
    '''

    cdata_info("=========测试ONU端口vlan为trunk=========")
    tn = vlan_trunk_suit
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:配置onu端口vlan为trunk 2000-2007"):
        Vlan_list=[2000, 2001, 2002, 2003, 2004, 2005, 2006]
        assert ont_port_trunk_profile(tn, Ont_Srvprofile_ID,Ont_Port_ID,Vlan_list)
    with allure.step("步骤4:添加虚端口vlan透传2000,2001,2002,2003,2004,2005,2006,2007"):
        Vlan_list = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step("步骤5:打流测试"):
        assert streamstest_ont_port_vlan_trunk(port_location=port_location, packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name)


@allure.feature("onu端口vlan测试")
@allure.story("onu端口vlan测试")
@allure.title("测试onu端口vlan为translate")
@pytest.mark.run(order=1619)
def test_onu_translate(vlan_translate_suit):
    '''
    用例描述
    测试目的： 测试onu端口为translate，translate100-107 转2000-2007,测试上下行流量是否正常
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3：配置onu端口translate(100-107)转成（2000-2007）
    步骤4：添加虚端口vlan 透传2000,2001,2002, 2003, 2004, 2005, 2006, 2007
    步骤5：打流测试
    1）下行发vlan2000-2008的流，上行发vlan100-108的流
    down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.0.12 ipv4_1.destination=192.168.0.22',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:13 vlan_1.id=2002  ethernetII_1.destMacAdd=00:00:00:22:22:23 ipv4_1.source=192.168.0.13 ipv4_1.destination=192.168.0.23',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:14 vlan_1.id=2003  ethernetII_1.destMacAdd=00:00:00:22:22:24 ipv4_1.source=192.168.0.14 ipv4_1.destination=192.168.0.24',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:15 vlan_1.id=2004  ethernetII_1.destMacAdd=00:00:00:22:22:25 ipv4_1.source=192.168.0.15 ipv4_1.destination=192.168.0.25',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:16 vlan_1.id=2005  ethernetII_1.destMacAdd=00:00:00:22:22:26 ipv4_1.source=192.168.0.16 ipv4_1.destination=192.168.0.26',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:17 vlan_1.id=2006  ethernetII_1.destMacAdd=00:00:00:22:22:27 ipv4_1.source=192.168.0.17 ipv4_1.destination=192.168.0.27',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:18 vlan_1.id=2007  ethernetII_1.destMacAdd=00:00:00:22:22:28 ipv4_1.source=192.168.0.18 ipv4_1.destination=192.168.0.28',
            )

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=100  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=101  ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.0.22 ipv4_1.destination=192.168.0.12',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:23 vlan_1.id=102  ethernetII_1.destMacAdd=00:00:00:11:11:13 ipv4_1.source=192.168.0.23 ipv4_1.destination=192.168.0.13',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:24 vlan_1.id=103  ethernetII_1.destMacAdd=00:00:00:11:11:14 ipv4_1.source=192.168.0.24 ipv4_1.destination=192.168.0.14',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:25 vlan_1.id=104  ethernetII_1.destMacAdd=00:00:00:11:11:15 ipv4_1.source=192.168.0.25 ipv4_1.destination=192.168.0.15',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:26 vlan_1.id=105  ethernetII_1.destMacAdd=00:00:00:11:11:16 ipv4_1.source=192.168.0.26 ipv4_1.destination=192.168.0.16',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:27 vlan_1.id=106  ethernetII_1.destMacAdd=00:00:00:11:11:17 ipv4_1.source=192.168.0.27 ipv4_1.destination=192.168.0.17',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:28 vlan_1.id=107  ethernetII_1.destMacAdd=00:00:00:11:11:18 ipv4_1.source=192.168.0.28 ipv4_1.destination=192.168.0.18',
        )
    预期结果: 下行vlan2000-2006的通，下行vlan2007的不通；上行vlan100-106的通，上行vlan107的不通
    步骤6：onu端口vlan恢复为transparent
    步骤7：删除onu
    '''

    cdata_info("=========测试ONU端口vlan为translate=========")

    tn = vlan_translate_suit
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:配置onu端口translate(100-800)转成（2000-2007）"):
        S_Vlan_list = [2000, 2001, 2002, 2003, 2004, 2005, 2006]
        C_Vlan_list = [100,101,102,103,104,105,106]
        assert ont_port_translate_profile(tn,Ont_Srvprofile_ID,Ont_Port_ID,S_Vlan_list,C_Vlan_list)
    with allure.step("步骤4:添加虚端口vlan透传2000,2001,2002, 2003, 2004, 2005, 2006, 2007"):
        Vlan_list = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step('步骤5:打流测试'):
        assert streamstest_ont_port_vlan_translate(port_location=port_location, packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name)



if __name__ == '__main__':
    pytest.main(['-v','-s','test_onu_vlan.py::test_onu_transparent'])




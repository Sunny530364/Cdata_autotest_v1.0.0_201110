#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.MA5800_G.vlan_func import *
from src.MA5800_G.gemport import *
from src.xinertel.unicast66 import *
from src.config.initialization_config import *
from src.MA5800_G.ont_auth import *
import pytest
import allure

from src.scenes.ont_port_vlan_scene import *

current_dir_name = 'MA5800_G'

@pytest.fixture(scope='function')
def vlan_trunk_suit(login):
    tn=login
    yield tn
    with allure.step("步骤6:onu端口vlan恢复为transparent"):
        assert ont_port_trunk_del(tn,Ont_Srvprofile_ID)

@pytest.fixture(scope='function')
def vlan_translate_suit(login):
    tn=login
    yield tn
    with allure.step("步骤6:onu端口vlan恢复为transparent"):
        assert ont_port_translate_del(tn, Ont_Srvprofile_ID)

# class TestVlan():

@allure.feature("onu端口vlan测试")
@allure.story("onu端口vlan测试")
@allure.title("测试onu端口vlan为transparent")
@pytest.mark.run(order=5815)
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
    Vlan_list = [2000, 2001]
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:配置onu端口vlan为transparent"):
        assert ont_port_transparent(tn,Gpon_PonID, Gpon_OnuID,Ont_Port_ID)
    with allure.step('步骤4:配置gemport为vlan2000,2001 '):
        assert gemport_vlan(tn, Ont_Lineprofile_ID,Vlan_list,Gemport_ID)

    with allure.step("步骤4:添加虚端口vlan透传2000,2001"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step("步骤5:打流测试"):
        assert streamstest_ont_port_vlan_transparent_G(port_location=port_location,
                                                       packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name)

    # with  allure.step("步骤5:打流测试"):
    #     # 清除测试仪的对象，防止影响下个用例的执行
    #     time.sleep(5)
    #     reset_rom_cmd = ResetROMCommand()
    #     reset_rom_cmd.execute()
    #
    #     # 发流量测试，onu的Eth1发送两条流2000，和vlan2001
    #     # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
    #     duration = 10
    #     down_stream_header = (
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.0.12 ipv4_1.destination=192.168.0.22',
    #     )
    #
    #     up_stream_header = (
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.0.22 ipv4_1.destination=192.168.0.12',
    #     )
    #     result = unicast_test(port_location=port_location, down_stream_header=down_stream_header,
    #                                 up_stream_header=up_stream_header,
    #                                 packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
    #                                 num=2, dataclassname=StreamBlockStats,
    #                                 duration=duration)
    #
    #     result_stats = result[0]
    #     # 判断如果文件存在，就开始分析报文
    #     tag_result = 'PASS'
    #     packet_filenames = result[1]
    #
    #     # # 判断vlan2000的上下行流量是否都是通的，如果是返回PASS，否则返回FAIL
    #     # result1 = check_stream_static(result_stats[0], result_stats[2])
    #     # # 判断vlan2001的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
    #     # result2 = check_stream_static(result_stats[1], result_stats[3])
    #
    #     for i in range(4):
    #         if (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:11':
    #             result11 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:12':
    #             result12 = check_stream_static1(result_stats[i])
    #
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:21':
    #             result21 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:22':
    #             result22 = check_stream_static1(result_stats[i])
    #
    #     # 正确的结果vlan2000的能通，vlan2001的不通
    #     if result11 == 'PASS' and result12 == 'PASS' and result21 == 'PASS' and result22 == 'PASS':
    #         result = 'PASS'
    #         cdata_info("ONU端口为transparent:打流测试正常")
    #     else:
    #         result = 'FAIL'
    #         cdata_error("ONU端口为transparent:打流测试失败")
    #     assert result == 'PASS'

@allure.feature("onu端口vlan测试")
@allure.story("onu端口vlan测试")
@allure.title("测试onu端口vlan为trunk")
@pytest.mark.run(order=5816)
def test_onu_trunk(login):
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
    步骤6：删除onu
    '''

    # tn=login
    #配置onu端口为trunk模式
    # ont_port_trunk(tn)
    cdata_info("=========测试ONU端口vlan为trunk=========")
    Vlan_list = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:配置onu端口vlan为trunk 2000-2006"):
        assert ont_port_trunk(tn,Gpon_PonID, Gpon_OnuID,Ont_Port_ID,Vlan_list=[2000, 2001, 2002, 2003, 2004, 2005, 2006])
    with allure.step('步骤4:配置gemport为vlan2000-2007 '):
        assert gemport_vlan(tn, Ont_Lineprofile_ID, Vlan_list, Gemport_ID)
    with allure.step("步骤4:添加虚端口vlan透传2000,2001,2002,2003,2004,2005,2006,2007"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step("步骤5:打流测试"):
        assert streamstest_ont_port_vlan_trunk(port_location=port_location,
                                               packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name)

    # with allure.step("步骤5:打流测试"):
    #     # 清除测试仪的对象，防止影响下个用例的执行
    #     time.sleep(5)
    #     reset_rom_cmd = ResetROMCommand()
    #     reset_rom_cmd.execute()
    #
    #     # 发流量测试，发送两条流2000，和vlan2001,和vlan2002
    #     # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
    #     duration = 10
    #     down_stream_header = (
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.0.12 ipv4_1.destination=192.168.0.22',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:13 vlan_1.id=2002  ethernetII_1.destMacAdd=00:00:00:22:22:23 ipv4_1.source=192.168.0.13 ipv4_1.destination=192.168.0.23',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:14 vlan_1.id=2003  ethernetII_1.destMacAdd=00:00:00:22:22:24 ipv4_1.source=192.168.0.14 ipv4_1.destination=192.168.0.24',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:15 vlan_1.id=2004  ethernetII_1.destMacAdd=00:00:00:22:22:25 ipv4_1.source=192.168.0.15 ipv4_1.destination=192.168.0.25',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:16 vlan_1.id=2005  ethernetII_1.destMacAdd=00:00:00:22:22:26 ipv4_1.source=192.168.0.16 ipv4_1.destination=192.168.0.26',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:17 vlan_1.id=2006  ethernetII_1.destMacAdd=00:00:00:22:22:27 ipv4_1.source=192.168.0.17 ipv4_1.destination=192.168.0.27',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:18 vlan_1.id=2007  ethernetII_1.destMacAdd=00:00:00:22:22:28 ipv4_1.source=192.168.0.18 ipv4_1.destination=192.168.0.28',
    #         # 'ethernetII_1.sourceMacAdd=00:00:00:11:11:19 vlan_1.id=2008  ethernetII_1.destMacAdd=00:00:00:22:22:29 ipv4_1.source=192.168.0.19 ipv4_1.destination=192.168.0.29'
    #     )
    #
    #     up_stream_header = (
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.0.22 ipv4_1.destination=192.168.0.12',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:23 vlan_1.id=2002  ethernetII_1.destMacAdd=00:00:00:11:11:13 ipv4_1.source=192.168.0.23 ipv4_1.destination=192.168.0.13',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:24 vlan_1.id=2003  ethernetII_1.destMacAdd=00:00:00:11:11:14 ipv4_1.source=192.168.0.24 ipv4_1.destination=192.168.0.14',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:25 vlan_1.id=2004  ethernetII_1.destMacAdd=00:00:00:11:11:15 ipv4_1.source=192.168.0.25 ipv4_1.destination=192.168.0.15',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:26 vlan_1.id=2005  ethernetII_1.destMacAdd=00:00:00:11:11:16 ipv4_1.source=192.168.0.26 ipv4_1.destination=192.168.0.16',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:27 vlan_1.id=2006  ethernetII_1.destMacAdd=00:00:00:11:11:17 ipv4_1.source=192.168.0.27 ipv4_1.destination=192.168.0.17',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:28 vlan_1.id=2007  ethernetII_1.destMacAdd=00:00:00:11:11:18 ipv4_1.source=192.168.0.28 ipv4_1.destination=192.168.0.18',
    #         # 'ethernetII_1.sourceMacAdd=00:00:00:22:22:29 vlan_1.id=2008  ethernetII_1.destMacAdd=00:00:00:11:11:19 ipv4_1.source=192.168.0.29 ipv4_1.destination=192.168.0.19'
    #     )
    #     result = unicast_test(port_location=port_location, down_stream_header=down_stream_header,
    #                                 up_stream_header=up_stream_header,
    #                                 packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
    #                                 num=8, dataclassname=StreamBlockStats,
    #                                 duration=duration)
    #
    #     result_stats = result[0]
    #     # 判断如果文件存在，就开始分析报文
    #     tag_result = 'PASS'
    #     packet_filenames = result[1]
    #
    #     for i in range(8*2):
    #         if (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:11':
    #             result11=check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:12':
    #             result12 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:13':
    #             result13 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:14':
    #             result14 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:15':
    #             result15 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:16':
    #             result16 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:17':
    #             result17 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:18':
    #             result18 = check_stream_loss1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:21':
    #             result21= check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:22':
    #             result22 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:23':
    #             result23 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:24':
    #             result24 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:25':
    #             result25 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:26':
    #             result26 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:27':
    #             result27 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:28':
    #             result28 = check_stream_loss1(result_stats[i])
    #         # elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:19':
    #         #     result19 = check_stream_loss1(result_stats[i])
    #         # elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:29':
    #         #     result29 = check_stream_loss1(result_stats[i])
    #
    #
    #     #恢复默认配置
    #     # ont_port_trunk_del(tn)
    #
    #     # 正确的结果vlan2000和vlan2001的能通，vlan2002的不通
    #     if result11 == 'PASS' and result12 == 'PASS' and result13=='PASS' and result14 == 'PASS' \
    #             and result15 == 'PASS'  and result16 == 'PASS'     and result17 == 'PASS' and result18 == 'PASS'     \
    #      and result21 == 'PASS' and result22 == 'PASS' and result23 == 'PASS' and result24 == 'PASS'\
    #             and result25 == 'PASS' and result26 == 'PASS' and result27 == 'PASS' \
    #             and result28 == 'PASS'  :
    #         result = 'PASS'
    #         cdata_info("ONU端口为trunk:打流测试正常")
    #     else:
    #         result = 'FAIL'
    #         cdata_error("ONU端口为trunk:打流测试失败")
    #     assert result == 'PASS'


@allure.feature("onu端口vlan测试")
@allure.story("onu端口vlan测试")
@allure.title("测试onu端口vlan为translate")
@pytest.mark.run(order=5817)
def test_onu_translate(login):
    '''
    用例描述
    测试目的： 测试onu端口为translate，translate100-107 转2000-2007,测试上下行流量是否正常
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3：配置onu端口translate(100-108)转成（2000-2007）
    步骤4：添加虚端口vlan透传2000,2001,2002, 2003, 2004, 2005, 2006, 2007, 2008
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
    步骤6：删除onu
    '''

    cdata_info("=========测试ONU端口vlan为translate=========")
    Vlan_list = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:配置onu端口translate(100-106)转成（2000-2006）"):
        assert ont_port_translate(tn,Gpon_PonID, Gpon_OnuID,Ont_Port_ID,S_Vlan_list=[2000, 2001, 2002, 2003, 2004, 2005, 2006],
                                  C_Vlan_list=[100,101,102,103,104,105,106])
    with allure.step('步骤4:配置gemport为vlan2000-2007 '):
        assert gemport_vlan(tn, Ont_Lineprofile_ID, Vlan_list, Gemport_ID)
    with allure.step("步骤4:添加虚端口vlan透传2000,2001,2002, 2003, 2004, 2005, 2006"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step('步骤5:打流测试'):
        assert streamstest_ont_port_vlan_translate(port_location=port_location,packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name)

    # with  allure.step("步骤5:打流测试"):
    #     # 清除测试仪的对象，防止影响下个用例的执行
    #     time.sleep(5)
    #     reset_rom_cmd = ResetROMCommand()
    #     reset_rom_cmd.execute()
    #
    #     #'//192.168.0.180/1/9'连接上联口，'//192.168.0.180/1/10'连接onu端口
    #     # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
    #     #跑流的时长为10s
    #     duration = 10
    #     # 发流量测试，发送三条流vlan100，和vlan200,和vlan300
    #     down_stream_header = (
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.0.12 ipv4_1.destination=192.168.0.22',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:13 vlan_1.id=2002  ethernetII_1.destMacAdd=00:00:00:22:22:23 ipv4_1.source=192.168.0.13 ipv4_1.destination=192.168.0.23',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:14 vlan_1.id=2003  ethernetII_1.destMacAdd=00:00:00:22:22:24 ipv4_1.source=192.168.0.14 ipv4_1.destination=192.168.0.24',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:15 vlan_1.id=2004  ethernetII_1.destMacAdd=00:00:00:22:22:25 ipv4_1.source=192.168.0.15 ipv4_1.destination=192.168.0.25',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:16 vlan_1.id=2005  ethernetII_1.destMacAdd=00:00:00:22:22:26 ipv4_1.source=192.168.0.16 ipv4_1.destination=192.168.0.26',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:17 vlan_1.id=2006  ethernetII_1.destMacAdd=00:00:00:22:22:27 ipv4_1.source=192.168.0.17 ipv4_1.destination=192.168.0.27',
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:11:18 vlan_1.id=2007  ethernetII_1.destMacAdd=00:00:00:22:22:28 ipv4_1.source=192.168.0.18 ipv4_1.destination=192.168.0.28',
    #         # 'ethernetII_1.sourceMacAdd=00:00:00:11:11:19 vlan_1.id=2008  ethernetII_1.destMacAdd=00:00:00:22:22:29 ipv4_1.source=192.168.0.19 ipv4_1.destination=192.168.0.29'
    #     )
    #
    #     up_stream_header = (
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=100  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=101  ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.0.22 ipv4_1.destination=192.168.0.12',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:23 vlan_1.id=102  ethernetII_1.destMacAdd=00:00:00:11:11:13 ipv4_1.source=192.168.0.23 ipv4_1.destination=192.168.0.13',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:24 vlan_1.id=103  ethernetII_1.destMacAdd=00:00:00:11:11:14 ipv4_1.source=192.168.0.24 ipv4_1.destination=192.168.0.14',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:25 vlan_1.id=104  ethernetII_1.destMacAdd=00:00:00:11:11:15 ipv4_1.source=192.168.0.25 ipv4_1.destination=192.168.0.15',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:26 vlan_1.id=105  ethernetII_1.destMacAdd=00:00:00:11:11:16 ipv4_1.source=192.168.0.26 ipv4_1.destination=192.168.0.16',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:27 vlan_1.id=106  ethernetII_1.destMacAdd=00:00:00:11:11:17 ipv4_1.source=192.168.0.27 ipv4_1.destination=192.168.0.17',
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:22:28 vlan_1.id=107  ethernetII_1.destMacAdd=00:00:00:11:11:18 ipv4_1.source=192.168.0.28 ipv4_1.destination=192.168.0.18',
    #         # 'ethernetII_1.sourceMacAdd=00:00:00:22:22:29 vlan_1.id=108  ethernetII_1.destMacAdd=00:00:00:11:11:19 ipv4_1.source=192.168.0.29 ipv4_1.destination=192.168.0.19'
    #     )
    #     result = unicast_test(port_location=port_location, down_stream_header=down_stream_header,
    #                                 up_stream_header=up_stream_header,
    #                                 packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
    #                                 num=8, dataclassname=StreamBlockStats,
    #                                 duration=duration)
    #
    #     result_stats = result[0]
    #     # 判断如果文件存在，就开始分析报文
    #     tag_result = 'PASS'
    #     packet_filenames = result[1]
    #
    #     for i in range(8*2):
    #         if (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:11':
    #             result11 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:12':
    #             result12 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:13':
    #             result13 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:14':
    #             result14 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:15':
    #             result15 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:16':
    #             result16 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:17':
    #             result17 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:18':
    #             result18 = check_stream_loss1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:21':
    #             result21 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:22':
    #             result22 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:23':
    #             result23 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:24':
    #             result24 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:25':
    #             result25 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:26':
    #             result26 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:27':
    #             result27 = check_stream_static1(result_stats[i])
    #         elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:28':
    #             result28 = check_stream_loss1(result_stats[i])
    #         # elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:19':
    #         #     result19 = check_stream_loss1(result_stats[i])
    #         # elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:29':
    #         #     result29 = check_stream_loss1(result_stats[i])
    #
    #     # 恢复默认配置
    #     # ont_port_trunk_del(tn)
    #
    #     # 正确的结果vlan2000和vlan2001的能通，vlan2002的不通
    #     if result11 == 'PASS' and result12 == 'PASS' and result13 == 'PASS' and result14 == 'PASS' \
    #             and result15 == 'PASS' and result16 == 'PASS' and result17 == 'PASS' and result18 == 'PASS' \
    #             and result21 == 'PASS' and result22 == 'PASS' and result23 == 'PASS' and result24 == 'PASS' \
    #             and result25 == 'PASS' and result26 == 'PASS' and result27 == 'PASS'  and result28 == 'PASS':
    #         result = 'PASS'
    #         cdata_info("ONU端口为translate:打流测试正常")
    #     else:
    #         result = 'FAIL'
    #         cdata_error("ONU端口为translate:打流测试失败")
    #     assert result == 'PASS'


if __name__ == '__main__':
    pytest.main(['-v','-s','-x','test_onu_vlan.py'])



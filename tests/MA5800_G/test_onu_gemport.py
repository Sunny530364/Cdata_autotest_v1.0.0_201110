#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI
from src.MA5800_G.gemport import *
from src.MA5800_G.vlan_func import *
from src.xinertel.unicast66 import *
from src.MA5800_G.ont_auth import *
from src.config.initialization_config import *
import pytest
import allure

current_dir_name = 'MA5800_G'

@allure.feature("gemport测试")
@allure.story("gemport测试")
@allure.title("测试mapping-mode为vlan")
@pytest.mark.run(order=5811)
def test_gemport_vlan(login):
    '''
    用例描述
    测试目的： 测试mapping-mode is vlan , mapping 为vlan2000时，vlan2000的报文上下行是否都正常,vlan2001上下行报文是否不通
    测试步骤：
    步骤1:发现未注册的ONU
    步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3:修改gemport配置为vlan 2000
    步骤4:配置虚端口vlan2000透传，vlan2001透传
    步骤5:打流测试
    测试方法：上下行发流量测试，发送两条流vlan 2000，和vlan2001
    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:22:22:21',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001 ethernetII_1.destMacAdd=00:00:00:22:22:22')
    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:11',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2001 ethernetII_1.destMacAdd=00:00:00:11:11:12',)
    预期结果：vlan2000的能通，vlan2001的不通

    '''

    cdata_info("=========mapping_mode为vlan测试=========")
    Vlan_list = [2000, 2001]
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3：配置onu端口为transparent'):
        assert  ont_port_transparent(tn,Gpon_PonID, Gpon_OnuID,Ont_Port_ID)
    with allure.step("步骤4:修改gemport配置为vlan"):
        assert gemport_vlan(tn, Ont_Lineprofile_ID,[2000],Gemport_ID)
    with allure.step("步骤5:配置虚端口vlan2000透传，vlan2001透传"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)

    with allure.step("步骤6:打流测试"):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(5)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        #发流量测试，发送两条流vlan 2000，和vlan2001
        # 配置参数：
        # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
        duration = 10
        down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001 ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.0.12 ipv4_1.destination=192.168.0.22')

        up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2001 ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.0.22 ipv4_1.destination=192.168.0.12',
        )
        #获取所有流量的统计值
        result = unicast_test(port_location=port_location, down_stream_header=down_stream_header,
                                    up_stream_header=up_stream_header,
                                    packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                    num=2,dataclassname=StreamBlockStats, duration=duration)

        result_stats = result[0]
        # 判断如果文件存在，就开始分析报文
        tag_result = 'PASS'
        packet_filenames = result[1]

        # #判断vlan2000的上下行流量是否都是通的，如果是返回PASS，否则返回FAIL
        # # 判断vlan2001的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
        for i in range(4):
            if (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:11':
                result11 = check_stream_static1(result_stats[i])
            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:12':
                result12 = check_stream_loss1(result_stats[i])

            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:21':
                result21 = check_stream_static1(result_stats[i])
            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:22':
                result22 = check_stream_loss1(result_stats[i])

        # #恢复默认配置
        # gemport_transparent(tn)

        #正确的结果vlan2000的能通，vlan2001的不通
        if result11=='PASS' and result12=='PASS' and result21=='PASS' and result22=='PASS':
            result='PASS'
            cdata_info("mapping_mode为vlan测试:打流测试正常")
        else:
            result='FAIL'
            cdata_error("mapping_mode为vlan测试:打流测试失败")

        assert result=='PASS'


@allure.feature("gemport测试")
@allure.story("gemport测试")
@allure.title("测试mapping-mode为vlan_pri")
@pytest.mark.run(order=5812)
def test_gemport_vlan_pri(login):
    '''
    用例描述
    测试目的： 测试mapping-mode is vlan+pri, mapping 为vlan2000+pri2时，vlan2000+2和vlan200+3和vlan2001+pri2的报文上下行是否都正常
    测试步骤：
    步骤1:发现未注册的ONU
    步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3:修改gemport配置为vlan 2000+pri2
    步骤4:配置虚端口vlan2000透传，vlan2001透传
    步骤5:打流测试
    测试方法：上下行各发送三条流：vlan2000 pri2和 vlan2000 pri3 ；发送vlan 2001 pri2
    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:22:22:21',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2000 vlan_1.priority=3 ethernetII_1.destMacAdd=00:00:00:22:22:22',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:13 vlan_1.id=2001 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:22:22:23',)
    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:11:11:11',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2000 vlan_1.priority=3 ethernetII_1.destMacAdd=00:00:00:11:11:12',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:23 vlan_1.id=2001 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:11:11:13',)
    预期结果：vlan 2000 pri2的上下行都能通；vlan2000 pri3下行能通，vlan2000 pri3上行不通;vlan 2001上下行都不通
    '''
    # tn=login
    # # 修改配置
    # gemport_vlan_pri(tn)
    cdata_info("=========mapping_mode为vlan_pri测试=========")
    tn = login
    Vlan_list = [2000, 2001]
    #vlan2000+pri2
    Vlan_pri_list=[(2000,2)]
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3：配置onu端口为transparent'):
        assert ont_port_transparent(tn,Gpon_PonID, Gpon_OnuID,Ont_Port_ID='1')
    with allure.step("步骤4:修改gemport配置为vlan 2000 priority 2"):
        assert gemport_vlan_pri(tn,Ont_Lineprofile_ID,Vlan_pri_list,Gemport_ID)
    with allure.step("步骤5:配置虚端口vlan2000和vlan 2001透传"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step("步骤6:打流测试"):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(5)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # 发流量测试，发送两条流vlan 2000+pri2，和vlan2000+pri3
        # 配置参数：
        # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
        duration = 10
        down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2000 vlan_1.priority=3 ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.0.12 ipv4_1.destination=192.168.0.22',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:13 vlan_1.id=2001 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:22:22:23 ipv4_1.source=192.168.0.13 ipv4_1.destination=192.168.0.23',)

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2000 vlan_1.priority=3 ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.0.22 ipv4_1.destination=192.168.0.12',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:23 vlan_1.id=2001 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:11:11:13 ipv4_1.source=192.168.0.23 ipv4_1.destination=192.168.0.13',
        )
        result = unicast_test(port_location=port_location, down_stream_header=down_stream_header,
                                    up_stream_header=up_stream_header,
                                    packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                    num=3, dataclassname=StreamBlockStats,
                                    duration=duration)

        result_stats = result[0]
        # 判断如果文件存在，就开始分析报文
        tag_result = 'PASS'
        packet_filenames = result[1]

        # # 判断vlan2000+pri2的上下行流量是否都是通的，如果是返回PASS，否则返回FAIL
        # # 判断vlan2000+pri3的上行流量不通，下行流量能通，如果是返回PASS，否则返回FAIL

        for i in range(6):
            if (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:11':
                result11=check_stream_static1(result_stats[i])
            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:12':
                result12 = check_stream_static1(result_stats[i])
            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:13':
                result13 = check_stream_loss1(result_stats[i])

            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:21':
                result21 = check_stream_static1(result_stats[i])
            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:22':
                result22 = check_stream_loss1(result_stats[i])
            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:23':
                result23 = check_stream_loss1(result_stats[i])


        # #恢复默认配置
        # gemport_transparent(tn)

        # 正确的结果vlan2000+pri2的能通，vlan2000+pri3的不通
        if result11 == 'PASS' and result12 == 'PASS' and result21=='PASS' and result22=='PASS' and result13=='PASS'\
                and result23=='PASS':
            result = 'PASS'
            cdata_info("mapping_mode为vlan+pri测试:打流测试正常")
        else:
            result = 'FAIL'
            cdata_error("mapping_mode为vlan+pri测试:打流测试失败")

        assert result == 'PASS'


@allure.feature("gemport测试")
@allure.story("gemport测试")
@allure.title("测试mapping-mode为pri")
@pytest.mark.run(order=5813)
def test_gemport_pri(login):
    '''
    用例描述
    测试目的： 测试mapping-mode is pri, mapping 为pri2时，vlan2000+2和vlan2000+3报文上下行是否都正常
    测试步骤：
    步骤1:发现未注册的ONU
    步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3:修改gemport配置为pri2
    步骤4:配置虚端口vlan2000透传
    步骤5:打流测试
    测试方法：上下行各发送两条流：vlan2000 pri2和 vlan2000 pri3
    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:22:22:21',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2000 vlan_1.priority=3 ethernetII_1.destMacAdd=00:00:00:22:22:22')
    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:11:11:11',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2000 vlan_1.priority=3 ethernetII_1.destMacAdd=00:00:00:11:11:12',)
    预期结果：pri2的上下行都能通；pri3下行能通，上行不通

    '''
    # tn=login
    # 修改配置
    # gemport_pri(tn)
    cdata_info("=========mapping_mode为pri测试=========")
    tn = login
    Vlan_list = [2000]
    Pir_list = [2]
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3：配置onu端口为transparent'):
        assert  ont_port_transparent(tn,Gpon_PonID, Gpon_OnuID,Ont_Port_ID='1')
    with allure.step("步骤3:修改gemport配置为pri 2"):
        assert gemport_pri(tn,Ont_Lineprofile_ID,Pir_list,Gemport_ID,mapping_mode='priority')
    with allure.step("步骤4:配置虚端口vlan2000透传"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step("步骤5:打流测试"):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(5)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # 发流量测试，发送两条流2000+pri2，和vlan2000+pri3
        # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
        duration = 10
        down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2000 vlan_1.priority=3 ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.0.12 ipv4_1.destination=192.168.0.22')

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2000 vlan_1.priority=3 ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.0.22 ipv4_1.destination=192.168.0.12',
        )
        # 获取所有流量的统计值
        result = unicast_test(port_location=port_location, down_stream_header=down_stream_header,
                                    up_stream_header=up_stream_header,
                                    packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                    num=2, dataclassname=StreamBlockStats,
                                    duration=duration)

        result_stats = result[0]
        # 判断如果文件存在，就开始分析报文
        tag_result = 'PASS'
        packet_filenames = result[1]

        for i in range(4):
            if (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:11':
                result11=check_stream_static1(result_stats[i])
            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:12':
                result12 = check_stream_static1(result_stats[i])

            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:21':
                result21= check_stream_static1(result_stats[i])
            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:22':
                result22 = check_stream_loss1(result_stats[i])

        #恢复默认配置
        # gemport_transparent(tn)

        # 正确的结果pri2的能通，pri3的不通
        if result11 == 'PASS' and result12 == 'PASS' and result21=='PASS' and result22=='PASS':
            result = 'PASS'
            cdata_info("mapping_mode为pir测试:打流测试成功")
        else:
            result = 'FAIL'
            cdata_error("mapping_mode为pir测试:打流测试失败")

        assert result == 'PASS'


@allure.feature("gemport测试")
@allure.story("gemport测试")
@allure.title("测试mapping-mode为port")
@pytest.mark.run(order=5814)
def test_gemport_port(login):
    '''
    用例描述
    测试目的： 测试mapping-mode is port, mapping 为port2时，往onu的port1 上下行发送vlan 2000的报文是否都正常
    测试步骤：
    步骤1:发现未注册的ONU
    步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3:修改gemport配置为port 2
    步骤4:配置虚端口vlan2000透传
    步骤5:打流测试
    测试方法：上下行各发送1条流：vlan2000
    down_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21',)
    up_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11',)
    结果：上下行都不通
    步骤6：修改gemport配置为port1
    步骤7:打流测试
    测试方法：上下行各发送1条流：vlan2000
    结果：上下行都能通

    '''

    # tn=login
    # 修改配置
    # gemport_port(tn)
    cdata_info("=========mapping_mode为port测试=========")
    tn = login
    Vlan_list = [2000]

    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤3：配置onu端口为transparent'):
        assert ont_port_transparent(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID='1')
    with allure.step("步骤3:修改gemport配置为port 2"):
        Port_list = [2]
        assert gemport_port(tn,Ont_Lineprofile_ID,Port_list,Gemport_ID,mapping_mode='port')
    with allure.step("步骤4:配置虚端口vlan2000透传"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)

    with allure.step("步骤5:打流测试"):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(5)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # 发流量测试，onu的Eth1发送vlan2000的报文
        # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
        duration = 10
        down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21',)
        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11', )
        result = unicast_test(port_location=port_location, down_stream_header=down_stream_header,
                                    up_stream_header=up_stream_header,
                                    packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                    num=1, dataclassname=StreamBlockStats,
                                    duration=duration)

        result_stats = result[0]
        # 判断如果文件存在，就开始分析报文
        tag_result = 'PASS'
        packet_filenames = result[1]

        # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
        # result1 = check_stream_loss(result_stats[0], result_stats[1])

        for i in range(2):
            if (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:11':
                result11=check_stream_loss1(result_stats[i])
            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:21':
                result21= check_stream_loss1(result_stats[i])

        # # 恢复默认配置
        # gemport_transparent(tn)

        # 正确的结果por1的不通
        if result11 == 'PASS' and result21=='PASS':
            result = 'PASS'
            cdata_info("mapping_mode为port测试（正常不通）:打流测试正常")
        else:
            result = 'FAIL'
            cdata_error("mapping_mode为port测试（正常不通）:打流测试失败")

        assert result == 'PASS'

    with allure.step("步骤6:修改gemport配置为port 1"):
        Port_list = [1]
        assert gemport_port(tn,Ont_Lineprofile_ID,Port_list,Gemport_ID,mapping_mode='port')

    with allure.step("步骤7:打流测试"):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(10)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # 发流量测试，onu的Eth1发送vlan2000的报文
        # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
        duration = 10
        down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',)
        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 vlan_1.priority=2 ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11', )
        result = unicast_test(port_location=port_location, down_stream_header=down_stream_header,
                                    up_stream_header=up_stream_header,
                                    packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                    num=1, dataclassname=StreamBlockStats,
                                    duration=duration)

        result_stats = result[0]
        # 判断如果文件存在，就开始分析报文
        tag_result = 'PASS'
        packet_filenames = result[1]

        # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
        # result1 = check_stream_loss(result_stats[0], result_stats[1])

        for i in range(2):
            if (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:11:11:11':
                result11=check_stream_static1(result_stats[i])
            elif (result_stats[i].__dict__)['_StreamBlockID']=='sourceMacAdd=00:00:00:22:22:21':
                result21 = check_stream_static1(result_stats[i])

        # # 恢复默认配置
        # gemport_transparent(tn)

        # 正确的结果por1的不通
        if result11 == 'PASS' and result21=='PASS':
            result = 'PASS'
            cdata_info("mapping_mode为port测试（正常通）:打流测试正常")
        else:
            result = 'FAIL'
            cdata_error("mapping_mode为port测试（正常通）:打流测试失败")

        assert result == 'PASS'



if __name__ == '__main__':
    pytest.main(['-v',"-s" ,'-x', 'test_onu_gemport.py'] )
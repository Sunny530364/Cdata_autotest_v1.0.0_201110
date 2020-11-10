#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

import pytest
from src.xinertel.muticast11 import *
from src.FD1616GS.ont_auth import *
from tests.FD1616GS.initialization_config import *
from src.FD1616GS.multicast import *
import allure

current_dir_name = 'FD1616GS'


@allure.feature("onu 组播测试")
@allure.story("onu 组播snooping测试")
@allure.title("测试onu组播正常通(下行untag)的情况")
@pytest.mark.run(order=1624)
def test_ont_snooping_Down_untag(login):
    '''
    用例描述
    测试目的：ont为snooping模式（mvlan为3000，ip 239.1.1.1）,onu的native-vlan为3000，测试onu为snooping模式下组播239.1.1.1是否通
    测试步骤：
    步骤1:发现未注册的ONU
    步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3:配置onu端口native-vlan为3000
    步骤4:添加虚端口vlan透传3000
    步骤5:onu端口绑定组播模板200（mvlan3000 ,ip 239.1.1.1 ,dynamic acl）
    步骤6:打流测试
    1）服务端发送数据流239.1.1.1，查看onu端口是否收到组播数据流239.1.1.1
    multicaststream_header=('ethernetII_1.destMacAdd=01:00:5e:01:01:01 vlan_1.id=3000 ipv4_1.destination=239.1.1.1')
    预期结果:onu端口无法收到组播数据流
    2）客户端发送report报文加入组播239.1.1.1 ，然后服务端口发送组播239.1.1.1的数据流(带tag3000)，10秒后，停止发流
    预期结果:服务端收到report报文，客户端收到组播数据流239.1.1.1
    3)客户端端口发送离开报文，离开组播组239.1.1.1
    预期结果：客户端接收不到数据
    '''
    renix_info("=========ONU组播snooping测试:组播正常通=========")
    cdata_info("=========ONU组播snooping测试:组播正常通=========")
    tn = login
    Vlan_list=[3000]
    User_Vlan = "3000"
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID,  Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn ,Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:配置onu端口native-vlan为3000"):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step("步骤4:添加虚端口vlan透传3000"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step('步骤5：组播模板配置下行组播vlan untag'):
        assert onu_multicast_forward_untag(tn, Ont_Igmpprofile_ID)
    with allure.step("步骤5:onu端口绑定组播模板"):
        assert ont_multicast(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID, Ont_Igmpprofile_ID)

    with allure.step("步骤6:onu组播打流测试"):
        # 配置ont端口native-vlan为3000，onu端口1绑定组播模板（mvlan3000,ip 239.1.1.1）

        time.sleep(8)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        #发流测试
        result = multicast_test_FD1616(tn,Gpon_PonID, Gpon_OnuID, Ont_Port_ID,port_location=port_location,
                       multicaststream_header=('ethernetII_1.destMacAdd=01:00:5e:01:01:01 vlan_1.id=3000 ipv4_1.destination=239.1.1.1'),
                       multicastgroupip='239.1.1.1',
                       packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                       duration=10)

        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # 判断如果文件存在，就开始分析报文
        tag_result = 'PASS'
        packet_filenames = result[1]
        if os.path.isfile(packet_filenames[1]):
            packets = rdpcap(packet_filenames[1])
            # cdata_info(packets)
            for data in packets:
                if data['Ether'].dst == '01:00:5e:01:01:01' and 'UDP' in data:
                    s = repr(data)
                    # cdata_debug(s)
                    # print((data['Ether'].decode()))
                    if 'Dot1Q'  not in data:
                        cdata_info('onu端口接收到下行组播数据流不带tag')
                    else:
                        cdata_error('onu端口接收到下行组播数据流带tag %s' % (data['Dot1Q'].vlan))
                        tag_result = 'FAIL'
                    break

        if result[0] == 'PASS' and  tag_result=='PASS':
            cdata_info("测试onu组播正常通(下行组播vlan为untag)的情况:打流测试正常,vlan tag正常")
        else:
            cdata_error("测试onu组播正常通(下行组播vlan为untag)的情况:打流测试失败或者vlan tag错误")

        assert result[0] == 'PASS' and tag_result == 'PASS'

@allure.feature("onu 组播测试")
@allure.story("onu 组播snooping测试")
@allure.title("测试onu组播正常通(下行transparent)的情况")
@pytest.mark.run(order=1624)
def test_ont_snooping_Down_transparent(login):
    '''
    用例描述
    测试目的：ont为snooping模式（mvlan为3000，ip 239.1.1.1）,onu的native-vlan为3000，测试onu为snooping模式下组播239.1.1.1是否通
    测试步骤：
    步骤1:发现未注册的ONU
    步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3:配置onu端口native-vlan为3000
    步骤4:添加虚端口vlan透传3000
    步骤5:onu端口绑定组播模板200（mvlan3000 ,ip 239.1.1.1 ,dynamic acl）
    步骤6:打流测试
    1）服务端发送数据流239.1.1.1，查看onu端口是否收到组播数据流239.1.1.1
    multicaststream_header=('ethernetII_1.destMacAdd=01:00:5e:01:01:01 vlan_1.id=3000 ipv4_1.destination=239.1.1.1')
    预期结果:onu端口无法收到组播数据流
    2）客户端发送report报文加入组播239.1.1.1 ，然后服务端口发送组播239.1.1.1的数据流(带tag3000)，10秒后，停止发流
    预期结果:服务端收到report报文，客户端收到组播数据流239.1.1.1
    3)客户端端口发送离开报文，离开组播组239.1.1.1
    预期结果：客户端接收不到数据
    '''
    renix_info("=========ONU组播snooping测试:组播正常通=========")
    cdata_info("=========ONU组播snooping测试:组播正常通=========")
    tn = login
    Vlan_list=[3000]
    User_Vlan = "3000"
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID,  Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn ,Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:配置onu端口native-vlan为3000"):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step("步骤4:添加虚端口vlan透传3000"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step('步骤5：组播模板配置下行组播vlan transparent'):
        assert onu_multicast_forward_transparent(tn, Ont_Igmpprofile_ID)
    with allure.step("步骤5:onu端口绑定组播模板"):
        assert ont_multicast(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID, Ont_Igmpprofile_ID)

    with allure.step("步骤6:onu组播打流测试"):
        # 配置ont端口native-vlan为3000，onu端口1绑定组播模板（mvlan3000,ip 239.1.1.1）

        time.sleep(8)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        #发流测试
        result = multicast_test_FD1616(tn,Gpon_PonID, Gpon_OnuID, Ont_Port_ID,port_location=port_location,
                       multicaststream_header=('ethernetII_1.destMacAdd=01:00:5e:01:01:01 vlan_1.id=3000 ipv4_1.destination=239.1.1.1'),
                       multicastgroupip='239.1.1.1',
                       packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                       duration=10)

        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # 判断如果文件存在，就开始分析报文
        tag_result = 'PASS'
        packet_filenames = result[1]
        if os.path.isfile(packet_filenames[1]):
            packets = rdpcap(packet_filenames[1])
            # cdata_info(packets)
            for data in packets:
                if data['Ether'].dst == '01:00:5e:01:01:01' and 'UDP' in data:
                    s = repr(data)
                    # cdata_debug(s)
                    # print((data['Ether'].decode()))
                    if 'Dot1Q' not  in data:
                        cdata_info('onu端口接收到下行组播数据流不带tag')
                        tag_result = 'FAIL'
                    else:
                        cdata_info('onu端口接收到下行组播数据流带tag %s' % (data['Dot1Q'].vlan))

                    break

        if result[0] == 'PASS' and  tag_result=='PASS':
            cdata_info("测试onu组播正常通(下行组播vlan为transparent)的情况:打流测试正常,vlan tag正常")
        else:
            cdata_error("测试onu组播正常通((下行组播vlan为transparent))的情况:打流测试失败或者vlan tag错误")

        assert result[0] == 'PASS' and tag_result == 'PASS'

@allure.feature("onu 组播测试")
@allure.story("onu 组播snooping测试")
@allure.title("测试onu组播正常通(下行translation)的情况")
@pytest.mark.run(order=1624)
def test_ont_snooping_Down_translation(login):
    '''
    用例描述
    测试目的：ont为snooping模式（mvlan为3000，ip 239.1.1.1）,onu的native-vlan为3000，测试onu为snooping模式下组播239.1.1.1是否通
    测试步骤：
    步骤1:发现未注册的ONU
    步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3:配置onu端口native-vlan为3000
    步骤4:添加虚端口vlan透传3000
    步骤5:onu端口绑定组播模板200（mvlan3000 ,ip 239.1.1.1 ,dynamic acl）
    步骤6:打流测试
    1）服务端发送数据流239.1.1.1，查看onu端口是否收到组播数据流239.1.1.1
    multicaststream_header=('ethernetII_1.destMacAdd=01:00:5e:01:01:01 vlan_1.id=3000 ipv4_1.destination=239.1.1.1')
    预期结果:onu端口无法收到组播数据流
    2）客户端发送report报文加入组播239.1.1.1 ，然后服务端口发送组播239.1.1.1的数据流(带tag3000)，10秒后，停止发流
    预期结果:服务端收到report报文，客户端收到组播数据流239.1.1.1
    3)客户端端口发送离开报文，离开组播组239.1.1.1
    预期结果：客户端接收不到数据
    '''
    renix_info("=========ONU组播snooping测试:组播正常通=========")
    cdata_info("=========ONU组播snooping测试:组播正常通=========")
    tn = login
    Vlan_list=[3000]
    User_Vlan = "3000"
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID,  Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn ,Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:配置onu端口native-vlan为3000"):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step("步骤4:添加虚端口vlan透传3000"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step('步骤5：组播模板配置下行组播vlan translation'):
        User_Vlan = "2000"
        assert onu_multicast_forward_translation(tn,Ont_Igmpprofile_ID,Cvlan=User_Vlan)
    with allure.step("步骤5:onu端口绑定组播模板"):
        assert ont_multicast(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID, Ont_Igmpprofile_ID)

    with allure.step("步骤6:onu组播打流测试"):
        # 配置ont端口native-vlan为3000，onu端口1绑定组播模板（mvlan3000,ip 239.1.1.1）

        time.sleep(8)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        #发流测试
        result = multicast_test_FD1616(tn,Gpon_PonID, Gpon_OnuID, Ont_Port_ID,port_location=port_location,
                       multicaststream_header=('ethernetII_1.destMacAdd=01:00:5e:01:01:01 vlan_1.id=3000 ipv4_1.destination=239.1.1.1'),
                       multicastgroupip='239.1.1.1',
                       packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                       duration=10)

        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # 判断如果文件存在，就开始分析报文
        tag_result = 'PASS'
        packet_filenames = result[1]
        if os.path.isfile(packet_filenames[1]):
            packets = rdpcap(packet_filenames[1])
            # cdata_info(packets)
            for data in packets:
                if data['Ether'].dst == '01:00:5e:01:01:01' and 'UDP' in data:
                    s = repr(data)
                    # cdata_debug(s)
                    # print((data['Ether'].decode()))
                    if 'Dot1Q' not  in data:
                        cdata_error('onu端口接收到下行组播数据流不带tag')
                        tag_result = 'FAIL'
                    elif 'Dot1Q' in data and data['Dot1Q'].vlan != int(User_Vlan):
                        cdata_error('onu端口接收到下行组播数据流带tag %s' % (data['Dot1Q'].vlan))
                        tag_result = 'FAIL'
                    elif 'Dot1Q' in data and data['Dot1Q'].vlan == int(User_Vlan):
                        cdata_info('onu端口接收到下行组播数据流带tag %s' % (data['Dot1Q'].vlan))
                    break

        if result[0] == 'PASS' and  tag_result=='PASS':
            cdata_info("测试onu组播正常通(下行组播报文vlan为translation %s)的情况:打流测试正常,vlan tag正常"%User_Vlan)
        elif result[0] == 'PASS' and  tag_result=='FAIL':
            cdata_info("测试onu组播正常通(下行组播报文vlan为translation %s)的情况:打流测试正常,vlan tag错误" % User_Vlan)
        else:
            cdata_error("测试onu组播正常通(下行组播报文vlan为translation %s)的情况:打流测试失败或者vlan tag错误"%User_Vlan)

        assert result[0] == 'PASS' and tag_result == 'PASS'

@allure.feature("onu 组播测试")
@allure.story("onu 组播snooping测试")
@allure.title("测试onu组播正常不通的情况")
@pytest.mark.run(order=1625)
# @pytest.mark.skip("暂时不执行")
def test_ont_snooping_abnormal(login):
    '''
    用例描述
    测试目的：ont为snooping模式（mvlan为3000，ip 239.1.1.1）,onu的native-vlan为3000，测试onu为snooping模式下组播239.2.2.2是否不通
    测试步骤：
    步骤1:发现未注册的ONU
    步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3:配置onu端口native-vlan为3000
    步骤4:添加虚端口vlan透传3000
    步骤5:onu端口绑定组播模板200（mvlan3000 ,ip 239.1.1.1 ,dynamic acl）
    步骤6:打流测试
    1）客户端发送report报文加入组播239.2.2.2 ，然后服务端口发送组播239.2.2.2的数据流
    multicaststream_header=('ethernetII_1.destMacAdd=01:00:5e:02:02:02 vlan_1.id=3000 ipv4_1.destination=239.2.2.2')
    预期结果：服务端口收到report报文收不到，客户端接收不到组播239.2.2.2的组播数据流

    '''
    renix_info("=========ONU组播snooping测试:组播正常不通=========")
    cdata_info("=========ONU组播snooping测试:组播正常不通=========")
    tn = login
    Vlan_list = [3000]
    User_Vlan = "3000"
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3:配置onu端口native-vlan为3000"):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step("步骤4:添加虚端口vlan透传3000"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step("步骤5:onu端口绑定组播模板"):
        assert ont_multicast(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID,Ont_Igmpprofile_ID)
    with allure.step("步骤6:onu组播打流测试"):

        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        result = multicast_test_FD1616(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID,port_location=port_location,
                       multicaststream_header=('ethernetII_1.destMacAdd=01:00:5e:02:02:02 vlan_1.id=3000 ipv4_1.destination=239.2.2.2'),
                       multicastgroupip='239.2.2.2',
                       check='abnormal',
                        packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                       duration=10)
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # 判断如果文件存在，就开始分析报文
        tag_result = 'PASS'
        packet_filenames = result[1]
        if os.path.isfile(packet_filenames[1]):
            packets = rdpcap(packet_filenames[1])
            # cdata_info(packets)
            for data in packets:
                if data['Ether'].dst == '01:00:5e:01:01:01' and 'UDP' in data:
                    s = repr(data)
                    # cdata_debug(s)
                    # print((data['Ether'].decode()))
                    if 'Dot1Q' not in data:
                        cdata_error('onu端口接收到下行组播数据流不带tag')
                    elif 'Dot1Q' in data :
                        cdata_error('onu端口接收到下行组播数据流带tag %s' % (data['Dot1Q'].vlan))
                    break

        if result[0] == 'PASS':
            cdata_info("测试onu组播正常不通的情况:打流测试正常")
        else:
            cdata_error("测试onu组播正常不通的情况:打流测试失败")

        assert result[0] == 'PASS'

@allure.feature("onu 组播测试")
@allure.story("onu 组播snooping测试")
@allure.title("测试onu跨组播vlan")
@pytest.mark.run(order=1626)
def test_ont_cross_mvlan(login):
    '''
    用例描述
    测试目的：ont为snooping模式（mvlan为3000，ip 239.1.1.1）,onu的native-vlan为2000，测试onu的跨组播vlan是否正常的
    测试步骤：
    步骤1:发现未注册的ONU
    步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线
    步骤3:配置onu端口native-vlan为2000
    步骤4:添加虚端口vlan透传2000
    步骤5:onu端口绑定组播模板200（mvlan3000 ,ip 239.1.1.1 ,dynamic acl）
    步骤6:打流测试
    1）客户端发送report报文加入组播239.1.1.1 ，然后服务端口发送组播239.1.1.1的数据流，10秒后，停止发流
    multicaststream_header=('ethernetII_1.destMacAdd=01:00:5e:01:01:01 vlan_1.id=3000 ipv4_1.destination=239.1.1.1')
    预期结果：服务端收到report报文，客户端收到组播数据流239.1.1.1
    2)服务端发送组播数据流，客户端发送离开报文，离开组播组239.1.1.1
    预期结果：客户端接收不到数据

    '''
    renix_info("=========ONU组播snooping测试:跨组播vlan测试=========")
    cdata_info("=========ONU组播snooping测试:跨组播vlan测试=========")
    tn = login
    Vlan_list = [2000]
    User_Vlan = "2000"
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID, Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过Gpon_SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn, Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step("步骤3：配置onu端口native-vlan为2000"):
        assert ont_native_vlan(tn, Gpon_PonID, Gpon_OnuID, Ont_Port_ID, User_Vlan)
    with allure.step("步骤4：添加虚端口vlan透传2000"):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step("步骤5:onu端口绑定组播模板"):
        assert ont_multicast(tn, Gpon_PonID, Gpon_OnuID,Ont_Port_ID,Ont_Igmpprofile_ID)
    with allure.step("步骤6:onu组播打流测试"):

        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # 发流测试
        result = multicast_test_FD1616(tn,Gpon_PonID, Gpon_OnuID, Ont_Port_ID,port_location=port_location,
                                multicaststream_header=('ethernetII_1.destMacAdd=01:00:5e:01:01:01 vlan_1.id=3000 ipv4_1.destination=239.1.1.1'),
                                multicastgroupip='239.1.1.1',
                                packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                duration=5)
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # 判断如果文件存在，就开始分析报文
        tag_result = 'PASS'
        packet_filenames = result[1]
        if os.path.isfile(packet_filenames[1]):
            packets = rdpcap(packet_filenames[1])
            # cdata_info(packets)
            for data in packets:
                if data['Ether'].dst == '01:00:5e:01:01:01' and 'UDP' in data:
                    s = repr(data)
                    # cdata_debug(s)
                    # print((data['Ether'].decode()))
                    if 'Dot1Q' in data:
                        cdata_info('onu端口接收到下行组播数据流带tag %s'%((data['Dot1Q'].vlan)))
                    elif 'Dot1Q' not in data:
                        cdata_info('onu端口接收到下行组播数据流不带tag')
                    break

        if result[0] == 'PASS':
            cdata_info("测试onu跨组播vlan的情况:打流测试正常")
        else:
            cdata_error("测试onu跨组播vlan的情况:打流测试失败")

        assert result[0]=='PASS'

if __name__ == '__main__':
    pytest.main(['-v','-s','test_onu_multicast.py'])



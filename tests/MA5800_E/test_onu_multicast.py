#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI


import pytest,allure
from src.MA5800_E.multicast import *
from src.MA5800_E.vlan_func import *
from src.xinertel.muticast11 import *
from src.MA5800_E.ont_auth import *
from src.config.initialization_config import *
from os.path import dirname, abspath
import scapy
from scapy.all import *
from scapy.utils import  PcapReader

current_dir_name='MA5800_E'

@pytest.fixture(scope='function')
def onu_igmp_transparent_suit(login):
    tn=login
    yield tn
    del_multicast_member(tn, Epon_PonID, Epon_OnuID, User_Vlan='3000')


@pytest.fixture(scope='function')
def onu_igmp_suit(login):
    tn=login
    yield tn
    del_ont_igmp_mvlan(tn, Ont_Srvprofile_ID, Ont_Port_ID, Mvlan)
    del_multicast_member(tn, Epon_PonID, Epon_OnuID, User_Vlan='3000')

@allure.feature("onu 组播测试")
@allure.story("onu 组播透传测试")
@allure.title("测试onu组播透传的情况")
@pytest.mark.run(order=15817)
def test_ont_igmp_transparent(onu_igmp_transparent_suit):
    cdata_info("=========onu为组播透传测试=========")

    tn = onu_igmp_transparent_suit
    Vlan_list=[3000]
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    # with allure.step("步骤3:配置onu端口vlan为transparent"):
    #     assert ont_port_transparent(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID)
    with allure.step('步骤3:ONU的以太网口1添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID, User_Vlan='3000')
    with allure.step('步骤4:在OLT配置ONU的service-port。'):
        assert add_service_port(tn, Epon_PonID, Epon_OnuID, Vlan_list)
    with allure.step('步骤5:配置onu组播模式为transparent'):
        assert ont_imgp_transparent(tn,Epon_PonID,Epon_OnuID,Mvlan='3000',User_Vlan='3000')
    with allure.step("步骤6:打流测试"):
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        # 发流测试
        result = multicast_test_MA5800(port_location=port_location,
                                multicaststream_header=(
                                    'ethernetII_1.destMacAdd=01:00:5e:01:01:01 vlan_1.id=3000 ipv4_1.destination=239.1.1.1'),
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
                    cdata_info(s)
                    # print((data['Ether'].decode()))
                    if 'Dot1Q' in data:
                        cdata_info('onu端口接收到下行组播数据流带tag %s' % (data['Dot1Q'].vlan))
                    elif 'Dot1Q' not in data:
                        cdata_info('onu端口接收到下行组播数据流不带tag')
                    break

        if result[0] == 'PASS':
            cdata_info("测试onu组播正常通的情况:打流测试正常")
        else:
            cdata_error("测试onu组播正常通的情况:打流测试失败")

        assert result[0] == 'PASS'

@allure.feature("onu 组播测试")
@allure.story("onu 组播snooping测试")
@allure.title("测试onu组播snooping的情况")
@pytest.mark.run(order=15818)
def test_ont_igmp_snooping(onu_igmp_suit):
    cdata_info("=========onu为组播snooping测试=========")
    tn = onu_igmp_suit
    Vlan_list = [3000]
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
        # with allure.step("步骤3:配置onu端口vlan为transparent"):
        #     assert ont_port_transparent(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID)
    with allure.step('步骤3:ONU的以太网口1添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID, User_Vlan='3000')
    with allure.step('步骤4:在OLT配置ONU的service-port。'):
        assert add_service_port(tn, Epon_PonID, Epon_OnuID, Vlan_list)
    with allure.step('步骤6:配置onu组播模式为snooping'):
        assert ont_imgp_snooping(tn,Epon_PonID,Epon_OnuID, Mvlan='3000',User_Vlan='3000')
    with allure.step('步骤6:配置onu组播模式为snooping'):
        assert ont_igmp_mvlan(tn,Ont_Srvprofile_ID, Ont_Port_ID, Mvlan)
    with allure.step("步骤6:打流测试"):
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        # 发流测试
        result = multicast_test_MA5800(port_location=port_location,
                                multicaststream_header=(
                                    'ethernetII_1.destMacAdd=01:00:5e:01:01:01 vlan_1.id=3000 ipv4_1.destination=239.1.1.1'),
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
                    cdata_info(s)
                    # print((data['Ether'].decode()))
                    if 'Dot1Q' in data:
                        cdata_info('onu端口接收到下行组播数据流带tag %s' % (data['Dot1Q'].vlan))
                    elif 'Dot1Q' not in data:
                        cdata_info('onu端口接收到下行组播数据流不带tag')
                    break

        if result[0] == 'PASS':
            cdata_info("测试onu组播snooping的情况:打流测试正常")
        else:
            cdata_error("测试onu组播snoooping的情况:打流测试失败")

        assert result[0] == 'PASS'

@allure.feature("onu 组播测试")
@allure.story("onu 组播snooping测试")
@allure.title("测试onu跨组播vlan")
@pytest.mark.run(order=15819)
# @pytest.mark.skip("暂时不执行")
def test_ont_cross_mvlan(onu_igmp_suit):
    cdata_info("=========onu为跨组播vlan测试=========")
    Vlan_list = [2000]
    tn = onu_igmp_suit
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
        # with allure.step("步骤3:配置onu端口vlan为transparent"):
        #     assert ont_port_transparent(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID)
    with allure.step('步骤3:ONU的以太网口1添加NATIVE-VLAN。'):
        assert ont_native_vlan(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID, User_Vlan='2000')
    with allure.step('步骤4:在OLT配置ONU的service-port。'):
        assert add_service_port(tn, Epon_PonID, Epon_OnuID, Vlan_list)

    with allure.step('步骤6:配置onu组播模式为snooping'):
        assert ont_imgp_snooping(tn, Epon_PonID, Epon_OnuID, Mvlan='3000',User_Vlan='2000')
    with allure.step('步骤6:配置onu组播模式为snooping'):
        assert ont_igmp_mvlan(tn, Ont_Srvprofile_ID, Ont_Port_ID, Mvlan)
    with allure.step("步骤6:打流测试"):
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        # 发流测试
        result = multicast_test_MA5800(port_location=port_location,
                                multicaststream_header=(
                                    'ethernetII_1.destMacAdd=01:00:5e:01:01:01 vlan_1.id=3000 ipv4_1.destination=239.1.1.1'),
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
                    cdata_info(s)
                    # print((data['Ether'].decode()))
                    if 'Dot1Q' in data:
                        cdata_info('onu端口接收到下行组播数据流带tag %s' % (data['Dot1Q'].vlan))
                    elif 'Dot1Q' not in data:
                        cdata_info('onu端口接收到下行组播数据流不带tag')
                    break
        if result[0] == 'PASS':
            cdata_info("测试onu组播正常通的情况:打流测试正常")
        else:
            cdata_error("测试onu组播正常通的情况:打流测试失败")

        assert result[0] == 'PASS'

if __name__ == '__main__':
    pytest.main(['-v','-s','-x','test_onu_multicast.py::test_ont_cross_mvlan'])
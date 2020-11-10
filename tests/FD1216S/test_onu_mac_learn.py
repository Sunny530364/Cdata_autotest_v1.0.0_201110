#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI
from src.xinertel.unicast66 import *
from src.FD1216S.mac_learn import *
from src.FD1216S.ont_auth import *
from tests.FD1216S.initialization_config import *
import pytest
import allure

import os
import sys

p = os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
if p not in sys.path:
    sys.path.append(p)

current_dir_name='FD1216S'

@allure.feature("onu mac地址上报测试")
@allure.story("onu mac地址上报测试")
@allure.title("onu mac地址上报测试")
@pytest.mark.run(order=1214)
def test_ont_mac_learn(login):
    '''
    用例描述
    测试目的： 测试onu端口mac地址学习是否正常
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过MAC的方式将ONU注册上线
    步骤3: 打流测试,查看onu端口mac地址表
    1）上下行各发送流00:00:00:22:22:21递增5条，在olt上查看onu端口mac地址表
    down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.1.11 ipv4_1.destination=92.168.1.21',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.1.12 ipv4_1.destination=92.168.1.22',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:13 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:23 ipv4_1.source=192.168.1.13 ipv4_1.destination=92.168.1.23',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:14 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:24 ipv4_1.source=192.168.1.14 ipv4_1.destination=92.168.1.24',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:15 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:25 ipv4_1.source=192.168.1.15 ipv4_1.destination=92.168.1.25',)
    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.1.21 ipv4_1.destination=92.168.1.11',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.1.22 ipv4_1.destination=92.168.1.12',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:23 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:13 ipv4_1.source=192.168.1.23 ipv4_1.destination=92.168.1.13',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:24 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:14 ipv4_1.source=192.168.1.24 ipv4_1.destination=92.168.1.14',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:25 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:15 ipv4_1.source=192.168.1.25 ipv4_1.destination=92.168.1.15',
    )
    预期结果: 上下行正常通，在olt上查看onu端口mac地址表有5条（00:00:00:22:22:21递增5条）
    '''
    renix_info("=========ONU MAC地址上报测试=========")
    cdata_info("=========ONU MAC地址上报测试=========")
    tn = login
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step("步骤3:打流测试,查看onu端口mac地址表"):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        duration = 10
        down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.1.11 ipv4_1.destination=92.168.1.21',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.1.12 ipv4_1.destination=92.168.1.22',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:13 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:23 ipv4_1.source=192.168.1.13 ipv4_1.destination=92.168.1.23',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:14 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:24 ipv4_1.source=192.168.1.14 ipv4_1.destination=92.168.1.24',
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:15 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:25 ipv4_1.source=192.168.1.15 ipv4_1.destination=92.168.1.25',)

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.1.21 ipv4_1.destination=92.168.1.11',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.1.22 ipv4_1.destination=92.168.1.12',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:23 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:13 ipv4_1.source=192.168.1.23 ipv4_1.destination=92.168.1.13',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:24 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:14 ipv4_1.source=192.168.1.24 ipv4_1.destination=92.168.1.14',
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:25 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:15 ipv4_1.source=192.168.1.25 ipv4_1.destination=92.168.1.15',
        )
        # 获取所有流量的统计值
        result = unicast_test(port_location=port_location, down_stream_header=down_stream_header,
                                    up_stream_header=up_stream_header,
                                    packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                    num=5, dataclassname=PortStats,
                                    duration=duration)

        result_stats = result[0]
        # 判断如果文件存在，就开始分析报文
        tag_result = 'PASS'
        packet_filenames = result[1]

        #判断流上下行接收是否正常
        result_stream  = check_port_static(result_stats[0],result_stats[1])
        #判断olt上是否能查看onu学习的mac地址
        tn = login
        result_show = ont_mac_learn(tn,Epon_PonID,Epon_OnuID,Ont_Port_ID)
        result_mac = 'PASS'
        if '00:00:00:22:22:21' in result_show and '00:00:00:22:22:22' in result_show and '00:00:00:22:22:23' in result_show \
            and  '00:00:00:22:22:24' in result_show and  '00:00:00:22:22:25' in result_show:
            result_mac = 'PASS'
        else:
            result_mac = 'FAIL'


        if result_mac == 'PASS':
            cdata_info("ONT MAC地址上报:MAC地址学习正常")
        else:
            cdata_error("ONT MAC地址上报:MAC地址学习失败")

        if result_stream == 'PASS':
            cdata_info("ONT MAC地址上报:打流正常")
        else:
            cdata_error("ONT MAC地址上报:打流失败")

        assert result_stream=='PASS' and result_mac =='PASS'


if __name__ == '__main__':
    pytest.main(['-s','test_onu_mac_learn.py::test_ont_mac_learn'])




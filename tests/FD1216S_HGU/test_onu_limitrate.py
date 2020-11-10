#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

import pytest
from src.xinertel.unicast66 import *
from src.Epon_HGU.ont_auth import *
from src.Epon_HGU.limitrate import *
from tests.FD1216S_HGU.initialization_config import *
from src.Epon_HGU.oam_wan import *
from src.xinertel.renix_test import *
import allure

current_dir_name='FD1216S_HGU'

@pytest.fixture(scope='function')
def dba_limitrate_suit(login):
    tn=login
    yield tn
    with allure.step('步骤5:dba模板恢复默认配置type4 max1000000'):
        assert dba_limitrate_type4(tn, Dba_Profile_ID, max='1000000')
    with allure.step('步骤9:删除oam_wan配置'):
        assert del_oam_wan(tn, Epon_PonID, Epon_OnuID)


@allure.feature("onu限速测试")
@allure.story("dba限速测试")
@allure.title("测试dba限速(type4)")
@pytest.mark.run(order=2009)
def test_dba_limitrate(dba_limitrate_suit):
    '''
    用例描述
    测试目的： 测试dba限速是否正常（type5）
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过SN的方式将ONU注册上线
    步骤3: 配置dba模板(type5 fix 10240 assure 20480 max 51200)
    步骤4: 配置虚端口vlan2000透传
    步骤5: 打流测试
    测试方法: 上下行各发送流：vlan2000 (如果onu端口为1000M,速率为端口速率的10%;如果onu端口为100M,速率为端口速率的100%)
    down_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21',)
    up_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11',)
    预期结果: 上下行正常通，上行不限速，下行限速50M
    步骤6: 配置dba模板(type4  max 1024000)

    '''

    cdata_info("=========DBA限速测试=========")
    tn = dba_limitrate_suit
    Vlan_list = [2000]
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:配置dba模板'):
        max = '51200'
        assert dba_limitrate_type5(tn, Dba_Profile_ID, fix='10240', assure='20480', max='51200')
    with allure.step('步骤3:在OLT配置PON口的VLAN。'):
        assert add_pon_vlan(tn, Epon_PonID, '2000')
    with allure.step('步骤4:添加桥接模式的oam_wan,VLAN为2000，业务类型为OTHER'):
        assert add_oam_wan_bridge_vlan_enable(tn, Epon_PonID, Epon_OnuID, 'cdata_test', 'enable', '2000', '0', 'vod','1-8')
        time.sleep(10)
    with allure.step('步骤5:打流测试。'):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(8)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        duration = 10
        down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.191.11 ipv4_1.destination=92.168.191.21',)

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.191.21 ipv4_1.destination=92.168.191.11',)
        # 获取所有流量的统计值
        result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header,
                                 up_stream_header=up_stream_header,
                                 packet_name=olt_type + '_' + sys._getframe().f_code.co_name,
                                 rate=100,
                                 duration=duration)
        result1 = check_stream_rate_inbound(result_stats[0], result_stats[1], max)

        # 正确的结果pri2的能通，pri3的不通
        if result1 == 'PASS' :
            result = 'PASS'
            cdata_info("DBA限速:打流测试正常")
        else:
            result = 'FAIL'
            cdata_error("DBA限速:打流测试失败")
        time.sleep(2)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        assert result == 'PASS'
    # with allure.step('步骤5:打流测试。'):
    #     # 清除测试仪的对象，防止影响下个用例的执行
    #     time.sleep(8)
    #     reset_rom_cmd = ResetROMCommand()
    #     reset_rom_cmd.execute()
    #
    #     port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
    #     duration = 10
    #     down_stream_header = (
    #         'ethernetII_1.sourceMacAdd=00:00:00:22:11:11  ethernetII_1.destMacAdd=00:00:00:11:22:22 ipv4_1.source=192.168.111.111 ipv4_1.destination=192.168.111.222',)
    #
    #     up_stream_header = (
    #         'ethernetII_1.sourceMacAdd=00:00:00:11:22:22  ethernetII_1.destMacAdd=00:00:00:22:11:11 ipv4_1.source=192.168.111.222 ipv4_1.destination=192.168.111.111',)
    #     # 获取所有流量的统计值
    #     result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header,
    #                              up_stream_header=up_stream_header,
    #                              rate=10,
    #                              duration=duration)
    #
    #         # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
    #         #onu端口为1000M，上下行都发送端口速率的10%，也就是100M,DBA上行限50M,所以下行比例是（100/100）=1， 上行是（50/100）=0.5
    #     result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.5)
    #
    #
    #     # 正确的结果pri2的能通，pri3的不通
    #     if result1 == 'PASS' :
    #         result = 'PASS'
    #         cdata_info("DBA限速:打流测试正常")
    #     else:
    #         result = 'FAIL'
    #         cdata_error("DBA限速:打流测试失败")
    #     time.sleep(2)
    #     reset_rom_cmd = ResetROMCommand()
    #     reset_rom_cmd.execute()
    #     assert result == 'PASS'


if __name__ == '__main__':
    # case_1()
    pytest.main(["-v",'-s', "-x", "test_onu_limitrate.py"])

#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

import pytest
from src.xinertel.unicast66 import *
from src.FD1216S.limitrate import *
from tests.FD1216S.initialization_config import *
from src.FD1216S.ont_auth import *
import allure

current_dir_name='FD1216S'

@pytest.fixture(scope='function')
def dba_limitrate_suit(login):
    tn=login
    yield tn
    with allure.step('步骤5:dba模板恢复默认配置type4 max1000000'):
        assert dba_limitrate_type4(tn,Dba_Profile_ID,max='1000000')

@pytest.fixture(scope='function')
def ont_port_inbound_limitrate(login):
    tn =login
    yield tn
    with allure.step('步骤5:删除onu端口的入口速率'):
        ont_port_limitrate_inbound_del(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID)

@pytest.fixture(scope='function')
def ont_port_outbound_limitrate(login):
    tn =login
    yield tn
    with allure.step('步骤5:删除onu端口的出口限速'):
        ont_port_limitrate_outbound_del(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID)

@allure.feature("onu限速测试")
@allure.story("dba限速测试")
@allure.title("dba限速测试")
@pytest.mark.run(order=1217)
def test_dba_limitrate(dba_limitrate_suit):
    '''
    用例描述
    测试目的： 测试dba限速是否正常（type5）
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过mac的方式将ONU注册上线
    步骤3: 配置dba模板(type5 fix 10240 assure 20480 max 51200)
    步骤4: 打流测试
    测试方法: 上下行各发送流：vlan2000 (如果onu端口为1000M,速率为端口速率的10%;如果onu端口为100M,速率为端口速率的100%)
    down_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21',)
    up_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11',)
    预期结果: 上下行正常通，上行不限速，下行限速50M
    步骤5: 配置dba模板(type4  max 1000000)

    '''

    # tn=login
    # #配置dba模板
    # dba_limitrate_type5(tn, Dba_Profile_ID=100)
    cdata_info("=========DBA限速测试=========")
    tn = dba_limitrate_suit
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:配置dba模板'):
        max='51200'
        assert dba_limitrate_type5(tn,Dba_Profile_ID,fix='10240',assure='20480',max='51200')
    with allure.step('步骤4:打流测试。'):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(8)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # #判断port2的速率协商
        # if port2_speed == 'SPEED_1G':
        #     rate = 10
        # elif port2_speed == 'SPEED_100M':
        #     rate = 100
        # 发流量测试，上下行发送流量，速率为100M
        # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
        duration = 10
        down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.1.11 ipv4_1.destination=92.168.1.21',)

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.1.21 ipv4_1.destination=92.168.1.11',)
        # 获取所有流量的统计值
        result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header,
                                 up_stream_header=up_stream_header,
                                 packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                 rate=100,
                                 duration=duration)

        result1 = check_stream_rate_inbound(result_stats[0], result_stats[1], max)
        # if port2_speed == 'SPEED_100M' and port1_speed == 'SPEED_100M':
        #     # onu端口为1000M，上下行都发送端口速率的100%，也就是100M,onu端口下行限10M,所以下行比例是（10/100）=0.1， 上行是（100/100）=1
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.5, outbound_percent=1)
        # elif port2_speed == 'SPEED_100M' and port1_speed == 'SPEED_1G':
        #     # onu端口为1000M，上下行都发送端口速率的10%，也就是100M,onu端口下行限10M,所以下行比例是（10/100）=0.1， 上行是（100/100）=1
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.05, outbound_percent=1)
        # elif port2_speed == 'SPEED_1G' and port1_speed == 'SPEED_100M':
        #     # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限10M,所以下行比例是（10/1000）=0.01， 上行是（100/100）=1
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.5, outbound_percent=0.1)
        # elif port2_speed == 'SPEED_1G' and port1_speed == 'SPEED_1G':
        #     # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限10M,所以下行比例是（10/1000）=0.01， 上行是（100/100）=1
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.05, outbound_percent=1)


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

@allure.feature("onu 限速测试")
@allure.story("onu 入口限速测试")
@allure.title("onu 入口限速测试")
@pytest.mark.run(order=1215)
def test_ont_port_inbound_limitrate(ont_port_inbound_limitrate):
    '''
    用例描述
    测试目的： 测试onu端口上行限速是否正常
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过mac的方式将ONU注册上线
    步骤3: 配置onu端口的入口的速率(cir 10240)
    步骤4: 打流测试
    测试方法: 上下行各发送流：vlan2000 (如果onu端口为1000M,速率为端口速率的10%;如果onu端口为100M,速率为端口速率的100%)
    down_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21',)
    up_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11',)
    预期结果: 上下行正常通，下行不限速，上行限速10M
    步骤5:删除onu端口的入口限速

    '''
    renix_info("=========ONU端口入口限速测试=========")
    cdata_info("=========ONU端口入口限速测试=========")
    tn = ont_port_inbound_limitrate
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:配置onu端口的入口的速率'):
        cir = '10240'
        assert ont_port_limitrate_inbound(tn,Epon_PonID,Epon_OnuID,Ont_Port_ID,cir)

    with allure.step('步骤4:打流测试。'):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(5)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()

        # if port2_speed == 'SPEED_1G':
        #     rate = 10
        # elif port2_speed == 'SPEED_100M':
        #     rate = 100
        # 发流量测试，上下行发送流量，速率为100M
        # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
        duration = 10
        down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.1.11 ipv4_1.destination=92.168.1.21',)

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.1.21 ipv4_1.destination=92.168.1.11',)
        # 获取所有流量的统计值
        result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header,
                                up_stream_header=up_stream_header,
                                packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                rate=100,
                                duration=duration )
        # if rate == 10:
        #     # onu端口为1000M，上下行都发送端口速率的10%，也就是100M,onu端口下行限10M,所以下行比例是（10/100）=0.1， 上行是（100/100）=1
        #     # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.1)
        # elif rate == 100:
        #     # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限10M,所以下行比例是（10/1000）=0.01， 上行是（100/100）=1
        #     # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.01)
        result1 = check_stream_rate_inbound(result_stats[0], result_stats[1], cir)

        # #删除onu端口的限速配置
        # ont_port_limitrate_del(tn)

        # 正确的结果pri2的能通，pri3的不通
        if result1 == 'PASS':
            result = 'PASS'
            cdata_info("ONU端口入口限速:打流测试正常")
        else:
            result = 'FAIL'
            cdata_error("ONU端口入口限速:打流测试失败")
        assert result == 'PASS'

@allure.feature("onu 限速测试")
@allure.story("onu 出口限速测试")
@allure.title("onu 出口限速测试")
@pytest.mark.run(order=1216)
def test_ont_port_outbound_limitrate(ont_port_outbound_limitrate):
    '''
    用例描述
    测试目的： 测试onu端口上行限速是否正常
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过SN的方式将ONU注册上线
    步骤3: 配置onu端口的入口的速率（cir='10240' ,pir='20480'）
    步骤4: 打流测试
    测试方法: 上下行各发送流：vlan2000 (如果onu端口为1000M,速率为端口速率的10%;如果onu端口为100M,速率为端口速率的100%)
    down_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21',)
    up_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11',)
    预期结果: 上下行正常通，下行不限速，上行限速20M
    步骤5:删除onu端口的出口限速
    '''
    renix_info("=========ONU端口出口限速测试=========")
    cdata_info("=========ONU端口出口限速测试=========")
    tn = ont_port_outbound_limitrate
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Epon_ONU_MAC)
    with allure.step('步骤3:配置onu端口的出口的速率'):
        cir = '10240'
        pir = '20480'
        assert ont_port_limitrate_outbound(tn,Epon_PonID,Epon_OnuID,Ont_Port_ID,cir ,pir)
    with allure.step('步骤4:打流测试。'):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(5)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        # 发流量测试，上下行发送流量，速率为100M
        # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
        duration = 10
        down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.1.11 ipv4_1.destination=92.168.1.21',)

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.1.21 ipv4_1.destination=92.168.1.11',)
        # 获取所有流量的统计值
        result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header,
                                 up_stream_header=up_stream_header,
                                 packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                 rate=100,
                                 duration=duration )
        result1 = check_stream_rate_outbound(result_stats[0],result_stats[1],pir)

        # 正确的结果pri2的能通，pri3的不通
        if result1 == 'PASS':
            result = 'PASS'
            cdata_info("ONU端口出口限速:打流测试正常")
        else:
            result = 'FAIL'
            cdata_error("ONU端口出口限速:打流测试失败")
        assert result == 'PASS'



if __name__ == '__main__':
    pytest.main(['-s','-x','test_onu_limitrate.py::test_dba_limitrate'])
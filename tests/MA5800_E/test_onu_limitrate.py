#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

import pytest
from src.xinertel.unicast66 import *
from src.MA5800_E.vlan_func import *
from src.MA5800_E.limitrate import *
from src.MA5800_E.ont_auth import *
from src.config.initialization_config import *
import allure

current_dir_name='MA5800_E'

@pytest.fixture(scope='function')
def dba_limitrate_suit(login):
    tn=login
    yield tn
    with allure.step('步骤6:dba模板恢复默认配置type4 max1000000'):
        dba_profile_type4(tn,Dba_Profile_ID,max='1000000')

@pytest.fixture(scope='function')
def ont_port_limitrate_suit(login):
    tn = login
    yield tn
    with allure.step('步骤6:ONT端口删除绑定流量模板'):
        ont_port_limitrate_del(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID)

@allure.feature("onu限速测试")
@allure.story("onu端口限速测试")
@allure.title("测试onu端口入口限速")
@pytest.mark.run(order=15814)
def test_ont_port_inbound_limitrate(ont_port_limitrate_suit):
    '''
    用例描述
    测试目的： 测试onu端口上行限速是否正常
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过Gpon_Gpon_SN的方式将ONU注册上线
    步骤3: 配置onu端口的入口的速率（traffic-profile 1:
           traffic-profile  profile-id 1 profile-name inbound_limit cir 20480 pir 30960 cbs 2000 pbs 2000)
    步骤4: 配置虚端口vlan2000透传
    步骤5: 打流测试
    测试方法: 上下行各发送流：vlan2000 (如果onu端口为1000M,速率为端口速率的10%;如果onu端口为100M,速率为端口速率的100%)
    down_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21',)
    up_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11',)
    预期结果: 上下行正常通，下行不限速，上行限速30M

    '''
    renix_info("=========ONU端口入口限速测试=========")
    cdata_info("=========ONU端口入口限速测试=========")
    tn = ont_port_limitrate_suit
    Vlan_list = [2000]
    Traffic_Profile_ID_inbound='100'
    # 配置onu端口的入口和出口的速率（traffic-profile ）
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, ONU_MAC=Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, ONU_MAC=Epon_ONU_MAC)
    with allure.step("步骤3:配置onu端口vlan为transparent"):
        assert ont_port_transparent(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID)
    with allure.step('步骤4:配置onu端口的入口的速率（traffic-profile ）'):
        assert ont_port_limitrate_inbound(tn, Traffic_Profile_ID_inbound, Epon_PonID, Epon_OnuID, Ont_Port_ID)
    with allure.step('步骤5:在OLT配置ONU的service-port。'):
        assert add_service_port(tn, Epon_PonID, Epon_OnuID, Vlan_list)
    with allure.step('步骤6:打流测试。'):
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
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',)

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11',)
        # 获取所有流量的统计值
        result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header,
                                up_stream_header=up_stream_header,
                                packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                rate=100,
                                duration=duration )
        # if rate == 10:
        #     # onu端口为1000M，上下行都发送端口速率的10%，也就是100M,onu端口下行限30M,所以下行比例是（30/100）=0.3， 上行是（100/100）=1
        #     # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.3)
        # elif rate == 100:
        #     # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限30M,所以下行比例是（30/1000）=0.03， 上行是（100/100）=1
        #     # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.03)
        if port2_speed == 'SPEED_100M' and port1_speed == 'SPEED_100M':
            # onu端口为1000M，上下行都发送端口速率的100%，也就是100M,onu端口下行限10M,所以下行比例是（10/100）=0.1， 上行是（100/100）=1
            result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.3, outbound_percent=1)
        elif port2_speed == 'SPEED_100M' and port1_speed == 'SPEED_1G':
            # onu端口为1000M，上下行都发送端口速率的10%，也就是100M,onu端口下行限10M,所以下行比例是（10/100）=0.1， 上行是（100/100）=1
            result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.03, outbound_percent=1)
        elif port2_speed == 'SPEED_1G' and port1_speed == 'SPEED_100M':
            # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限10M,所以下行比例是（10/1000）=0.01， 上行是（100/100）=1
            result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.3, outbound_percent=0.1)
        elif port2_speed == 'SPEED_1G' and port1_speed == 'SPEED_1G':
            # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限10M,所以下行比例是（10/1000）=0.01， 上行是（100/100）=1
            result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.03, outbound_percent=1)

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

@allure.feature("onu限速测试")
@allure.story("onu端口限速测试")
@allure.title("测试onu端口出口限速")
@pytest.mark.run(order=15815)
def test_ont_port_outbound_limitrate(ont_port_limitrate_suit):
    '''
    用例描述
    测试目的： 测试onu端口上行限速是否正常
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过Gpon_Gpon_SN的方式将ONU注册上线
    步骤3: 配置onu端口的入口的速率（traffic-profile 2:
           traffic-profile  profile-id 2 profile-name outbound_limit cir 10240 pir 20480 cbs 2000 pbs 2000)
    步骤4: 配置虚端口vlan2000透传
    步骤5: 打流测试
    测试方法: 上下行各发送流：vlan2000 (如果onu端口为1000M,速率为端口速率的10%;如果onu端口为100M,速率为端口速率的100%)
    down_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:22:22:21',)
    up_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:11',)
    预期结果: 上下行正常通，上行不限速，下行限速20M

    '''
    cdata_info("=========ONU端口出口限速测试=========")
    tn = ont_port_limitrate_suit
    Vlan_list = [2000]
    Traffic_Profile_ID_outbound = '100'
    # 配置onu端口的入口和出口的速率（traffic-profile ）
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, ONU_MAC=Epon_ONU_MAC)
    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, ONU_MAC=Epon_ONU_MAC)
    with allure.step("步骤3:配置onu端口vlan为transparent"):
        assert ont_port_transparent(tn, Epon_PonID, Epon_OnuID, Ont_Port_ID)
    with allure.step('步骤4:配置onu端口的出口的速率（traffic-profile ）'):
        assert ont_port_limitrate_outbound(tn,Traffic_Profile_ID_outbound,Epon_PonID,Epon_OnuID,Ont_Port_ID)
    with allure.step('步骤5:在OLT配置ONU的service-port。'):
        assert add_service_port(tn, Epon_PonID, Epon_OnuID, Vlan_list)
    with allure.step('步骤6:打流测试。'):
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
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',)

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11',)
        # 获取所有流量的统计值
        result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header,
                                 up_stream_header=up_stream_header,
                                 packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                 rate=100,
                                 duration=duration)
        # if rate == 10:
        #     # onu端口为1000M，上下行都发送端口速率的10%，也就是100M,onu端口下行限30M,所以下行比例是（30/100）=0.3， 上行是（100/100）=1
        #     # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], outbound_percent=0.3)
        # elif rate == 100:
        #     # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限30M,所以下行比例是（30/1000）=0.03， 上行是（100/100）=1
        #     # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], outbound_percent=0.03)
        if port2_speed == 'SPEED_100M' and port1_speed =='SPEED_100M':
            result1 = check_stream_rate(result_stats[0], result_stats[1],inbound_percent=1, outbound_percent=0.3)
        elif port2_speed == 'SPEED_100M' and port1_speed =='SPEED_1G':
            result1 = check_stream_rate(result_stats[0], result_stats[1],inbound_percent=0.1, outbound_percent=0.3)
        elif port2_speed == 'SPEED_1G' and port1_speed =='SPEED_100M':
            result1 = check_stream_rate(result_stats[0], result_stats[1],inbound_percent=1, outbound_percent=0.03)
        elif port2_speed == 'SPEED_1G' and port1_speed =='SPEED_1G':
            result1 = check_stream_rate(result_stats[0], result_stats[1],inbound_percent=1, outbound_percent=0.03)
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


@allure.feature("onu限速测试")
@allure.story("dba限速测试")
@allure.title("测试dba限速(type5)")
@pytest.mark.run(order=15816)
@pytest.mark.skip('华为EPON 修改dba限速有问题，暂无法执行该用例')
def test_dba_limitrate(dba_limitrate_suit):
    '''
    用例描述
    测试目的： 测试dba限速是否正常（type5）
    测试步骤：
    步骤1: 发现未注册的ONU
    步骤2: 在OLT上通过Gpon_Gpon_SN的方式将ONU注册上线
    步骤3: 配置dba模板(type5 fix 10240 assure 20480 max 51200)
    步骤4: 配置虚端口vlan2000透传
    步骤5: 打流测试
    测试方法: 上下行各发送流：vlan2000 (如果onu端口为1000M,速率为端口速率的10%;如果onu端口为100M,速率为端口速率的100%)
    down_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21',)
    up_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11',)
    预期结果: 上下行正常通，上行不限速，下行限速50M
    步骤6: 配置dba模板(type4  max 1024000)

    '''

    # tn=login
    # #配置dba模板
    # dba_limitrate_type5(tn, dba_profile_id=100)
    cdata_info("=========DBA限速测试=========")
    tn = dba_limitrate_suit
    Vlan_list = [2000]

    with allure.step('步骤5:配置dba模板'):
        assert dba_profile_type5(tn, Dba_Profile_ID, fix='10240', assure='20480', max='51200')
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Epon_PonID, Epon_OnuID, ONU_MAC=Epon_ONU_MAC)

    with allure.step('步骤2:在OLT上通过MAC认证的方式将ONU注册上线。'):
        assert auth_by_mac(tn, Epon_PonID, Epon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, ONU_MAC=Epon_ONU_MAC)
    with allure.step("步骤3:配置onu端口vlan为transparent"):
        assert ont_port_transparent(tn,Epon_PonID, Epon_OnuID,Ont_Port_ID)
    with allure.step('步骤4:在OLT配置ONU的service-port。'):
        assert add_service_port(tn, Epon_PonID, Epon_OnuID, Vlan_list)

    with allure.step('步骤6:打流测试。'):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(8)
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
            'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.0.11 ipv4_1.destination=192.168.0.21',)

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.0.21 ipv4_1.destination=192.168.0.11',)
        # 获取所有流量的统计值
        result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header,
                                 up_stream_header=up_stream_header,
                                 packet_name=current_dir_name + '_' + sys._getframe().f_code.co_name,
                                 rate=100,
                                 duration=duration)
        # cdata_info(result_stats[0].__dict__)
        # cdata_info(result_stats[1].__dict__)
        # if rate == 10:
        #     # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
        #     #onu端口为1000M，上下行都发送端口速率的10%，也就是100M,DBA上行限50M,所以下行比例是（100/100）=1， 上行是（50/100）=0.5
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.5)
        # elif rate ==100:
        #     # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,DBA上行限50M,所以下行比例是（100/100）=1， 上行是（50/1000）=0.05
        #     result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.05,outbound_percent=1)

        if port2_speed == 'SPEED_100M' and port1_speed == 'SPEED_100M':
            # onu端口为1000M，上下行都发送端口速率的100%，也就是100M,onu端口下行限10M,所以下行比例是（10/100）=0.1， 上行是（100/100）=1
            result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.5, outbound_percent=1)
        elif port2_speed == 'SPEED_100M' and port1_speed == 'SPEED_1G':
            # onu端口为1000M，上下行都发送端口速率的10%，也就是100M,onu端口下行限10M,所以下行比例是（10/100）=0.1， 上行是（100/100）=1
            result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.05, outbound_percent=1)
        elif port2_speed == 'SPEED_1G' and port1_speed == 'SPEED_100M':
            # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限10M,所以下行比例是（10/1000）=0.01， 上行是（100/100）=1
            result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.5, outbound_percent=0.1)
        elif port2_speed == 'SPEED_1G' and port1_speed == 'SPEED_1G':
            # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限10M,所以下行比例是（10/1000）=0.01， 上行是（100/100）=1
            result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.05, outbound_percent=1)

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



if __name__ == '__main__':
    # for i in range(5):
    pytest.main(['-v',"-s",'test_onu_limitrate.py'])
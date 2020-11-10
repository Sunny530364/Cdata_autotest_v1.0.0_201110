#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

import pytest
from src.xinertel.unicast_hgu import *
from src.Gpon_HGU.limitrate import *
from src.Gpon_HGU.ont_auth import *
from tests.FD1616GS_HGU.initialization_config import *
from src.Gpon_HGU.omci_wan import *
from src.xinertel.renix_test import *
import allure


@pytest.fixture(scope='function')
def dba_limitrate_suit(login):
    tn=login
    with allure.step('步骤3:配置dba模板'):
        assert dba_limitrate_type5(tn, dba_profile_id=Dba_Profile_ID)
    yield tn
    with allure.step('步骤6:dba模板恢复默认配置type4 max1024000'):
        assert dba_limitrate_type4(tn, dba_profile_id=Dba_Profile_ID)


@allure.feature("onu限速测试")
@allure.story("dba限速测试")
@allure.title("测试dba限速(type4)")
@pytest.mark.run(order=1014)
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

    # tn=login
    # #配置dba模板
    # dba_limitrate_type5(tn, dba_profile_id=100)
    cdata_info("=========DBA限速测试=========")
    tn = dba_limitrate_suit
    Vlan_list = [2000]
    with allure.step('步骤1:发现未注册的ONU。'):
        assert autofind_onu(tn, Gpon_PonID,  Gpon_OnuID, Gpon_SN)
    with allure.step('步骤2:在OLT上通过SN的方式将ONU注册上线。'):
        assert auth_by_sn(tn ,Gpon_PonID, Gpon_OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, Gpon_SN)
    with allure.step('步骤4:添加虚端口vlan透传2000'):
        assert add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Vlan_list)
    with allure.step('步骤4:添加omci_wan配置'):
        assert add_omci_wan_bridge_tag(tn, Gpon_PonID, Gpon_OnuID, WAN_ID, WAN_service_type, '2000', '0',  ETH_list, SSID_list, SSID_5g_list)
        time.sleep(10)
    # with allure.step('步骤5:测试仪发送双向100000个报文'):
    #     assert stream_test(stream_rate, stream_num, download_capture_num, port_location)
    with allure.step('步骤5:打流测试。'):
        # 清除测试仪的对象，防止影响下个用例的执行
        time.sleep(8)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        ont_speed = check_ont_capability(tn, ponid=Gpon_PonID, ontid=Gpon_OnuID, ethid=Ont_Port_ID)
        if ont_speed == "FE":
            rate = 100
        else:
            rate = 10
        # 发流量测试，上下行发送流量，速率为100M
        #port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
        duration = 10
        down_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:22:11:11  ethernetII_1.destMacAdd=00:00:00:11:22:22 ipv4_1.source=192.168.111.111 ipv4_1.destination=192.168.111.222',)

        up_stream_header = (
            'ethernetII_1.sourceMacAdd=00:00:00:11:22:22  ethernetII_1.destMacAdd=00:00:00:22:11:11 ipv4_1.source=192.168.111.222 ipv4_1.destination=192.168.111.111',)
        # 获取所有流量的统计值
        result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header,
                                 up_stream_header=up_stream_header,
                                 rate=rate,
                                 duration=duration)
        #cdata_info(result_stats[0].__dict__)
        #cdata_info(result_stats[1].__dict__)
        if rate == 10:
            # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
            #onu端口为1000M，上下行都发送端口速率的10%，也就是100M,DBA上行限50M,所以下行比例是（100/100）=1， 上行是（50/100）=0.5
            result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.5)
        elif rate ==100:
            # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,DBA上行限50M,所以下行比例是（100/100）=1， 上行是（50/1000）=0.05
            result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=0.05,outbound_percent=1)

        # for i in range(2):
        #     if (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:11':
        #         result11 = check_stream_rate1(result_stats[i],percent=1)
        #     elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:21':
        #         result21 = check_stream_rate1(result_stats[i],percent=0.5)

        # #dba模板恢复默认配置
        # dba_limitrate_type4(tn, dba_profile_id=100)

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
    pytest.main(['-v',"-s" ,'-x', 'test_onu_limitrate.py'] )



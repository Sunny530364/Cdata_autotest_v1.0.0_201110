#!/usr/bin/python
# -*- coding UTF-8 -*-

# author: ZHONGQI

from renix_py_api import renix
import logging
import time
import re

import sys, os
from os.path import dirname, abspath
import scapy
from scapy.all import *
from scapy.utils import  PcapReader

sys.path.append(os.path.dirname(os.path.dirname(abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(abspath(__file__)))))

renix.initialize(log_level=logging.INFO)
from renix_py_api.api_gen import *
from renix_py_api.rom_manager import *
from renix_py_api.core import EnumRelationDirection
from src.config.Cdata_loggers import *

# 变量port的端口速率
port1_speed = 'SPEED_1G'
port2_speed = 'SPEED_1G'
packet_folder_path = 'C:\CDATA_AUTOTEST_PACKETS'
MaxDownloadCount = 1000

#捕获的文件名（废弃）
def captures_filename():
    # 当前文件的绝对路径
    script_path = os.path.abspath(sys.argv[0])
    print(script_path)

    if os.path.isfile(script_path):
        current_path_1, current_file_name_ext = os.path.split(script_path)
        # print(current_path_1, current_file_name_ext)
        current_file_name, extention_name = current_file_name_ext.split('.')

    packet_folder_path1 = os.path.join(current_path_1, "packets")
    # 如果不存在packet文件夹，则在当前目录下创建packet文件夹
    if not os.path.exists(packet_folder_path1):
        os.makedirs(packet_folder_path1)

    # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
    # log的文件名称
    # file_name = "%s_%s.pcap" % (current_file_name, '_'.join(port_location[1].split('/')[2:]))
    # capture_file_path = os.path.join(log_folder_path, file_name)
    # print(capture_file_path)
    return packet_folder_path1

#测试仪预约端口并使端口上线
def create_ports(sys_entry, location):
    '''
    连接测试仪，预约端口并且使端口上线
    :param sys_entry:创建测试仪的根节点
    :param location: 存放端口
    :return:port
    '''
    renix_info('create ports with location:'.format(location))
    port1 = Port(upper=sys_entry, location=location[0])
    port2 = Port(upper=sys_entry, location=location[1])
    assert port1.handle
    assert port2.handle
    bring_port_online_cmd = BringPortsOnlineCommand(portlist=[port1.handle, port2.handle])
    bring_port_online_cmd.execute()
    if not wait_port_online(port1):
        raise Exception('bring online port({}) failed'.format(port1.handle))
    if not wait_port_online(port2):
        raise Exception('bring online port({}) failed'.format(port2.handle))
    return port1, port2

#创建流
def create_stream(port, name, rate, stream_header,packet_length=1024):
    '''
    create stream,add header,'_HeaderTypes': ['ARP.arp', 'Custom.custom', 'DHCPv4.dhcpv4Client', 'DHCPv4.dhcpv4Server',
    'DHCPv6.dhcpv6Client', 'DHCPv6.dhcpv6Server', 'Ethernet.ethernetII', 'Ethernet.8023', 'Goose.goose', 'GRE.gre',
     'GTPv1.gtpv1', 'GTPv1.gtpv1Opt', 'GTPv1Ext.gtpv1Ext', 'GTPv1Ext.gtpv1ExtHdr', 'IGMP.igmpv1', 'IGMP.igmpv2',
     'IGMP.igmpv3Report', 'IGMP.igmpv3Query', 'IGMP.igmpv1Query', 'IGMP.igmpv2Query', 'IPv4.ipv4', 'IPv6.ipv6',
     'ICMPv4.destUnreach', 'ICMPv4.echoReply', 'ICMPv4.echoRequest', 'ICMPv4.informationReply',
      'ICMPv4.informationRequest', 'ICMPv4.parameterProblem', 'ICMPv4.redirect', 'ICMPv4.sourceQuench',
      'ICMPv4.timeExceeded', 'ICMPv4.timestampReply', 'ICMPv4.timestampRequest', 'ICMPv4.icmpMaskRequest',
      'ICMPv4.icmpMaskReply', 'ICMPv6.destinationUnreachable', 'ICMPv6.echoReply', 'ICMPv6.echoRequest',
      'ICMPv6.packetTooBig', 'ICMPv6.parameterProblem', 'ICMPv6.timeExceed', 'ICMPv6.routerSolicit',
      'ICMPv6.routerAdvertise', 'ICMPv6.neighborSolicit', 'ICMPv6.neighborAdvertise', 'L2TPv3.l2tpv3ControlOverIp',
       'L2TPv3.l2tpv3ControlOverUdp', 'L2TPv3.l2tpv3DataOverIp', 'L2TPv3.l2tpv3DataOverUdp', 'L2TPv2.l2tpv2Control',
       'L2TPv2.l2tpv2Data', 'MPLS.mpls', 'Pause.pause', 'PPP.ppp', 'PPPoE.pppoeDiscovery', 'PPPoE.pppoe', 'TCP.tcp',
        'UDP.udp', 'VLAN.vlan', 'VXLAN.vxlan', 'CHDLC.chdlc']
    :param port: 在port上创建数据流
    :param packet_length: 报文的长度
    :return: stream
    '''
    #['Ethernet.ethernetII', 'VLAN.vlan', 'IPv4.ipv4', 'UDP.udp']
    renix_info('port({}) create streams'.format(port.Location))

    stream = StreamTemplate(upper=port, Name=name)
    assert stream.handle
    # 配置每条流的速率
    stream_template_load_profile = stream.get_children('StreamTemplateLoadProfile')[0]

    stream_template_load_profile.edit(Unit=EnumFrameLoadUnit.PERCENT, Rate=rate)
    # 配置流的报头

    create_stream_header_cmd = CreateHeaderCommand(stream.handle, stream_header)
    create_stream_header_cmd.execute()
    # 获取header的配置方法
    # list_instance_leaf_cmd = ListInstanceLeafCommand(stream.handle, Deep=True)
    # list_instance_leaf_cmd.execute()
    # print(list_instance_leaf_cmd.__dict__)

    if len(create_stream_header_cmd.HeaderNames) != len(stream_header):
        raise Exception('{} create EthernetII and IPv4 header failed'.format(stream.handle))
    stream.FixedLength = packet_length
    stream.get()

    return stream

#编辑流
def edit_stream(stream, parameter):
    '''
    编辑流量，
    :param stream:
    :param parameter:需要修改的数据流的参数，字符串类型，举例：'ethernetII_1.destMacAdd=01:00:5e:02:02:02 ipv4_1.destination=239.2.2.2'
    '_Stream': 'StreamTemplate_1', '_ParentName': None, '_Deep': True, '_Leaves': ['ethernetII_1', 'ethernetII_1.destMacAdd',
    'ethernetII_1.sourceMacAdd', 'ethernetII_1.protocolType', 'vlan_1', 'vlan_1.priority', 'vlan_1.cfi', 'vlan_1.id', 'vlan_1.protocol',
    'ipv4_1', 'ipv4_1.version', 'ipv4_1.headLen', 'ipv4_1.tos', 'ipv4_1.tos.tos', 'ipv4_1.tos.tos.precedence', 'ipv4_1.tos.tos.delay',
    'ipv4_1.tos.tos.throughput', 'ipv4_1.tos.tos.reliability', 'ipv4_1.tos.tos.monetaryCost', 'ipv4_1.tos.tos.reserved', 'ipv4_1.tos.diffServe',
     'ipv4_1.tos.diffServe.dscp', 'ipv4_1.tos.diffServe.dscp.codePoint', 'ipv4_1.tos.diffServe.dscp.codePoint.precedence',
     'ipv4_1.tos.diffServe.dscp.classSelector', 'ipv4_1.tos.diffServe.dscp.classSelector.precedence', 'ipv4_1.tos.diffServe.dscp.classSelector.drop',
      'ipv4_1.tos.diffServe.dscp.classSelector.undefine', 'ipv4_1.tos.diffServe.ecnSetting', 'ipv4_1.totalLength', 'ipv4_1.id', 'ipv4_1.flags',
       'ipv4_1.offset', 'ipv4_1.ttl', 'ipv4_1.protocol', 'ipv4_1.checksum', 'ipv4_1.source', 'ipv4_1.destination', 'ipv4_1.ipv4HeaderOption',
       'ipv4_1.padding', 'ipv4_1.gateway', 'udp_1', 'udp_1.sourcePort', 'udp_1.destPort', 'udp_1.length', 'udp_1.checksum'],
       '_CommandState': <ROMCommandStateEnum.INIT: 0>, '_AutoDelete': None, '_StartTime': '', '_ElapsedTime': '', '_Name': None,
       '_Enable': None, '_ROMTag': None, 'force_auto_sync': False, 'args': ['-Stream StreamTemplate_1', '-Deep True'], 'show_return_value': False
    :return:
    '''
    update_header_cmd = UpdateHeaderCommand(Stream=stream.handle, Parameter=parameter)
    update_header_cmd.execute()
    stream.get()
    return stream

#判断端口是否上线
def wait_port_online(port, times=10):
    '''
    判断端口是否上线
    :param port:
    :param times:
    :return: True or False
    '''
    port.set_force_auto_sync(True)
    while times:
        if port.Online:
            return True
        else:
            times -= 1
            time.sleep(1)
    else:
        return False

#添加接口
def add_interface(port):
    '''
    add interface
    :param port: 添加port的interface，这里添加的是ipv4接口,也可以添加以太网接口，或者ipv6接口
    :return: interface
    '''
    interface = Interface(upper=port)
    build_ipv4 = BuildInterfaceCommand(InterfaceList=interface.Name, NetworkLayers=['eth', 'ipv4'])
    build_ipv4.execute()
    interface.get()
    return interface

#编辑流分类模式
def edit_streamconfig(port):
    '''
    编辑流分类模式
    :param port:
    :return: None
    '''
    stream_port_config = port.get_children('StreamPortConfig')[0]
    stream_port_config.edit(LoadProfileType=EnumLoadProfileType.STREAM_BASE)
    stream_load_profile = stream_port_config.get_children('StreamLoadProfile')[0]
    stream_load_profile.edit(Unit=EnumRateUnit.FRAME_PER_SEC)
    return stream_load_profile

#增加统计视图
def add_view(dataclassname):
    '''
    添加统计视图
    :param dataclassname:
    :return:
    '''
    resultview = ResultView(upper=sys_entry, DataClassName=dataclassname)
    resultquery = ResultQuery(upper=resultview)
    SubscribeResultCommand(ResultViewHandles=resultview.handle).execute()
    CommitCommand().execute()
    return resultquery

#添加统计视图
def creat_view(sys_entry, dataclassname=StreamBlockStats):
    # create result view
    # DataClassName can be PortStats|StreamStats|StreamTxStats|StreamRxStats|StreamblockStats|StreamblockTxStats|StreamblockRxStats
    resultView_create = CreateResultViewCommand(DataClassName=dataclassname.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
   # sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]
    return page_result_view

#预发流
def pre_start_stream():
    # Pre-Start stream
    startallstream = StartAllStreamCommand()
    startallstream.execute()
    time.sleep(2)
    stopallstream = StopAllStreamCommand()
    stopallstream.execute()

#开始发流测试
def start_stream(duration):
    # Start stream and stop stream
    startallstream = StartAllStreamCommand()
    startallstream.execute()
    time.sleep(duration)
    stopallstream = StopAllStreamCommand()
    stopallstream.execute()

#检测基于端口的报文统计（正常通的情况）
def check_port_static(port1_stats, port2_stats):
    '''判断对发端口，两个端口frame统计情况，验证报文通的情况'''
    # check  port1_stats rx equal to tx
    verdict = 'PASS'
    errInfo = []
    port1 = (port1_stats.__dict__)['_PortID']
    port2 = (port2_stats.__dict__)['_PortID']
    if port1_stats.RxTotalFrames == 0 or port1_stats.TxTotalFrames == 0 or port2_stats.TxTotalFrames == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({}) or [{}] tx packets ({}) is 0 or [{}] tx packets ({})is 0'.
                format(port1, port1_stats.RxTotalFrames, port1, port1_stats.TxTotalFrames, port2,
                       port2_stats.TxTotalFrames))
    elif (port1_stats.RxTotalFrames / port2_stats.TxTotalFrames) < 0.99:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({})is not equal to  port2_stats tx packets ({})'.format(port1,
                                                                                                 port1_stats.RxTotalFrames,
                                                                                                 port2_stats.TxTotalFrames))
    else:
        renix_info('[test pass] [{}] rx packet ({})is  equal to port2_stats tx packets ({})'.format(port1,
                                                                                                    port1_stats.RxTotalFrames,
                                                                                                    port2_stats.TxTotalFrames))

    # check  port2_stats rx equal to tx
    if port2_stats.TxTotalFrames == 0 or port2_stats.RxTotalFrames == 0 or port1_stats.TxTotalFrames == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({}) or [{}]tx packets ({}) is 0 or [{}] tx packets ({})'.format(port2,
                                                                                                         port2_stats.RxTotalFrames,
                                                                                                         port2,
                                                                                                         port2_stats.TxTotalFrames,
                                                                                                         port1,
                                                                                                         port1_stats.TxTotalFrames))
    elif port2_stats.RxTotalFrames / port1_stats.TxTotalFrames < 0.99:
        verdict = 'fail'
        renix_error(
            '[test fail] [{}] rx packet ({})is not equal to  port1_stats tx packets ({})'.format(port2,
                                                                                                 port2_stats.RxTotalFrames,
                                                                                                 port1_stats.TxTotalFrames))
    else:
        renix_info('[test pass] [{}] rx packet ({})is equal to  port1_stats tx packets ({})'.format(port2,
                                                                                                    port2_stats.RxTotalFrames,
                                                                                                    port1_stats.TxTotalFrames))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

#检测基于流的报文统计（正常不通的情况），判断对发的两条流的情况
def check_stream_loss(stream1_2_stats, stream2_1_stats):
    '''判断对发流量，两条流frame统计情况，验证报文不通的情况'''
    verdict = 'PASS'
    errInfo = []
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']
    name2_1 = (stream2_1_stats.__dict__)['_StreamBlockID']
    # check  loss packet
    # 如果发送报文不为0，接收报文的丢包等于发送报文的个数，则判断改报文不通
    # _RxLossStreamFrames没有数据
    if stream1_2_stats.TxStreamFrames != 0 and stream1_2_stats.LostStreamFrames == stream1_2_stats.TxStreamFrames:
        renix_info(
            '[test Pass] [{}] realtime loss packet ({})is  equal to  tx packet({})'.format(name1_2,
                                                                                           stream1_2_stats.LostStreamFrames,
                                                                                           stream1_2_stats.TxStreamFrames))
    else:
        verdict = 'FAIL'
        renix_error('[test fail] [{}] realtime loss packet ({})is not equal to tx packet({}) '.format(name1_2,
                                                                                                      stream1_2_stats.RxLossStreamFrames,
                                                                                                      stream1_2_stats.TxStreamFrames))

    if stream2_1_stats.TxStreamFrames != 0 and stream2_1_stats.LostStreamFrames == stream2_1_stats.TxStreamFrames:
        renix_info(
            '[test Pass] [{}] realtime loss packet ({})is  equal to  tx packet({})'.format(name2_1,
                                                                                           stream2_1_stats.LostStreamFrames,
                                                                                           stream2_1_stats.TxStreamFrames))
    else:
        verdict = 'FAIL'
        renix_error('[test fail] [{}] realtime loss packet ({})is not equal to  tx packet({}) '.format(name2_1,
                                                                                                       stream2_1_stats.LostStreamFrames,
                                                                                                       stream2_1_stats.TxStreamFrames))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

#检测基于流的报文统计（正常不通的情况），判断单条流的情况
def check_stream_loss1(stream1_2_stats, ):
    '''判断对发流量，两条流frame统计情况，验证报文不通的情况'''
    verdict = 'PASS'
    errInfo = []
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']
    # check  loss packet
    # 如果发送报文不为0，接收报文的丢包等于发送报文的个数，则判断改报文不通
    # _RxLossStreamFrames没有数据
    if stream1_2_stats.TxStreamFrames != 0 and stream1_2_stats.LostStreamFrames == stream1_2_stats.TxStreamFrames:
        renix_info(
            '[test Pass] [{}]rx({}), realtime loss packet ({})is  equal to  tx packet({})'.format(name1_2,
                                                                                                  stream1_2_stats.RxStreamFrames,
                                                                                                  stream1_2_stats.LostStreamFrames,
                                                                                                  stream1_2_stats.TxStreamFrames))
    else:
        verdict = 'FAIL'
        renix_error('[test fail] [{}]rx({}), realtime loss packet ({})is not equal to tx packet({}) '.format(name1_2,
                                                                                                             stream1_2_stats.RxStreamFrames,
                                                                                                             stream1_2_stats.RxLossStreamFrames,
                                                                                                             stream1_2_stats.TxStreamFrames))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

#检测基于流的报文统计（正常通的情况），判断对发的两条流的情况
def check_stream_static(stream1_2_stats, stream2_1_stats):
    '''判断对发流量，两条流frame统计情况，验证通的情况'''
    verdict = 'PASS'
    errInfo = []
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']
    name2_1 = (stream2_1_stats.__dict__)['_StreamBlockID']
    print(stream1_2_stats.__dict__)
    print(stream2_1_stats.__dict__)
    # 如果流量发送和接收都不为0，and 接收报文达到发送报文的99%以上，丢包为0，则判断流量正常
    # check rx equal to tx
    if stream1_2_stats.RxStreamFrames == 0 or stream1_2_stats.TxStreamFrames == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({}) or tx packets ({}) is 0'.format(name1_2, stream1_2_stats.RxStreamFrames,
                                                                             stream1_2_stats.TxStreamFrames))
    elif stream1_2_stats.RxStreamFrames / stream1_2_stats.TxStreamFrames < 0.99:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({})is not equal to  tx packets ({})'.format(name1_2,
                                                                                     stream1_2_stats.RxStreamFrames,
                                                                                     stream1_2_stats.TxStreamFrames))
    else:
        renix_info('[test pass] [{}] rx packet ({})is  equal to tx packets ({})'.format(name1_2,
                                                                                        stream1_2_stats.RxStreamFrames,
                                                                                        stream1_2_stats.TxStreamFrames))

    if stream2_1_stats.RxStreamFrames == 0 or stream2_1_stats.TxStreamFrames == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({}) or tx packets ({}) is 0'.format(name2_1, stream2_1_stats.RxStreamFrames,
                                                                             stream2_1_stats.TxStreamFrames))
    elif stream2_1_stats.RxStreamFrames / stream2_1_stats.TxStreamFrames < 0.99:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({})is not equal to  tx packets ({})'.format(name2_1,
                                                                                     stream2_1_stats.RxStreamFrames,
                                                                                     stream2_1_stats.TxStreamFrames))
    else:
        renix_info('[test pass] [{}] rx packet ({})is  equal to tx packets ({})'.format(name2_1,
                                                                                        stream2_1_stats.RxStreamFrames,
                                                                                        stream2_1_stats.TxStreamFrames))
    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

#检测基于流的报文统计（正常通的情况），判断单条流的情况
def check_stream_static1(stream1_2_stats):
    '''判断对发流量，两条流frame统计情况，验证通的情况'''
    verdict = 'PASS'
    errInfo = []
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']

    # 如果流量发送和接收都不为0，and 接收报文达到发送报文的99%以上，丢包为0，则判断流量正常
    # check rx equal to tx
    if stream1_2_stats.RxStreamFrames == 0 or stream1_2_stats.TxStreamFrames == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({}) or tx packets ({}) is 0'.format(name1_2, stream1_2_stats.RxStreamFrames,
                                                                             stream1_2_stats.TxStreamFrames))
    elif stream1_2_stats.RxStreamFrames / stream1_2_stats.TxStreamFrames < 0.99:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({})is not equal to  tx packets ({})'.format(name1_2,
                                                                                     stream1_2_stats.RxStreamFrames,
                                                                                     stream1_2_stats.TxStreamFrames))
    else:
        renix_info('[test pass] [{}] rx packet ({})is  equal to tx packets ({})'.format(name1_2,
                                                                                        stream1_2_stats.RxStreamFrames,
                                                                                        stream1_2_stats.TxStreamFrames))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

#检测基于流的速率（正常通的情况,onu出口），判断对发的两条流的情况
def check_stream_rate_outbound(stream1_2_stats, stream2_1_stats, limit_rate):
    '''判断对发流量，两条流速率统计情况，验证报文不通的情况'''
    verdict = 'PASS'
    errInfo = []
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']
    name2_1 = (stream2_1_stats.__dict__)['_StreamBlockID']
    # (stream1_2_stats.TxUtil)*0.99<= stream1_2_stats.RxUtil <= (stream1_2_stats.TxUtil)*1.01
    # (stream1_2_stats.TxUtil) * 0.99 >= stream1_2_stats.RxUtil or stream1_2_stats.RxUtil >= (stream1_2_stats.TxUtil)*1.01
    print(port1_speed,port2_speed)

    if port2_speed == 'SPEED_100M' and port1_speed == 'SPEED_100M':
        # onu端口为1000M，上下行都发送端口速率的100%，也就是100M,onu端口下行限10M,所以下行比例是（10/100）=0.1， 上行是（100/100）=1
        inbound_percent = (102400/102400)
        outbound_percent = (int(limit_rate)/102400)
    elif port2_speed == 'SPEED_100M' and port1_speed == 'SPEED_1G':
        # onu端口为1000M，上下行都发送端口速率的10%，也就是100M,onu端口下行限10M,所以下行比例是（10/100）=0.1， 上行是（100/100）=1
        inbound_percent=0.1
        #outbound_percent=0.2
        outbound_percent = (int(limit_rate)/102400)
    elif port2_speed == 'SPEED_1G' and port1_speed == 'SPEED_100M':
        # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限10M,所以下行比例是（10/1000）=0.01， 上行是（100/100）=1
        inbound_percent=1
        #outbound_percent=0.02
        outbound_percent = (int(limit_rate)/1024000)
    elif port2_speed == 'SPEED_1G' and port1_speed == 'SPEED_1G':
        # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限10M,所以下行比例是（10/1000）=0.01， 上行是（100/100）=1
        inbound_percent=1
        #outbound_percent=0.02
        outbound_percent = (int(limit_rate) / 1024000)

    if stream1_2_stats.RxUtil == 0 or stream1_2_stats.TxUtil == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({}) or tx rate ({}) is 0'.format(name1_2, stream1_2_stats.RxUtil,
                                                                        stream1_2_stats.TxUtil))
    elif ((stream1_2_stats.TxUtil) * outbound_percent) * 0.9 >= stream1_2_stats.RxUtil or \
            stream1_2_stats.RxUtil >= ((stream1_2_stats.TxUtil) * outbound_percent) * 1.1:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({})is not equal to  tx rate ({})* {}'.format(name1_2,
                                                                                    stream1_2_stats.RxUtil,
                                                                                    stream1_2_stats.TxUtil,
                                                                                    outbound_percent))
    else:
        renix_info('[test pass] [{}] rx rate ({})is  equal to tx rate ({}) * {}'.format(name1_2, stream1_2_stats.RxUtil,
                                                                                        stream1_2_stats.TxUtil,
                                                                                        outbound_percent))

    if stream2_1_stats.RxUtil == 0 or stream2_1_stats.TxUtil == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({}) or tx rate ({}) is 0'.format(name2_1, stream2_1_stats.RxUtil,
                                                                        stream2_1_stats.TxUtil))
    elif ((stream2_1_stats.TxUtil * inbound_percent)) * 0.9 >= stream2_1_stats.RxUtil or \
            stream2_1_stats.RxUtil >= ((stream2_1_stats.TxUtil) * inbound_percent) * 1.1:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({})is not equal to  tx rate ({}) * {}'.format(name2_1,
                                                                                     stream2_1_stats.RxUtil,
                                                                                     stream2_1_stats.TxUtil,
                                                                                     inbound_percent))
    else:
        renix_info('[test pass] [{}] rx rate ({})is  equal to tx rate ({}) * {}'.format(name2_1, stream2_1_stats.RxUtil,
                                                                                        stream2_1_stats.TxUtil,
                                                                                        inbound_percent))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

#检测基于流的速率（正常通的情况，onu入口），判断对发的两条流的情况
def check_stream_rate_inbound(stream1_2_stats, stream2_1_stats, limit_rate):
    '''判断对发流量，两条流速率统计情况，验证报文不通的情况'''
    verdict = 'PASS'
    errInfo = []
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']
    name2_1 = (stream2_1_stats.__dict__)['_StreamBlockID']
    # (stream1_2_stats.TxUtil)*0.99<= stream1_2_stats.RxUtil <= (stream1_2_stats.TxUtil)*1.01
    # (stream1_2_stats.TxUtil) * 0.99 >= stream1_2_stats.RxUtil or stream1_2_stats.RxUtil >= (stream1_2_stats.TxUtil)*1.01


    if port2_speed == 'SPEED_100M' and port1_speed == 'SPEED_100M':
        # onu端口为1000M，上下行都发送端口速率的100%，也就是100M,onu端口下行限10M,所以下行比例是（10/100）=0.1， 上行是（100/100）=1
        inbound_percent=(int(limit_rate)/102400)
        outbound_percent=1
    elif port2_speed == 'SPEED_100M' and port1_speed == 'SPEED_1G':
        # onu端口为1000M，上下行都发送端口速率的10%，也就是100M,onu端口下行限10M,所以下行比例是（10/100）=0.1， 上行是（100/100）=1
        inbound_percent=(int(limit_rate)/1024000)
        outbound_percent=1
    elif port2_speed == 'SPEED_1G' and port1_speed == 'SPEED_100M':
        # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限10M,所以下行比例是（10/1000）=0.01， 上行是（100/100）=1
        inbound_percent=(int(limit_rate)/102400)
        outbound_percent=0.1
    elif port2_speed == 'SPEED_1G' and port1_speed == 'SPEED_1G':
        # onu端口为100M，上下行都发送端口速率的100%，也就是下行1000M,上行100M,onu端口下行限10M,所以下行比例是（10/1000）=0.01， 上行是（100/100）=1
        inbound_percent=(int(limit_rate)/1024000)
        outbound_percent=1

    if stream1_2_stats.RxUtil == 0 or stream1_2_stats.TxUtil == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({}) or tx rate ({}) is 0'.format(name1_2, stream1_2_stats.RxUtil,
                                                                        stream1_2_stats.TxUtil))
    elif ((stream1_2_stats.TxUtil) * outbound_percent) * 0.9 >= stream1_2_stats.RxUtil or \
            stream1_2_stats.RxUtil >= ((stream1_2_stats.TxUtil) * outbound_percent) * 1.1:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({})is not equal to  tx rate ({})* {}'.format(name1_2,
                                                                                    stream1_2_stats.RxUtil,
                                                                                    stream1_2_stats.TxUtil,
                                                                                    outbound_percent))
    else:
        renix_info('[test pass] [{}] rx rate ({})is  equal to tx rate ({}) * {}'.format(name1_2, stream1_2_stats.RxUtil,
                                                                                        stream1_2_stats.TxUtil,
                                                                                        outbound_percent))

    if stream2_1_stats.RxUtil == 0 or stream2_1_stats.TxUtil == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({}) or tx rate ({}) is 0'.format(name2_1, stream2_1_stats.RxUtil,
                                                                        stream2_1_stats.TxUtil))
    elif ((stream2_1_stats.TxUtil * inbound_percent)) * 0.9 >= stream2_1_stats.RxUtil or \
            stream2_1_stats.RxUtil >= ((stream2_1_stats.TxUtil) * inbound_percent) * 1.1:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({})is not equal to  tx rate ({}) * {}'.format(name2_1,
                                                                                     stream2_1_stats.RxUtil,
                                                                                     stream2_1_stats.TxUtil,
                                                                                     inbound_percent))
    else:
        renix_info('[test pass] [{}] rx rate ({})is  equal to tx rate ({}) * {}'.format(name2_1, stream2_1_stats.RxUtil,
                                                                                        stream2_1_stats.TxUtil,
                                                                                        inbound_percent))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

#检测基于流的速率（正常通的情况），判断单条流的情况
def check_stream_rate1(stream1_2_stats, percent=1):
    '''判断对发流量，两条流速率统计情况，验证报文不通的情况'''
    verdict = 'PASS'
    errInfo = []
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']
    # (stream1_2_stats.TxUtil)*0.99<= stream1_2_stats.RxUtil <= (stream1_2_stats.TxUtil)*1.01
    # (stream1_2_stats.TxUtil) * 0.99 >= stream1_2_stats.RxUtil or stream1_2_stats.RxUtil >= (stream1_2_stats.TxUtil)*1.01

    if stream1_2_stats.RxUtil == 0 or stream1_2_stats.TxUtil == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({}) or tx rate ({}) is 0'.format(name1_2, stream1_2_stats.RxUtil,
                                                                        stream1_2_stats.TxUtil))
    elif ((stream1_2_stats.TxUtil) * percent) * 0.9 >= stream1_2_stats.RxUtil or \
            stream1_2_stats.RxUtil >= ((stream1_2_stats.TxUtil) * percent) * 1.1:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({})is not equal to  tx rate ({})* {}'.format(name1_2,
                                                                                    stream1_2_stats.RxUtil,
                                                                                    stream1_2_stats.TxUtil, percent))
    else:
        renix_info('[test pass] [{}] rx rate ({})is  equal to tx rate ({}) * {}'.format(name1_2, stream1_2_stats.RxUtil,
                                                                                        stream1_2_stats.TxUtil,
                                                                                        percent))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

#速率测试用例
def rate_test(port_location, down_stream_header, up_stream_header, packet_name, rate=10, duration=10,
              stream_header=['Ethernet.ethernetII', 'VLAN.vlan', 'IPv4.ipv4', 'UDP.udp']):
    # 定义变量
    sys_entry = get_sys_entry()

    # 预约端口
    port1, port2 = create_ports(sys_entry, port_location)

    packet_name = packet_name + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')
    packet_child_dir = []
    for i in range(len(port_location)):
        res1 = re.split(r'[//.////]+', port_location[i])
        res2 = '_'.join(res1[1:])
        packet_child_dir.append(res2)

    # 查看测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed)))
    cdata_info("===========================================================================")

    global port1_speed,port2_speed
    port1_speed = (str(port1.get_children('EthCopper')[0].LineSpeed).split('.'))[1]
    port2_speed = (str(port2.get_children('EthCopper')[0].LineSpeed).split('.'))[1]

    # 修改端口流发送模式
    edit_streamconfig(port1)
    edit_streamconfig(port2)

    # 编辑流
    port1_stream_header = down_stream_header
    port2_stream_header = up_stream_header
    name1 = re.findall(r'sourceMacAdd=\d+:\d+:\d+:\d+:\d+:\d+', port1_stream_header[0])[0]
    name2 = re.findall(r'sourceMacAdd=\d+:\d+:\d+:\d+:\d+:\d+', port2_stream_header[0])[0]
    # 创建流模板
    stream1 = create_stream(port1, name1, rate, stream_header)
    stream2 = create_stream(port2, name2, rate, stream_header)

    # 编辑流
    edit_stream(stream1, port1_stream_header[0])
    edit_stream(stream2, port2_stream_header[0])
    # config rx port
    stream1.set_relatives('Rxport', port2, EnumRelationDirection.TARGET)
    stream2.set_relatives('Rxport', port1, EnumRelationDirection.TARGET)

    # create result view
    page_result_view = creat_view(sys_entry=sys_entry, dataclassname=StreamBlockStats)
    # Pre-Start stream
    pre_start_stream()
    # Clear statistic
    result_clear_cmd = ClearResultCommand(ResultViewHandles=page_result_view.handle)
    result_clear_cmd.execute()

    # 报文捕获配置
    cap_conf_1 = port1.get_children('CaptureConfig')[0]
    cap_conf_2 = port2.get_children('CaptureConfig')[0]
    # 设置捕获端口接收的报文
    # cap_conf_1.edit(CaptureMode=EnumCaptureMode.ALL)
    # cap_conf_2.edit(CaptureMode=EnumCaptureMode.ALL)
    # cap_conf_1.edit(CaptureMode=EnumCaptureMode.ALL, CacheCapacity=EnumCacheCapacity.Cache_64KB,
    #                 FilterMode=EnumFilterMode.NONE, BufferFullAction=EnumBufferFullAction.WRAP, StartingFrameIndex=10,
    #                 AttemptDownloadPacketCount=1000)
    # cap_conf_2.edit(CaptureMode=EnumCaptureMode.ALL, CacheCapacity=EnumCacheCapacity.Cache_64KB,
    #                 FilterMode=EnumFilterMode.NONE, BufferFullAction=EnumBufferFullAction.WRAP, StartingFrameIndex=10,
    #                 AttemptDownloadPacketCount=1000)

    for i in range(5):
        cdata_info(
            '第%d次查看状态：port1的端口状态：%s ;port2的端口状态：%s' % ((i + 1), port1.get_children('EthCopper')[0]._LinkStatus._name_,
                                                       port2.get_children('EthCopper')[0]._LinkStatus._name_))
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':

            # 开始捕获
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            cdata_debug('测试仪开启端口的报文捕获')

            # Start stream
            cdata_debug('测试仪端口开始发流')
            startallstream = StartAllStreamCommand()
            startallstream.execute()
            time.sleep(duration)
            cdata_debug('测试仪端口打流结束')
            # get stream statistic
            result_query = page_result_view.get_children()[0]
            stream_stats = result_query.get_children('StreamBlockStats')
            cdata_debug('获取测试仪流量统计值')

            # 停止测试仪接口抓包
            stop_all_cap_cmd = StopAllCaptureCommand()
            stop_all_cap_cmd.execute()
            time.sleep(2)
            cdata_debug('测试仪停止端口的报文捕获')
            # cdata_debug('测试仪端口1报文捕获数量：%s'%cap_conf_1.CapturedPacketCount)
            # cdata_debug('测试仪端口2报文捕获数量：%s'%cap_conf_2.CapturedPacketCount)
            #把报文导出
            download_cap_data_cmd_1 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_1.handle,
                                                                 FileDir=packet_folder_path,
                                                                 FileName=packet_name,
                                                                 MaxDownloadDataCount=MaxDownloadCount)
            download_cap_data_cmd_1.execute()
            cdata_info('port1捕获的报文文件名：%s//%s//%s' % (packet_folder_path, packet_child_dir[0], packet_name))
            cdata_debug('测试仪端口1报文捕获数量：%s' % cap_conf_1.CapturedPacketCount)
            # 等待测试仪接口1的报文下载完成
            for i in range(1, 60):
                # print(cap_conf_1.DownloadedPacketCount)
                if cap_conf_1.DownloadedPacketCount == cap_conf_1.CapturedPacketCount or cap_conf_1.DownloadedPacketCount == MaxDownloadCount:
                    cdata_debug('测试仪接口1报文下载完成')
                    time.sleep(1)
                    cdata_debug('测试仪接口1下载报文数量%s' % cap_conf_1.DownloadedPacketCount)
                    break
                else:
                    cdata_debug('port1正在下载报文')
                    time.sleep(2)
            else:
                cdata_warn('测试仪接口1下载报文失败，请检查测试仪配置')
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle,
                                                                 FileDir=packet_folder_path,
                                                                 FileName=packet_name,
                                                                 MaxDownloadDataCount=MaxDownloadCount)
            download_cap_data_cmd_2.execute()
            cdata_info('port2捕获的报文文件名：%s//%s//%s' % (packet_folder_path, packet_child_dir[1], packet_name))
            cdata_debug('测试仪端口2报文捕获数量：%s' % cap_conf_2.CapturedPacketCount)
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount or cap_conf_2.DownloadedPacketCount == MaxDownloadCount:
                    cdata_debug('测试仪接口2报文下载完成')
                    time.sleep(1)
                    cdata_debug('测试仪接口2下载报文数量%s' % cap_conf_1.DownloadedPacketCount)
                    break
                else:
                    cdata_debug('port2正在下载报文')
                    time.sleep(2)
            else:
                cdata_warn('测试仪接口2下载报文失败，请检查测试仪配置')

            break
        else:
            time.sleep(10)
            continue

    else:
        verdict = 'FAIL'
        cdata_warn('端口状态为DOWN')

    return stream_stats


#单播测试用例
def unicast_test(port_location, down_stream_header, up_stream_header, packet_name, num=1,
                 dataclassname=StreamBlockStats,
                 stream_header=['Ethernet.ethernetII', 'VLAN.vlan', 'IPv4.ipv4', 'UDP.udp'], duration=10):


    # 定义变量, 'UDP.udp',port_location, down_stream_header, up_stream_header, packet_name, num=1,
    #                  dataclassname=StreamBlockStats,
    #                  stream_header=['Ethernet.ethernetII', 'VLAN.vlan', 'IPv4.ipv4', 'UDP.udp'], duration=10
    sys_entry = get_sys_entry()
    verdict = 'PASS'
    errInfo = []
    result = []
    rate_1 = 10
    rate_2 = 10
    # 生成报文下载的子目录；将port //192.168.0.180/1/1 转成192_168_0_180_1_1
    packet_child_dir = []
    for i in range(len(port_location)):
        res1 = re.split(r'[//.////]+', port_location[i])
        res2 = '_'.join(res1[1:])
        packet_child_dir.append(res2)

    # 预约端口
    port1, port2 = create_ports(sys_entry, port_location)
    packet_name = packet_name + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')
    # packet_name_port1 = packet_name + '_port1_' + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')
    # packet_name_port2  = packet_name +  '_port2_' + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')

    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed)))
    cdata_info("===========================================================================")
    port1_speed = (port1.get_children('EthCopper')[0].LineSpeed)
    port2_speed = (port2.get_children('EthCopper')[0].LineSpeed)
    # 修改端口流发送模式
    edit_streamconfig(port1)
    edit_streamconfig(port2)

    if port1_speed == 'SPEED_100M' and port2_speed == 'SPEED_1G':
        rate_1 = 10
        rate_2 = 1
    elif port1_speed == 'SPEED_1G' and port2_speed == 'SPEED_1G':
        rate_1 = 1
        rate_2 = 10
    elif port1_speed == port2_speed:
        rate_1 = 10
        rate_2 = 10
    # 编辑流
    port1_stream_header = down_stream_header
    port2_stream_header = up_stream_header

    for i in range(num):
        name1 = re.findall(r'sourceMacAdd=\d+:\d+:\d+:\d+:\d+:\d+', port1_stream_header[i])[0]
        name2 = re.findall(r'sourceMacAdd=\d+:\d+:\d+:\d+:\d+:\d+', port2_stream_header[i])[0]
        # 创建流模板
        rate_1=0.01
        rate_2=0.01
        stream1 = create_stream(port1, name1, rate_1, stream_header)
        stream2 = create_stream(port2, name2, rate_2, stream_header)

        # 编辑流
        edit_stream(stream1, port1_stream_header[i])
        edit_stream(stream2, port2_stream_header[i])
        # config rx port
        stream1.set_relatives('Rxport', port2, EnumRelationDirection.TARGET)
        stream2.set_relatives('Rxport', port1, EnumRelationDirection.TARGET)

    # 报文捕获配置
    cap_conf_1 = port1.get_children('CaptureConfig')[0]
    cap_conf_2 = port2.get_children('CaptureConfig')[0]
    # 设置捕获端口接收的报文
    cap_conf_1.edit(CaptureMode=EnumCaptureMode.ALL)
    cap_conf_2.edit(CaptureMode=EnumCaptureMode.ALL)

    if dataclassname == StreamBlockStats:
        for i in range(5):
            cdata_info('第%d次查看状态：port1的端口状态：%s ;port2的端口状态：%s' % (
            (i + 1), port1.get_children('EthCopper')[0]._LinkStatus._name_,
            port2.get_children('EthCopper')[0]._LinkStatus._name_))
            result_stats = []
            if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
                0]._LinkStatus._name_ == 'UP':

                # 开始捕获
                cdata_debug('测试仪端口开始报文捕获')
                start_all_cap_cmd = StartAllCaptureCommand()
                start_all_cap_cmd.execute()

                # create result view
                page_result_view = creat_view(sys_entry=sys_entry, dataclassname=StreamBlockStats)
                # Pre-Start stream
                pre_start_stream()
                # Clear statistic
                result_clear_cmd = ClearResultCommand(ResultViewHandles=page_result_view.handle)
                result_clear_cmd.execute()

                cdata_debug('测试仪开始打流测试')
                # Start stream and stop stream
                start_stream(duration=duration)
                cdata_debug('测试仪打流结束')
                # get stream statistic
                time.sleep(3)
                result_query = page_result_view.get_children()[0]
                streams_stats = []
                for i in range(len(result_query.get_children('StreamBlockStats'))):
                    stream_stats = result_query.get_children('StreamBlockStats')[i]
                    streams_stats.append(stream_stats)
                result_stats = streams_stats

                # 停止测试仪接口抓包
                stop_all_cap_cmd = StopAllCaptureCommand()
                stop_all_cap_cmd.execute()
                time.sleep(2)
                cdata_debug('停止测试仪端口报文捕获')
                # #把报文导出
                download_cap_data_cmd_1 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_1.handle,
                                                                     FileDir=packet_folder_path,
                                                                     FileName=packet_name,
                                                                     MaxDownloadDataCount=MaxDownloadCount)
                download_cap_data_cmd_1.execute()
                cdata_debug('测试仪端口1捕获报文数：%s' % cap_conf_1.CapturedPacketCount)
                cdata_info('port1捕获的报文文件名：%s//%s//%s' % (packet_folder_path, packet_child_dir[0], packet_name))
                # 等待测试仪接口1的报文下载完成
                for i in range(1, 60):
                    # print(cap_conf_1.DownloadedPacketCount)
                    if cap_conf_1.DownloadedPacketCount == cap_conf_1.CapturedPacketCount or cap_conf_1.DownloadedPacketCount == MaxDownloadCount:
                        cdata_debug('测试仪接口1报文下载完成')
                        time.sleep(1)
                        break
                    else:
                        cdata_debug('port1正在下载报文')
                        time.sleep(2)
                else:
                    cdata_warn('测试仪接口1下载报文失败，请检查测试仪配置')
                download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle,
                                                                     FileDir=packet_folder_path,
                                                                     FileName=packet_name,
                                                                     MaxDownloadDataCount=MaxDownloadCount)
                download_cap_data_cmd_2.execute()
                cdata_debug('测试仪端口2捕获报文数：%s' % cap_conf_2.CapturedPacketCount)
                cdata_info('port2捕获的报文文件名：%s//%s//%s' % (packet_folder_path, packet_child_dir[1], packet_name))
                for i in range(1, 60):
                    if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount or cap_conf_2.DownloadedPacketCount == MaxDownloadCount:
                        cdata_debug('测试仪接口2报文下载完成')
                        time.sleep(1)
                        break
                    else:
                        cdata_debug('port2正在下载报文')
                        time.sleep(2)
                else:
                    cdata_warn('测试仪接口2下载报文失败，请检查测试仪配置')

                break
            else:
                time.sleep(10)
                continue

        else:
            verdict = 'FAIL'
            cdata_warn('端口状态为DOWN')

    elif dataclassname == PortStats:
        for i in range(5):
            cdata_info('第%d次查看状态：port1的端口状态：%s ;port2的端口状态：%s' % (
            (i + 1), port1.get_children('EthCopper')[0]._LinkStatus._name_,
            port2.get_children('EthCopper')[0]._LinkStatus._name_))
            result_stats = []
            if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
                0]._LinkStatus._name_ == 'UP':

                # # 开始捕获
                cdata_debug('测试仪端口开始报文捕获')
                start_all_cap_cmd = StartAllCaptureCommand()
                start_all_cap_cmd.execute()

                # create result view
                page_result_view = creat_view(sys_entry=sys_entry, dataclassname=PortStats)
                # Pre-Start stream
                pre_start_stream()
                # Clear statistic
                result_clear_cmd = ClearResultCommand(ResultViewHandles=page_result_view.handle)
                result_clear_cmd.execute()
                # Start stream and stop stream
                cdata_debug('测试仪开始打流测试')
                start_stream(duration=duration)
                # get stream statistic
                time.sleep(3)
                cdata_debug('测试仪打流结束')
                result_query = page_result_view.get_children()[0]
                port1_stats = result_query.get_children('PortStats')[0]
                port2_stats = result_query.get_children('PortStats')[1]
                result_stats = [port1_stats, port2_stats]

                # 停止测试仪接口抓包
                stop_all_cap_cmd = StopAllCaptureCommand()
                stop_all_cap_cmd.execute()
                cdata_debug('测试仪关闭停止报文捕获')
                time.sleep(2)
                # #把报文导出
                download_cap_data_cmd_1 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_1.handle,
                                                                     FileDir=packet_folder_path,
                                                                     FileName=packet_name,
                                                                     MaxDownloadDataCount=MaxDownloadCount)
                download_cap_data_cmd_1.execute()
                cdata_debug('测试仪端口1捕获报文数：%s' % cap_conf_1.CapturedPacketCount)
                cdata_info('port1捕获的报文文件名：%s//%s//%s' % (packet_folder_path, packet_child_dir[0], packet_name))

                # 等待测试仪接口1的报文下载完成
                for i in range(1, 60):
                    # print(cap_conf_1.DownloadedPacketCount)
                    if cap_conf_1.DownloadedPacketCount == cap_conf_1.CapturedPacketCount or cap_conf_1.DownloadedPacketCount == MaxDownloadCount:
                        cdata_debug('测试仪接口1报文下载完成')
                        time.sleep(1)
                        break
                    else:
                        cdata_debug('port1正在下载报文')
                        time.sleep(2)
                else:
                    cdata_warn('测试仪接口1下载报文失败，请检查测试仪配置')

                download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle,
                                                                     FileDir=packet_folder_path,
                                                                     FileName=packet_name,
                                                                     MaxDownloadDataCount=MaxDownloadCount)
                download_cap_data_cmd_2.execute()

                cdata_debug('测试仪端口2捕获报文数：%s' % cap_conf_2.CapturedPacketCount)
                cdata_info('port2捕获的报文文件名：%s//%s//%s' % (packet_folder_path, packet_child_dir[1], packet_name))
                # 等待测试仪接口2的报文下载完成
                for i in range(1, 60):
                    if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount or cap_conf_2.DownloadedPacketCount == MaxDownloadCount:
                        cdata_debug('测试仪接口2报文下载完成')
                        time.sleep(1)
                        break
                    else:
                        cdata_debug('port2正在下载报文')
                        time.sleep(1)
                else:
                    cdata_warn('测试仪接口2下载报文失败，请检查测试仪配置')
                break
            else:
                time.sleep(10)
                continue

        else:
            verdict = 'FAIL'
            cdata_warn('端口状态为DOWN')

    #待分析的报文packet_folder_path, packet_child_dir[0], packet_name
    packet_filename_1 = packet_folder_path + '//' + packet_child_dir[0] + '//' + packet_name + '.pcap'
    cdata_debug('port1待分析的报文文件名:%s' % packet_filename_1)
    packet_filename_2 = packet_folder_path + '//' + packet_child_dir[1] + '//' + packet_name + '.pcap'
    cdata_debug('port2待分析的报文文件名:%s' % packet_filename_2)
    packet_filenames = [packet_filename_1,packet_filename_2]

    # print(result_stats, len(result_stats))
    release_port_cmd = ReleasePortCommand(LocationList=port_location)
    release_port_cmd.execute()
    chassis = DisconnectChassisCommand('HardwareChassis_1')
    chassis.execute()

    return result_stats,packet_filenames


if __name__ == '__main__':
    # 配置onu端口的入口和出口的速率

    # 清除测试仪的对象，防止影响下个用例的执行
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()

    # 发流量测试，上下行发送流量，速率为100M
    port_location = ['//192.168.0.180/1/3', '//192.168.0.180/1/4']
    duration = 60
    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11   ethernetII_1.destMacAdd=00:00:00:22:22:21',)

    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21  ethernetII_1.destMacAdd=00:00:00:11:11:11',)
    # 获取所有流量的统计值
    # result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header,
    #                          up_stream_header=up_stream_header,
    #                          rate=10,
    #                          duration=duration)
    # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
    #result1 = check_stream_rate(result_stats[0], result_stats[1], inbound_percent=1, outbound_percent=1)
    #result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header, up_stream_header=up_stream_header,packet_name='tt',rate=100, duration=duration)

    rate_test(port_location, down_stream_header, up_stream_header, packet_name='tt', rate=10, duration=10,stream_header=['Ethernet.ethernetII', 'VLAN.vlan', 'IPv4.ipv4', 'UDP.udp'])



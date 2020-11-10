#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from renix_py_api import renix
import logging
import time
import re

renix.initialize(log_level=logging.INFO)
from renix_py_api.api_gen import *
from renix_py_api.rom_manager import *
from renix_py_api.core import EnumRelationDirection

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

def create_stream(port,name, rate=10, packet_length=1024):
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
    renix_info('port({}) create streams'.format(port.Location))

    stream = StreamTemplate(upper=port,Name=name)
    assert stream.handle
    # 配置每条流的速率
    stream_template_load_profile = stream.get_children('StreamTemplateLoadProfile')[0]

    stream_template_load_profile.edit(Unit=EnumFrameLoadUnit.PERCENT, Rate=rate)
    # 配置流的报头
    create_stream_header_cmd = CreateHeaderCommand(stream.handle,
                                                   ['Ethernet.ethernetII', 'IPv4.ipv4', 'UDP.udp'])
    create_stream_header_cmd.execute()
    # 获取header的配置方法
    # list_instance_leaf_cmd = ListInstanceLeafCommand(stream.handle, Deep=True)
    # list_instance_leaf_cmd.execute()
    # print(list_instance_leaf_cmd.__dict__)
    print(len(create_stream_header_cmd.HeaderNames))
    if len(create_stream_header_cmd.HeaderNames) != 3:
        raise Exception('{} create EthernetII and IPv4 header failed'.format(stream.handle))
    stream.FixedLength = packet_length
    stream.get()

    return stream

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
    return  stream_load_profile

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

def creat_view(sys_entry,dataclassname=StreamBlockStats):
    # create result view
    #DataClassName can be PortStats|StreamStats|StreamTxStats|StreamRxStats|StreamblockStats|StreamblockTxStats|StreamblockRxStats
    resultView_create = CreateResultViewCommand(DataClassName=dataclassname.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]
    return page_result_view

def pre_start_stream():
    # Pre-Start stream
    startallstream = StartAllStreamCommand()
    startallstream.execute()
    time.sleep(2)
    stopallstream = StopAllStreamCommand()
    stopallstream.execute()

def start_stream(duration):
    # Start stream and stop stream
    startallstream = StartAllStreamCommand()
    startallstream.execute()
    time.sleep(duration)
    stopallstream = StopAllStreamCommand()
    stopallstream.execute()

def check_port_static(port1_stats,port2_stats):
    '''判断对发端口，两个端口frame统计情况，验证报文通的情况'''
    # check  port1_stats rx equal to tx
    verdict = 'PASS'
    errInfo =[]
    port1 = (port1_stats.__dict__)['_PortID']
    port2 = (port2_stats.__dict__)['_PortID']
    if port1_stats.RxTotalFrames == 0 or port1_stats.TxTotalFrames == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({}) or tx packets ({}) is 0'.format(port1,port1_stats.RxTotalFrames,
                                                                                    port1_stats.TxTotalFrames))
    elif port1_stats.RxTotalFrames / port2_stats.TxTotalFrames < 0.99:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({})is not equal to  port2_stats tx packets ({})'.format(port1,
                port1_stats.RxTotalFrames, port2_stats.TxTotalFrames))
    else:
        renix_info('[test pass] [{}] rx packet ({})is  equal to port2_stats tx packets ({})'.format(port1,
            port1_stats.RxTotalFrames,
            port2_stats.TxTotalFrames))

    # check  port2_stats rx equal to tx
    if port2_stats.TxTotalFrames == 0 or port2_stats.RxTotalFrames == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({}) or tx packets ({}) is 0'.format(port2,port2_stats.RxTotalFrames,
                                                                                    port2_stats.TxTotalFrames))
    elif port2_stats.RxTotalFrames / port1_stats.TxTotalFrames < 0.99:
        verdict = 'fail'
        renix_error(
            '[test fail] [{}] rx packet ({})is not equal to  port1_stats tx packets ({})'.format(port2,
                port2_stats.RxTotalFrames,
                port1_stats.TxTotalFrames))
    else:
        renix_info('[test pass] [{}] rx packet ({})is equal to  port1_stats tx packets ({})'.format(port2,
            port2_stats.RxTotalFrames,port1_stats.TxTotalFrames))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

def check_stream_loss(stream1_2_stats,stream2_1_stats):
    '''判断对发流量，两条流frame统计情况，验证报文不通的情况'''
    verdict = 'PASS'
    errInfo=[]
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']
    name2_1 = (stream2_1_stats.__dict__)['_StreamBlockID']
    # check  loss packet
    #如果发送报文不为0，接收报文的丢包等于发送报文的个数，则判断改报文不通
    #_RxLossStreamFrames没有数据
    if stream1_2_stats.TxStreamFrames!=0 and stream1_2_stats.LostStreamFrames == stream1_2_stats.TxStreamFrames:
        renix_info(
            '[test Pass] [{}] realtime loss packet ({})is  equal to  tx packet({})'.format(name1_2,stream1_2_stats.LostStreamFrames,stream1_2_stats.TxStreamFrames))
    else:
        verdict = 'FAIL'
        renix_error('[test fail] [{}] realtime loss packet ({})is not equal to tx packet({}) '.format(name1_2,
            stream1_2_stats.RxLossStreamFrames, stream1_2_stats.TxStreamFrames))

    if stream2_1_stats.TxStreamFrames!=0 and stream2_1_stats.LostStreamFrames == stream2_1_stats.TxStreamFrames:
        renix_info(
            '[test Pass] [{}] realtime loss packet ({})is  equal to  tx packet({})'.format(name2_1,stream2_1_stats.LostStreamFrames,stream2_1_stats.TxStreamFrames))
    else:
        verdict = 'FAIL'
        renix_error('[test fail] [{}] realtime loss packet ({})is not equal to  tx packet({}) '.format(name2_1,
            stream2_1_stats.LostStreamFrames, stream2_1_stats.TxStreamFrames))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

def check_stream_loss1(stream1_2_stats,):
    '''判断对发流量，两条流frame统计情况，验证报文不通的情况'''
    verdict = 'PASS'
    errInfo=[]
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']
    # check  loss packet
    #如果发送报文不为0，接收报文的丢包等于发送报文的个数，则判断改报文不通
    #_RxLossStreamFrames没有数据
    if stream1_2_stats.TxStreamFrames!=0 and stream1_2_stats.LostStreamFrames == stream1_2_stats.TxStreamFrames:
        renix_info(
            '[test Pass] [{}]rx({}), realtime loss packet ({})is  equal to  tx packet({})'.format(name1_2,stream1_2_stats.RxStreamFrames,stream1_2_stats.LostStreamFrames,stream1_2_stats.TxStreamFrames))
    else:
        verdict = 'FAIL'
        renix_error('[test fail] [{}]rx({}), realtime loss packet ({})is not equal to tx packet({}) '.format(name1_2,stream1_2_stats.RxStreamFrames,
            stream1_2_stats.RxLossStreamFrames, stream1_2_stats.TxStreamFrames))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

def check_stream_static(stream1_2_stats,stream2_1_stats):
    '''判断对发流量，两条流frame统计情况，验证通的情况'''
    verdict='PASS'
    errInfo = []
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']
    name2_1 = (stream2_1_stats.__dict__)['_StreamBlockID']
    print(stream1_2_stats.__dict__)
    print(stream2_1_stats.__dict__)
    #如果流量发送和接收都不为0，and 接收报文达到发送报文的99%以上，丢包为0，则判断流量正常
    # check rx equal to tx
    if stream1_2_stats.RxStreamFrames == 0 or stream1_2_stats.TxStreamFrames == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({}) or tx packets ({}) is 0'.format(name1_2,stream1_2_stats.RxStreamFrames,
                                                                                  stream1_2_stats.TxStreamFrames))
    elif stream1_2_stats.RxStreamFrames / stream1_2_stats.TxStreamFrames < 0.99:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({})is not equal to  tx packets ({})'.format(name1_2,
                stream1_2_stats.RxStreamFrames, stream1_2_stats.TxStreamFrames))
    else:
        renix_info('[test pass] [{}] rx packet ({})is  equal to tx packets ({})'.format(name1_2,stream1_2_stats.RxStreamFrames,
                                                                                        stream1_2_stats.TxStreamFrames))

    if stream2_1_stats.RxStreamFrames == 0 or stream2_1_stats.TxStreamFrames == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({}) or tx packets ({}) is 0'.format(name2_1,stream2_1_stats.RxStreamFrames,
                                                                                  stream2_1_stats.TxStreamFrames))
    elif stream2_1_stats.RxStreamFrames / stream2_1_stats.TxStreamFrames < 0.99:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({})is not equal to  tx packets ({})'.format(name2_1,
                stream2_1_stats.RxStreamFrames, stream2_1_stats.TxStreamFrames))
    else:
        renix_info('[test pass] [{}] rx packet ({})is  equal to tx packets ({})'.format(name2_1,stream2_1_stats.RxStreamFrames,
                                                                                        stream2_1_stats.TxStreamFrames))
    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

def check_stream_static1(stream1_2_stats):
    '''判断对发流量，两条流frame统计情况，验证通的情况'''
    verdict='PASS'
    errInfo = []
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']

    #如果流量发送和接收都不为0，and 接收报文达到发送报文的99%以上，丢包为0，则判断流量正常
    # check rx equal to tx
    if stream1_2_stats.RxStreamFrames == 0 or stream1_2_stats.TxStreamFrames == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({}) or tx packets ({}) is 0'.format(name1_2,stream1_2_stats.RxStreamFrames,
                                                                                  stream1_2_stats.TxStreamFrames))
    elif stream1_2_stats.RxStreamFrames / stream1_2_stats.TxStreamFrames < 0.99:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx packet ({})is not equal to  tx packets ({})'.format(name1_2,
                stream1_2_stats.RxStreamFrames, stream1_2_stats.TxStreamFrames))
    else:
        renix_info('[test pass] [{}] rx packet ({})is  equal to tx packets ({})'.format(name1_2,stream1_2_stats.RxStreamFrames,
                                                                                        stream1_2_stats.TxStreamFrames))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

def check_stream_rate(stream1_2_stats,stream2_1_stats,inbound_percent=1,outbound_percent=1):
    '''判断对发流量，两条流速率统计情况，验证报文不通的情况'''
    verdict = 'PASS'
    errInfo = []
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']
    name2_1 = (stream2_1_stats.__dict__)['_StreamBlockID']
    # (stream1_2_stats.TxUtil)*0.99<= stream1_2_stats.RxUtil <= (stream1_2_stats.TxUtil)*1.01
    # (stream1_2_stats.TxUtil) * 0.99 >= stream1_2_stats.RxUtil or stream1_2_stats.RxUtil >= (stream1_2_stats.TxUtil)*1.01

    if stream1_2_stats.RxUtil == 0 or stream1_2_stats.TxUtil == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({}) or tx rate ({}) is 0'.format(name1_2,stream1_2_stats.RxUtil,
                                                                                  stream1_2_stats.TxUtil))
    elif ((stream1_2_stats.TxUtil)*outbound_percent) * 0.9 >= stream1_2_stats.RxUtil or \
            stream1_2_stats.RxUtil >= ((stream1_2_stats.TxUtil)*outbound_percent)*1.1:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({})is not equal to  tx rate ({})* {}'.format(name1_2,
                stream1_2_stats.RxUtil, stream1_2_stats.TxUtil,outbound_percent))
    else:
        renix_info('[test pass] [{}] rx rate ({})is  equal to tx rate ({}) * {}'.format(name1_2,stream1_2_stats.RxUtil,
                                                                                        stream1_2_stats.TxUtil,outbound_percent))

    if stream2_1_stats.RxUtil == 0 or stream2_1_stats.TxUtil == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({}) or tx rate ({}) is 0'.format(name2_1,stream2_1_stats.RxUtil,
                                                                        stream2_1_stats.TxUtil))
    elif ((stream2_1_stats.TxUtil*inbound_percent)) * 0.9 >= stream2_1_stats.RxUtil or \
            stream2_1_stats.RxUtil >= ((stream2_1_stats.TxUtil)*inbound_percent)*1.1:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({})is not equal to  tx rate ({}) * {}'.format(name2_1,
                                                 stream2_1_stats.RxUtil, stream2_1_stats.TxUtil,inbound_percent))
    else:
        renix_info('[test pass] [{}] rx rate ({})is  equal to tx rate ({}) * {}'.format(name2_1,stream2_1_stats.RxUtil,
                                                                              stream2_1_stats.TxUtil,inbound_percent))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict

def check_stream_rate1(stream1_2_stats,percent=1):
    '''判断对发流量，两条流速率统计情况，验证报文不通的情况'''
    verdict = 'PASS'
    errInfo = []
    name1_2 = (stream1_2_stats.__dict__)['_StreamBlockID']
    # (stream1_2_stats.TxUtil)*0.99<= stream1_2_stats.RxUtil <= (stream1_2_stats.TxUtil)*1.01
    # (stream1_2_stats.TxUtil) * 0.99 >= stream1_2_stats.RxUtil or stream1_2_stats.RxUtil >= (stream1_2_stats.TxUtil)*1.01

    if stream1_2_stats.RxUtil == 0 or stream1_2_stats.TxUtil == 0:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({}) or tx rate ({}) is 0'.format(name1_2,stream1_2_stats.RxUtil,
                                                                                  stream1_2_stats.TxUtil))
    elif ((stream1_2_stats.TxUtil)*percent) * 0.9 >= stream1_2_stats.RxUtil or \
            stream1_2_stats.RxUtil >= ((stream1_2_stats.TxUtil)*percent)*1.1:
        verdict = 'FAIL'
        renix_error(
            '[test fail] [{}] rx rate ({})is not equal to  tx rate ({})* {}'.format(name1_2,
                stream1_2_stats.RxUtil, stream1_2_stats.TxUtil,percent))
    else:
        renix_info('[test pass] [{}] rx rate ({})is  equal to tx rate ({}) * {}'.format(name1_2,stream1_2_stats.RxUtil,
                                                                                        stream1_2_stats.TxUtil,percent))

    # if verdict == 'FAIL':
    #     for i in errInfo:
    #         renix_error(i)
    return verdict


def rate_test(port_location,down_stream_header,up_stream_header,rate=10,duration=10):
    # 定义变量
    sys_entry = get_sys_entry()

    # 预约端口
    port1, port2 = create_ports(sys_entry, port_location)
    # 修改端口流发送模式
    edit_streamconfig(port1)
    edit_streamconfig(port2)

    # 编辑流
    port1_stream_header = down_stream_header
    port2_stream_header = up_stream_header
    name1 = re.findall(r'sourceMacAdd=\d+:\d+:\d+:\d+:\d+:\d+', port1_stream_header[0])[0]
    name2 = re.findall(r'sourceMacAdd=\d+:\d+:\d+:\d+:\d+:\d+', port2_stream_header[0])[0]
    # 创建流模板
    stream1 = create_stream(port1, name1, rate)
    stream2 = create_stream(port2, name2, rate)

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
    # Start stream
    startallstream = StartAllStreamCommand()
    startallstream.execute()
    time.sleep(duration)
    # get stream statistic
    result_query = page_result_view.get_children()[0]
    stream_stats = result_query.get_children('StreamBlockStats')

    return stream_stats

def unicast_test(port_location,down_stream_header,up_stream_header,rate=10,num=1,dataclassname=StreamBlockStats,duration=10):
    # 定义变量
    sys_entry = get_sys_entry()
    verdict = 'PASS'
    errInfo = []
    result = []
    #预约端口
    port1, port2 = create_ports(sys_entry, port_location)
    # 修改端口流发送模式
    edit_streamconfig(port1)
    edit_streamconfig(port2)

    #编辑流
    port1_stream_header = down_stream_header
    port2_stream_header = up_stream_header

    for i in range(num):
        name1 = re.findall(r'sourceMacAdd=\d+:\d+:\d+:\d+:\d+:\d+',port1_stream_header[i])[0]
        name2 = re.findall(r'sourceMacAdd=\d+:\d+:\d+:\d+:\d+:\d+',port2_stream_header[i])[0]
        # 创建流模板
        stream1 = create_stream(port1, name1,rate)
        stream2 = create_stream(port2, name2,rate)

        #编辑流
        edit_stream(stream1, port1_stream_header[i])
        edit_stream(stream2, port2_stream_header[i])
        # config rx port
        stream1.set_relatives('Rxport', port2, EnumRelationDirection.TARGET)
        stream2.set_relatives('Rxport', port1, EnumRelationDirection.TARGET)

    if dataclassname==StreamBlockStats:
        # create result view
        page_result_view = creat_view(sys_entry=sys_entry, dataclassname=StreamBlockStats)
        # Pre-Start stream
        pre_start_stream()
        # Clear statistic
        result_clear_cmd = ClearResultCommand(ResultViewHandles=page_result_view.handle)
        result_clear_cmd.execute()
        # Start stream and stop stream
        start_stream(duration=duration)
        # get stream statistic
        time.sleep(3)
        result_query = page_result_view.get_children()[0]
        streams_stats=[]
        for i in range(len(result_query.get_children('StreamBlockStats'))):
            stream_stats = result_query.get_children('StreamBlockStats')[i]
            streams_stats.append(stream_stats)

        result_stats=streams_stats

    elif dataclassname==PortStats:
        # create result view
        page_result_view = creat_view(sys_entry=sys_entry, dataclassname=PortStats)
        # Pre-Start stream
        pre_start_stream()
        # Clear statistic
        result_clear_cmd = ClearResultCommand(ResultViewHandles=page_result_view.handle)
        result_clear_cmd.execute()
        # Start stream and stop stream
        start_stream(duration=duration)
        # get stream statistic
        time.sleep(3)
        result_query = page_result_view.get_children()[0]
        port1_stats = result_query.get_children('PortStats')[0]
        port2_stats = result_query.get_children('PortStats')[1]
        result_stats=[port1_stats,port2_stats]

    release_port_cmd = ReleasePortCommand(LocationList=port_location)
    release_port_cmd.execute()
    chassis = DisconnectChassisCommand('HardwareChassis_1')
    chassis.execute()
    return result_stats



if __name__ == '__main__':

    #配置onu端口的入口和出口的速率

    # 清除测试仪的对象，防止影响下个用例的执行
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()

    # 发流量测试，上下行发送流量，速率为100M
    port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
    duration = 60
    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11   ethernetII_1.destMacAdd=00:00:00:22:22:21',)

    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21  ethernetII_1.destMacAdd=00:00:00:11:11:11',)
    # 获取所有流量的统计值
    result_stats = rate_test(port_location=port_location, down_stream_header=down_stream_header,
                                up_stream_header=up_stream_header,
                                rate=10,
                                duration=duration )
    # 判断port1的上下行流量是否都是不通的，如果是返回PASS，否则返回FAIL
    result1 = check_stream_rate(result_stats[0], result_stats[1],inbound_percent=1,outbound_percent=1)
    print(result1)
# if __name__ == '__main__':
#     port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
#     duration = 10
#     # down_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:11:11:11 ethernetII_1.destMacAdd=00:00:00:22:22:21',
#     #                       'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 ethernetII_1.destMacAdd=00:00:00:22:22:22',
#     #                       'ethernetII_1.sourceMacAdd=00:00:00:11:11:13 ethernetII_1.destMacAdd=00:00:00:22:22:23',
#     #                       'ethernetII_1.sourceMacAdd=00:00:00:11:11:14 ethernetII_1.destMacAdd=00:00:00:22:22:24')
#     #
#     # up_stream_header = ( 'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 ethernetII_1.destMacAdd=00:00:00:11:11:11',
#     #                      'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 ethernetII_1.destMacAdd=00:00:00:11:11:12',
#     #                      'ethernetII_1.sourceMacAdd=00:00:00:22:22:23 ethernetII_1.destMacAdd=00:00:00:11:11:13',
#     #                      'ethernetII_1.sourceMacAdd=00:00:00:22:22:24 ethernetII_1.destMacAdd=00:00:00:11:11:14')
#     down_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=3000 ethernetII_1.destMacAdd=00:00:00:22:22:21',)
#     up_stream_header = ('ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=3000 ethernetII_1.destMacAdd=00:00:00:11:11:11',)
#     unicast_test(port_location=port_location,down_stream_header=down_stream_header,up_stream_header=up_stream_header,num=1,duration=duration)
#     time.sleep(3)
#     reset_rom_cmd = ResetROMCommand()
#     reset_rom_cmd.execute()

#!/usr/bin/python
# -*- coding UTF-8 -*-

from renix_py_api.renix import *
import logging, time
import os
import sys

initialize(log_level=logging.INFO)
from renix_py_api.api_gen import *
from renix_py_api.core import EnumRelationDirection
from renix_py_api.rom_manager import *
# from src.config.initialization_config import *
from src.config.Cdata_loggers import *
import scapy
from scapy.all import *
from scapy.utils import PcapReader

# current_dir = os.getcwd()
# packet_dir = current_dir[:current_dir.index('tests')] + 'data'
# packet_path1 = (packet_dir + '\\' + '_'.join(port_location[0][2:].replace('/', '.').split('.')) + '\\')
# packet_path2 = (packet_dir + '\\' + '_'.join(port_location[1][2:].replace('/', '.').split('.')) + '\\')
# print(packet_path1)
# print(packet_path2)

current_dir = os.getcwd()
packet_dir = current_dir[:current_dir.index('tests')] + 'data'

def get_packet_path(port_location):
    packet_path1 = (packet_dir + '\\' + '_'.join(port_location[0][2:].replace('/', '.').split('.')) + '\\')
    packet_path2 = (packet_dir + '\\' + '_'.join(port_location[1][2:].replace('/', '.').split('.')) + '\\')
    # print(packet_path1)
    # print(packet_path2)
    return packet_path1,packet_path2


# 占用测试仪接口
def create_ports(sys_entry, locations):
    renix_info('Create ports with locations:{}'.format(locations))
    port1 = Port(upper=sys_entry, location=locations[0])
    port2 = Port(upper=sys_entry, location=locations[1])
    assert port1.handle
    assert port2.handle
    bring_port_online_cmd = BringPortsOnlineCommand(portlist=[port1.handle, port2.handle])
    bring_port_online_cmd.execute()
    print(wait_port_online(port1))
    if not wait_port_online(port1):
        raise Exception('bring online port({}) failed'.format(port1.handle))
    if not wait_port_online(port2):
        raise Exception('bring online port({}) failed'.format(port2.handle))
    return port1, port2


# 创建带VLAN的数据量
def create_stream_vlan(port, packet_length=128):
    renix_info('port({}) create streams'.format(port.Location))
    stream = StreamTemplate(upper=port)
    assert stream.handle
    create_stream_header_cmd = CreateHeaderCommand(stream.handle,
                                                   ['Ethernet.ethernetII', 'VLAN.vlan', 'IPv4.ipv4', 'UDP.udp'])
    create_stream_header_cmd.execute()
    if len(create_stream_header_cmd.HeaderNames) != 4:
        raise Exception('{} create EthernetII and IPv4 header failed'.format(stream.handle))
    stream.FixedLength = packet_length
    stream.get()
    return stream


# 创建不带VLAN的数据量
def create_stream(port, packet_length=128):
    # renix_info('port({}) create streams'.format(port_location))
    renix_info('port({}) create streams'.format(port.Location))

    stream = StreamTemplate(upper=port)
    assert stream.handle
    create_stream_header_cmd = CreateHeaderCommand(stream.handle, ['Ethernet.ethernetII', 'IPv4.ipv4', 'UDP.udp'])
    create_stream_header_cmd.execute()
    if len(create_stream_header_cmd.HeaderNames) != 3:
        raise Exception('{} create EthernetII and IPv4 header failed'.format(stream.handle))
    stream.FixedLength = packet_length
    stream.get()
    return stream


# 编辑数据流
def edit_stream(stream, parameter):
    update_header_cmd = UpdateHeaderCommand(Stream=stream.handle, Parameter=parameter)
    update_header_cmd.execute()
    stream.get()


# 等待测试仪端口上线
def wait_port_online(port, times=30):
    while times:
        if port.Online:
            return True
        else:
            times -= 1
            time.sleep(1)
    else:
        return False


# 发送数据流测试
def stream_test(stream_rate, stream_num, port_location, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream(port1)
    stream2_1 = create_stream(port2)
    edit_stream(stream1_2, 'ethernetII_1.sourceMacAdd=00:00:00:22:11:11 ethernetII_1.destMacAdd=00:00:00:11:22:22')
    edit_stream(stream2_1, 'ethernetII_1.sourceMacAdd=00:00:00:11:22:22 ethernetII_1.destMacAdd=00:00:00:22:11:11')
    # edit_stream(stream1_2,'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=1001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=5')
    # edit_stream(stream2_1,'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=1001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=5')
    edit_stream(stream1_2,
                'ipv4_1.destination.XetModifier.StreamType=InterModifier ipv4_1.destination.XetModifier.Type=Increment ipv4_1.destination.XetModifier.Start=192.168.110.222 ipv4_1.destination.XetModifier.Step=1 ipv4_1.destination.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ipv4_1.destination.XetModifier.StreamType=InterModifier ipv4_1.destination.XetModifier.Type=Increment ipv4_1.destination.XetModifier.Start=192.168.110.111 ipv4_1.destination.XetModifier.Step=1 ipv4_1.destination.XetModifier.Count=1')
    edit_stream(stream1_2,
                'ipv4_1.source.XetModifier.StreamType=InterModifier ipv4_1.source.XetModifier.Type=Increment ipv4_1.source.XetModifier.Start=192.168.110.111 ipv4_1.source.XetModifier.Step=1 ipv4_1.source.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ipv4_1.source.XetModifier.StreamType=InterModifier ipv4_1.source.XetModifier.Type=Increment ipv4_1.source.XetModifier.Start=192.168.110.222 ipv4_1.source.XetModifier.Step=1 ipv4_1.source.XetModifier.Count=1')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())

    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()

    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]


    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            cdata_info('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            cdata_info('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue
        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(stream_num) and stream2_1_stats.RxStreamFrames == int(
                stream_num) and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            cdata_info("测试仪发流成功")
            download_cap_data_cmd_1 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_1.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port1_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_1.CapturedPacketCount)
            download_cap_data_cmd_1.execute()

            # 等待测试仪接口1的报文下载完成
            for i in range(1, 60):
                # print(cap_conf_1.DownloadedPacketCount)
                if cap_conf_1.DownloadedPacketCount == cap_conf_1.CapturedPacketCount:
                    cdata_debug('测试仪接口1报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                cdata_warn('测试仪接口1下载报文失败，请检查测试仪配置')

            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    cdata_debug('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                cdata_warn('测试仪接口2下载报文失败，请检查测试仪配置')
            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            break
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        cdata_error("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False

    packet_path1,packet_path2 = get_packet_path(port_location)
    packets_port1 = rdpcap(packet_path1 + packet_name + '_port1_' + now + '.pcap')
    packets_port2 = rdpcap(packet_path2 + packet_name + '_port2_' + now + '.pcap')
    total_port1 = 0
    total_port2 = 0
    for data in packets_port1:
        if len(data) == 128 and 'Dot1Q' not in data and data['Ether'].dst == '00:00:00:22:11:11' and data[
            'Ether'].src == '00:00:00:11:22:22' and data['IP'].dst == '192.168.110.111' and data[
            'IP'].src == '192.168.110.222' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 110 and data['UDP'].len == 90:
            total_port1 += 1

    for data in packets_port2:
        if len(data) == 128 and 'Dot1Q' not in data and data['Ether'].src == '00:00:00:22:11:11' and data[
            'Ether'].dst == '00:00:00:11:22:22' and data['IP'].src == '192.168.110.111' and data[
            'IP'].dst == '192.168.110.222' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 110 and data['UDP'].len == 90:
            total_port2 += 1

    print(total_port1)
    print(total_port2)
    if total_port1 == int(stream_num) and total_port2 == int(stream_num):
        cdata_info("##################################")
        cdata_info("PASS")
        cdata_info("报文分析成功。")
        cdata_info("端口1收到%s个报文。" % (total_port1))
        cdata_info("端口2收到%s个报文。" % (total_port2))
        cdata_info("##################################")
        return True
    else:
        cdata_error("##################################")
        cdata_error("FAILED")
        cdata_error("报文分析失败。")
        cdata_error("端口1收到%s个报文。" % (total_port1))
        cdata_error("端口2收到%s个报文。" % (total_port2))
        cdata_error("##################################")
        return False


# 上下行发送携带untag报文，上行流量不通，下行流量是通的
def stream_test_1(stream_rate, stream_num, port_location, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream(port1)
    stream2_1 = create_stream(port2)
    edit_stream(stream1_2, 'ethernetII_1.sourceMacAdd=00:00:00:22:11:11 ethernetII_1.destMacAdd=00:00:00:11:22:22')
    edit_stream(stream2_1, 'ethernetII_1.sourceMacAdd=00:00:00:11:22:22 ethernetII_1.destMacAdd=00:00:00:22:11:11')
    # edit_stream(stream1_2,'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=1001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=5')
    # edit_stream(stream2_1,'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=1001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=5')
    edit_stream(stream1_2,
                'ipv4_1.destination.XetModifier.StreamType=InterModifier ipv4_1.destination.XetModifier.Type=Increment ipv4_1.destination.XetModifier.Start=192.168.110.222 ipv4_1.destination.XetModifier.Step=1 ipv4_1.destination.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ipv4_1.destination.XetModifier.StreamType=InterModifier ipv4_1.destination.XetModifier.Type=Increment ipv4_1.destination.XetModifier.Start=192.168.110.111 ipv4_1.destination.XetModifier.Step=1 ipv4_1.destination.XetModifier.Count=1')
    edit_stream(stream1_2,
                'ipv4_1.source.XetModifier.StreamType=InterModifier ipv4_1.source.XetModifier.Type=Increment ipv4_1.source.XetModifier.Start=192.168.110.111 ipv4_1.source.XetModifier.Step=1 ipv4_1.source.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ipv4_1.source.XetModifier.StreamType=InterModifier ipv4_1.source.XetModifier.Type=Increment ipv4_1.source.XetModifier.Start=192.168.110.222 ipv4_1.source.XetModifier.Step=1 ipv4_1.source.XetModifier.Count=1')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue
        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(
                stream_num) and stream2_1_stats.RxStreamFrames == 0 and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")

            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    print('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口2下载报文失败，请检查测试仪配置')

            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            break
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False

    packet_path1, packet_path2 = get_packet_path(port_location)
    packets_port2 = rdpcap(packet_path2 + packet_name + '_port2_' + now + '.pcap')
    total_port2 = 0

    for data in packets_port2:
        if len(data) == 128 and 'Dot1Q' not in data and data['Ether'].src == '00:00:00:22:11:11' and data[
            'Ether'].dst == '00:00:00:11:22:22' and data['IP'].src == '192.168.110.111' and data[
            'IP'].dst == '192.168.110.222' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 110 and data['UDP'].len == 90:
            total_port2 += 1

    if total_port2 == 10000:
        print("##################################")
        print("PASS")
        print("报文分析成功。")
        print("端口2收到%s个报文。" % (total_port2))
        print("##################################")
        return True
    else:
        print("##################################")
        print("FAILED")
        print("报文分析失败。")
        print("端口2收到%s个报文。" % (total_port2))
        print("##################################")
        return False


def stream_test_vlan(stream_rate, stream_num, port_location, stream_vlan_id, stream_vlan_pri, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream_vlan(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:02:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:02:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:02:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:02:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')

    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    edit_stream(stream2_1,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    edit_stream(stream1_2, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream2_1, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream1_2, 'ipv4_1.source=192.168.112.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.112.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.112.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.112.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue
        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(stream_num) and stream2_1_stats.RxStreamFrames == int(
                stream_num) and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")
            download_cap_data_cmd_1 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_1.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port1_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_1.CapturedPacketCount)
            download_cap_data_cmd_1.execute()

            # 等待测试仪接口1的报文下载完成
            for i in range(1, 60):
                # print(cap_conf_1.DownloadedPacketCount)
                if cap_conf_1.DownloadedPacketCount == cap_conf_1.CapturedPacketCount:
                    print('测试仪接口1报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口1下载报文失败，请检查测试仪配置')

            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    print('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口2下载报文失败，请检查测试仪配置')

            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            break
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False

    packet_path1,packet_path2 = get_packet_path(port_location)
    packets_port1 = rdpcap(packet_path1 + packet_name + '_port1_' + now + '.pcap')
    packets_port2 = rdpcap(packet_path2 + packet_name + '_port2_' + now + '.pcap')
    total_port1 = 0
    total_port2 = 0

    if stream_vlan_id == '2000':
        for data in packets_port1:
            if len(data) == 124 and 'Dot1Q' not in data and data['Ether'].dst == '00:00:02:22:11:11' and data[
                'Ether'].src == '00:00:02:11:22:22' and data['IP'].dst == '192.168.112.112' and data[
                'IP'].src == '192.168.112.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port1 += 1

        for data in packets_port2:
            if len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
                'Dot1Q'].vlan == int(stream_vlan_id) and data['Ether'].src == '00:00:02:22:11:11' and data[
                'Ether'].dst == '00:00:02:11:22:22' and data['IP'].src == '192.168.112.112' and data[
                'IP'].dst == '192.168.112.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port2 += 1
    else:
        for data in packets_port1:
            if len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
                'Dot1Q'].vlan == int(stream_vlan_id) and data['Ether'].dst == '00:00:02:22:11:11' and data[
                'Ether'].src == '00:00:02:11:22:22' and data['IP'].dst == '192.168.112.112' and data[
                'IP'].src == '192.168.112.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port1 += 1

        for data in packets_port2:
            if len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
                'Dot1Q'].vlan == int(stream_vlan_id) and data['Ether'].src == '00:00:02:22:11:11' and data[
                'Ether'].dst == '00:00:02:11:22:22' and data['IP'].src == '192.168.112.112' and data[
                'IP'].dst == '192.168.112.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port2 += 1

    if total_port1 == 10000 and total_port2 == 10000:
        print("##################################")
        print("PASS")
        print("报文分析成功。")
        print("端口1收到%s个报文。" % (total_port1))
        print("端口2收到%s个报文。" % (total_port2))
        print("##################################")
        return True
    else:
        print("##################################")
        print("FAILED")
        print("报文分析失败。")
        print("端口1收到%s个报文。" % (total_port1))
        print("端口2收到%s个报文。" % (total_port2))
        print("##################################")
        return False


def stream_test_vlan_pri(stream_rate, stream_num, port_location, stream_vlan_id, stream_vlan_pri, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream_vlan(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:02:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:02:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:02:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:02:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')

    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    edit_stream(stream2_1,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    edit_stream(stream1_2, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream2_1, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream1_2, 'ipv4_1.source=192.168.112.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.112.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.112.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.112.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue
        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(stream_num) and stream2_1_stats.RxStreamFrames == int(
                stream_num) and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")
            download_cap_data_cmd_1 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_1.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port1_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_1.CapturedPacketCount)
            download_cap_data_cmd_1.execute()

            # 等待测试仪接口1的报文下载完成
            for i in range(1, 60):
                # print(cap_conf_1.DownloadedPacketCount)
                if cap_conf_1.DownloadedPacketCount == cap_conf_1.CapturedPacketCount:
                    print('测试仪接口1报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口1下载报文失败，请检查测试仪配置')

            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    print('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口2下载报文失败，请检查测试仪配置')

            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            break
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False

    packet_path1,packet_path2 = get_packet_path(port_location)
    packets_port1 = rdpcap(packet_path1 + packet_name + '_port1_' + now + '.pcap')
    packets_port2 = rdpcap(packet_path2 + packet_name + '_port2_' + now + '.pcap')
    total_port1 = 0
    total_port2 = 0

    if stream_vlan_id == '2000':
        for data in packets_port1:
            if len(data) == 124 and 'Dot1Q' not in data and data['Ether'].dst == '00:00:02:22:11:11' and data[
                'Ether'].src == '00:00:02:11:22:22' and data['IP'].dst == '192.168.112.112' and data[
                'IP'].src == '192.168.112.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port1 += 1

        for data in packets_port2:
            if len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == 0 and data['Dot1Q'].vlan == int(
                    stream_vlan_id) and data['Ether'].src == '00:00:02:22:11:11' and data[
                'Ether'].dst == '00:00:02:11:22:22' and data['IP'].src == '192.168.112.112' and data[
                'IP'].dst == '192.168.112.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port2 += 1
    else:
        for data in packets_port1:
            if len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
                'Dot1Q'].vlan == int(stream_vlan_id) and data['Ether'].dst == '00:00:02:22:11:11' and data[
                'Ether'].src == '00:00:02:11:22:22' and data['IP'].dst == '192.168.112.112' and data[
                'IP'].src == '192.168.112.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port1 += 1

        for data in packets_port2:
            if len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
                'Dot1Q'].vlan == int(stream_vlan_id) and data['Ether'].src == '00:00:02:22:11:11' and data[
                'Ether'].dst == '00:00:02:11:22:22' and data['IP'].src == '192.168.112.112' and data[
                'IP'].dst == '192.168.112.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port2 += 1

    if total_port1 == 10000 and total_port2 == 10000:
        print("##################################")
        print("PASS")
        print("报文分析成功。")
        print("端口1收到%s个报文。" % (total_port1))
        print("端口2收到%s个报文。" % (total_port2))
        print("##################################")
        return True
    else:
        print("##################################")
        print("FAILED")
        print("报文分析失败。")
        print("端口1收到%s个报文。" % (total_port1))
        print("端口2收到%s个报文。" % (total_port2))
        print("##################################")
        return False


def stream_test_vlan_1(stream_rate, stream_num, port_location, stream_vlan_pri, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream_vlan(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:03:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:03:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:03:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:03:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')

    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=2001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=7')
    edit_stream(stream2_1,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=2001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=7')
    edit_stream(stream1_2, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream2_1, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream1_2, 'ipv4_1.source=192.168.113.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.113.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.113.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.113.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue

        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(stream_num) and stream2_1_stats.RxStreamFrames == int(
                stream_num) and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")
            download_cap_data_cmd_1 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_1.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port1_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_1.CapturedPacketCount)
            download_cap_data_cmd_1.execute()

            # 等待测试仪接口1的报文下载完成
            for i in range(1, 60):
                # print(cap_conf_1.DownloadedPacketCount)
                if cap_conf_1.DownloadedPacketCount == cap_conf_1.CapturedPacketCount:
                    print('测试仪接口1报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口1下载报文失败，请检查测试仪配置')

            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    print('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口2下载报文失败，请检查测试仪配置')

            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            break
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False
    packet_path1,packet_path2 = get_packet_path(port_location)
    packets_port1 = rdpcap(packet_path1 + packet_name + '_port1_' + now + '.pcap')
    packets_port2 = rdpcap(packet_path2 + packet_name + '_port2_' + now + '.pcap')
    total_port1_stream1 = 0
    total_port1_stream2 = 0
    total_port1_stream3 = 0
    total_port1_stream4 = 0
    total_port1_stream5 = 0
    total_port1_stream6 = 0
    total_port1_stream7 = 0
    total_port2_stream1 = 0
    total_port2_stream2 = 0
    total_port2_stream3 = 0
    total_port2_stream4 = 0
    total_port2_stream5 = 0
    total_port2_stream6 = 0
    total_port2_stream7 = 0

    for data in packets_port1:
        if len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2001 and data['Ether'].dst == '00:00:03:22:11:11' and data[
            'Ether'].src == '00:00:03:11:22:22' and data['IP'].dst == '192.168.113.112' and data[
            'IP'].src == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port1_stream1 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2002 and data['Ether'].dst == '00:00:03:22:11:12' and data[
            'Ether'].src == '00:00:03:11:22:23' and data['IP'].dst == '192.168.113.112' and data[
            'IP'].src == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port1_stream2 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2003 and data['Ether'].dst == '00:00:03:22:11:13' and data[
            'Ether'].src == '00:00:03:11:22:24' and data['IP'].dst == '192.168.113.112' and data[
            'IP'].src == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port1_stream3 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2004 and data['Ether'].dst == '00:00:03:22:11:14' and data[
            'Ether'].src == '00:00:03:11:22:25' and data['IP'].dst == '192.168.113.112' and data[
            'IP'].src == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port1_stream4 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2005 and data['Ether'].dst == '00:00:03:22:11:15' and data[
            'Ether'].src == '00:00:03:11:22:26' and data['IP'].dst == '192.168.113.112' and data[
            'IP'].src == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port1_stream5 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2006 and data['Ether'].dst == '00:00:03:22:11:16' and data[
            'Ether'].src == '00:00:03:11:22:27' and data['IP'].dst == '192.168.113.112' and data[
            'IP'].src == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port1_stream6 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2007 and data['Ether'].dst == '00:00:03:22:11:17' and data[
            'Ether'].src == '00:00:03:11:22:28' and data['IP'].dst == '192.168.113.112' and data[
            'IP'].src == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port1_stream7 += 1

    for data in packets_port2:
        if len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2001 and data['Ether'].src == '00:00:03:22:11:11' and data[
            'Ether'].dst == '00:00:03:11:22:22' and data['IP'].src == '192.168.113.112' and data[
            'IP'].dst == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream1 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2002 and data['Ether'].src == '00:00:03:22:11:12' and data[
            'Ether'].dst == '00:00:03:11:22:23' and data['IP'].src == '192.168.113.112' and data[
            'IP'].dst == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream2 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2003 and data['Ether'].src == '00:00:03:22:11:13' and data[
            'Ether'].dst == '00:00:03:11:22:24' and data['IP'].src == '192.168.113.112' and data[
            'IP'].dst == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream3 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2004 and data['Ether'].src == '00:00:03:22:11:14' and data[
            'Ether'].dst == '00:00:03:11:22:25' and data['IP'].src == '192.168.113.112' and data[
            'IP'].dst == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream4 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2005 and data['Ether'].src == '00:00:03:22:11:15' and data[
            'Ether'].dst == '00:00:03:11:22:26' and data['IP'].src == '192.168.113.112' and data[
            'IP'].dst == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream5 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2006 and data['Ether'].src == '00:00:03:22:11:16' and data[
            'Ether'].dst == '00:00:03:11:22:27' and data['IP'].src == '192.168.113.112' and data[
            'IP'].dst == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream6 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2007 and data['Ether'].src == '00:00:03:22:11:17' and data[
            'Ether'].dst == '00:00:03:11:22:28' and data['IP'].src == '192.168.113.112' and data[
            'IP'].dst == '192.168.113.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream7 += 1

    if total_port1_stream1 == 1000 and total_port1_stream2 == 1000 and total_port1_stream3 == 1000 and total_port1_stream4 == 1000 and total_port1_stream5 == 1000 and total_port1_stream6 == 1000 and total_port1_stream7 == 1000 and total_port2_stream1 == 1000 and total_port2_stream2 == 1000 and total_port2_stream3 == 1000 and total_port2_stream4 == 1000 and total_port2_stream5 == 1000 and total_port2_stream6 == 1000 and total_port2_stream7 == 1000:
        print("##################################")
        print("PASS")
        print("报文分析成功。")
        print("端口1收到VLAN为2001的%s个报文。" % (total_port1_stream1))
        print("端口1收到VLAN为2002的%s个报文。" % (total_port1_stream2))
        print("端口1收到VLAN为2003的%s个报文。" % (total_port1_stream3))
        print("端口1收到VLAN为2004的%s个报文。" % (total_port1_stream4))
        print("端口1收到VLAN为2005的%s个报文。" % (total_port1_stream5))
        print("端口1收到VLAN为2006的%s个报文。" % (total_port1_stream6))
        print("端口1收到VLAN为2007的%s个报文。" % (total_port1_stream7))
        print("端口2收到VLAN为2001的%s个报文。" % (total_port2_stream1))
        print("端口2收到VLAN为2002的%s个报文。" % (total_port2_stream2))
        print("端口2收到VLAN为2003的%s个报文。" % (total_port2_stream3))
        print("端口2收到VLAN为2004的%s个报文。" % (total_port2_stream4))
        print("端口2收到VLAN为2005的%s个报文。" % (total_port2_stream5))
        print("端口2收到VLAN为2006的%s个报文。" % (total_port2_stream6))
        print("端口2收到VLAN为2007的%s个报文。" % (total_port2_stream7))
        print("##################################")
        return True
    else:
        print("##################################")
        print("FAILED")
        print("报文分析失败。")
        print("端口1收到VLAN为2001的%s个报文。" % (total_port1_stream1))
        print("端口1收到VLAN为2002的%s个报文。" % (total_port1_stream2))
        print("端口1收到VLAN为2003的%s个报文。" % (total_port1_stream3))
        print("端口1收到VLAN为2004的%s个报文。" % (total_port1_stream4))
        print("端口1收到VLAN为2005的%s个报文。" % (total_port1_stream5))
        print("端口1收到VLAN为2006的%s个报文。" % (total_port1_stream6))
        print("端口1收到VLAN为2007的%s个报文。" % (total_port1_stream7))
        print("端口2收到VLAN为2001的%s个报文。" % (total_port2_stream1))
        print("端口2收到VLAN为2002的%s个报文。" % (total_port2_stream2))
        print("端口2收到VLAN为2003的%s个报文。" % (total_port2_stream3))
        print("端口2收到VLAN为2004的%s个报文。" % (total_port2_stream4))
        print("端口2收到VLAN为2005的%s个报文。" % (total_port2_stream5))
        print("端口2收到VLAN为2006的%s个报文。" % (total_port2_stream6))
        print("端口2收到VLAN为2007的%s个报文。" % (total_port2_stream7))
        print("##################################")
        return False


def stream_test_vlan_1_pri(stream_rate, stream_num, port_location, stream_vlan_pri, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream_vlan(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:03:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:03:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:03:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:03:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')

    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=2001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=7')
    edit_stream(stream2_1,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=2001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=7')
    edit_stream(stream1_2, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream2_1, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream1_2, 'ipv4_1.source=192.168.113.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.113.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.113.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.113.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue

        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(stream_num) and stream2_1_stats.RxStreamFrames == int(
                stream_num) and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")
            download_cap_data_cmd_1 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_1.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port1_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_1.CapturedPacketCount)
            download_cap_data_cmd_1.execute()

            # 等待测试仪接口1的报文下载完成
            for i in range(1, 60):
                # print(cap_conf_1.DownloadedPacketCount)
                if cap_conf_1.DownloadedPacketCount == cap_conf_1.CapturedPacketCount:
                    print('测试仪接口1报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口1下载报文失败，请检查测试仪配置')

            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    print('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口2下载报文失败，请检查测试仪配置')

            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            return True
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False


# 上下行发送携带vlan为2000，优先级从0递增到6的报文，上下行流量都通
def stream_test_vlan_2(stream_rate, stream_num, port_location, stream_vlan_id, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream_vlan(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:04:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:04:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:04:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:04:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')
    edit_stream(stream1_2,
                'vlan_1.priority.XetModifier.StreamType=InterModifier vlan_1.priority.XetModifier.Type=Increment vlan_1.priority.XetModifier.Start=0 vlan_1.priority.id.XetModifier.Step=1 vlan_1.priority.XetModifier.Count=7')
    edit_stream(stream2_1,
                'vlan_1.priority.XetModifier.StreamType=InterModifier vlan_1.priority.XetModifier.Type=Increment vlan_1.priority.XetModifier.Start=0 vlan_1.priority.id.XetModifier.Step=1 vlan_1.priority.XetModifier.Count=7')
    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    edit_stream(stream2_1,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    edit_stream(stream1_2, 'ipv4_1.source=192.168.114.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.114.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.114.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.114.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]

            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(stream_num) and stream2_1_stats.RxStreamFrames == int(
                stream_num) and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")
            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            return True
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False


# 上下行发送携带vlan为2000，上行流量不通，下行流量是通的
def stream_test_vlan_3(stream_rate, stream_num, port_location, stream_vlan_id, stream_vlan_pri, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream_vlan(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:05:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:05:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:05:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:05:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')

    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    edit_stream(stream2_1,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    edit_stream(stream1_2, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream2_1, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream1_2, 'ipv4_1.source=192.168.115.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.115.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.115.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.115.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]

            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(
                stream_num) and stream2_1_stats.RxStreamFrames == 0 and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")
            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            return True
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False


# 上下行发送携带vlan为2001到2007的报文，上行流量不通，下行流量是通的
def stream_test_vlan_4(stream_rate, stream_num, port_location, stream_vlan_pri, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream_vlan(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:06:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:06:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:06:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:06:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')

    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=2001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=7')
    edit_stream(stream2_1,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=2001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=7')
    edit_stream(stream1_2, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream2_1, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream1_2, 'ipv4_1.source=192.168.116.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.116.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.116.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.116.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue

        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(
                stream_num) and stream2_1_stats.RxStreamFrames == 0 and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")

            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    print('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口2下载报文失败，请检查测试仪配置')

            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            break
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False
    packet_path1, packet_path2 = get_packet_path(port_location)
    packets_port2 = rdpcap(packet_path2 + packet_name + '_port2_' + now + '.pcap')
    total_port2_stream1 = 0
    total_port2_stream2 = 0
    total_port2_stream3 = 0
    total_port2_stream4 = 0
    total_port2_stream5 = 0
    total_port2_stream6 = 0
    total_port2_stream7 = 0

    for data in packets_port2:
        if len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2001 and data['Ether'].src == '00:00:06:22:11:11' and data[
            'Ether'].dst == '00:00:06:11:22:22' and data['IP'].src == '192.168.116.112' and data[
            'IP'].dst == '192.168.116.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream1 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2002 and data['Ether'].src == '00:00:06:22:11:12' and data[
            'Ether'].dst == '00:00:06:11:22:23' and data['IP'].src == '192.168.116.112' and data[
            'IP'].dst == '192.168.116.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream2 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2003 and data['Ether'].src == '00:00:06:22:11:13' and data[
            'Ether'].dst == '00:00:06:11:22:24' and data['IP'].src == '192.168.116.112' and data[
            'IP'].dst == '192.168.116.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream3 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2004 and data['Ether'].src == '00:00:06:22:11:14' and data[
            'Ether'].dst == '00:00:06:11:22:25' and data['IP'].src == '192.168.116.112' and data[
            'IP'].dst == '192.168.116.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream4 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2005 and data['Ether'].src == '00:00:06:22:11:15' and data[
            'Ether'].dst == '00:00:06:11:22:26' and data['IP'].src == '192.168.116.112' and data[
            'IP'].dst == '192.168.116.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream5 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2006 and data['Ether'].src == '00:00:06:22:11:16' and data[
            'Ether'].dst == '00:00:06:11:22:27' and data['IP'].src == '192.168.116.112' and data[
            'IP'].dst == '192.168.116.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream6 += 1
        elif len(data) == 128 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
            'Dot1Q'].vlan == 2007 and data['Ether'].src == '00:00:06:22:11:17' and data[
            'Ether'].dst == '00:00:06:11:22:28' and data['IP'].src == '192.168.116.112' and data[
            'IP'].dst == '192.168.116.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
            'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
            total_port2_stream7 += 1

    if total_port2_stream1 == 1000 and total_port2_stream2 == 1000 and total_port2_stream3 == 1000 and total_port2_stream4 == 1000 and total_port2_stream5 == 1000 and total_port2_stream6 == 1000 and total_port2_stream7 == 1000:
        print("##################################")
        print("PASS")
        print("报文分析成功。")
        print("端口2收到VLAN为2001的%s个报文。" % (total_port2_stream1))
        print("端口2收到VLAN为2002的%s个报文。" % (total_port2_stream2))
        print("端口2收到VLAN为2003的%s个报文。" % (total_port2_stream3))
        print("端口2收到VLAN为2004的%s个报文。" % (total_port2_stream4))
        print("端口2收到VLAN为2005的%s个报文。" % (total_port2_stream5))
        print("端口2收到VLAN为2006的%s个报文。" % (total_port2_stream6))
        print("端口2收到VLAN为2007的%s个报文。" % (total_port2_stream7))
        print("##################################")
        return True
    else:
        print("##################################")
        print("FAILED")
        print("报文分析失败。")
        print("端口2收到VLAN为2001的%s个报文。" % (total_port2_stream1))
        print("端口2收到VLAN为2002的%s个报文。" % (total_port2_stream2))
        print("端口2收到VLAN为2003的%s个报文。" % (total_port2_stream3))
        print("端口2收到VLAN为2004的%s个报文。" % (total_port2_stream4))
        print("端口2收到VLAN为2005的%s个报文。" % (total_port2_stream5))
        print("端口2收到VLAN为2006的%s个报文。" % (total_port2_stream6))
        print("端口2收到VLAN为2007的%s个报文。" % (total_port2_stream7))
        print("##################################")
        return False


def stream_test_vlan_4_pri(stream_rate, stream_num, port_location, stream_vlan_pri, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream_vlan(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:06:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:06:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:06:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:06:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')

    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=2001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=7')
    edit_stream(stream2_1,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=2001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=7')
    edit_stream(stream1_2, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream2_1, 'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream1_2, 'ipv4_1.source=192.168.116.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.116.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.116.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.116.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue

        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(
                stream_num) and stream2_1_stats.RxStreamFrames == 0 and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")

            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    print('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口2下载报文失败，请检查测试仪配置')

            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            return True
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False


# 上下行发送携带vlan为2001到2007的报文，优先级从0递增到6，上行流量不通，下行流量是通的
def stream_test_vlan_5(stream_rate, stream_num, port_location, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream_vlan(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:07:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:07:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:07:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:07:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')
    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=2001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=7')
    edit_stream(stream2_1,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=2001 vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=7')
    edit_stream(stream1_2,
                'vlan_1.priority.XetModifier.StreamType=InterModifier vlan_1.priority.XetModifier.Type=Increment vlan_1.priority.XetModifier.Start=0 vlan_1.priority.XetModifier.Step=1 vlan_1.priority.XetModifier.Count=7')
    edit_stream(stream2_1,
                'vlan_1.priority.XetModifier.StreamType=InterModifier vlan_1.priority.XetModifier.Type=Increment vlan_1.priority.XetModifier.Start=0 vlan_1.priority.XetModifier.Step=1 vlan_1.priority.XetModifier.Count=7')
    edit_stream(stream1_2, 'ipv4_1.source=192.168.117.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.117.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.117.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.117.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue

        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(
                stream_num) and stream2_1_stats.RxStreamFrames == 0 and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")

            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    print('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口2下载报文失败，请检查测试仪配置')

            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            return True
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False


# 上下行发送携带vlan为2000，优先级从0递增到6的报文，上流量不通，下行流量通
def stream_test_vlan_6(stream_rate, stream_num, port_location, stream_vlan_id, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream_vlan(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:08:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:08:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:08:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=7')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:08:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=7')
    edit_stream(stream1_2,
                'vlan_1.priority.XetModifier.StreamType=InterModifier vlan_1.priority.XetModifier.Type=Increment vlan_1.priority.XetModifier.Start=0 vlan_1.priority.XetModifier.Step=1 vlan_1.priority.XetModifier.Count=7')
    edit_stream(stream2_1,
                'vlan_1.priority.XetModifier.StreamType=InterModifier vlan_1.priority.XetModifier.Type=Increment vlan_1.priority.XetModifier.Start=0 vlan_1.priority.XetModifier.Step=1 vlan_1.priority.XetModifier.Count=7')
    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    edit_stream(stream2_1,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    edit_stream(stream1_2, 'ipv4_1.source=192.168.118.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.118.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.118.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.118.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue

        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(
                stream_num) and stream2_1_stats.RxStreamFrames == 0 and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")

            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    print('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口2下载报文失败，请检查测试仪配置')

            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            return True
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False


# 上下行流量都通
def stream_test_vlan_gemport_1(stream_rate, stream_num, port_location, stream_vlan_id, stream_vlan_pri, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:09:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:09:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:09:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:09:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')

    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    # edit_stream(stream2_1,'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (stream_vlan_id))
    edit_stream(stream1_2, 'vlan_1.priority=%s' % (stream_vlan_pri))
    # edit_stream(stream2_1,'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream1_2, 'ipv4_1.source=192.168.119.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.119.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.119.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.119.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue
        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(stream_num) and stream2_1_stats.RxStreamFrames == int(
                stream_num) and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")
            download_cap_data_cmd_1 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_1.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port1_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_1.CapturedPacketCount)
            download_cap_data_cmd_1.execute()

            # 等待测试仪接口1的报文下载完成
            for i in range(1, 60):
                # print(cap_conf_1.DownloadedPacketCount)
                if cap_conf_1.DownloadedPacketCount == cap_conf_1.CapturedPacketCount:
                    print('测试仪接口1报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口1下载报文失败，请检查测试仪配置')

            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    print('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口2下载报文失败，请检查测试仪配置')

            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            break
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False

    packet_path1,packet_path2 = get_packet_path(port_location)
    packets_port1 = rdpcap(packet_path1 + packet_name + '_port1_' + now + '.pcap')
    packets_port2 = rdpcap(packet_path2 + packet_name + '_port2_' + now + '.pcap')
    total_port1 = 0
    total_port2 = 0

    if stream_vlan_id == '2000':
        for data in packets_port1:
            if len(data) == 128 and 'Dot1Q' not in data and data['Ether'].dst == '00:00:09:22:11:11' and data[
                'Ether'].src == '00:00:09:11:22:22' and data['IP'].dst == '192.168.119.112' and data[
                'IP'].src == '192.168.119.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 110 and data['UDP'].len == 90:
                total_port1 += 1

        for data in packets_port2:
            if len(data) == 124 and 'Dot1Q' not in data and data['Ether'].src == '00:00:09:22:11:11' and data[
                'Ether'].dst == '00:00:09:11:22:22' and data['IP'].src == '192.168.119.112' and data[
                'IP'].dst == '192.168.119.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port2 += 1
    else:
        for data in packets_port1:
            if len(data) == 132 and 'Dot1Q' in data and data['Dot1Q'].prio == int(stream_vlan_pri) and data[
                'Dot1Q'].vlan == int(stream_vlan_id) and data['Ether'].dst == '00:00:09:22:11:11' and data[
                'Ether'].src == '00:00:09:11:22:22' and data['IP'].dst == '192.168.119.112' and data[
                'IP'].src == '192.168.119.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 110 and data['UDP'].len == 90:
                total_port1 += 1

        for data in packets_port2:
            if len(data) == 124 and 'Dot1Q' not in data and data['Ether'].src == '00:00:09:22:11:11' and data[
                'Ether'].dst == '00:00:09:11:22:22' and data['IP'].src == '192.168.119.112' and data[
                'IP'].dst == '192.168.119.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port2 += 1

    if total_port1 == 10000 and total_port2 == 10000:
        print("##################################")
        print("PASS")
        print("报文分析成功。")
        print("端口1收到%s个报文。" % (total_port1))
        print("端口2收到%s个报文。" % (total_port2))
        print("##################################")
        return True
    else:
        print("##################################")
        print("FAILED")
        print("报文分析失败。")
        print("端口1收到%s个报文。" % (total_port1))
        print("端口2收到%s个报文。" % (total_port2))
        print("##################################")
        return False


# 上下行流量都不通
def stream_test_vlan_gemport_2(stream_rate, stream_num, port_location, stream_vlan_id, stream_vlan_pri, packet_name):
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()
    # service-port配置完成后，需要等待一段时间流才能通
    time.sleep(10)
    sys_entry = get_sys_entry()

    # 占用测试仪端口
    port1, port2 = create_ports(sys_entry, port_location)

    # 插卡测试仪接口当前的双工速率
    cdata_info("===========================================================================")
    cdata_info("当前端口1的协商速率为：%s" % ((port1.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("当前端口2的协商速率为：%s" % ((port2.get_children('EthCopper')[0].LineSpeed._name_)))
    cdata_info("===========================================================================")

    # 配置测试仪Load Profiles模板(速率为10%，打流方式为突发方式，双向发送100000个报文)
    stream_port_cfg_1 = port1.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_1 = stream_port_cfg_1.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_1.edit(Rate=int(stream_rate))
    stream_port_cfg_2 = port2.get_children(StreamPortConfig.cls_name())[0]
    inter_frame_gap_cfg_2 = stream_port_cfg_2.get_children(InterFrameGapProfile.cls_name())[0]
    inter_frame_gap_cfg_2.edit(Rate=int(stream_rate))
    stream_port_cfg_1.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_2.edit(TransmitMode=EnumTransmitMode.BURST)
    stream_port_cfg_1.get()
    stream_port_cfg_2.get()
    Burst_transmit_config_1 = stream_port_cfg_1.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_2 = stream_port_cfg_2.get_children('BurstTransmitConfig')[0]
    Burst_transmit_config_1.edit(FramePerBurst=int(stream_num))
    Burst_transmit_config_2.edit(FramePerBurst=int(stream_num))

    # 创建数据流
    stream1_2 = create_stream_vlan(port1)
    stream2_1 = create_stream(port2)
    edit_stream(stream1_2,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:0a:22:11:11 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream1_2,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:0a:11:22:22 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.sourceMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.sourceMacAdd.XetModifier.Type=Increment ethernetII_1.sourceMacAdd.XetModifier.Start=00:00:0a:11:22:22 ethernetII_1.sourceMacAdd.XetModifier.Step=1 ethernetII_1.sourceMacAdd.XetModifier.Count=1')
    edit_stream(stream2_1,
                'ethernetII_1.destMacAdd.XetModifier.StreamType=InterModifier ethernetII_1.destMacAdd.XetModifier.Type=Increment ethernetII_1.destMacAdd.XetModifier.Start=00:00:0a:22:11:11 ethernetII_1.destMacAdd.XetModifier.Step=1 ethernetII_1.destMacAdd.XetModifier.Count=1')

    edit_stream(stream1_2,
                'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (
                    stream_vlan_id))
    # edit_stream(stream2_1,'vlan_1.id.XetModifier.StreamType=InterModifier vlan_1.id.XetModifier.Type=Increment vlan_1.id.XetModifier.Start=%s vlan_1.id.XetModifier.Step=1 vlan_1.id.XetModifier.Count=1' % (stream_vlan_id))
    edit_stream(stream1_2, 'vlan_1.priority=%s' % (stream_vlan_pri))
    # edit_stream(stream2_1,'vlan_1.priority=%s' % (stream_vlan_pri))
    edit_stream(stream1_2, 'ipv4_1.source=192.168.120.112')
    edit_stream(stream2_1, 'ipv4_1.source=192.168.120.223')
    edit_stream(stream1_2, 'ipv4_1.destination=192.168.120.223')
    edit_stream(stream2_1, 'ipv4_1.destination=192.168.120.112')
    stream1_2.set_relatives('RxPort', port2, EnumRelationDirection.TARGET)
    stream2_1.set_relatives('RxPort', port1, EnumRelationDirection.TARGET)

    # 配置测试仪查看测试结果的视图
    resultView_create = CreateResultViewCommand(DataClassName=StreamBlockStats.cls_name())
    resultView_create.execute()
    resultView_create = ROMManager.get_object(resultView_create.ResultViewHandle)
    subscribe_result_cmd = SubscribeResultCommand(ResultViewHandles=resultView_create.handle)
    subscribe_result_cmd.execute()
    # cap_conf_1 = port1.get_children('CaptureConfig')[0]
    # cap_conf_2 = port2.get_children('CaptureConfig')[0]

    # 开始测试仪抓包
    # start_all_cap_cmd = StartAllCaptureCommand()
    # start_all_cap_cmd.execute()
    sys_entry.get()
    page_result_view = sys_entry.get_children(PageResultView.cls_name())[0]

    # 开始测试仪发包
    for i in range(0, 5):
        # 开始测试仪发包
        if port2.get_children('EthCopper')[0]._LinkStatus._name_ == 'UP' and port1.get_children('EthCopper')[
            0]._LinkStatus._name_ == 'UP':
            cap_conf_1 = port1.get_children('CaptureConfig')[0]
            cap_conf_2 = port2.get_children('CaptureConfig')[0]
            start_all_cap_cmd = StartAllCaptureCommand()
            start_all_cap_cmd.execute()
            start_all_stream_cmd = StartAllStreamCommand()
            start_all_stream_cmd.execute()
            time.sleep(10)
            result_query = page_result_view.get_children()[0]
            # 读取测试仪接口的发包和收包数据
            stream1_2_stats = result_query.get_children()[0]
            stream2_1_stats = result_query.get_children()[1]
            print('上行收到的报文数量为：' + str(stream2_1_stats.RxStreamFrames))
            print('下行收到的报文数量为：' + str(stream1_2_stats.RxStreamFrames))
        else:
            time.sleep(10)
            continue

        # 停止测试接口仪抓包
        stop_all_cap_cmd = StopAllCaptureCommand()
        stop_all_cap_cmd.execute()
        # 判断是否丢包
        if stream1_2_stats.RxStreamFrames == int(
                stream_num) and stream2_1_stats.RxStreamFrames == 0 and stream1_2_stats.RxLossStreamFrames == 0 and stream2_1_stats.RxLossStreamFrames == 0:
            print("测试仪发流成功")
            # 等待测试仪接口2的报文下载完成
            download_cap_data_cmd_2 = DownloadCaptureDataCommand(CaptureConfigs=cap_conf_2.handle, FileDir=packet_dir,
                                                                 FileName=packet_name + '_port2_' + now + '.pcap',
                                                                 MaxDownloadDataCount=cap_conf_2.CapturedPacketCount)
            download_cap_data_cmd_2.execute()
            for i in range(1, 60):
                if cap_conf_2.DownloadedPacketCount == cap_conf_2.CapturedPacketCount:
                    print('测试仪接口2报文下载完成')
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
            else:
                print('测试仪接口2下载报文失败，请检查测试仪配置')

            release_port_cmd = ReleasePortCommand(LocationList=port_location)
            release_port_cmd.execute()
            chassis = DisconnectChassisCommand('HardwareChassis_1')
            chassis.execute()
            time.sleep(3)
            reset_rom_cmd = ResetROMCommand()
            reset_rom_cmd.execute()
            break
        else:
            result_clear_cmd = ClearAllResultCommand()
            result_clear_cmd.execute()

    else:
        print("测试仪发流失败")
        release_port_cmd = ReleasePortCommand(LocationList=port_location)
        release_port_cmd.execute()
        chassis = DisconnectChassisCommand('HardwareChassis_1')
        chassis.execute()
        time.sleep(3)
        reset_rom_cmd = ResetROMCommand()
        reset_rom_cmd.execute()
        return False
    packet_path1, packet_path2 = get_packet_path(port_location)
    packets_port2 = rdpcap(packet_path2 + packet_name + '_port2_' + now + '.pcap')
    total_port2 = 0

    if stream_vlan_id == '2000':

        for data in packets_port2:
            if len(data) == 124 and 'Dot1Q' not in data and data['Ether'].src == '00:00:0a:22:11:11' and data[
                'Ether'].dst == '00:00:0a:11:22:22' and data['IP'].src == '192.168.120.112' and data[
                'IP'].dst == '192.168.120.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port2 += 1
    else:

        for data in packets_port2:
            if len(data) == 124 and 'Dot1Q' not in data and data['Ether'].src == '00:00:0a:22:11:11' and data[
                'Ether'].dst == '00:00:0a:11:22:22' and data['IP'].src == '192.168.120.112' and data[
                'IP'].dst == '192.168.120.223' and data['IP'].proto == 17 and data['UDP'].sport == 1024 and data[
                'UDP'].dport == 1024 and data['IP'].len == 106 and data['UDP'].len == 86:
                total_port2 += 1

    if total_port2 == 10000:
        print("##################################")
        print("PASS")
        print("报文分析成功。")
        print("端口2收到%s个报文。" % (total_port2))
        print("##################################")
        return True
    else:
        print("##################################")
        print("FAILED")
        print("报文分析失败。")
        print("端口2收到%s个报文。" % (total_port2))
        print("##################################")
        return False


if __name__ == '__main__':
    for i in range(1, 100):
        if stream_test('10', '100000', '100000', ['//192.168.0.180/1/1', '//192.168.0.180/1/2']):
            print("===========================================================================")
            print("第%s次测试成功" % (i))
            print("===========================================================================")
        else:
            print("===========================================================================")
            print("第%s次测试失败" % (i))
            exit

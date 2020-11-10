#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI


from src.xinertel.unicast66 import *

#epon_onu端口为transparent时，打流测试
def streamstest_ont_port_vlan_transparent_E(port_location, packet_name):
    #'''packet_name='current_dir_name + '_' + sys._getframe().f_code.co_name''''
    # 清除测试仪的对象，防止影响下个用例的执行
    time.sleep(5)
    reset_rom_cmd = ResetROMCommand()

    reset_rom_cmd.execute()

    # 发流量测试，onu的Eth1发送两条流2000，和vlan2001
    # port_location = ['//192.168.0.180/1/7', '//192.168.0.180/1/8']
    duration = 10
    num = 2
    dataclassname = StreamBlockStats
    stream_header = ['Ethernet.ethernetII', 'VLAN.vlan', 'IPv4.ipv4', 'UDP.udp']
    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.1.11 ipv4_1.destination=192.168.1.21',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.1.12 ipv4_1.destination=192.168.1.22',
    )

    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.1.21 ipv4_1.destination=192.168.1.11',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.1.22 ipv4_1.destination=192.168.1.12',
    )
    result = unicast_test(port_location, down_stream_header,up_stream_header,packet_name,num, dataclassname,stream_header,duration)

    result_stats = result[0]

    for i in range(2*num):
        if (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:11':
            result11 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:12':
            result12 = check_stream_static1(result_stats[i])

        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:21':
            result21 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:22':
            result22 = check_stream_static1(result_stats[i])

    # 正确的结果vlan2000的能通，vlan2001的不通
    if result11 == 'PASS' and result12 == 'PASS' and result21 == 'PASS' and result22 == 'PASS':
        stream_result = 'PASS'
        cdata_info("ONU端口为transparent:打流测试正常")
    else:
        stream_result = 'FAIL'
        cdata_error("ONU端口为transparent:打流测试失败")

    # 判断如果文件存在，就开始分析报文
    tag_result = 'PASS'
    packet_filenames = result[1]
    cdata_debug('待分析的报文:%s' % packet_filenames)
    # 对port2的报文进行分析（也就是下行的报文）
    if os.path.isfile(packet_filenames[1]):
        packets = rdpcap(packet_filenames[1])
        # cdata_info(packets)
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:11' and data['Ether'].dst == '00:00:00:22:22:21':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:22:22:21)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:22:22:21)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:12' and data['Ether'].dst == '00:00:00:22:22:22':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:22:22:21)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:22:22:21)数据流不带tag')
                    tag_result = 'FAIL'
                break
    if stream_result=='PASS' and tag_result == 'PASS':
        res='PASS'
    else:
        res = 'FAIL'
    return res

#gpon_onu端口为transparent时，打流测试
def streamstest_ont_port_vlan_transparent_G(port_location, packet_name):
    #'''packet_name='current_dir_name + '_' + sys._getframe().f_code.co_name''''
    # 清除测试仪的对象，防止影响下个用例的执行
    time.sleep(5)
    reset_rom_cmd = ResetROMCommand()

    reset_rom_cmd.execute()

    # 发流量测试，onu的Eth1发送两条流2000，和vlan2001
    # port_location = ['//192.168.0.180/1/7', '//192.168.0.180/1/8']
    duration = 10
    num = 2
    dataclassname = StreamBlockStats
    stream_header = ['Ethernet.ethernetII', 'VLAN.vlan', 'IPv4.ipv4', 'UDP.udp']
    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.1.11 ipv4_1.destination=192.168.1.21',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.1.12 ipv4_1.destination=192.168.1.22',
    )

    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.1.21 ipv4_1.destination=192.168.1.11',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.1.22 ipv4_1.destination=192.168.1.12',
    )
    result = unicast_test(port_location, down_stream_header,up_stream_header,packet_name,num, dataclassname,stream_header,duration)

    result_stats = result[0]

    for i in range(2*num):
        if (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:11':
            result11 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:12':
            result12 = check_stream_static1(result_stats[i])

        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:21':
            result21 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:22':
            result22 = check_stream_static1(result_stats[i])

    # 正确的结果vlan2000的能通，vlan2001的不通
    if result11 == 'PASS' and result12 == 'PASS' and result21 == 'PASS' and result22 == 'PASS':
        stream_result = 'PASS'
        cdata_info("ONU端口为transparent:打流测试正常")
    else:
        stream_result = 'FAIL'
        cdata_error("ONU端口为transparent:打流测试失败")

    # 判断如果文件存在，就开始分析报文
    tag_result = 'PASS'
    packet_filenames = result[1]
    cdata_debug('待分析的报文:%s' % packet_filenames)
    # 对port2的报文进行分析（也就是下行的报文）
    if os.path.isfile(packet_filenames[1]):
        packets = rdpcap(packet_filenames[1])
        # cdata_info(packets)
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:11' and data['Ether'].dst == '00:00:00:22:22:21':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:22:22:21)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:22:22:21)数据流不带tag')
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:12' and data['Ether'].dst == '00:00:00:22:22:22':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:22:22:21)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:22:22:21)数据流不带tag')
                    tag_result = 'FAIL'
                break
    if stream_result=='PASS' and tag_result == 'PASS':
        res='PASS'
    else:
        res = 'FAIL'
    return res

#epon_onu端口为tag模式时，打流测试
def streamstest_ont_port_vlan_tag_normal(port_location,packet_name):
    # 清除测试仪的对象，防止影响下个用例的执行
    time.sleep(3)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()

    # 发流量测试，上下行发untag的报文
    # port_location = ['//192.168.0.180/1/7', '//192.168.0.180/1/8']
    duration = 10
    stream_header = ['Ethernet.ethernetII', 'IPv4.ipv4', 'UDP.udp']
    dataclassname = StreamBlockStats
    num = 1
    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.1.12 ipv4_1.destination=92.168.1.21',
    )

    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21   ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.1.21 ipv4_1.destination=92.168.1.12',
    )
    #result = unicast_test(port_location, down_stream_header,up_stream_header,packet_name,num,dataclassname, stream_header,duration)
    result = unicast_test(port_location, down_stream_header, up_stream_header, packet_name, num, dataclassname, stream_header,duration)

    result_stats = result[0]

    for i in range(2*num):
        if (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:11':
            result11 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:21':
            result21 = check_stream_static1(result_stats[i])

    # 判断如果文件存在，就开始分析报文
    tag_result = 'PASS'
    packet_filenames = result[1]
    cdata_debug('待分析的报文:%s' % packet_filenames)
    # 对port2的报文进行分析（也就是下行的报文）
    if os.path.isfile(packet_filenames[1]):
        packets = rdpcap(packet_filenames[1])
        # cdata_info(packets)
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:11' and data['Ether'].dst == '00:00:00:22:22:21':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:11)数据流带tag %s' % (data['Dot1Q'].vlan))
                    tag_result = 'FAIL'
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:11)数据流不带tag')
                break


    # 正确的结果vlan2000和vlan2001的能通，vlan2002的不通
    if result11 == 'PASS' and result21 == 'PASS':
        stream_result = 'PASS'
        cdata_info("ONU端口为tag:上行不带tag(通)打流测试正常")
    else:
        stream_result = 'FAIL'
        cdata_error("ONU端口为tag:上行不带tag(通)打流测试失败")

    if stream_result == 'PASS' and tag_result == 'PASS':
        res = 'PASS'
    else:
        res = 'FAIL'

    return  res

#epon_onu端口为tag模式时，异常测试，打流测试
def streamstest_ont_port_vlan_tag_abnormal(port_location,packet_name):
    # 清除测试仪的对象，防止影响下个用例的执行
    time.sleep(5)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()

    # 发流量测试，发送两条流2000，和vlan2001,和vlan2002
    # port_location = ['//192.168.0.180/1/7', '//192.168.0.180/1/8']
    duration = 10
    stream_header = ['Ethernet.ethernetII', 'VLAN.vlan', 'IPv4.ipv4', 'UDP.udp']
    dataclassname = StreamBlockStats
    num = 1
    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.1.12 ipv4_1.destination=192.168.1.22',
    )

    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:22  vlan_1.id=2000 ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.1.22 ipv4_1.destination=192.168.1.12',
    )
    result = unicast_test(port_location, down_stream_header,up_stream_header,packet_name, num,dataclassname,stream_header,duration)
    result_stats = result[0]
    # 判断如果文件存在，就开始分析报文
    tag_result = 'PASS'
    packet_filenames = result[1]

    for i in range(2):
        if (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:22':
            result22 = check_stream_loss1(result_stats[i])

    # 正确的结果vlan2000和vlan2001的能通，vlan2002的不通
    if result22 == 'PASS':
        stream_result = 'PASS'
        cdata_info("ONU端口为tag:上行带tag(不通)打流测试正常")
    else:
        stream_result = 'FAIL'
        cdata_error("ONU端口为tag:上行带tag(不通)打流测试失败")

    return  stream_result

#onu端口为translate模式时，打流测试
def streamstest_ont_port_vlan_translate(port_location,packet_name):
    # 清除测试仪的对象，防止影响下个用例的执行
    time.sleep(5)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()

    # '//192.168.0.180/1/9'连接上联口，'//192.168.0.180/1/10'连接onu端口
    # port_location = ['//192.168.0.180/1/7', '//192.168.0.180/1/8']
    # 跑流的时长为10s
    duration = 10
    num = 8
    dataclassname = StreamBlockStats
    stream_header = ['Ethernet.ethernetII', 'VLAN.vlan', 'IPv4.ipv4', 'UDP.udp']

    # 发流量测试，发送三条流vlan100，和vlan200,和vlan300
    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.1.11 ipv4_1.destination=92.168.1.21',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.1.12 ipv4_1.destination=92.168.1.22',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:13 vlan_1.id=2002  ethernetII_1.destMacAdd=00:00:00:22:22:23 ipv4_1.source=192.168.1.13 ipv4_1.destination=92.168.1.23',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:14 vlan_1.id=2003  ethernetII_1.destMacAdd=00:00:00:22:22:24 ipv4_1.source=192.168.1.14 ipv4_1.destination=92.168.1.24',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:15 vlan_1.id=2004  ethernetII_1.destMacAdd=00:00:00:22:22:25 ipv4_1.source=192.168.1.15 ipv4_1.destination=92.168.1.25',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:16 vlan_1.id=2005  ethernetII_1.destMacAdd=00:00:00:22:22:26 ipv4_1.source=192.168.1.16 ipv4_1.destination=92.168.1.26',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:17 vlan_1.id=2006  ethernetII_1.destMacAdd=00:00:00:22:22:27 ipv4_1.source=192.168.1.17 ipv4_1.destination=92.168.1.27',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:18 vlan_1.id=2007  ethernetII_1.destMacAdd=00:00:00:22:22:28 ipv4_1.source=192.168.1.18 ipv4_1.destination=92.168.1.28',
    )

    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=100  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.1.21 ipv4_1.destination=192.168.1.11',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=101  ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.1.22 ipv4_1.destination=192.168.1.12',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:23 vlan_1.id=102  ethernetII_1.destMacAdd=00:00:00:11:11:13 ipv4_1.source=192.168.1.23 ipv4_1.destination=192.168.1.13',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:24 vlan_1.id=103  ethernetII_1.destMacAdd=00:00:00:11:11:14 ipv4_1.source=192.168.1.24 ipv4_1.destination=192.168.1.14',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:25 vlan_1.id=104  ethernetII_1.destMacAdd=00:00:00:11:11:15 ipv4_1.source=192.168.1.25 ipv4_1.destination=192.168.1.15',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:26 vlan_1.id=105  ethernetII_1.destMacAdd=00:00:00:11:11:16 ipv4_1.source=192.168.1.26 ipv4_1.destination=192.168.1.16',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:27 vlan_1.id=106  ethernetII_1.destMacAdd=00:00:00:11:11:17 ipv4_1.source=192.168.1.27 ipv4_1.destination=192.168.1.17',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:28 vlan_1.id=107  ethernetII_1.destMacAdd=00:00:00:11:11:18 ipv4_1.source=192.168.1.28 ipv4_1.destination=192.168.1.18',
        )
    result = unicast_test(port_location, down_stream_header,up_stream_header,packet_name,num, dataclassname,stream_header,duration)

    result_stats = result[0]

    for i in range(2*num):
        if (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:11':
            result11 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:12':
            result12 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:13':
            result13 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:14':
            result14 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:15':
            result15 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:16':
            result16 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:17':
            result17 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:21':
            result21 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:22':
            result22 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:23':
            result23 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:24':
            result24 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:25':
            result25 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:26':
            result26 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:27':
            result27 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:18':
            result18 = check_stream_loss1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:28':
            result28 = check_stream_loss1(result_stats[i])

    # 恢复默认配置
    # ont_port_trunk_del(tn)

    # 正确的结果vlan2000和vlan2001的能通，vlan2002的不通
    if result11 == 'PASS' and result12 == 'PASS' and result13 == 'PASS' and result14 == 'PASS' \
            and result15 == 'PASS' and result16 == 'PASS' and result17 == 'PASS' and result18 == 'PASS' \
            and result21 == 'PASS' and result22 == 'PASS' and result23 == 'PASS' and result24 == 'PASS' \
            and result25 == 'PASS' and result26 == 'PASS' and result27 == 'PASS' :
        stream_result = 'PASS'
        cdata_info("ONU端口为translate:打流测试正常")
    else:
        stream_result = 'FAIL'
        cdata_error("ONU端口为translate:打流测试失败")

    # 判断如果文件存在，就开始分析报文
    tag_result = 'PASS'
    packet_filenames = result[1]
    # cdata_debug('待分析的报文:%s' % packet_filenames)
    # 对port2的报文进行分析（也就是下行的报文）
    if os.path.isfile(packet_filenames[1]):
        packets = rdpcap(packet_filenames[1])
        # cdata_info(packets)
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:11' and data['Ether'].dst == '00:00:00:22:22:21':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:11,2000转100)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:11,2000转100)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:12' and data['Ether'].dst == '00:00:00:22:22:22':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:12,2001转101)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:12,2001转101)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:13' and data['Ether'].dst == '00:00:00:22:22:23':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:13,2002转102)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:13,2002转102)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:14' and data['Ether'].dst == '00:00:00:22:22:24':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:14,2003转103)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:14,2003转103)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:15' and data['Ether'].dst == '00:00:00:22:22:25':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:15,2004转104)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:15,2004转104)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:16' and data['Ether'].dst == '00:00:00:22:22:26':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:16,2005转105)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:16,2005转105)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:17' and data['Ether'].dst == '00:00:00:22:22:27':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:17,2006转106)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:17,2006转106)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:18' and data['Ether'].dst == '00:00:00:22:22:28':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:18,2007)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:18,2007)数据流不带tag')
                break
    # 对port1的报文进行分析（也就是上行的报文）
    if os.path.isfile(packet_filenames[0]):
        packets = rdpcap(packet_filenames[0])
        # cdata_info(packets)
        for data in packets:
            if data['Ether'].dst == '00:00:00:11:11:11' and data['Ether'].src == '00:00:00:22:22:21':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'olt上联口接收到上行(srcmac==00:00:00:22:22:21,100转2000)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('olt上联口接收到上行(srcmac==00:00:00:22:22:21,100转2000)数据流不带tag')
                break
        for data in packets:
            if data['Ether'].dst == '00:00:00:11:11:12' and data['Ether'].src == '00:00:00:22:22:22':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'olt上联口接收到上行(srcmac==00:00:00:22:22:22,101转2001)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('olt上联口接收到上行(srcmac==00:00:00:22:22:22,101转2001)数据流不带tag')
                break
        for data in packets:
            if data['Ether'].dst == '00:00:00:11:11:13' and data['Ether'].src == '00:00:00:22:22:23':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'olt上联口接收到上行(srcmac==00:00:00:22:22:23,102转2002)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('olt上联口接收到上行(srcmac==00:00:00:22:22:23,2002转2002)数据流不带tag')
                break
        for data in packets:
            if data['Ether'].dst == '00:00:00:11:11:14' and data['Ether'].src == '00:00:00:22:22:24':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'olt上联口接收到上行(srcmac==00:00:00:22:22:24,103转2003)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('olt上联口接收到上行(srcmac==00:00:00:22:22:24,103转2003)数据流不带tag')
                break
        for data in packets:
            if data['Ether'].dst == '00:00:00:11:11:15' and data['Ether'].src == '00:00:00:22:22:25':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'olt上联口接收到上行(srcmac==00:00:00:22:22:25,104转2004)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('olt上联口接收到上行(srcmac==00:00:00:22:22:25,104转2004)数据流不带tag')
                break
        for data in packets:
            if data['Ether'].dst == '00:00:00:11:11:16' and data['Ether'].src == '00:00:00:22:22:26':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'olt上联口接收到上行(srcmac==00:00:00:22:22:26,105转2005)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('olt上联口接收到上行(srcmac==00:00:00:22:22:26,105转2005)数据流不带tag')
                break
        for data in packets:
            if data['Ether'].dst == '00:00:00:11:11:17' and data['Ether'].src == '00:00:00:22:22:27':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'olt上联口接收到上行(srcmac==00:00:00:22:22:27,106转2006)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('olt上联口接收到上行(srcmac==00:00:00:22:22:27,106转2006)数据流不带tag')
                break
        for data in packets:
            if data['Ether'].dst == '00:00:00:11:11:18' and data['Ether'].src == '00:00:00:22:22:28':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'olt上联口接收到上行(srcmac==00:00:00:22:22:28,107转2007)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('olt上联口接收到上行(srcmac==00:00:00:22:22:28,107转2007)数据流不带tag')
                break
    if stream_result=='PASS' and  tag_result == 'PASS':
        res = 'PASS'
    else:
        res = 'FAIL'

    return res

#onu端口为trunk时，打流测试
def streamstest_ont_port_vlan_trunk(port_location,packet_name):
# 清除测试仪的对象，防止影响下个用例的执行
    time.sleep(5)
    reset_rom_cmd = ResetROMCommand()
    reset_rom_cmd.execute()

    # 发流量测试，发送两条流2000，和vlan2001,和vlan2002
    # port_location = ['//192.168.0.180/1/9', '//192.168.0.180/1/10']
    duration = 10
    num = 8
    dataclassname = StreamBlockStats
    stream_header = ['Ethernet.ethernetII', 'VLAN.vlan', 'IPv4.ipv4', 'UDP.udp']

    down_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:11 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:22:22:21 ipv4_1.source=192.168.1.11 ipv4_1.destination=192.168.1.21',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:12 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:22:22:22 ipv4_1.source=192.168.1.12 ipv4_1.destination=192.168.1.22',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:13 vlan_1.id=2002  ethernetII_1.destMacAdd=00:00:00:22:22:23 ipv4_1.source=192.168.1.13 ipv4_1.destination=192.168.1.23',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:14 vlan_1.id=2003  ethernetII_1.destMacAdd=00:00:00:22:22:24 ipv4_1.source=192.168.1.14 ipv4_1.destination=192.168.1.24',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:15 vlan_1.id=2004  ethernetII_1.destMacAdd=00:00:00:22:22:25 ipv4_1.source=192.168.1.15 ipv4_1.destination=192.168.1.25',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:16 vlan_1.id=2005  ethernetII_1.destMacAdd=00:00:00:22:22:26 ipv4_1.source=192.168.1.16 ipv4_1.destination=192.168.1.26',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:17 vlan_1.id=2006  ethernetII_1.destMacAdd=00:00:00:22:22:27 ipv4_1.source=192.168.1.17 ipv4_1.destination=192.168.1.27',
        'ethernetII_1.sourceMacAdd=00:00:00:11:11:18 vlan_1.id=2007  ethernetII_1.destMacAdd=00:00:00:22:22:28 ipv4_1.source=192.168.1.18 ipv4_1.destination=192.168.1.28',
       # 'ethernetII_1.sourceMacAdd=00:00:00:11:11:19 vlan_1.id=2008  ethernetII_1.destMacAdd=00:00:00:22:22:29 ipv4_1.source=192.168.1.19 ipv4_1.destination=192.168.1.29'
    )

    up_stream_header = (
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:21 vlan_1.id=2000  ethernetII_1.destMacAdd=00:00:00:11:11:11 ipv4_1.source=192.168.1.21 ipv4_1.destination=192.168.1.11',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:22 vlan_1.id=2001  ethernetII_1.destMacAdd=00:00:00:11:11:12 ipv4_1.source=192.168.1.22 ipv4_1.destination=192.168.1.12',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:23 vlan_1.id=2002  ethernetII_1.destMacAdd=00:00:00:11:11:13 ipv4_1.source=192.168.1.23 ipv4_1.destination=192.168.1.13',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:24 vlan_1.id=2003  ethernetII_1.destMacAdd=00:00:00:11:11:14 ipv4_1.source=192.168.1.24 ipv4_1.destination=192.168.1.14',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:25 vlan_1.id=2004  ethernetII_1.destMacAdd=00:00:00:11:11:15 ipv4_1.source=192.168.1.25 ipv4_1.destination=192.168.1.15',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:26 vlan_1.id=2005  ethernetII_1.destMacAdd=00:00:00:11:11:16 ipv4_1.source=192.168.1.26 ipv4_1.destination=192.168.1.16',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:27 vlan_1.id=2006  ethernetII_1.destMacAdd=00:00:00:11:11:17 ipv4_1.source=192.168.1.27 ipv4_1.destination=192.168.1.17',
        'ethernetII_1.sourceMacAdd=00:00:00:22:22:28 vlan_1.id=2007  ethernetII_1.destMacAdd=00:00:00:11:11:18 ipv4_1.source=192.168.1.28 ipv4_1.destination=192.168.1.18',
        #'ethernetII_1.sourceMacAdd=00:00:00:22:22:29 vlan_1.id=2008  ethernetII_1.destMacAdd=00:00:00:11:11:19 ipv4_1.source=192.168.1.29 ipv4_1.destination=192.168.1.19'
    )
    result = unicast_test(port_location, down_stream_header,up_stream_header,packet_name,num, dataclassname,stream_header,duration)

    result_stats = result[0]

    for i in range(2*num):
        if (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:11':
            result11 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:12':
            result12 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:13':
            result13 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:14':
            result14 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:15':
            result15 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:16':
            result16 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:17':
            result17 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:21':
            result21 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:22':
            result22 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:23':
            result23 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:24':
            result24 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:25':
            result25 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:26':
            result26 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:27':
            result27 = check_stream_static1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:11:11:18':
            result18 = check_stream_loss1(result_stats[i])
        elif (result_stats[i].__dict__)['_StreamBlockID'] == 'sourceMacAdd=00:00:00:22:22:28':
            result28 = check_stream_loss1(result_stats[i])


    # 正确的结果vlan2000和vlan2001的能通，vlan2002的不通
    if result11 == 'PASS' and result12 == 'PASS' and result13 == 'PASS' and result14 == 'PASS' \
            and result15 == 'PASS' and result16 == 'PASS' and result17 == 'PASS' and result18 == 'PASS' \
            and result21 == 'PASS' and result22 == 'PASS' and result23 == 'PASS' and result24 == 'PASS' \
            and result25 == 'PASS' and result26 == 'PASS' and result27 == 'PASS' and result28 == 'PASS' :
        stream_result = 'PASS'
        cdata_info("ONU端口为trunk:打流测试正常")
    else:
        stream_result = 'FAIL'
        cdata_error("ONU端口为trunk:打流测试失败")

    # 判断如果文件存在，就开始分析报文
    tag_result = 'PASS'
    packet_filenames = result[1]
    # cdata_debug('待分析的报文:%s' % packet_filenames)
    # 对port2的报文进行分析（也就是下行的报文）
    if os.path.isfile(packet_filenames[1]):
        packets = rdpcap(packet_filenames[1])
        # cdata_info(packets)
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:11' and data['Ether'].dst == '00:00:00:22:22:21':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'onu端口接收到下行(srcmac==00:00:00:11:11:11,2000)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:11,2000)数据流不带tag')
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:12' and data['Ether'].dst == '00:00:00:22:22:22':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'onu端口接收到下行(srcmac==00:00:00:11:11:12,2001)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:12,2001)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:13' and data['Ether'].dst == '00:00:00:22:22:23':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'onu端口接收到下行(srcmac==00:00:00:11:11:13,2002)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:13,2002)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:14' and data['Ether'].dst == '00:00:00:22:22:24':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'onu端口接收到下行(srcmac==00:00:00:11:11:14,2003)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:14,2003)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:15' and data['Ether'].dst == '00:00:00:22:22:25':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'onu端口接收到下行(srcmac==00:00:00:11:11:15,2004)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:15,2004)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:16' and data['Ether'].dst == '00:00:00:22:22:26':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'onu端口接收到下行(srcmac==00:00:00:11:11:16,2005)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:16,2005)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:17' and data['Ether'].dst == '00:00:00:22:22:27':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'onu端口接收到下行(srcmac==00:00:00:11:11:17,2006)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:17,2006)数据流不带tag')
                    tag_result = 'FAIL'
                break
        for data in packets:
            if data['Ether'].src == '00:00:00:11:11:18' and data['Ether'].dst == '00:00:00:22:22:28':
                s = repr(data)
                # cdata_debug(s)
                # print((data['Ether'].decode()))
                if 'Dot1Q' in data:
                    cdata_info(
                        'onu端口接收到下行(srcmac==00:00:00:11:11:18,2007)数据流带tag %s' % (data['Dot1Q'].vlan))
                elif 'Dot1Q' not in data:
                    cdata_info('onu端口接收到下行(srcmac==00:00:00:11:11:18,2007)数据流不带tag')
                    tag_result = 'FAIL'
                break

    if stream_result == 'PASS' and tag_result == 'PASS':
        res = 'PASS'
    else:
        res = 'FAIL'
    return  res
#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client_MA5800 import *
import re

def gemport_del(tn,Ont_Lineprofile_ID,Gemport_ID='1',):
    # 判断当前的视图是否正确。
    tn.write(b"\n")
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    if result:
        pass
    else:
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    try:
        tn.write(('ont-lineprofile gpon profile-id %s' % (Ont_Lineprofile_ID)).encode() + b'\n')
        tn.read_until(b'{ <cr>|profile-name<K> }:', timeout=2)
        tn.write(b'\n')
        tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    except:
        raise Exception("该线路模板视图可能有其他人的在使用")
    for i in range(8):
        tn.write(('undo gem mapping %s %s'%(Gemport_ID,i)).encode()+b'\n')
        tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    # tn.write(b'display ont-lineprofile current' + b'\n')
    # tn.read_until(b'{ <cr>||<K> }:', timeout=2)
    # tn.write(b'\n')
    # command_result = tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
    #                                timeout=2).decode("utf-8")
    # #print((command_result.split('--------------------------------------------------------------------')[3]).split('\r\n')[3])
    # print((command_result.split('--------------------------------------------------------------------')))

def gemport_vlan(tn,Ont_Lineprofile_ID,Vlan_list,Gemport_ID,mapping_mode='vlan'):
    #进入线路模板视图，并且将Gemport_ID的gem mapping全部清除
    gemport_del(tn, Ont_Lineprofile_ID, Gemport_ID )
    # 修改mapping-mode is vlan
    tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    # 判断mapping_mode设置是否正常
    tn.write(b'display ont-lineprofile current ' + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ',timeout=2)
    tn.write(b'\n')
    result = tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(),timeout=2).decode("utf-8")
    if "Mapping mode        :VLAN" in result:
        cdata_info("线路模板:mapping_mode设置成vlan正常")
    else:
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成vlan失败")
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    for i in range(len(Vlan_list)):
        # 配置gem mapping 为vlan2000
        tn.write(('gem mapping %s %s vlan %s'%(Gemport_ID,str(i),Vlan_list[i])).encode() + b'\n')
        tn.read_until(b'{ <cr>|flow-car<K>|priority<K>|transparent<K> }: ',timeout=2)
        tn.write(b'\n')
        tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
        tn.write(b'display ont-lineprofile current' + b'\n')
        tn.read_until(b'{ <cr>||<K> }:',timeout=2)
        tn.write(b'\n')
        command_result = tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
                                       timeout=2).decode("utf-8")
        #'1       2000  - '
        if re.search(r"%s(\s+)%s(\s+)-"%(str(i),Vlan_list[i]), command_result):
            cdata_info('线路模板:配置gem mapping 为%s成功'%Vlan_list[i])
        else:
            cdata_error("===============ERROR!!!===================")
            cdata_error('线路模板:配置gem mapping 为vlan%s失败'%Vlan_list[i])
            cdata_error("==========================================")
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
            tn.write(b'quit' + b'\n')
            return False
    cdata_info('线路模板:配置gem mapping 为%s成功' % Vlan_list)
    # 保存配置，退出线路模板
    tn.write(b'commit' + b'\n')
    tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'quit' + b'\n')
    return True

def gemport_vlan_pri(tn,Ont_Lineprofile_ID,Vlan_pri_list,Gemport_ID,mapping_mode='vlan-priority '):
    '''
    配置mapping-mode为vlan-priority，gem mapping 1 1 vlan 2000 pri 2为透传
    :param tn: telnet登录对象
    :param mapping_mode: mapping-mode 的模式
    '''
    # Vlan_pri_list=[(2000,2)]
    cdata_info("配置mapping_mode为vlan+pri")
    # 进入线路模板视图，并且将Gemport_ID的gem mapping全部清除
    gemport_del(tn, Ont_Lineprofile_ID, Gemport_ID)

    # 修改mapping-mode is vlan_pri
    tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    # 判断mapping_mode设置是否正常
    tn.write(b'display ont-lineprofile current ' + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ', timeout=2)
    tn.write(b'\n')
    result = tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(),
                           timeout=2).decode("utf-8")

    #re.search(r'Mapping mode(\s+):VLAN+802.1p PRI',result)

    if "Mapping mode        :VLAN+802.1p PRI" in result:
        cdata_info("线路模板:mapping_mode设置成vlan+pri正常")
    else:
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成vlan+pri失败")
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

    # 配置gem mapping 为vlan+pri
    for i in range(len(Vlan_pri_list)):
        tn.write(('gem mapping  %s %s vlan %s priority %s '%(Gemport_ID,str(i),Vlan_pri_list[i][0],Vlan_pri_list[i][1])).encode() + b'\n')
        tn.read_until(b'{ <cr>|flow-car<K>|priority<K>|transparent<K> }: ', timeout=2)
        tn.write(b'\n')
        tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'display ont-lineprofile current' + b'\n')
    tn.read_until(b'{ <cr>||<K> }:', timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
                                   timeout=2).decode("utf-8")
    for i in range(len(Vlan_pri_list)):
        # '1       2000  2 '
        if re.search(r"%s(\s+)%s(\s+)%s(\s+)" % (str(i),Vlan_pri_list[i][0], Vlan_pri_list[i][1]), command_result):
            continue
        else:
            cdata_error("===============ERROR!!!===================")
            cdata_error('线路模板:配置gem mapping 为vlan%s+pri%s失败'%(Vlan_pri_list[i][0], Vlan_pri_list[i][1]))
            cdata_error("==========================================")
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
            tn.write(b'quit' + b'\n')
            return False
    cdata_info('线路模板:配置gem mapping 为vlan+pri %s成功'%Vlan_pri_list)
    # 保存配置，退出线路模板
    tn.write(b'commit' + b'\n')
    tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'quit' + b'\n')
    return True

def gemport_pri(tn,Ont_Lineprofile_ID,Pir_list,Gemport_ID,mapping_mode='priority'):

    # Pir_list=[2]
    # 进入线路模板视图下
    cdata_info("配置mapping_mode为pri")
    # 进入线路模板视图，并且将Gemport_ID的gem mapping全部清除
    gemport_del(tn, Ont_Lineprofile_ID, Gemport_ID)

    # 修改mapping-mode is vlan
    tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    # 判断mapping_mode设置是否正常
    tn.write(b'display ont-lineprofile current ' + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ', timeout=2)
    tn.write(b'\n')
    result = tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(),
                           timeout=2).decode("utf-8")

    # re.search(r'Mapping mode(\s+):VLAN+802.1p PRI',result)

    if "Mapping mode        :802.1p PRI" in result:
        cdata_info("线路模板:mapping_mode设置成pri正常")
    else:
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成pri失败")
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

    # 配置gem mapping 为pri
    for i in range(len(Pir_list)):

        tn.write(('gem mapping %s %s priority %s '%(Gemport_ID,str(i),Pir_list[i])).encode() + b'\n')
        tn.read_until(b'{ <cr>|flow-car<K>|priority<K>|transparent<K> }: ', timeout=2)
        tn.write(b'\n')
        tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'display ont-lineprofile current' + b'\n')
    tn.read_until(b'{ <cr>||<K> }:', timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
                                   timeout=2).decode("utf-8")
    for i in range(len(Pir_list)):
        # '1       -     2'
        if re.search(r"%s(\s+)-(\s+)%s(\s+)" % (str(i), Pir_list[i]), command_result):
            continue
        else:
            cdata_error("===============ERROR!!!===================")
            cdata_error('线路模板:配置gem mapping 为pri%s失败' % (Pir_list[i]))
            cdata_error("==========================================")
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
            tn.write(b'quit' + b'\n')
            return False
    cdata_info('线路模板:配置gem mapping 为pri %s成功'% Pir_list)
    # 保存配置，退出线路模板
    tn.write(b'commit' + b'\n')
    tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'quit' + b'\n')
    return True

def gemport_port(tn,Ont_Lineprofile_ID,Port_list,Gemport_ID,mapping_mode='port'):
    # 判断当前的视图是否正确。
    # 进入线路模板视图下
    cdata_info("配置mapping-mode为port")

    # 进入线路模板视图，并且将Gemport_ID的gem mapping全部清除
    gemport_del(tn, Ont_Lineprofile_ID, Gemport_ID)

    # 修改mapping-mode is vlan
    tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    # 判断mapping_mode设置是否正常
    tn.write(b'display ont-lineprofile current ' + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ', timeout=2)
    tn.write(b'\n')
    result = tn.read_until(('MA5800-X15(config-gpon-lineprofile-%s)#' % (Ont_Lineprofile_ID)).encode(),
                           timeout=2).decode("utf-8")

    # re.search(r'Mapping mode(\s+):VLAN+802.1p PRI',result)

    if "Mapping mode        :PORT" in result:
        cdata_info("线路模板:mapping_mode设置成port正常")
    else:
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成port失败")
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

    # 配置gem mapping 为PORT
    for i in range(len(Port_list)):
        tn.write(('gem mapping %s %s eth %s  '%(Gemport_ID,str(i),Port_list[i])).encode() + b'\n')
        tn.read_until(b'{ <cr>|flow-car<K>|priority<K>|transparent<K> }: ', timeout=2)
        tn.write(b'\n')
        tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'display ont-lineprofile current' + b'\n')
    tn.read_until(b'{ <cr>||<K> }:', timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
                                   timeout=2).decode("utf-8")
    for i in range(len(Port_list)):
        #'1       -     -        ETH     2'
        if re.search(r"%s(\s+)-(\s+)-(\s+)ETH(\s+)%s(\s+)" % (str(i), Port_list[i]), command_result):
            continue
        else:
            cdata_error("===============ERROR!!!===================")
            cdata_error('线路模板:配置gem mapping 为port%s失败' % (Port_list[i]))
            cdata_error("==========================================")
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
            tn.write(b'quit' + b'\n')
            return False
    cdata_info('线路模板:配置gem mapping 为port%s成功' % Port_list)
    # 保存配置，退出线路模板
    tn.write(b'commit' + b'\n')
    tn.read_until('MA5800-X15(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'quit' + b'\n')
    return True


if __name__ == '__main__':
    tn = telnet_host(host_ip='192.168.5.82', username='test111', password='test123')[0]
    gemport_port(tn, Ont_Lineprofile_ID, Port_list=[1], Gemport_ID='1', mapping_mode='port')
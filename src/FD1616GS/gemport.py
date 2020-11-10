#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI
import time
from src.config.telnet_client import *
import logging
from src.config.Cdata_loggers import *
import re
# initialize(log_level=logging.INFO)

# def ont_lineprofile_view(tn,Ont_Lineprofile_ID):
#     '''
#     进入线路模板视图
#     '''
#     tn.read_until(b'OLT(config)# ', timeout=2)
#     tn.write('ont-lineprofile gpon profile-id {} '.format(Ont_Lineprofile_ID).encode() + b'\n')

def change_mapping_mode(tn,mapping_mode,Ont_Lineprofile_ID):
    '''
    配置mapping-mode ，可以是（vlan,vlan_pri,pri,port）
    '''
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode()+ b'\n')

def gemport_transparent(tn,Ont_Lineprofile_ID,Gemport_ID,mapping_mode='vlan'):
    '''
    配置mapping-mode为vlan，gem mapping 1 1 为透传
    :param tn: telnet登录对象
    :param mapping_mode: mapping-mode 的模式
    :return: None
    '''
    cdata_info("配置gemport为transparent")
    # 判断当前的视图是否正确。
    # 进入线路模板视图下
    tn.write('ont-lineprofile gpon profile-id {} '.format(Ont_Lineprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    if result:
        pass
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        print("==========================================")
        tn.write(b"commit" + b"\n")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 删除gemport_id 下的所有mapping
    for i in range(1,9):
        tn.write(('no gem mapping  %s  %s '%(Gemport_ID,i)).encode() + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    # 修改mapping-mode为vlan
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    #判断mapping_mode设置是否正常
    tn.write(b'show ont-lineprofile current' + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2).decode("utf-8")
    if "Mapping mode     : VLAN" in result:
        cdata_info("线路模板:mapping_mode设置成vlan正常")
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成vlan失败")
        print("==========================================")
        tn.write(b"commit" + b"\n")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 配置gemport_id mapping 1 为transparent
    tn.write(('gem mapping  %s  1 vlan  transparent'%Gemport_ID).encode() + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-lineprofile current' + b'\n')
    command_result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),timeout=2).decode("utf-8")
    # print((command_result.split('----------------------------------------------------------------------------'))[3])
    if '1           -         -             -' in command_result:
        cdata_info('线路模板:配置gemport %s为transparent成功'%Gemport_ID)
        # 保存配置，退出线路模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('线路模板:配置gemport %s为transparent失败'%Gemport_ID)
        print("==========================================")
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

def gemport_vlan(tn,Ont_Lineprofile_ID,Vlan_list,Gemport_ID,mapping_mode='vlan'):
    '''
        配置mapping-mode为vlan，gem mapping 1 vlan 2000 为透传
        :param tn: telnet登录对象
        :param mapping_mode: mapping-mode 的模式
        :return: None
        '''
    cdata_info("配置mapping_mode为vlan")
    # 判断当前的视图是否正确。
    # 进入线路模板视图下
    tn.write('ont-lineprofile gpon profile-id {} '.format(Ont_Lineprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    if result:
        pass
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        print("==========================================")
        tn.write(b"commit"+b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 删除gemport_id 下的所有mapping
    for i in range(1, 9):
        tn.write(('no gem mapping  %s  %s ' % (Gemport_ID, i)).encode() + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    #修改mapping-mode is vlan
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    # 判断mapping_mode设置是否正常
    tn.write(b'show ont-lineprofile current' + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
                           timeout=2).decode("utf-8")
    if "Mapping mode     : VLAN" in result:
        cdata_info("线路模板:mapping_mode设置成vlan正常")
    else:
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成vlan失败")
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    #配置gem mapping 为Vlan_list
    for i in range(len(Vlan_list)):
        tn.write(('gem mapping %s %s vlan %s'%(Gemport_ID,str(i+1),str(Vlan_list[i]))).encode()+b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
        tn.write(b'show ont-lineprofile current' + b'\n')
        command_result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
                                       timeout=2).decode("utf-8")
        #判断mapping配置是否正常
        # '1           2000      -             - '
        if re.search(r"%s(\s+)%s(\s+)-(\s+)-" % (str(i+1), Vlan_list[i]), command_result):
        # if '1           2000      -             - ' in command_result:
            cdata_info('线路模板:配置gem mapping 为%s成功'%Vlan_list[i])

        else:
            print("==========================================")
            print("===============ERROR!!!===================")
            cdata_error('线路模板:配置gem mapping 为vlan%s失败'%Vlan_list[i])
            print("==========================================")
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    # 保存配置，退出线路模板
    cdata_info('线路模板:配置gem mapping 为%s成功' % Vlan_list)
    tn.write(b'commit' + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'exit' + b'\n')
    return True


def gemport_vlan_pri(tn,Ont_Lineprofile_ID,Vlan_pri_list,Gemport_ID,mapping_mode='vlan-priority '):
    '''
    配置mapping-mode为vlan-priority，gem mapping 1 1 vlan 2000 pri 2为透传
    :param tn: telnet登录对象
    :param mapping_mode: mapping-mode 的模式
    :param Vlan_pri_list: vlan+pri ,举例[(2000,2),(3000,3)],The Gem port can be mapped only to the flow with same VLAN or Same Priority
    '''
    cdata_info("配置mapping_mode为vlan+pri")
    # 判断当前的视图是否正确。
    # 进入线路模板视图下
    tn.write('ont-lineprofile gpon profile-id {} '.format(Ont_Lineprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    if result:
        pass
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 删除gemport_id 下的所有mapping
    for i in range(1, 9):
        tn.write(('no gem mapping  %s  %s ' % (Gemport_ID, str(i))).encode() + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)

    #修改mapping-mode is vlan-priority
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    # 判断mapping_mode设置是否正常
    tn.write(b'show ont-lineprofile current' + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
                           timeout=2).decode("utf-8")
    if " Mapping mode     : VLAN + 802.1p PRI" in result:
        cdata_info("线路模板:mapping_mode设置成vlan+pri正常")
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成vlan+pri失败")
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    for i in range(len(Vlan_pri_list)):
        print(str(i+1))
        #配置gem mapping 为vlan 2000+pri 2
        tn.write((' gem mapping  %s %s vlan %s priority %s '%(Gemport_ID,str(i+1),Vlan_pri_list[i][0],Vlan_pri_list[i][1])).encode() + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
        tn.write(b'show ont-lineprofile current' + b'\n')
        command_result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2).decode("utf-8")
        if re.search(r"%s(\s+)%s(\s+)%s(\s+)-" % (str(i+1), Vlan_pri_list[i][0], Vlan_pri_list[i][1]), command_result):
        # if '1           2000      2             - ' in command_result:
            cdata_info('线路模板:配置gem mapping 为vlan %s+pri %s成功'%(Vlan_pri_list[i][0],Vlan_pri_list[i][1]))

        else:
            cdata_error('线路模板:配置gem mapping 为vlan %s+pri %s失败'%(Vlan_pri_list[i][0],Vlan_pri_list[i][1]))
            tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False

    # 保存配置，退出线路模板
    cdata_info('线路模板:配置gem mapping 为vlan +pri %s成功' % (Vlan_pri_list))
    tn.write(b'commit' + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'exit' + b'\n')
    return True

def gemport_pri(tn,Ont_Lineprofile_ID,Pir_list,Gemport_ID,mapping_mode='priority'):

    # 判断当前的视图是否正确。
    # 进入线路模板视图下
    cdata_info("配置mapping_mode为pri")
    tn.write('ont-lineprofile gpon profile-id {} '.format(Ont_Lineprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    if result:
        pass
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 删除gemport_id 下的所有mapping
    for i in range(8):
        tn.write(('no gem mapping  %s  %s ' % (Gemport_ID, str(i+1))).encode() + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)

    # 修改mapping-mode is priority
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    # 判断mapping_mode设置是否正常
    tn.write(b'show ont-lineprofile current' + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
                           timeout=2).decode("utf-8")
    if " Mapping mode     : 802.1p PRI" in result:
        cdata_info("线路模板:mapping_mode设置成pri正常")
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成pri失败")
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 配置gem mapping 为Pir_list
    for i in range(len(Pir_list)):
        tn.write((' gem mapping %s %s priority %s  '%(Gemport_ID,str(i+1),Pir_list[i])).encode() + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
        tn.write(b'show ont-lineprofile current' + b'\n')
        command_result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
                                       timeout=2).decode("utf-8")
        if re.search(r"%s(\s+)-(\s+)%s(\s+)-" % (str(i+1), Pir_list[i]), command_result):
        # if '1           -         2             - ' in command_result:
            cdata_info('线路模板配置gem mapping 为pri%s成功'%Pir_list[i])

        else:
            cdata_error('线路模板配置gem mapping pri%s失败'%Pir_list[i])
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    # 保存配置，退出线路模板
    cdata_info('线路模板配置gem mapping 为pri %s成功' % Pir_list)
    tn.write(b'commit' + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'exit' + b'\n')
    return True

def gemport_port(tn,Ont_Lineprofile_ID,Port_list,Gemport_ID,mapping_mode='port'):
    '''
    :param tn:
    :param Ont_Lineprofile_ID:
    :param Port_list: list ,举例[2,3], Error: The Gem port can be mapped only to the flow with same Port and Same Vlan or Priority.
    :param Gemport_ID:
    :param mapping_mode:default is port
    :return:
    '''
    # 判断当前的视图是否正确。
    # 进入线路模板视图下
    cdata_info("配置mapping-mode为port")

    tn.write('ont-lineprofile gpon profile-id {} '.format(Ont_Lineprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    if result:
        pass
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
    # 删除gemport_id 下的所有mapping
    for i in range(8):
        tn.write(('no gem mapping  %s  %s ' % (Gemport_ID, str(i + 1))).encode() + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    # 修改mapping-mode is port
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    # 判断mapping_mode设置是否正常
    tn.write(b'show ont-lineprofile current' + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
                           timeout=2).decode("utf-8")
    if " Mapping mode     : PORT" in result:
        cdata_info("线路模板:mapping_mode设置成port正常")
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成port失败")
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
    # 配置gem mapping 为port 2
    for i in range(len(Port_list)):
        tn.write(('gem mapping %s %s eth %s '%(Gemport_ID,str(i+1),Port_list[i])).encode() + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
        tn.write(b'show ont-lineprofile current' + b'\n')
        command_result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(),
                                       timeout=2).decode("utf-8")
        if re.search(r"%s(\s+)-(\s+)-(\s+)%s(\s+)" % (str(i+1), Port_list[i]), command_result):
        # if '1           -         -             %s '%(Ont_Port_ID) in command_result:
            cdata_info('线路模板配置gem mapping 为port %s成功'%Port_list[i])

        else:
            cdata_error('线路模板配置gem mapping 为port %s失败'%Port_list[i])
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False

    # 保存配置，退出线路模板
    cdata_info('线路模板配置gem mapping 为port %s成功' % Port_list)
    tn.write(b'commit' + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'exit' + b'\n')
    return True


if __name__ == '__main__':
    host_ip = '192.168.0.181'
    username = 'root'
    password = 'admin'
    tn = telnet_host(host_ip, username, password)[0]
    # gemport_vlan(tn, Ont_Lineprofile_ID='200', Vlan_list=[2000,3000], Gemport_ID='1', mapping_mode='vlan')
    # gemport_vlan_pri(tn, Ont_Lineprofile_ID='200', Vlan_pri_list=[(2000,2),(2000,4)], Gemport_ID='1', mapping_mode='vlan-priority ')
    # gemport_pri(tn, Ont_Lineprofile_ID='200', Pir_list=[3,2], Gemport_ID='1', mapping_mode='priority')
    # gemport_port(tn, Ont_Lineprofile_ID='200', Port_list=[3,1], Gemport_ID='1', mapping_mode='port')
    # gemport_port(tn)
    # gemport_vlan(tn)
    # gemport_pri(tn)
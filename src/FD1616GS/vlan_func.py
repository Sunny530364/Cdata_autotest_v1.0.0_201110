#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
from src.config.Cdata_loggers import *
import re

def ont_port_transparent_profile(tn,Ont_Srvprofile_ID):
    '''
    config ont  port 1-4 is transparent ,
    '''
    # 进入服务模板视图下
    tn.write('ont-srvprofile gpon profile-id {} '.format(Ont_Srvprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    #配置ont port1-4为transaprent
    tn.write(b'port vlan eth 1-4 transparent' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current'+ b'\n')
    command_result =  tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2).decode("utf-8")
    if "ETH    1    Transparent"  in command_result and "ETH    2    Transparent"  in command_result\
            and "ETH    3    Transparent"  in command_result and "ETH    4    Transparent"  in command_result:
        cdata_info("配置onu eth1-4 vlan为transparent成功")
        #保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error("配置onu eth1-4 vlan为transparent失败")
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

def ont_port_trunk_profile(tn,Ont_Srvprofile_ID,Ont_Port_ID,Vlan_list):
    # 进入服务模板视图下
    tn.write('ont-srvprofile gpon profile-id {} '.format(Ont_Srvprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    for vlanid in Vlan_list:
        tn.write(('port  vlan eth %s %s'%(Ont_Port_ID,vlanid)).encode()+b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current' + b'\n')
    command_result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2).decode()
    for i in range(len(Vlan_list)):
        if re.search(r"%s(\s+)-(\s+)%s" % (Vlan_list[i], Vlan_list[i]),command_result):
            continue
        else:
            cdata_error("配置onu 端口 vlan为trunk%s失败"%Vlan_list)
            # 保存配置，退出服务模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    cdata_info("配置onu 端口 vlan为trunk %s成功"%Vlan_list)
    # 保存配置，退出服务模板
    tn.write(b'commit' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'exit' + b'\n')
    return True

def ont_port_vlan_del_profile(tn,Ont_Srvprofile_ID,Ont_Port_ID,Vlan_list):
    # 进入服务模板视图下
    tn.write('ont-srvprofile gpon profile-id {} '.format(Ont_Srvprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    for i in range(len(Vlan_list)):
        tn.write((' no port  vlan eth %s %s'%(Ont_Port_ID,Vlan_list[i])).encode() + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current' + b'\n')
    command_result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(),timeout=2).decode()
    if "ETH    %s    Transparent  "%Ont_Port_ID in command_result:
        cdata_info("删除onu eth %s的vlan 成功"%Ont_Port_ID)
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error("删除onu eth%s的vlan失败"%Ont_Port_ID)
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

def ont_port_translate_profile(tn,Ont_Srvprofile_ID,Ont_Port_ID,S_Vlan_list,C_Vlan_list):
    '''
    config  ont port 1 translation , vlan 100——>2000,vlan 200——>2001
    '''
    # 进入服务模板视图下
    tn.write('ont-srvprofile gpon profile-id {} '.format(Ont_Srvprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    for i in range(len(S_Vlan_list)):
        tn.write(('port  vlan eth %s translation %s user-vlan %s' % (Ont_Port_ID, S_Vlan_list[i], C_Vlan_list[i])).encode() + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current' + b'\n')
    command_result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2).decode()

    for i in range(len(C_Vlan_list)):
        #"2000   -     100    -"
        if re.search(r"%s(\s+)-(\s+)%s(\s+)-" % (S_Vlan_list[i], C_Vlan_list[i]), command_result):
            continue
        else:
            cdata_error("配置onu 端口 vlan为translate %s 转 %s失败" % (C_Vlan_list, S_Vlan_list))
            # 保存配置，退出服务模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    cdata_info("配置onu 端口 vlan为translate %s 转 %s成功" % (C_Vlan_list, S_Vlan_list))
    # 保存配置，退出服务模板
    tn.write(b'commit' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'exit' + b'\n')
    return True


# def ont_port_translate_del(tn,Ont_Srvprofile_ID,Ont_Port_ID,Vlan_list):
#     '''
#      delete ont port 1 translate vlan 100,200,300,400,500,600,700,800
#      '''
#     # 进入服务模板视图下
#     tn.write('ont-srvprofile gpon profile-id {} '.format(Ont_Srvprofile_ID).encode() + b'\n')
#     result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
#     if result:
#         pass
#     else:
#         cdata_info("==========================================")
#         cdata_error("===============ERROR!!!===================")
#         cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
#         cdata_info("==========================================")
#         tn.write(b"commit" + b'\n')
#         tn.write(b"exit" + b"\n")
#         result = tn.read_until(b"OLT(config)#", timeout=2)
#         return False
#
#     # 删除配置onu 端口1vlan100
#     for i in range(len(Vlan_list)):
#         tn.write(b' no port  vlan eth %s %s'%(Ont_Port_ID,Vlan_list[i]) + b'\n')
#         tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
#     tn.write(b'show ont-srvprofile current' + b'\n')
#     command_result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(),timeout=2).decode()
#     if "ETH    1    Transparent" in command_result:
#         cdata_info("删除onu eth1的vlan 成功")
#         # 保存配置，退出服务模板
#         tn.write(b'commit' + b'\n')
#         tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
#         tn.write(b'exit' + b'\n')
#         return True
#     else:
#         cdata_error("删除onu eth1的vlan失败")
#         # 保存配置，退出服务模板
#         tn.write(b'commit' + b'\n')
#         tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
#         tn.write(b'exit' + b'\n')
#         return False

if __name__ == '__main__':
    host_ip = '192.168.0.181'
    username = 'root'
    password = 'admin'
    tn = telnet_host(host_ip, username, password)[0]
    # ont_port_trunk(tn, Ont_Srvprofile_ID='200', Ont_Port_ID='1',Vlan_list=[2000,2004,2001])
    # ont_port_trunk_del(tn, Ont_Srvprofile_ID='200', Ont_Port_ID='1',Vlan_list=[2000,2004,2001])
    S_Vlan_list = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]
    C_Vlan_list = [100, 101, 102, 103, 104, 105, 106, 107]
    ont_port_translate(tn, Ont_Srvprofile_ID='200', Ont_Port_ID='1', S_Vlan_list=S_Vlan_list, C_Vlan_list=C_Vlan_list)
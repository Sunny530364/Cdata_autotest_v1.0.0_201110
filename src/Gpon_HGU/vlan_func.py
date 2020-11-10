#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
from src.config.Cdata_loggers import *

def ont_port_transparent(tn,ont_srvprofile_id=200):
    '''
    config ont  port 1-4 is transparent ,
    '''
    # 进入服务模板视图下
    tn.write('ont-srvprofile gpon profile-id {} '.format(ont_srvprofile_id).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
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
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current'+ b'\n')
    command_result =  tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2).decode("utf-8")
    if "ETH    1    Transparent"  in command_result and "ETH    2    Transparent"  in command_result\
            and "ETH    3    Transparent"  in command_result and "ETH    4    Transparent"  in command_result:
        cdata_info("配置onu eth1-4 vlan为transparent成功")
        #保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error("配置onu eth1-4 vlan为transparent失败")
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

def ont_port_trunk(tn,ont_srvprofile_id=200):
    '''
    config ont port 1 trunk vlan 2000,2001
    '''
    # 进入服务模板视图下
    tn.write('ont-srvprofile gpon profile-id {} '.format(ont_srvprofile_id).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
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

    #配置onu 端口1为trunk 2000
    tn.write(b'port  vlan eth 1 2000-2007' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current' + b'\n')
    time.sleep(0.1)
    tn.write(b'\n')
    time.sleep(1)
    command_result = tn.read_very_eager().decode("utf-8")
    if "2000   -     2000" in command_result and "2001   -     2001" in command_result \
            and "2002   -     2002" in command_result and "2003   -     2003" in command_result \
            and "2004   -     2004" in command_result and "2005   -     2005" in command_result\
            and "2006   -     2006" in command_result and "2007   -     2007" in command_result:
        cdata_info("配置onu eth1-4 vlan为trunk 2000—2007成功")
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error("配置onu eth1-4 vlan为trunk 2000—2007失败")
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

def ont_port_trunk_del(tn,ont_srvprofile_id=200):
    '''
     delete ont port 1 trunk vlan 2000,2001
        '''
    # 进入服务模板视图下
    tn.write('ont-srvprofile gpon profile-id {} '.format(ont_srvprofile_id).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
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

    # 配置onu 端口1为trunk 2000
    tn.write(b' no port  vlan eth 1 2000-2007' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current' + b'\n')
    time.sleep(0.1)
    tn.write(b'\n')
    time.sleep(1)
    command_result = tn.read_very_eager().decode("utf-8")
    print(command_result)
    if "ETH    1    Transparent  " in command_result:
        cdata_info("删除onu eth1的vlan 成功")
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error("删除onu eth1的vlan失败")
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

def ont_port_translate(tn,ont_srvprofile_id=200):
    '''
    config  ont port 1 translation , vlan 100——>2000,vlan 200——>2001
    '''
    # 进入服务模板视图下
    tn.write('ont-srvprofile gpon profile-id {} '.format(ont_srvprofile_id).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
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

    #配置onu端口1 为user-vlan 100转2000
    tn.write(b'port  vlan eth 1 translation 2000 user-vlan 100' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    # 配置onu端口1 为user-vlan 200转2001
    tn.write(b'port  vlan eth 1 translation 2001 user-vlan 101' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    # 配置onu端口1 为user-vlan 300转2002
    tn.write(b'port  vlan eth 1 translation 2002 user-vlan 102' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    # 配置onu端口1 为user-vlan 400转2003
    tn.write(b'port  vlan eth 1 translation 2003 user-vlan 103' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    # 配置onu端口1 为user-vlan 500转2004
    tn.write(b'port  vlan eth 1 translation 2004 user-vlan 104' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    # 配置onu端口1 为user-vlan 600转2005
    tn.write(b'port  vlan eth 1 translation 2005 user-vlan 105' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    # 配置onu端口1 为user-vlan 700转2006
    tn.write(b'port  vlan eth 1 translation 2006 user-vlan 106' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    # 配置onu端口1 为user-vlan 800转2007
    tn.write(b'port  vlan eth 1 translation 2007 user-vlan 107' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current' + b'\n')
    time.sleep(0.1)
    tn.write(b'\n')
    time.sleep(1)
    command_result = tn.read_very_eager().decode("utf-8")
    if "2000   -     100    -" in command_result and "2001   -     101    -" in command_result \
            and "2002   -     102    -" in command_result and "2003   -     103    -" in command_result \
            and "2004   -     104    -" in command_result and "2005   -     105    -" in command_result \
            and "2006   -     106    -" in command_result and "2007   -     107    -" in command_result:
        cdata_info("配置onu eth1-4 vlan为translate100-107转2000-2007成功")
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error("配置onu eth1 vlan为translate100-107转2000-2007失败")
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

    #保存配置，退出服务模板
    tn.write(b'commit' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    tn.write(b'exit' + b'\n')

def ont_port_translate_del(tn,ont_srvprofile_id=200):
    '''
     delete ont port 1 translate vlan 100,200,300,400,500,600,700,800
     '''
    # 进入服务模板视图下
    tn.write('ont-srvprofile gpon profile-id {} '.format(ont_srvprofile_id).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
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

    # 删除配置onu 端口1vlan100
    tn.write(b' no port  vlan eth 1 100-107' + b'\n')
    tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current' + b'\n')
    time.sleep(0.1)
    tn.write(b'\n')
    time.sleep(1)
    command_result = tn.read_very_eager().decode("utf-8")
    if "ETH    1    Transparent" in command_result:
        cdata_info("删除onu eth1的vlan 成功")
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error("删除onu eth1的vlan失败")
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-srvprofile-{})#  '.format(ont_srvprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

if __name__ == '__main__':
    host_ip = '192.168.5.164'
    username = 'root'
    password = 'admin'
    tn = telnet_host(host_ip, username, password)[0]
    ont_port_translate(tn)
    ont_port_translate_del(tn)
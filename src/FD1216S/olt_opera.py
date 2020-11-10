#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
# from src.config.initialization_config import *
from src.config.Cdata_loggers import *
from telnetlib import Telnet
import time

def load_config(tn,tftp_server_ip,olt_config_file):
    tn.write('load configuration format txt tftp {} {} '.format(tftp_server_ip,olt_config_file).encode() + b'\n')
    #result = tn.read_until(b'OLT(config)# ', timeout=2)
    time.sleep(0.1)
    tn.write(b'y'+b'\n')
    result = tn.read_until(b'OLT(config)# ', timeout=20).decode('utf-8')
    if 'The loading is successful!' in result:
        cdata_info('配置下载正常')

    else:
        cdata_error('配置下载失败')
        return False
    tn.write(b'reboot'+b'\n')
    tn.write(b'y' + b'\n')
    return True

def check_telnet(host_ip):
    for i in range(6):
        try:
            Telnet(host_ip, port=23)
        except:
            cdata_info('设备重启中。。。')
            time.sleep(30)
            continue
        cdata_info('重启后设备登录成功')
        time.sleep(10)
        return True

def no_shutdown_epon(tn,PonID):
    try:
        tn.write(b'interface epon 0/0'+b'\n')
        result = tn.read_until(b'OLT(config-interface-epon-0/0)#',timeout=2)
        tn.write(('no shutdown %s'%PonID).encode()+b'\n')
        result = tn.read_until(b'OLT(config-interface-epon-0/0)#', timeout=2)
        tn.write(('show port state %s'%PonID).encode()+b'\n')
        time.sleep(1)
        result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2).decode('utf-8')
        print(result)
        if 'Enable state                     : Enable' in result:
            cdata_info('pon %s 端口使能成功'%PonID)
            tn.write(b'exit \n')
            tn.read_until(b'OLT(config)# ', timeout=2)
            return True
        else:
            cdata_error('pon %s 端口使能失败'%PonID)
            tn.write(b'exit \n')
            tn.read_until(b'OLT(config)# ', timeout=2)
            return False
            # raise Exception("OLT_PON %s 端口未使能成功"%PonID)
    except:
        cdata_error('pon %s 端口使能失败')
        tn.write(b'exit \n')
        tn.read_until(b'OLT(config)# ', timeout=2)
        return False
        # raise Exception("OLT_PON %s 端口未使能成功" % PonID)

def shutdown_epon(tn,PonID):
    try:
        tn.write(b'interface epon 0/0'+b'\n')
        result = tn.read_until(b'OLT(config-interface-epon-0/0)#',timeout=2)
        tn.write(('shutdown %s'%PonID).encode()+b'\n')
        result = tn.read_until(b'OLT(config-interface-epon-0/0)#', timeout=2)
        tn.write(('show port state %s'%PonID).encode()+b'\n')
        time.sleep(1)
        result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2).decode('utf-8')
        if 'Enable state                     : Disable' in result:
            cdata_info('pon %s 端口去使能'%PonID)
            tn.write(b'exit \n')
            tn.read_until(b'OLT(config)# ', timeout=2)
            return True
        else:
            cdata_error('pon %s 端口去使能失败'%PonID)
            tn.write(b'exit \n')
            tn.read_until(b'OLT(config)# ', timeout=2)
            return False
    except:
        # raise Exception("OLT_PON %s 端口去使能使能" % PonID)
        cdata_error('pon %s 端口去使能失败' % PonID)
        tn.write(b'exit \n')
        tn.read_until(b'OLT(config)# ', timeout=2)
        return False



if __name__ == '__main__':
    host_ip = '192.168.3.138'
    username = 'root'
    password = 'admin'
    PonID = '5'
    ontid = '1'
    ethid = '1'
    tn = telnet_host(host_ip, username, password)[0]
    shutdown_pon(tn,PonID)
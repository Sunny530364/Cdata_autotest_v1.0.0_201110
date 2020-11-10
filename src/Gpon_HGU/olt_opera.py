#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

# from src.config.initialization_config import *
from src.config.Cdata_loggers import *
from telnetlib import Telnet
import time

def load_config(tn,tftp_server_ip,olt_config_file):
    tn.write('load configuration format txt tftp {} {} '.format(tftp_server_ip,olt_config_file).encode() + b'\n')
    result = tn.read_until(b'OLT(config)# ', timeout=2)
    tn.write(b'y'+b'\n')
    result = tn.read_until(b'OLT(config)# ', timeout=2).decode('utf-8')
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
        return True

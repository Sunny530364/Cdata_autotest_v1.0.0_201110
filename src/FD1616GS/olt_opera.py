#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
from src.config.Cdata_loggers import *
from telnetlib import Telnet
import time

def load_config(tn,tftp_server_ip,olt_config_file):
    tn.write('load configuration format txt tftp {} {} '.format(tftp_server_ip,olt_config_file).encode() + b'\n')
    result = tn.read_until(b'OLT(config)# ', timeout=2)
    tn.write(b'y'+b'\n')
    result = tn.read_until(b'OLT(config)# ',timeout=10).decode('utf-8')
    if 'The loading is successful!' in result:
        cdata_info('配置下载正常')

    else:
        cdata_error('配置下载失败')
        return False
    tn.write(b'reboot'+b'\n')
    tn.write(b'y' + b'\n')
    time.sleep(10)
    return True

def check_telnet(host_ip):
    time.sleep(10)
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

def no_shutdown_gpon(tn,PonID):
    try:
        tn.write(b'interface gpon 0/0'+b'\n')
        result = tn.read_until(b'OLT(config-interface-gpon-0/0)#',timeout=2)
        tn.write(('no shutdown %s'%PonID).encode()+b'\n')
        result = tn.read_until(b'OLT(config-interface-gpon-0/0)#', timeout=2)
        tn.write(('show port state %s'%PonID).encode()+b'\n')
        result = tn.read_until(b'OLT(config-interface-gpon-0/0)#',timeout=2).decode('utf-8')
        if 'Admin state                      : enable' in result:
            cdata_info('pon %s 端口使能成功'%PonID)

            return True
        else:
            cdata_error('pon %s 端口使能失败'%PonID)
            return False
            # raise Exception("OLT_PON %s 端口使能失败"%PonID)
    except:
        return False
        # raise Exception("OLT_PON %s 端口使能失败" % PonID)

def shutdown_gpon(tn,PonID):
    try:
        tn.write(b'interface gpon 0/0'+b'\n')
        result = tn.read_until(b'OLT(config-interface-gpon-0/0)#',timeout=2)
        tn.write(('shutdown %s'%PonID).encode()+b'\n')
        result = tn.read_until(b'OLT(config-interface-gpon-0/0)#', timeout=2)
        tn.write(('show port state %s'%PonID).encode()+b'\n')
        time.sleep(3)
        result = tn.read_until(b'OLT(config-interface-gpon-0/0)#',timeout=2).decode('utf-8')
        print(result)
        if 'Admin state                      : disable' in result:
            cdata_info('pon %s 端口去使能成功'%PonID)
            tn.write(b'exit \n')
            tn.read_until(b'OLT(config)# ', timeout=2)
            return True
        else:
            cdata_error('pon %s 端口去使能失败'%PonID)
            tn.write(b'exit \n')
            tn.read_until(b'OLT(config)# ', timeout=2)
            return False
            # raise Exception("OLT_PON %s 端口去使能失败"%PonID)
    except:
        tn.write(b'exit \n')
        tn.read_until(b'OLT(config)# ', timeout=2)
        return False
        # raise Exception("OLT_PON %s 端口去使能失败"%PonID)

if __name__ == '__main__':
    host_ip = '192.168.0.185'
    username = 'root'
    password = 'admin'
    # tn = telnet_host(host_ip, username, password)[0]
    # noshutdown_pon(tn, PonID)
    # tn = Telnet(host_ip, port=23)
    # print(tn)
    # # 设置调试级别，debuglevel的值越高，得到的调试输出就越多(在sys.stdout上)
    # Telnet.set_debuglevel(tn, debuglevel=1)
    # # except:
    # #     cdata_warn('%s 设备telnet连接失败' % host_ip)
    # #     return False,
    # # 等待login出现后输入用户名，最多等待5秒
    # tn.read_until(b'>>User name: ', timeout=5)
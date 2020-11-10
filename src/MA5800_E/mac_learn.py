#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI
from src.config.telnet_client_MA5800 import *
import re

def ont_mac_learn(tn,PonID,OnuID,Ont_Port_ID):
    # 判断当前的视图是否正确。
    tn.write(b"\n")
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    #查看onu端口的mac地址
    tn.write(('display mac-address ont 0/2/%s %s eth %s '%(PonID, OnuID, Ont_Port_ID)).encode()+b'\n')
    tn.read_until(b'{ <cr>|vlanid<U><1,4094>||<K> }: ',timeout=2)
    tn.write(b'\n')
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2).decode()
    cdata_debug(result)
    # mac_all = re.findall('\d+:\d+:\d+:\d+:\d+:\d+', result)
    #0/ 1/4     40    ETH              1   0000-0201-0107     2000
    mac_all = re.findall('[0-9a-fA-F]+-[0-9a-fA-F]+-[0-9a-fA-F]+',result)
    t_macs = []

    if len(mac_all)==0:
        cdata_error('onu端口没有学习到mac地址')
    else:
        for t_mac in mac_all:
            #将mac地址xxxx-xxxx-xxxx 转成 xx:xx:xx:xx:xx:xx
            t_mac = ':'.join((':'.join((''.join((list(t_mac.split('-')[0])[0], list(t_mac.split('-')[0])[1])),
                                        ''.join((list(t_mac.split('-')[0])[-2], list(t_mac.split('-')[0])[-1])))),
                              ':'.join((''.join((list(t_mac.split('-')[1])[0], list(t_mac.split('-')[1])[1])),
                                        ''.join((list(t_mac.split('-')[1])[-2], list(t_mac.split('-')[1])[-1])))),
                              ':'.join((''.join((list(t_mac.split('-')[2])[0], list(t_mac.split('-')[2])[1])),
                                        ''.join((list(t_mac.split('-')[2])[-2], list(t_mac.split('-')[2])[-1]))))))
            t_macs.append(t_mac)
        print(t_macs)

    return t_macs


if __name__ == '__main__':
    tn = telnet_host(host_ip='192.168.5.82', username='test111', password='test123')[0]
    ont_mac_learn(tn,PonID='4',OnuID='40',Ont_Port_ID='1')


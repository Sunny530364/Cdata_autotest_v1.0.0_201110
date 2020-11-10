#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
import time
import re


def ont_mac_learn(tn,ponid,ontid,ethid):
    #进入gpon视图下
    tn.read_until(b'OLT(config)# ', timeout=2)
    tn.write(b'interface gpon 0/0 ' + b'\n')
    tn.read_until(b'OLT(config-interface-gpon-0/0)# ',timeout=2)
    tn.write('show ont port learned-mac {} {} eth {} '.format(ponid,ontid,ethid).encode()+b'\n')
    time.sleep(2)
    result = tn.read_very_eager().decode('utf-8')
    print(result)
    tn.read_until(b'OLT(config-interface-gpon-0/0)# ', timeout=2)
    tn.write(b'exit ' + b'\n')
    mac_all = re.findall('\d+:\d+:\d+:\d+:\d+:\d+',result)
    return mac_all



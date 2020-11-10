#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
import time
import re


def ont_mac_learn(tn,PonID,OnuID,Ont_Port_ID):
    # 进入gpon视图下
    # 判断当前的视图是否正确。
    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
    tn.read_until(b'OLT(config-interface-gpon-0/0)# ',timeout=2)
    tn.write('show ont port learned-mac {} {} eth {} '.format(PonID,OnuID,Ont_Port_ID).encode()+b'\n')
    time.sleep(2)
    result = tn.read_very_eager().decode('utf-8')
    print(result)
    tn.read_until(b'OLT(config-interface-gpon-0/0)# ', timeout=2)
    tn.write(b'exit ' + b'\n')
    mac_all = re.findall('\d+:\d+:\d+:\d+:\d+:\d+',result)
    return mac_all



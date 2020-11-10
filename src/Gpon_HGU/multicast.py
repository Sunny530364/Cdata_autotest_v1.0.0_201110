#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

import time
from src.config.telnet_client import *
from src.config.Cdata_loggers import *

def ont_multicast(tn,ponid="16",ontid="2",ethid="1",ont_igmpprofile_id="200"):

    #ont 的port1 绑定组播模板200
    tn.read_until(b'OLT(config)# ', timeout=2)
    #进入gpon视图下
    tn.write(b'interface gpon 0/0 '+b'\n')
    tn.read_until(b'OLT(config-interface-gpon-0/0)# ',timeout=2)
    tn.write('ont port attribute {} {} eth {} igmp-profile profile-id {} '.format(ponid,ontid,ethid,ont_igmpprofile_id).encode()+b'\n')
    tn.read_until(b'OLT(config-interface-gpon-0/0)# ',timeout=2)
    tn.write('show ont port attribute {} {} eth all  '.format(ponid,ontid).encode()+b'\n')
    command_result = tn.read_until(b'OLT(config-interface-gpon-0/0)# ',timeout=2).decode()
    #获取相应行
    result = (((command_result.split('-----------------------------------------------------------------------------')[1]).
          split('----------------------------------------------------------------------------'))[1].split('\r\n')[int(ethid)]).split()
    # print(result,result[-1],type(result[-1]),ont_igmpprofile_id,type(ont_igmpprofile_id))
    if str(ont_igmpprofile_id) == result[-1] :
        cdata_info('onu端口绑定组播模板成功')
        tn.write(b'exit'+b'\n')
        tn.read_until(b'OLT(config)# ', timeout=2)
        return True
    else:
        cdata_error('onu端口绑定组播模板失败')
        tn.write(b'exit' + b'\n')
        tn.read_until(b'OLT(config)# ', timeout=2)
        return False



def del_ont_multicast(tn,ponid, ontid, ethid):
    # ont 的port1 去绑定组播模板200
    tn.read_until(b'OLT(config)# ', timeout=2)
    # 进入gpon视图下
    tn.write(b'interface gpon 0/0 ' + b'\n')
    tn.read_until(b'OLT(config-interface-gpon-0/0)# ',timeout=2)
    tn.write('no ont port attribute {} {} eth {} igmp-profile  '.format(ponid, ontid, ethid).encode() + b'\n')
    tn.read_until(b'OLT(config-interface-gpon-0/0)# ',timeout=2)
    tn.write(b'exit' + b'\n')


if __name__ == '__main__':
    host_ip = '192.168.5.164'
    username = 'root'
    password = 'admin'
    tn = telnet_host(host_ip, username, password)[0]
    ont_multicast(tn)
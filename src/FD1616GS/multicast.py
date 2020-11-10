#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

import time
from src.config.telnet_client import *
from src.config.Cdata_loggers import *

def ont_multicast(tn,PonID,OnuID,Ont_Port_ID,Ont_Igmpprofile_ID):
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
    #onu端口绑定组播模板
    tn.write('ont port attribute {} {} eth {} igmp-profile profile-id {} '.format(PonID,OnuID,Ont_Port_ID,Ont_Igmpprofile_ID).encode()+b'\n')
    tn.read_until(b'OLT(config-interface-gpon-0/0)# ',timeout=2)
    #查看onu端口绑定组播模板是否正常
    tn.write('show ont port attribute {} {} eth all  '.format(PonID,OnuID).encode()+b'\n')
    command_result = tn.read_until(b'OLT(config-interface-gpon-0/0)# ',timeout=2).decode()
    #获取相应行
    result = (((command_result.split('-----------------------------------------------------------------------------')[1]).
          split('----------------------------------------------------------------------------'))[1].split('\r\n')[int(Ont_Port_ID)]).split()
    # print(result,result[-1],type(result[-1]),Ont_Igmpprofile_ID,type(Ont_Igmpprofile_ID))
    if str(Ont_Igmpprofile_ID) == result[-1] :
        cdata_info('onu端口绑定组播模板成功')
        tn.write(b'exit'+b'\n')
        tn.read_until(b'OLT(config)# ', timeout=2)
        return True
    else:
        cdata_error('onu端口绑定组播模板失败')
        tn.write(b'exit' + b'\n')
        tn.read_until(b'OLT(config)# ', timeout=2)
        return False

def onu_multicast_forward_untag(tn,Ont_Igmpprofile_ID):
    # 判断当前的视图是否正确。
    tn.write( b"\n")
    result = tn.read_until(b"OLT(config)# ", timeout=2)
    if result:
        pass
    else:
        cdata_info("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        return False
    tn.write(('ont-igmpprofile gpon profile-id %s'%Ont_Igmpprofile_ID).encode()+b'\n')
    tn.read_until(('OLT(config-ont-igmpprofile-%s)# '%Ont_Igmpprofile_ID).encode(),timeout=2)
    tn.write(b'multicast-forward untag'+b'\n')
    tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-igmpprofile current '+b'\n')
    command_result = tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2).decode()
    if 'Downstream IGMP packet forward mode  : untag' in command_result:
        cdata_info('配置onu下行组播vlan转发为untag 正常')
        tn.write(b'commit \n')
        tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2)
        tn.write(b'exit \n')
        tn.read_until(b'OLT(config)# ',timeout=2)
        return True
    else:
        cdata_error('配置onu下行组播vlan转发为untag 失败')
        tn.write(b'commit \n')
        tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2)
        tn.write(b'exit \n')
        tn.read_until(b'OLT(config)# ', timeout=2)
        return False

def onu_multicast_forward_transparent(tn,Ont_Igmpprofile_ID):
    # 判断当前的视图是否正确。
    tn.write( b"\n")
    result = tn.read_until(b"OLT(config)# ", timeout=2)
    if result:
        pass
    else:
        cdata_info("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        return False
    tn.write(('ont-igmpprofile gpon profile-id %s'%Ont_Igmpprofile_ID).encode()+b'\n')
    tn.read_until(('OLT(config-ont-igmpprofile-%s)# '%Ont_Igmpprofile_ID).encode(),timeout=2)
    tn.write(b'multicast-forward tag transparent'+b'\n')
    tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-igmpprofile current '+b'\n')
    command_result = tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2).decode()
    if 'Downstream IGMP packet forward mode  : transparent' in command_result:
        cdata_info('配置onu下行组播vlan转发为transparent 正常')
        tn.write(b'commit \n')
        tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2)
        tn.write(b'exit \n')
        tn.read_until(b'OLT(config)# ',timeout=2)
        return True
    else:
        cdata_error('配置onu下行组播vlan转发为transparent 失败')
        tn.write(b'commit \n')
        tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2)
        tn.write(b'exit \n')
        tn.read_until(b'OLT(config)# ', timeout=2)
        return False

def onu_multicast_forward_translation(tn,Ont_Igmpprofile_ID,Cvlan):
    # 判断当前的视图是否正确。
    tn.write( b"\n")
    result = tn.read_until(b"OLT(config)# ", timeout=2)
    if result:
        pass
    else:
        cdata_info("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        return False
    tn.write(('ont-igmpprofile gpon profile-id %s'%Ont_Igmpprofile_ID).encode()+b'\n')
    tn.read_until(('OLT(config-ont-igmpprofile-%s)# '%Ont_Igmpprofile_ID).encode(),timeout=2)
    tn.write(('multicast-forward tag translation %s '%Cvlan).encode()+b'\n')
    tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-igmpprofile current '+b'\n')
    command_result = tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2).decode()
    if 'Downstream IGMP packet forward mode  : translate' in command_result and\
            'Downstream IGMP packet forward VLAN  : %s'%Cvlan in command_result:
        cdata_info('配置onu下行组播vlan 转发为 translation %s 正常'%Cvlan)
        tn.write(b'commit \n')
        tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2)
        tn.write(b'exit \n')
        tn.read_until(b'OLT(config)# ',timeout=2)
        return True
    else:
        cdata_error('配置onu下行组播vlan转发为 translation %s 失败'%Cvlan)
        tn.write(b'commit \n')
        tn.read_until(('OLT(config-ont-igmpprofile-%s)# ' % Ont_Igmpprofile_ID).encode(), timeout=2)
        tn.write(b'exit \n')
        tn.read_until(b'OLT(config)# ', timeout=2)
        return False

def del_ont_multicast(tn,PonID, OnuID, Ont_Port_ID):
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
    #onu端口删除绑定的组播模板
    tn.write('no ont port attribute {} {} eth {} igmp-profile  '.format(PonID, OnuID, Ont_Port_ID).encode() + b'\n')
    tn.read_until(b'OLT(config-interface-gpon-0/0)# ',timeout=2)
    tn.write(b'exit' + b'\n')


def show_multicast_groups(tn,PonID, OnuID, Ont_Port_ID):
    # 查看olt侧的组播表项
    tn.read_until(b'OLT(config)#', timeout=2)
    tn.write(b'show igmp group all \n')
    command_result = tn.read_until(b'OLT(config)#', timeout=2).decode()
    cdata_debug(command_result)
    # 查看onu侧的组播表现
    tn.write(b'interface gpon 0/0  \n')
    tn.read_until(b'OLT(config-interface-gpon-0/0)# ', timeout=2)
    tn.write(('show ont port multicast-group %s %s eth %s '%(PonID, OnuID, Ont_Port_ID)).encode()+b'\n')
    command_result = tn.read_until(b'OLT(config-interface-gpon-0/0)# ', timeout=2).decode()
    cdata_debug(command_result)
    tn.write(b'exit \n')
    tn.read_until(b'OLT(config)#', timeout=2)



if __name__ == '__main__':
    host_ip = '192.168.0.181'
    username = 'root'
    password = 'admin'
    tn = telnet_host(host_ip, username, password)[0]
    #onu_multicast_forward_untag(tn, Ont_Igmpprofile_ID='200')
    onu_multicast_forward_translation(tn, Ont_Igmpprofile_ID='200', Cvlan='2000')
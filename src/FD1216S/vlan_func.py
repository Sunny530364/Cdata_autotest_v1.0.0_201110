#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
from src.config.Cdata_loggers import *
import time
import re

#在服务模板下配置onu端口为tranparent
def ont_port_transparent_profile(tn,Ont_Srvprofile_ID):
    '''
    config ont  port 1-4 is transparent ,
    '''
    # 进入服务模板视图下
    tn.write('ont-srvprofile epon profile-id  {} '.format(Ont_Srvprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    if result:
        pass
    else:
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    #配置ont port1-4为transaprent
    tn.write(b'port vlan eth 1-4  transparent' + b'\n')
    tn.read_until('OLT(config-epon-srvprofile-{})#   '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current'+ b'\n')
    command_result =  tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2).decode("utf-8")
    print(command_result)
    if "ETH   1    Transparent"  in command_result and "ETH   2    Transparent"  in command_result\
            and "ETH   3    Transparent"  in command_result and "ETH   4    Transparent"  in command_result:
        cdata_info("配置onu eth1-4 vlan为transparent成功")
        #保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error("配置onu eth1-4 vlan为transparent失败")
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

#在服务模板下配置onu端口为tag模式
def ont_port_tag_profile(tn,Ont_Srvprofile_ID,Ont_Port_ID,User_Vlan):
    # 进入服务模板视图下
    tn.write('ont-srvprofile epon profile-id  {} '.format(Ont_Srvprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
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

    #配置onu 端口为tag 2000
    tn.write(('port vlan eth %s %s'%(Ont_Port_ID,User_Vlan)).encode() + b'\n')
    tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write((' port native-vlan eth %s %s '%(Ont_Port_ID,User_Vlan)).encode() + b'\n')
    tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current' + b'\n')
    command_result =  tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2).decode("utf-8")
    print(command_result)
    '''
    Port  Port Service-type Index N-VLAN N-PRI S-VLAN S-PRI C-VLAN C-PRI
    type  ID 
    ---------------------------------------------------------------------------
    ETH   1    Translation  1     2000   0     2000   -     2000   -  
    '''
    if re.search(r"ETH   %s    Translation(\s+)(\d)(\s+)%s(\s+)%s(\s+)%s(\s+)-(\s+)%s(\s+)" % (Ont_Port_ID,User_Vlan,0,User_Vlan,User_Vlan), command_result):
    # if " 2000   0     2000   -     2000" in command_result :
        cdata_info("配置onu eth %s 为tag %s成功"%(Ont_Port_ID,User_Vlan))
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error("配置onu eth1 vlan为tag %s失败"%User_Vlan)
        # 保存配置，退出服务模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

#在服务模板下配置onu端口为translate模式
def ont_port_translate_profile(tn,Ont_Srvprofile_ID,Ont_Port_ID,S_Vlan_list,C_Vlan_list):
    '''
    config  ont port 1 translation , vlan 100——>2000,vlan 200——>2001
    '''
    # 进入服务模板视图下
    tn.write('ont-srvprofile epon profile-id {} '.format(Ont_Srvprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
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
    #配置onu端口translate
    for i in range(len(S_Vlan_list)):
        tn.write(('port vlan eth %s translation %s user-vlan %s'%( Ont_Port_ID,S_Vlan_list[i],C_Vlan_list[i])).encode()+b'\n')
        tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current' + b'\n')
    command_result =  tn.read_until('OLT(config-epon-srvprofile-{})# '.format(Ont_Srvprofile_ID).encode(), timeout=2).decode("utf-8")
    '''
    ----------------------------------------------------------------------------
    Port  Port Service-type Index N-VLAN N-PRI S-VLAN S-PRI C-VLAN C-PRI
     type  ID 
    ---------------------------------------------------------------------------
     ETH   1    Translation  1     2000   0     2000   -     2000   -  
                          2                  2000   -     100    -  
    '''
    for i in range(len(C_Vlan_list)):
        #  2000   -     100    -
        if re.search(r"%s(\s+)-(\s+)%s(\s+)-" % (S_Vlan_list[i], C_Vlan_list[i]), command_result):
            continue
        else:
            cdata_error("配置onu 端口 vlan为translate %s 转 %s失败" %(C_Vlan_list[i],S_Vlan_list[i]))
            # 保存配置，退出服务模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    cdata_info("配置onu 端口 vlan为translate %s 转 %s成功" %(C_Vlan_list,S_Vlan_list))
    # 保存配置，退出服务模板
    tn.write(b'commit' + b'\n')
    tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'exit' + b'\n')
    return True

#在服务模板下配置onu端口为trunk模式
def ont_port_trunk_profile(tn,Ont_Srvprofile_ID,Ont_Port_ID,Vlan_list):

    # 进入服务模板视图下
    tn.write('ont-srvprofile epon profile-id {} '.format(Ont_Srvprofile_ID).encode() + b'\n')
    result = tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
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
        tn.write((' port vlan eth %s %s'%(Ont_Port_ID,Vlan_list[i])).encode() + b'\n')
        tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'show ont-srvprofile current' + b'\n')
    command_result = tn.read_until('OLT(config-epon-srvprofile-{})# '.format(Ont_Srvprofile_ID).encode(),timeout=2).decode("utf-8")
    for i in range(len(Vlan_list)):
        #  2000   -     2000   -
        if re.search(r"%s(\s+)-(\s+)%s(\s+)-" % (Vlan_list[i], Vlan_list[i]), command_result):
            continue
        else:
            cdata_error("配置onu 端口 vlan为trunk %s失败" % (Vlan_list[i]))
            # 保存配置，退出服务模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    cdata_info("配置onu 端口 vlan为trunk %s成功" % (Vlan_list))
    # 保存配置，退出服务模板
    tn.write(b'commit' + b'\n')
    tn.read_until('OLT(config-epon-srvprofile-{})#  '.format(Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'exit' + b'\n')
    return True


def ont_port_transparent_remote(tn,PonID,OnuID,Ont_Port_ID):
    tn.write(b'interface epon 0/0'+ b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(b'ont port vlan %s %s eth %s transparent'%(PonID,OnuID,Ont_Port_ID),b'\n')
    result = tn.read_until('show ont  port vlan remote %s %s eth %s'%(PonID,OnuID,Ont_Port_ID), timeout=2).decode("utf-8")
    if 'VLAN type              : Transparent' in result:
        cdata_info("配置onu eth1 vlan为transparent成功")
        # 退出epon视图
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error("配置onu eth1 vlan为transparent失败")
        # 退出epon视图
        tn.write(b'exit' + b'\n')
        return False
    # 退出epon视图
    tn.write(b'exit' + b'\n')

def ont_port_tag_remote(tn,PonID, OnuID, Ont_Port_ID,User_Vlan):
    # 判断当前的视图是否正确。
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(('ont port vlan %s %s eth %s %s'%(PonID, OnuID, Ont_Port_ID,User_Vlan)).encode()+ b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(('ont port native-vlan %s %s eth %s vlan %s'%(PonID, OnuID, Ont_Port_ID,User_Vlan)).encode()+ b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    time.sleep(2)
    tn.write(('show ont  port vlan remote %s %s eth %s' % (PonID, OnuID, Ont_Port_ID)).encode() + b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2).decode('utf-8')
    print(result )
    if 'VLAN type              : Tag' in result and 'Default VLAN VID       : %s'%User_Vlan in result:
        cdata_info('配置 onu 端口%s vlan 为 tag %s' % (Ont_Port_ID,User_Vlan))
        # 退出epon视图
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error('配置onu eth%s vlan为tag %s' % (Ont_Port_ID,User_Vlan))
        # 退出epon视图
        tn.write(b'exit' + b'\n')
        return False

#废弃
def ont_port_trunk_remote(tn,PonID, OnuID, Ont_Port_ID):
    tn.write(b'interface epon 0/0' + b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(b'ont port vlan %s %s eth %s 2000' % (PonID, OnuID, Ont_Port_ID), b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(b'ont port vlan 5 1 eth 1 2001' % (PonID, OnuID, Ont_Port_ID), b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(b'ont port vlan 5 1 eth 1 2002' % (PonID, OnuID, Ont_Port_ID), b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(b'ont port vlan 5 1 eth 1 2003' % (PonID, OnuID, Ont_Port_ID), b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(b'ont port vlan 5 1 eth 1 2004' % (PonID, OnuID, Ont_Port_ID), b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(b'ont port vlan 5 1 eth 1 2005' % (PonID, OnuID, Ont_Port_ID), b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(b'ont port vlan 5 1 eth 1 2006' % (PonID, OnuID, Ont_Port_ID), b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(b'ont port vlan 5 1 eth 1 2007' % (PonID, OnuID, Ont_Port_ID), b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write(('show ont  port vlan remote %s %s eth %s' % (PonID, OnuID, Ont_Port_ID)).encode()+b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)

    if 'VLAN type              : Trunk' in result and '0x8100 0    0    2000' in result and '0x8100 0    0    2001' in result\
            and '0x8100 0    0    2002' in result and '0x8100 0    0    2003' in result and '0x8100 0    0    2004' in result \
            and '0x8100 0    0    2005' in result and '0x8100 0    0    2006' in result and '0x8100 0    0    2007' in result:
        cdata_info('配置 onu 端口%s vlan 为 trunk 2000-2007 成功' % Ont_Port_ID)
        # 退出epon视图
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error("配置onu eth1 vlan为trunk 2000-2007失败")
        # 退出epon视图
        tn.write(b'exit' + b'\n')
        return False

    # 退出epon视图
    tn.write(b'exit' + b'\n')

def ont_port_vlan_remote_del(tn,PonID, OnuID, Ont_Port_ID):
    tn.write(b'interface epon 0/0' + b'\n')
    result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2)
    tn.write((' no ont port vlan %s %s eth %s'%(PonID, OnuID, Ont_Port_ID)).encode()+b'\n')
    command_result = tn.read_very_eager().decode("utf-8")
    if 'Restore to the profile configuration successfully' in  command_result:
        cdata_info('清除onu端口离散vlan配置')
        tn.write(('show ont  port vlan remote %s %s eth %s' % (PonID, OnuID, Ont_Port_ID)).encode() + b'\n')
        result = tn.read_until(b'OLT(config-interface-epon-0/0)# ', timeout=2).decode('utf-8')
        if 'VLAN type              : Transparent'  in result:
            cdata_info('onu端口为transparent')
        tn.write(b'exit \n')
        return True
    else:
        cdata_error('清除onu端口离散vlan配置失败')
        tn.write(b'exit \n')
        return False


if __name__ == '__main__':
    host_ip = '192.168.0.140'
    username = 'root'
    password = 'admin'
    PonID='5'
    OnuID='1'
    Ont_Port_ID='4'
    tn = telnet_host(host_ip, username, password)[0]
    # ont_port_tag_remote(tn,PonID, OnuID, Ont_Port_ID)
    # ont_port_tag_profile(tn, Ont_Srvprofile_ID='200', User_Vlan='2000')
    # ont_port_translate_profile(tn, Ont_Srvprofile_ID='200', Ont_Port_ID='1', S_Vlan_list=[2000], C_Vlan_list=[100])
    # ont_port_tag_profile(tn, Ont_Srvprofile_ID='200', Ont_Port_ID='1', Vlan_list=[2000,2001])
    ont_port_tag_profile(tn, Ont_Srvprofile_ID='200', Ont_Port_ID='4', User_Vlan='2000')



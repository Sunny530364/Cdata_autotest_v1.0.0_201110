#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client_MA5800 import *
import re

def ont_port_tag(tn,PonID, OnuID,Ont_Port_ID,User_Vlan):
    # 判断当前的视图是否正确。
    tn.write(b"interface epon 0/2" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
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
    tn.write(('ont  port native-vlan %s %s eth %s vlan %s ' % (PonID, OnuID, Ont_Port_ID,User_Vlan)).encode() + b'\n')
    result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
    tn.write(('display ont port vlan remote %s %s eth %s' % (PonID, OnuID, Ont_Port_ID)).encode() + b'\n')
    tn.read_until(b"{ <cr>||<K> }:", timeout=2)
    tn.write(b'\n')
    result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode()
    if 'VLAN type                            : Tag' in result and 'Default VLAN VID                     : %s'%User_Vlan in result:
        cdata_info('配置onu端口为tag %s正常'%User_Vlan)
        tn.write(b'quit \n')
        return True
    else:
        cdata_error('配置onu端口为tag %s失败'%User_Vlan)
        tn.write(b'quit \n')
        return True

def ont_port_transparent(tn,PonID, OnuID,Ont_Port_ID):
    # 判断当前的视图是否正确。
    tn.write(b"interface epon 0/2" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
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
    tn.write(('ont  port vlan %s %s eth %s transparent '%(PonID, OnuID, Ont_Port_ID)).encode()+b'\n')
    result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
    tn.write(('display ont port vlan remote %s %s eth %s'%(PonID, OnuID,Ont_Port_ID)).encode()+b'\n')
    tn.read_until(b"{ <cr>||<K> }:", timeout=2)
    tn.write(b'\n')
    result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode()
    if 'VLAN type                            : Transparent' in result:
        cdata_info('配置onu端口为transparent正常')
        tn.write(b'quit \n')
        return True
    else:
        cdata_error('配置onu端口为transparent失败')
        tn.write(b'quit \n')
        return True

def ont_port_trunk(tn,PonID, OnuID,Ont_Port_ID,Vlan_list):
    # vlan_list = [2000,2001,2002,2003,2004,2005,2006,2007]
    # 判断当前的视图是否正确。
    tn.write(b"interface epon 0/2" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
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

    tn.write(('ont port vlan %s %s eth %s %s-%s '%(PonID, OnuID, Ont_Port_ID,Vlan_list[0],Vlan_list[-1])).encode()+b'\n')
    # tn.read_until(b'{ <cr>|priority<K>|prival<U><0,7> }:',timeout=2)
    # tn.write(b'\n')
    tn.read_until(b'MA5800-X15(config-if-epon-0/2)#',timeout=2)
    tn.write(('display ont info %s %s' % (PonID, OnuID)).encode() + b'\n')
    tn.read_until(b"{ <cr>||<K> }:", timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode()
    for i in range(len(Vlan_list)):
        #ETH       1       Translation  1     2000   2000
        if re.search(r"ETH(\s+)%s(\s+)Translation(\s+)%s(\s+)%s(\s+)%s" % (Ont_Port_ID,str(i+1),Vlan_list[i], Vlan_list[i]),command_result):
            continue
        else:
            cdata_error("配置onu 端口 vlan为trunk%s失败"%Vlan_list)
            tn.write(b'quit' + b'\n')
            return False
    cdata_info("配置onu 端口 vlan为trunk %s成功"%Vlan_list)
    tn.write(b'quit' + b'\n')
    return True

def ont_port_translate(tn,PonID, OnuID,Ont_Port_ID,S_Vlan_list,C_Vlan_list):
    # s_vlan_list = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]
    # c_vlan_list = [100,101,102,103,104,105,106,107]
    # 判断当前的视图是否正确。
    tn.write(b"interface epon 0/2" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
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
    for i in range(len(S_Vlan_list)):
        tn.write(('ont  port vlan %s %s eth %s translation %s user-vlan %s'%(PonID, OnuID, Ont_Port_ID,S_Vlan_list[i],C_Vlan_list[i])).encode()+b'\n')
        # tn.read_until(b'{ <cr>|prival<U><0,7>|user-encap<K> }:',timeout=2)
        # tn.write(b'\n')
        tn.read_until(b"MA5800-X15(config)#", timeout=2)
    tn.write(('display ont info %s %s' % (PonID, OnuID)).encode() + b'\n')
    tn.read_until(b"{ <cr>||<K> }:", timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode()
    for i in range(len(C_Vlan_list)):
        #  ETH       1       Translation  1     2000   100
        if re.search(r"ETH(\s+)%s(\s+)Translation(\s+)%s(\s+)%s(\s+)%s" % (
        Ont_Port_ID, str(i + 1), S_Vlan_list[i], C_Vlan_list[i]), command_result):
            continue
        else:
            cdata_error("配置onu 端口 vlan为translate %s 转 %s失败" %(C_Vlan_list[i],S_Vlan_list[i]))
            tn.write(b'quit' + b'\n')
            return False
    cdata_info("配置onu 端口 vlan为translate %s 转 %s成功" %(C_Vlan_list,S_Vlan_list))
    tn.write(b'quit' + b'\n')
    return True



if __name__ == '__main__':
    tn = telnet_host(host_ip='192.168.5.82', username='test111', password='test123')[0]
    # ont_port_translate_del(tn)
    # create_ontlineprofile(Ont_Lineprofile_ID='200', Dba_Profile_ID='100')
    create_ontsrvprofile(Ont_Srvprofile_ID='200')
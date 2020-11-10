#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client_MA5800 import *
import re

def ont_port_transparent(tn,PonID, OnuID,Ont_Port_ID):
    # 判断当前的视图是否正确。
    tn.write(b"interface gpon 0/1" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
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
    result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
    tn.write(('display ont info %s %s'%(PonID, OnuID)).encode()+b'\n')
    tn.read_until(b"{ <cr>||<K> }:", timeout=2)
    tn.write(b'\n')
    result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode()
    if 'ETH    1      Transparent' in result:
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
    tn.write(b"interface gpon 0/1" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
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
    for vlanid in Vlan_list:
        tn.write(('ont  port vlan %s %s eth %s %s'%(PonID, OnuID, Ont_Port_ID,vlanid)).encode()+b'\n')
        tn.read_until(b'{ <cr>|priority<K>|prival<U><0,7> }:',timeout=2)
        tn.write(b'\n')
        tn.read_until(b'MA5800-X15(config-if-gpon-0/1)#',timeout=2)
    tn.write(('display ont info %s %s' % (PonID, OnuID)).encode() + b'\n')
    tn.read_until(b"{ <cr>||<K> }:", timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode()
    for i in range(len(Vlan_list)):
        if re.search(r"%s(\s+)-(\s+)%s" % (Vlan_list[i], Vlan_list[i]),command_result):
            continue
        else:
            cdata_error("配置onu 端口 vlan为trunk%s失败"%Vlan_list)
            tn.write(b'quit' + b'\n')
            return False
    cdata_info("配置onu 端口 vlan为trunk %s成功"%Vlan_list)
    tn.write(b'quit' + b'\n')
    return True

    # if "2000   -     2000" in command_result and "2001   -     2001" in command_result \
    #         and "2002   -     2002" in command_result and "2003   -     2003" in command_result \
    #         and "2004   -     2004" in command_result and "2005   -     2005" in command_result\
    #         and "2006   -     2006" in command_result and "2007   -     2007" in command_result:
    #     cdata_info("配置onu 端口 vlan为trunk 2000—2007成功")
    #     tn.write(b'quit' + b'\n')
    #     return True
    # else:
    #     cdata_error("配置onu 端口 vlan为trunk 2000—2007失败")
    #     tn.write(b'quit' + b'\n')
    #     return False

def ont_port_translate(tn,PonID, OnuID,Ont_Port_ID,S_Vlan_list,C_Vlan_list):
    # s_vlan_list = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]
    # c_vlan_list = [100,101,102,103,104,105,106,107]
    # 判断当前的视图是否正确。
    tn.write(b"interface gpon 0/1" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
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
        tn.read_until(b'{ <cr>|prival<U><0,7>|user-encap<K> }:',timeout=2)
        tn.write(b'\n')
        tn.read_until(b"MA5800-X15(config)#", timeout=2)
    tn.write(('display ont info %s %s' % (PonID, OnuID)).encode() + b'\n')
    tn.read_until(b"{ <cr>||<K> }:", timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode()
    for i in range(len(C_Vlan_list)):
        if re.search(r"%s(\s+)-(\s+)%s(\s+)-" % (S_Vlan_list[i], C_Vlan_list[i]), command_result):
            continue
        else:
            cdata_error("配置onu 端口 vlan为translate %s 转 %s失败" %(C_Vlan_list,S_Vlan_list))
            tn.write(b'quit' + b'\n')
            return False
    cdata_info("配置onu 端口 vlan为translate %s 转 %s成功" %(C_Vlan_list,S_Vlan_list))
    tn.write(b'quit' + b'\n')
    return True


def ont_port_trunk_del(tn,PonID, OnuID,Ont_Port_ID):
    vlan_list = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]
    # 判断当前的视图是否正确。
    tn.write(b"interface gpon 0/1" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
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
    for vlanid in vlan_list:
        tn.write(('undo ont  port vlan %s %s eth %s %s' % (PonID, OnuID, Ont_Port_ID, vlanid)).encode() + b'\n')
        tn.read_until(b'{ <cr>|prival<U><0,7>|user-encap<E><IPoE,PPPoE,IPv6-IPoE> }:', timeout=2)
        tn.write(b'\n')
        tn.read_until(b'MA5800-X15(config-if-gpon-0/1)#', timeout=2)
    tn.write(('display ont info %s %s' % (PonID, OnuID)).encode() + b'\n')
    tn.read_until(b"{ <cr>||<K> }:", timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode()
    if "2000   -     2000" not in command_result and "2001   -     2001" not in command_result \
            and "2002   -     2002" not in command_result and "2003   -     2003" not in command_result \
            and "2004   -     2004" not in command_result and "2005   -     2005" not in command_result \
            and "2006   -     2006" not in command_result and "2007   -     2007" not in command_result:
        cdata_info("删除onu 端口 vlan为trunk 2000—2007成功")
        tn.write(b'quit' + b'\n')
        return True
    else:
        cdata_error("删除onu 端口 vlan为trunk 2000—2007失败")
        tn.write(b'quit' + b'\n')
        return False

def ont_port_transparent_del(tn,PonID, OnuID,Ont_Port_ID):
    # 判断当前的视图是否正确。
    tn.write(b"interface gpon 0/1" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
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
    tn.write(('undo ont  port vlan %s %s eth %s transparent' % (PonID, OnuID, Ont_Port_ID)).encode() + b'\n')
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
    tn.write(('display ont info %s %s' % (PonID, OnuID)).encode() + b'\n')
    tn.read_until(b"{ <cr>||<K> }:", timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode()
    if 'ETH    1      Transparent' not in result:
        cdata_info('删除onu端口为transparent正常')
        tn.write(b'quit \n')
        return True
    else:
        cdata_error('删除onu端口为transparent失败')
        tn.write(b'quit \n')
        return True

def ont_port_translate_del(tn,PonID, OnuID,Ont_Port_ID):
    c_vlan_list = [100, 101, 102, 103, 104, 105, 106, 107]
    # 判断当前的视图是否正确。
    tn.write(b"interface gpon 0/1" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
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
    for vlanid in c_vlan_list:
        tn.write(
            ('undo ont  port vlan %s %s eth %s %s' % (PonID, OnuID, Ont_Port_ID, vlanid)).encode() + b'\n')
        tn.read_until(b'{ <cr>|prival<U><0,7>|user-encap<E><IPoE,PPPoE,IPv6-IPoE> }:', timeout=2)
        tn.write(b'\n')
        tn.read_until(b'MA5800-X15(config-if-gpon-0/1)#', timeout=2)
    tn.write(('display ont info %s %s' % (PonID, OnuID)).encode() + b'\n')
    tn.read_until(b"{ <cr>||<K> }:", timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode()
    if "2000   -     100    -" not in command_result and "2001   -     101    -" not in command_result \
            and "2002   -     102    -" not in command_result and "2003   -     103    -" not in command_result \
            and "2004   -     104    -" not in command_result and "2005   -     105    -" not in command_result \
            and "2006   -     106    -" not in command_result and "2007   -     107    -" not in command_result:
        cdata_info("删除onu eth1-4 vlan为translate100-107转2000-2007成功")
        tn.write(b'quit' + b'\n')
        return True
    else:
        cdata_error("删除onu eth1 vlan为translate100-107转2000-2007失败")
        tn.write(b'quit' + b'\n')
        return False



if __name__ == '__main__':
    tn = telnet_host(host_ip='192.168.5.82', username='test111', password='test123')[0]
    # ont_port_translate_del(tn)
    # create_gpon_ontlineprofile(tn,Ont_Lineprofile_ID='200', Dba_Profile_ID='100')
    create_gpon_ontsrvprofile(tn, Ont_Srvprofile_ID='200')
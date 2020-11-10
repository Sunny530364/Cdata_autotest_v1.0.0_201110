#!/usr/bin/python
# -*- coding UTF-8 -*-

import getpass
import telnetlib
import os
import sys
import time
import re
# from src.config.initialization_config import *
from src.config.telnet_client import *
from os.path import dirname, abspath
from src.config.Cdata_loggers import *

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)


        
def add_omci_wan_bridge_tag(tn, PonID, OnuID, WAN_ID, WAN_service_type, User_Vlan, WAN_pri, ETH_list, SSID_list, SSID_5g_list):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add %s %s %s bridge %s vlan-mode tag %s priority %s binding eth %s ssid %s 5g-ssid %s' % (PonID, OnuID, WAN_ID, WAN_service_type, User_Vlan , WAN_pri, ETH_list, SSID_list, SSID_5g_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : bridge' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN id                          : %s' %(User_Vlan) in command_result and 'VLAN priority                    : %s' % (WAN_pri) in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_omci_wan_bridge_transparent(tn, PonID, OnuID, WAN_ID, WAN_service_type, User_Vlan, WAN_pri, ETH_list, SSID_list, SSID_5g_list):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add %s %s %s bridge %s vlan-mode transparent binding eth %s ssid %s 5g-ssid %s' % (PonID, OnuID, WAN_ID, WAN_service_type, ETH_list, SSID_list, SSID_5g_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : bridge' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN mode                        : transparent' in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_omci_wan_bridge_untag(tn, PonID, OnuID, WAN_ID, WAN_service_type, ETH_list, SSID_list, SSID_5g_list):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add %s %s %s bridge %s vlan-mode untag binding eth %s ssid %s 5g-ssid %s' % (PonID, OnuID, WAN_ID, WAN_service_type, ETH_list, SSID_list, SSID_5g_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : bridge' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN mode                        : untag' in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
        
def add_omci_wan_route_dhcp_tag(tn, PonID, OnuID, WAN_ID, WAN_service_type, User_Vlan, WAN_pri, ETH_list, SSID_list, SSID_5g_list):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add  %s %s %s route %s  dhcp vlan-mode tag %s priority %s binding eth %s ssid %s 5g-ssid %s' % (PonID, OnuID, WAN_ID, WAN_service_type, User_Vlan , WAN_pri, ETH_list, SSID_list, SSID_5g_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : route' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN id                          : %s' %(User_Vlan) in command_result and 'DSP  mode                        : DHCP' in command_result and 'VLAN priority                    : %s' % (WAN_pri) in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_omci_wan_route_static_tag(tn, PonID, OnuID, WAN_ID, WAN_service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, User_Vlan, WAN_pri, ETH_list, SSID_list, SSID_5g_list):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add %s %s %s route %s static ip %s mask %s gateway %s primary-dns %s  secondary-dns %s vlan-mode tag %s priority %s binding eth %s ssid %s 5g-ssid %s' % (PonID, OnuID, WAN_ID, WAN_service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, User_Vlan , WAN_pri, ETH_list, SSID_list, SSID_5g_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : route' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN id                          : %s' %(User_Vlan) in command_result and 'DSP  mode                        : Static' in command_result and 'VLAN priority                    : %s' % (WAN_pri) in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_omci_wan_route_pppoe_tag(tn, PonID, OnuID, WAN_ID, WAN_service_type, User_Vlan, pppoe_name, pppoe_password, WAN_pri, ETH_list, SSID_list, SSID_5g_list):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add %s %s %s route %s pppoe username %s password %s vlan-mode tag %s priority %s binding eth %s ssid %s 5g-ssid %s' % (PonID, OnuID, WAN_ID, WAN_service_type, pppoe_name, pppoe_password, User_Vlan , WAN_pri, ETH_list, SSID_list, SSID_5g_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : route' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN id                          : %s' %(User_Vlan) in command_result and 'DSP  mode                        : PPPoE' in command_result and 'VLAN priority                    : %s' % (WAN_pri) in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_omci_wan_bridge_tag_1(tn, PonID, OnuID, WAN_ID, WAN_service_type, User_Vlan, WAN_pri):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add %s %s %s bridge %s vlan-mode tag %s priority %s' % (PonID, OnuID, WAN_ID, WAN_service_type, User_Vlan , WAN_pri)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : bridge' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN id                          : %s' %(User_Vlan) in command_result and 'VLAN priority                    : %s' % (WAN_pri) in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_omci_wan_route_dhcp_tag_1(tn, PonID, OnuID, WAN_ID, WAN_service_type, User_Vlan, WAN_pri):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add  %s %s %s route %s  dhcp vlan-mode tag %s priority %s' % (PonID, OnuID, WAN_ID, WAN_service_type, User_Vlan , WAN_pri)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : route' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN id                          : %s' %(User_Vlan) in command_result and 'DSP  mode                        : DHCP' in command_result and 'VLAN priority                    : %s' % (WAN_pri) in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_omci_wan_route_static_tag_1(tn, PonID, OnuID, WAN_ID, WAN_service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, User_Vlan, WAN_pri):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add %s %s %s route %s static ip %s mask %s gateway %s primary-dns %s  secondary-dns %s vlan-mode tag %s priority %s' % (PonID, OnuID, WAN_ID, WAN_service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, User_Vlan , WAN_pri)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : route' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN id                          : %s' %(User_Vlan) in command_result and 'DSP  mode                        : Static' in command_result and 'VLAN priority                    : %s' % (WAN_pri) in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_omci_wan_route_pppoe_tag_1(tn, PonID, OnuID, WAN_ID, WAN_service_type, User_Vlan, pppoe_name, pppoe_password, WAN_pri):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add %s %s %s route %s pppoe username %s password %s vlan-mode tag %s priority %s' % (PonID, OnuID, WAN_ID, WAN_service_type, pppoe_name, pppoe_password, User_Vlan , WAN_pri)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : route' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN id                          : %s' %(User_Vlan) in command_result and 'DSP  mode                        : PPPoE' in command_result and 'VLAN priority                    : %s' % (WAN_pri) in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_omci_wan_route_dhcp_untag(tn, PonID, OnuID, WAN_ID, WAN_service_type, ETH_list, SSID_list, SSID_5g_list):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add  %s %s %s route %s  dhcp vlan-mode untag binding eth %s ssid %s 5g-ssid %s' % (PonID, OnuID, WAN_ID, WAN_service_type, ETH_list, SSID_list, SSID_5g_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : route' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result  and 'DSP  mode                        : DHCP' in command_result and 'VLAN mode                        : untag' in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_omci_wan_route_static_untag(tn, PonID, OnuID, WAN_ID, WAN_service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, ETH_list, SSID_list, SSID_5g_list):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add %s %s %s route %s static ip %s mask %s gateway %s primary-dns %s  secondary-dns %s vlan-mode untag binding eth %s ssid %s 5g-ssid %s' % (PonID, OnuID, WAN_ID, WAN_service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, ETH_list, SSID_list, SSID_5g_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    print(command_write)
    print(command_result)
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : route' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN mode                        : untag' in command_result and 'DSP  mode                        : Static' in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_omci_wan_route_pppoe_untag(tn, PonID, OnuID, WAN_ID, WAN_service_type, pppoe_name, pppoe_password, ETH_list, SSID_list, SSID_5g_list):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan add %s %s %s route %s pppoe username %s password %s vlan-mode untag binding eth %s ssid %s 5g-ssid %s' % (PonID, OnuID, WAN_ID, WAN_service_type, pppoe_name, pppoe_password, ETH_list, SSID_list, SSID_5g_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Connect mode                     : route' in command_result and 'Connect type                     : %s'%(WAN_service_type.title()) in command_result and 'VLAN mode                        : untag'  in command_result and 'DSP  mode                        : PPPoE' in command_result:
        cdata_info("OMCI_WAN创建成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
       
def del_omci_wan(tn, PonID, OnuID, WAN_ID):

    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont wan del %s %s %s' % (PonID, OnuID, WAN_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan config %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'WAN ID                           : %s' %(WAN_ID) not in command_result:
        cdata_info("OMCI_WAN删除成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OMCI_WAN删除失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
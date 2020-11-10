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


# 添加桥接的WAN连接，勾选开启VLAN        
def add_oam_wan_bridge_vlan_enable(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, interface_list):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s %s %s connection-mode bridge service-type %s mtu 1500 bind-if %s' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, interface_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    time.sleep(5)
    command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : bridge' in command_result and 'VLAN ID              : %s'%(User_Vlan) in command_result and '802.1P               : %s'%(WAN_pri) in command_result :
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加路由模式下DHCP方式的WAN连接，勾选开启VLAN   
def add_oam_wan_dhcp_vlan_enable(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, interface_list):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s %s %s connection-mode route service-type %s ip-mode dhcp mtu 1500 bind-if %s' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, interface_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : route' in command_result and 'VLAN ID              : %s'%(User_Vlan) in command_result and '802.1P               : %s'%(WAN_pri) in command_result and 'IP Mode              : Dhcp' in command_result:
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加路由模式下STATIC方式的WAN连接，勾选开启VLAN 
def add_oam_wan_static_vlan_enable(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, interface_list):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s %s %s connection-mode route service-type %s ip-mode static ip-address %s mask %s gateway %s dns %s secondary-dns %s mtu 1500 bind-if %s' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, interface_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : route' in command_result and 'VLAN ID              : %s'%(User_Vlan) in command_result and '802.1P               : %s'%(WAN_pri) in command_result and 'IP Mode              : Static' in command_result:
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加路由模式下PPPoE方式的WAN连接，勾选开启VLAN 
def add_oam_wan_pppoe_vlan_enable(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, pppoe_name, pppoe_password,interface_list):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s %s %s connection-mode route service-type %s ip-mode pppoe %s %s mtu  1500 bind-if %s' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, pppoe_name, pppoe_password, interface_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : route' in command_result and 'VLAN ID              : %s'%(User_Vlan) in command_result and '802.1P               : %s'%(WAN_pri) in command_result and 'IP Mode              : Pppoe' in command_result:
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加桥接的WAN连接，不勾选开启VLAN 
def add_oam_wan_bridge_vlan_disable(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE, service_type, interface_list):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s connection-mode bridge service-type %s mtu 1500 bind-if %s' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, service_type, interface_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    time.sleep(5)
    command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : bridge' in command_result and 'VLAN ID              : -' in command_result and '802.1P               : -' in command_result :
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加路由模式下DHCP方式的WAN连接，不勾选开启VLAN
def add_oam_wan_dhcp_vlan_disable(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE,  service_type, interface_list):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s connection-mode route service-type %s ip-mode dhcp mtu 1500 bind-if %s' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, service_type, interface_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : route' in command_result and 'VLAN ID              : -' in command_result and '802.1P               : -' in command_result and 'IP Mode              : Dhcp' in command_result:
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加路由模式下STATIC方式的WAN连接，不勾选开启VLAN
def add_oam_wan_static_vlan_disable(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE,  service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, interface_list):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s connection-mode route service-type %s ip-mode static ip-address %s mask %s gateway %s dns %s secondary-dns %s mtu 1500 bind-if %s' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2, interface_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : route' in command_result and 'VLAN ID              : -' in command_result and '802.1P               : -' in command_result and 'IP Mode              : Static' in command_result:
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加路由模式下PPPoE方式的WAN连接，不勾选开启VLAN
def add_oam_wan_pppoe_vlan_disable(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE, service_type, pppoe_name, pppoe_password,interface_list):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s connection-mode route service-type %s ip-mode pppoe %s %s mtu  1500 bind-if %s' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, service_type, pppoe_name, pppoe_password, interface_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : route' in command_result and 'VLAN ID              : -' in command_result and '802.1P               : -' in command_result and 'IP Mode              : Pppoe' in command_result:
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加桥接的WAN连接，勾选开启VLAN，并且不绑定任何端口
def add_oam_wan_bridge_not_bind(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s %s %s connection-mode bridge service-type %s mtu 1500 bind-if not-bind' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    time.sleep(5)
    command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : bridge' in command_result and 'VLAN ID              : %s'%(User_Vlan) in command_result and '802.1P               : %s'%(WAN_pri) in command_result :
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加路由模式下DHCP方式的WAN连接，勾选开启VLAN，并且不绑定任何端口
def add_oam_wan_dhcp_not_bind(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s %s %s connection-mode route service-type %s ip-mode dhcp mtu 1500 bind-if not-bind' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : route' in command_result and 'VLAN ID              : %s'%(User_Vlan) in command_result and '802.1P               : %s'%(WAN_pri) in command_result and 'IP Mode              : Dhcp' in command_result:
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加路由模式下STATIC方式的WAN连接，勾选开启VLAN，并且不绑定任何端口
def add_oam_wan_static_not_bind(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s %s %s connection-mode route service-type %s ip-mode static ip-address %s mask %s gateway %s dns %s secondary-dns %s mtu 1500 bind-if not-bind' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, IP_addr, Net_mask, IP_default_gw, DNS1, DNS2)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : route' in command_result and 'VLAN ID              : %s'%(User_Vlan) in command_result and '802.1P               : %s'%(WAN_pri) in command_result and 'IP Mode              : Static' in command_result:
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加路由模式下PPPoE方式的WAN连接，勾选开启VLAN，并且不绑定任何端口
def add_oam_wan_pppoe_not_bind(tn, PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, pppoe_name, pppoe_password):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan config %s %s %s vlan %s %s %s connection-mode route service-type %s ip-mode pppoe %s %s mtu  1500 bind-if not-bind' % (PonID, OnuID, WAN_NAME, VLAN_ENABLE, User_Vlan , WAN_pri, service_type, pppoe_name, pppoe_password)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    for i in range(0,6):
        time.sleep(5)
        command_write = 'show ont wan name %s %s %s' % (PonID, OnuID, WAN_NAME)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Port                 : %s'%(PonID) in command_result and 'ONT-ID               : %s'%(OnuID) in command_result and 'WAN-Name             : %s'%(WAN_NAME) in command_result and  'Connection Mode      : route' in command_result and 'VLAN ID              : %s'%(User_Vlan) in command_result and '802.1P               : %s'%(WAN_pri) in command_result and 'IP Mode              : Pppoe' in command_result:
            cdata_info("OAM_WAN创建成功")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'ERROR: Unknown return code' in command_result:
            continue
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN创建失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 删除所有的OAM WAN连接       
def del_oam_wan(tn, PonID, OnuID):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'ont wan clear %s %s all' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show ont wan status %s %s all' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    if 'ONT wan is not exist!' in command_result:
        cdata_info("OAM_WAN删除成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("OAM_WAN删除失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 关闭EPON的PON口        
def shutdown_epon(tn, PonID):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'shutdown %s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show port state %s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    if 'Enable state                     : Disable' in command_result:
        cdata_info("EPON的OLT的PON口TX关闭成功。")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("EPON的OLT的PON口TX关闭失败。")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 开启EPON的PON口         
def no_shutdown_epon(tn, PonID):
    # 判断当前视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
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
    command_write = 'no shutdown %s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show port state %s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    if 'Enable state                     : Enable' in command_result:
        cdata_info("EPON的OLT的PON口TX开启成功。")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("EPON的OLT的PON口TX开启失败。")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
        
        
# 关闭GPON的PON口         
def shutdown_gpon(tn, PonID):
    # 判断当前视图是否正确
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
    command_write = 'shutdown %s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show port state %s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Admin state                      : disable' in command_result:
        cdata_info("GPON的OLT的PON口TX关闭成功。")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("GPON的OLT的PON口TX关闭失败。")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 开启GPON的PON口         
def no_shutdown_gpon(tn, PonID):
    # 判断当前视图是否正确
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
    command_write = 'no shutdown %s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    command_write = 'show port state %s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if 'Admin state                      : enable' in command_result:
        cdata_info("GPON的OLT的PON口TX开启成功。")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("GPON的OLT的PON口TX开启失败。")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
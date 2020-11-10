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

# 解决pon_id和onu_id不为个位数的时候，非升级测试用例判断失败的问题
def ttt(pon_id, onu_id):
    command = ''
    if len(pon_id) == 1:
        if len(onu_id) == 1:
            command = '0/0  %s  %s   ' % (pon_id, onu_id)
        else:
            command = '0/0  %s  %s  ' % (pon_id, onu_id)
    else:
        if len(onu_id) == 1:
            command = '0/0  %s %s   ' % (pon_id, onu_id)
        else:
            command = '0/0  %s %s  ' % (pon_id, onu_id)
    return command

# 解决pon_id和onu_id不为个位数的时候，升级测试用例判断失败的问题
def ttt1(pon_id, onu_id):
    command = ''
    if len(pon_id) == 1:
        if len(onu_id) == 1:
            command = '0/0  %s  %s   ' % (pon_id, onu_id)
        else:
            command = '0/0  %s  %s  ' % (pon_id, onu_id)
    else:
        if len(onu_id) == 1:
            command = '0/0 %s  %s   ' % (pon_id, onu_id)
        else:
            command = '0/0 %s  %s  ' % (pon_id, onu_id)
    return command

# 检测ONU是否可以自动发现
def autofind_onu(tn, PonID, OnuID, ONU_MAC):

    # 判断当前的视图是否正确。
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

    # 判断ONU是否可以被自动发现
    for i in range(1, 12):
        time.sleep(10)
        command_write = 'show ont autofind %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if ONU_MAC in command_result:
            cdata_info("ONU在OLT上被重新被发现。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上发现失败。")
        cdata_info("==========================================")
        return False

    # 判断当前ONU_ID是否已经被占用
    command_write = 'show ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    if 'The ONT is not exist' in command_result:
        cdata_info("当前ONU_ID没有被占用。")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("当前ONU_ID被占用,请更改ONU_ID或者删除该ONU后再进行测试")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 使用MAC认证ONU
def auth_by_mac(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, ONU_MAC):

    # 判断当前的视图是否正确。
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

    # 以SN的方式添加ONU
    command_write = 'ont add %s %s mac-auth %s ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, ONU_MAC, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)

    # 判断OLT上，ONU是否添加成功
    for i in range(0, 3):
        time.sleep(3)
        command_write = 'show ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(ttt(PonID, OnuID) + ONU_MAC)
        if ttt(PonID, OnuID) + ONU_MAC in command_result:
            cdata_info("ONU在OLT上添加成功。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上添加失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
    time.sleep(30)
    # 判断ONU是否认证成功
    for i in range(0, 6):
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        time.sleep(10)
        tn.write(command_write.encode('ascii') + b"\n")
        # tn.write(b"show ont info 2 1" + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if 'Run state            : online' in command_result and 'Config state         : success' in \
                command_result and 'Auth mode            : mac-auth' in command_result:
            cdata_info("ONU在OLT上通过MAC注册成功。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state            : online' in command_result and 'Config state         : failed' in \
                command_result and 'Auth mode            : mac-auth' in command_result:
            cdata_info("==========================================")
            cdata_error("===============ERROR!!!===================")
            cdata_error("查看ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上通过SN注册失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 使用LOID认证ONU        
def auth_by_loid(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, LOID, ONU_MAC):

    # 判断当前的视图是否正确。
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

    # 以SN的方式添加ONU
    command_write = 'ont add %s %s loid-auth %s ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, LOID, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    time.sleep(10)
    # 判断OLT上，ONU是否添加成功
    for i in range(0, 3):
        time.sleep(10)
        command_write = 'show ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if ttt(PonID, OnuID) + ONU_MAC in command_result:
            cdata_info("ONU在OLT上添加成功。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上添加失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
    time.sleep(30)
    # 判断ONU是否认证成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        # tn.write(b"show ont info 2 1" + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if 'Run state            : online' in command_result and 'Config state         : success' in \
                command_result and 'Auth mode            : loid-auth' in command_result:
            cdata_info("ONU在OLT上通过MAC注册成功。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state            : online' in command_result and 'Config state         : failed' in \
                command_result and 'Auth mode            : loid-auth' in command_result:
            cdata_info("==========================================")
            cdata_error("===============ERROR!!!===================")
            cdata_error("查看ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上通过SN注册失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False        

# 使用LOID+PASSWORD认证ONU              
def auth_by_loid_password(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, LOID, LOID_PASSWORD, ONU_MAC):

    # 判断当前的视图是否正确。
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

    # 以SN的方式添加ONU
    command_write = 'ont add %s %s loid-auth %s password-auth %s ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, LOID, LOID_PASSWORD, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    time.sleep(10)
    # 判断OLT上，ONU是否添加成功
    for i in range(0, 3):
        time.sleep(10)
        command_write = 'show ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        print(ttt(PonID, OnuID) + ONU_MAC)
        if ttt(PonID, OnuID) + ONU_MAC in command_result:
            cdata_info("ONU在OLT上添加成功。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上添加失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
    time.sleep(30)
    # 判断ONU是否认证成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        # tn.write(b"show ont info 2 1" + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if 'Run state            : online' in command_result and 'Config state         : success' in \
                command_result and 'Auth mode            : loid-password-auth' in command_result:
            cdata_info("ONU在OLT上通过MAC注册成功。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state            : online' in command_result and 'Config state         : failed' in \
                command_result and 'Auth mode            : loid-password-auth' in command_result:
            cdata_info("==========================================")
            cdata_error("===============ERROR!!!===================")
            cdata_error("查看ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上通过SN注册失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False  

# 添加sercice-port，可以使用列表的形式批量添加
def add_pon_vlan(tn, PonID, Vlan_list):
    # 判断当前的视图是否正确。
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

    command_write = 'vlan  mode %s trunk' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    command_write = 'vlan trunk %s %s' % (PonID, Vlan_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    command_write = 'show port vlan %s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')

    if Vlan_list in command_result:
        cdata_info('PON口的VLAN添加成功')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('PON口的VLAN添加失败。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_pon_vlan_untag(tn, PonID, Vlan_list):
    # 判断当前的视图是否正确。
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

    command_write = 'vlan  mode %s hybrid' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    command_write = 'vlan hybrid %s untagged %s' % (PonID, Vlan_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    command_write = 'show port vlan %s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')

    if Vlan_list in command_result:
        cdata_info('PON口的VLAN添加成功')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('PON口的VLAN添加失败。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def add_pon_native_vlan(tn, PonID, Vlan_list):
    # 判断当前的视图是否正确。
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

    command_write = 'vlan native-vlan %s %s' % (PonID, Vlan_list)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    command_write = 'show port state %s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')

    if 'Native vlan                      : %s'%(Vlan_list) in command_result:
        cdata_info('PON口的VLAN添加成功')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('PON口的VLAN添加失败。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

def bind_dba(tn, PonID, Dba_Profile_ID, Ont_Lineprofile_ID):
    # 判断当前的视图是否正确。
    tn.write(b"\n")
    result = tn.read_until(b"OLT(config)#", timeout=2)
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

    command_write = 'ont-lineprofile epon profile-id %s' % (Ont_Lineprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-epon-lineprofile-200)#", timeout=2)
    command_write = 'llid 1 dba-profile-id %s' % (Dba_Profile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    command_write = 'commit'
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-epon-lineprofile-200)#", timeout=2)
    
    command_write = 'show ont-lineprofile current'
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-epon-lineprofile-200)#", timeout=2).decode('ascii')
    print(command_result)
    if 'DBA Profile-ID      : %s'%(Dba_Profile_ID) in command_result:
        cdata_info('DBA模板绑定成功。')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('DBA模板绑定失败。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 删除sercice-port
def del_pon_vlan(tn, PonID, OnuID):
    # 判断当前的视图是否正确。
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
        
    command_write = 'no vlan trunk % 2-4094' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    command_write = 'show port vlan $s' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    
    if Vlan_list not in command_result:
        cdata_info('PON口的VLAN删除成功')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('PON口的VLAN删除失败。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 添加native-vlan
def ont_native_vlan(tn, PonID, OnuID, Onu_port_ID, User_vlan):
    # 判断当前的视图是否正确。
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
    command_write = 'ont port vlan %s %s eth %s %s' % (PonID, OnuID, Onu_port_ID, User_vlan)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    time.sleep(5)
    command_write = 'ont port native-vlan  %s %s eth %s vlan %s' % (PonID, OnuID, Onu_port_ID, User_vlan)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    # 查看NATIVE-VLAN是否添加成功
    time.sleep(5)
    tn.write(b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    command_write = 'show ont port  vlan remote %s %s eth %s' % (PonID, OnuID, Onu_port_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(10)
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    if 'Default VLAN VID       : %s'  % (User_vlan) in command_result:
        cdata_info("ONT Native-vlan配置成功")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONT Native-vlan配置失败")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")

        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 查看ONU的基本信息
def get_onu_info(tn, PonID, OnuID, ONU_MAC):

    # 判断当前的视图是否正确。
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
        

    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    command_write = 'show ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    get_ont_info = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(get_ont_info)
    
    command_write = 'show ont capability %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    get_ont_capability = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(get_ont_capability)
    
    command_write = 'show ont optical-info  %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    get_ont_optical_info = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(get_ont_optical_info)
    
    command_write = 'show ont version %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    get_ont_version = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(get_ont_version)
    
    
    # 获取ONU的关键参数
    if ONU_MAC in get_ont_info:
        # 提取ONU的关键参数
        FrameID_SlotID = re.findall('Frame/Slot           : (.*)', get_ont_info)
        Port = re.findall('Port                 : (.*)', get_ont_info)
        ONT_ID = re.findall('ONT-ID               : (.*)', get_ont_info)
        Control_flag = re.findall('Control flag         : (.*)', get_ont_info)
        Run_state = re.findall('Run state            : (.*)', get_ont_info)
        Config_state = re.findall('Config state         : (.*)', get_ont_info)
        Match_state = re.findall('Match state          : (.*)', get_ont_info)
        Distance = re.findall('ONT distance         : (.*)', get_ont_info)
        Authentic_mode = re.findall('Auth mode            : (.*)', get_ont_info)
        MAC_read = re.findall('MAC                  : (.*)', get_ont_info)

        ONT_TYPE = re.findall('Type                           : (.*)', get_ont_capability)
        Number_of_uplink_PON_ports = re.findall('Number of uplink PON ports     : (.*)', get_ont_capability)
        Number_of_ETH_ports = re.findall('Number of ETH ports            : (.*)', get_ont_capability)
        Number_of_POTS_ports = re.findall('Number of POTS ports           : (.*)', get_ont_capability)
        Number_of_CATV_UNI_ports = re.findall('Number of CATV ports           : (.*)', get_ont_capability)
        Number_of_WIFI = re.findall('Number of wifi ports           : (.*)', get_ont_capability)
        Number_of_uplink_queues = re.findall('Number of uplink queues        : (.*)', get_ont_capability)
        MAX_Number_of_uplink_queues = re.findall('MAX number of uplink queues    : (.*)', get_ont_capability)
        Number_of_downlink_queues = re.findall('Number of downlink queues      : (.*)', get_ont_capability)
        MAX_Number_of_downlink_queues = re.findall('MAX number of downlink queues  : (.*)', get_ont_capability)
        Number_of_LLID = re.findall('Number of LLID                 : (.*)', get_ont_capability)
        IPv6_Supported = re.findall('IPv6 Supported                 : (.*)', get_ont_capability) 

        Vendor_ID = re.findall('Vendor-ID                  : (.*)', get_ont_version)
        ONT_hardware_version = re.findall('ONT hardware version       : (.*)', get_ont_version)
        ONT_model = re.findall('ONT model                  : (.*)', get_ont_version)
        Extended_model = re.findall('Extended model             : (.*)', get_ont_version)
        ONT_software_version = re.findall('ONT software version       : (.*)', get_ont_version)
        ONT_chipset_vendor_ID = re.findall('ONT chipset vendor ID      : (.*)', get_ont_version)
        ONT_chipset_model = re.findall('ONT chipset model          : (.*)', get_ont_version)
        ONT_chipset_revision = re.findall('ONT chipset revision       : (.*)', get_ont_version)
        ONT_chipset_version = re.findall('ONT chipset version/date   : (.*)', get_ont_version)
        ONT_firmware_version = re.findall('ONT firmware version       : (.*)', get_ont_version) 

        Voltage = re.findall('Voltage\(V\)                 : (.*)', get_ont_optical_info)
        Tx_optical_power = re.findall('Tx optical power\(dBm\)      : (.*)', get_ont_optical_info)
        Rx_optical_power = re.findall('Rx optical power\(dBm\)      : (.*)', get_ont_optical_info)
        Laser_bias_current = re.findall('Laser bias current\(mA\)     : (.*)', get_ont_optical_info)
        Temperature = re.findall('Temperature\(C\)             : (.*)', get_ont_optical_info)        

        
        # 读取ONU的关键参数
        cdata_info("==========================================================")
        cdata_info('               ONU的基本信息：')
        cdata_info("==========================================================")
        cdata_info('机箱号和槽位号   ：%s' % (FrameID_SlotID[0]))
        cdata_info('PON口号          ：%s' % (Port[0]))
        cdata_info('ONU ID           ：%s' % (ONT_ID[0]))
        cdata_info('控制标志位       ：%s' % (Control_flag[0]))
        cdata_info('运行状态         ：%s' % (Run_state[0]))
        cdata_info('配置状态         ：%s' % (Config_state[0]))
        cdata_info('能力匹配状态     ：%s' % (Match_state[0]))
        cdata_info('测距距离         ：%s' % (Distance[0]))
        cdata_info('认证方式         ：%s' % (Authentic_mode[0]))
        cdata_info('MAC地址          ：%s' % (MAC_read[0]))
        cdata_info("==========================================================")
        cdata_info('\n') 
        cdata_info("==========================================================")
        cdata_info('               ONU上报的版本信息：')
        cdata_info("==========================================================")
        cdata_info('硬件版本号       ：%s' % (ONT_hardware_version[0]))
        cdata_info('软件版本号       ：%s' % (ONT_software_version[0]))
        cdata_info('Vendor ID        ：%s' % (Vendor_ID[0]))        
        cdata_info('ONT_model        ：%s' % (ONT_model[0]))
        cdata_info('Extended_model   ：%s' % (Extended_model[0]))
        cdata_info('芯片Vendor ID    ：%s' % (ONT_chipset_vendor_ID[0]))
        cdata_info('芯片型号         ：%s' % (ONT_chipset_model[0]))
        cdata_info('芯片revision     ：%s' % (ONT_chipset_revision[0]))
        cdata_info('芯片evision      ：%s' % (ONT_chipset_version[0]))
        cdata_info('固件版本         ：%s' % (ONT_firmware_version[0]))
        cdata_info("==========================================================")
        cdata_info('\n')
        cdata_info("==========================================================")
        cdata_info('               ONU上报的能力集信息：')
        cdata_info("==========================================================")
        cdata_info('ONU类型          ：%s' % (ONT_TYPE[0]))
        cdata_info('PON口接口数量    ：%s' % (Number_of_uplink_PON_ports[0]))
        cdata_info('以太网口数量     ：%s' % (Number_of_ETH_ports[0]))
        cdata_info('语音口数量       ：%s' % (Number_of_POTS_ports[0]))
        cdata_info('CATV接口数量     ：%s' % (Number_of_CATV_UNI_ports[0]))
        cdata_info('WIFI接口数量     ：%s' % (Number_of_WIFI[0]))
        cdata_info('上行队列数量     ：%s' % (Number_of_uplink_queues[0]))
        cdata_info('最大上行队列数量 ：%s' % (MAX_Number_of_uplink_queues[0]))
        cdata_info('下行队列数量     ：%s' % (Number_of_downlink_queues[0]))
        cdata_info('最大下行队列数量 ：%s' % (MAX_Number_of_downlink_queues[0]))
        cdata_info('LLID数量         ：%s' % (Number_of_LLID[0]))
        cdata_info('是否支持IPV6     ：%s' % (IPv6_Supported[0]))
        cdata_info("==========================================================")
        cdata_info('\n')    
        cdata_info("==========================================================")
        cdata_info('               ONU上报的光参数信息：')
        cdata_info("==========================================================")
        cdata_info('电压(V)             ：%s' % (Voltage[0]))
        cdata_info('TX光功率(dBm)       ：%s' % (Tx_optical_power[0]))
        cdata_info('RX光功率(dBm)       ：%s' % (Rx_optical_power[0]))
        cdata_info('电流(mA)            ：%s' % (Laser_bias_current[0]))
        cdata_info('温度(℃)            ：%s' % (Temperature[0]))
        cdata_info("==========================================================")
        cdata_info('\n')
        
        # 将ONU信息查询的结果保存到本地文件
        now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())) 
        current_dir = os.getcwd()
        file_path = current_dir[:current_dir.index('tests')] + 'data\\'
        filename = file_path + now+ '_epon_hgu_get_version.txt'
        print(filename)
        with open(filename,"w") as file:
            file.write("==========================================================\n")
            file.write('               ONU的基本信息：\n')
            file.write("==========================================================\n")
            file.write('机箱号和槽位号   ：%s' % (FrameID_SlotID[0]))
            file.write('PON口号          ：%s' % (Port[0]))
            file.write('ONU ID           ：%s' % (ONT_ID[0]))
            file.write('控制标志位       ：%s' % (Control_flag[0]))
            file.write('运行状态         ：%s' % (Run_state[0]))
            file.write('配置状态         ：%s' % (Config_state[0]))
            file.write('能力匹配状态     ：%s' % (Match_state[0]))
            file.write('测距距离         ：%s' % (Distance[0]))
            file.write('认证方式         ：%s' % (Authentic_mode[0]))
            file.write('MAC地址          ：%s' % (MAC_read[0]))
            file.write("==========================================================\n")
            file.write("==========================================================\n")
            file.write('               ONU上报的版本信息：\n')
            file.write("==========================================================\n")
            file.write('硬件版本号       ：%s' % (ONT_hardware_version[0]))
            file.write('软件版本号       ：%s' % (ONT_software_version[0]))
            file.write('Vendor ID        ：%s' % (Vendor_ID[0]))        
            file.write('ONT_model        ：%s' % (ONT_model[0]))
            file.write('Extended_model   ：%s' % (Extended_model[0]))
            file.write('芯片Vendor ID    ：%s' % (ONT_chipset_vendor_ID[0]))
            file.write('芯片型号         ：%s' % (ONT_chipset_model[0]))
            file.write('芯片revision     ：%s' % (ONT_chipset_revision[0]))
            file.write('芯片evision      ：%s' % (ONT_chipset_version[0]))
            file.write('固件版本         ：%s' % (ONT_firmware_version[0]))
            file.write("==========================================================\n")
            file.write("==========================================================\n")
            file.write('               ONU上报的能力集信息：\n')
            file.write("==========================================================\n")
            file.write('ONU类型          ：%s' % (ONT_TYPE[0]))
            file.write('PON口接口数量    ：%s' % (Number_of_uplink_PON_ports[0]))
            file.write('以太网口数量     ：%s' % (Number_of_ETH_ports[0]))
            file.write('语音口数量       ：%s' % (Number_of_POTS_ports[0]))
            file.write('CATV接口数量     ：%s' % (Number_of_CATV_UNI_ports[0]))
            file.write('WIFI接口数量     ：%s' % (Number_of_WIFI[0]))
            file.write('上行队列数量     ：%s' % (Number_of_uplink_queues[0]))
            file.write('最大上行队列数量 ：%s' % (MAX_Number_of_uplink_queues[0]))
            file.write('下行队列数量     ：%s' % (Number_of_downlink_queues[0]))
            file.write('最大下行队列数量 ：%s' % (MAX_Number_of_downlink_queues[0]))
            file.write('LLID数量         ：%s' % (Number_of_LLID[0]))
            file.write('是否支持IPV6     ：%s' % (IPv6_Supported[0]))
            file.write("==========================================================\n")    
            file.write("==========================================================\n")
            file.write('               ONU上报的光参数信息：\n')
            file.write("==========================================================\n")
            file.write('电压(V)             ：%s' % (Voltage[0]))
            file.write('TX光功率(dBm)       ：%s' % (Tx_optical_power[0]))
            file.write('RX光功率(dBm)       ：%s' % (Rx_optical_power[0]))
            file.write('电流(mA)            ：%s' % (Laser_bias_current[0]))
            file.write('温度(℃)            ：%s' % (Temperature[0]))
            file.write("==========================================================\n")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("查询ONU基本信息失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
        
# 远程重启ONU
def reboot_onu(tn, PonID, OnuID):
    # 判断当前的视图是否正确。
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

    # 在OLT上执行重启ONU的命令
    command_write = 'ont reboot %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')

    # 判断ONU是否重启
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if 'Run state            : offline' in command_result and 'Config state         : initial' \
                in command_result and 'Match state          : initial' in command_result:
            cdata_info("ONU正在重启。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU执行重启失败")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
    time.sleep(30)
    # 判断ONU重启后，是否可以注册成功
    for i in range(1, 12):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Run state            : online' in command_result and 'Config state         : success' \
                in command_result and 'Match state          : match' in command_result:
            cdata_info("ONU重启完成。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state            : online' in command_result and 'Config state         : failed' in \
                command_result and 'Match state          : match' in command_result:
            cdata_info("==========================================")
            cdata_error("===============ERROR!!!===================")
            cdata_error("ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU重启后，无法上线")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 去激活ONU
def deactive_onu(tn, PonID, OnuID):
    # 判断当前的视图是否正确。
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
    command_write = 'ont deactivate %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')

    # 判断ONU是否离线
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if 'Control flag         : deactive' in command_result:
            cdata_info("ONU去激活成功。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error(" ONU去激活失败")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行重新开启ONU的TX的命令
    command_write = 'ont activate %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')

    # 查看ONU是否可以重新上线
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        # tn.write(b"show ont info 2 1" + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if 'Control flag         : active' in command_result:
            cdata_info("ONU激活成功。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Control flag         : active' in command_result and 'Config state         : failed' in \
                command_result:
            cdata_info("==========================================")
            cdata_info("===============ERROR!!!===================")
            cdata_error("ONU去激活失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU重新上线失败")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# OMCI升级ONU
def upgrade_onu(tn, PonID, OnuID, tftp_server_ip, file_name):
    # 判断当前的视图是否正确。
    tn.write(b"\n")
    result = tn.read_until(b"OLT(config)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        tn.write(b"exit" + b"\n")
        cdata_info("==========================================")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 判断OLT上是否有升级文件
    command_write = 'show file %s ' % (file_name)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
    if 'not found!' in command_result:

        # 通过TFTP加载升级文件
        cdata_info('升级文件不存在，需要从TFTP加载升级文件。')
        command_write = 'load file tftp %s  %s ' % (tftp_server_ip, file_name)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config)#", timeout=120).decode('ascii')
        time.sleep(1)
        tn.write(b'\n')
        command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')

        # 判断升级文件是否加载失败
        if 'download is: Failed' in command_result:
            cdata_info("==========================================")
            cdata_info("===============ERROR!!!===================")
            cdata_error('文件或者服务器地址错误，请检查服务器地址或者文件名称')
            cdata_info("==========================================")
            return False
    else:
        cdata_info('步骤1：升级文件已存在，不需要从TFTP加载升级文件。')


    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    # 选择需要升级的ONU
    command_write = 'ont load select %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    time.sleep(1)
    tn.write(b"exit" + b"\n")
    result = tn.read_until(b"OLT(config)#", timeout=2)
    
    # 判断升级的ONU是否选择成功
    tn.write(b"show ont load select" + b"\n")
    command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
    print(command_result)
    print(ttt1(PonID, OnuID) + '    waiting      -')
    if ttt1(PonID, OnuID) + '    waiting      -' in command_result:
        cdata_info('选择升级的ONU成功')
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('选择升级的ONU失败')
        cdata_info("==========================================")
        return False

    # 开始执行升级ONU的命令
    command_write = 'ont load start %s commit-mode auto' % (file_name)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
    time.sleep(10)
    
    # 查看ONU的升级进度
    tn.write(b"show ont load select" + b"\n")
    command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
    if ttt1(PonID, OnuID) + '    loading' in command_result:
        cdata_info('ONU正在升级......')
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('ONU进入升级进程失败')
        cdata_info("==========================================")
        return False
    # 等待ONU在OLT上升级完成
    for i in range(0, 12):
        time.sleep(10)
        tn.write(b"show ont load select" + b"\n")
        command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
        if ttt1(PonID, OnuID) + '    loading      100%' in command_result:
            cdata_info("ONU在OLT上升级完成。")
            break
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU升级等待超时，请检查ONU是否异常")
        cdata_info("==========================================")
        return False

    # 查看ONU升级完成后是否重启
    tn.write(b"interface epon 0/0" + b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    for i in range(0, 10):
        time.sleep(30)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if 'Run state            : offline' in command_result and 'Config state         : initial' \
                in command_result and 'Match state          : initial' in command_result:
            cdata_info("ONU正在重启。")
            break
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU重启超时，请检查ONU是否异常。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
    # 查看ONU重启完成后，是否可以注册成功
    for i in range(0, 10):
        time.sleep(30)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        # tn.write(b"show ont info 2 1" + b"\n")

        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if 'Run state            : online' in command_result and 'Config state         : success' \
                in command_result and 'Match state          : match' in command_result:
            cdata_info("ONU重启完成。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            break
        elif 'Run state         : online' in command_result and 'Config state      : failed' in \
                command_result and 'Match state          : match' in command_result:
            cdata_info("==========================================")
            cdata_info("===============ERROR!!!===================")
            cdata_error("ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU重启后注册失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
        
    tn.write(b"show ont load select" + b"\n")
    command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
    print(command_result)
    if ttt1(PonID, OnuID) + '    success      -' in command_result:
        cdata_info('ONU升级完成')
        return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('ONU升级失败')
        cdata_info("==========================================")
        return False    

# 删除ONU
def ont_del(tn, PonID, OnuID, ONU_MAC):
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

    # 删除当前ONU
    command_write = 'ont del %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')

    # 判断ONU是否删除成功
    command_write = 'show ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    if 'The ONT is not exist' in command_result:
        cdata_info("ONU在OLT上删除成功")
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU在OLT上删除失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 判断ONU是否可以重新被发现
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont autofind %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if ONU_MAC in command_result:
            cdata_info("ONU在OLT上被重新被发现。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU在OLT上不能被重新被发现")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

# 删除ONU(升级ONU专用)
def ont_del_1(tn, PonID, OnuID, SN):
    SN = SN_12_to_16(SN)

    # 判断当前的视图是否正确。
    tn.write(b"\n")
    result = tn.read_until(b"OLT(config)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 删除选择的升级ONU
    command_write = 'no ont load select 0/0 %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config)#", timeout=2)
    tn.write(b"show ont load select 0/0" + b"\n")
    command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
    if 'There is no ont in the loading list' in command_result \
            or 'Total: 0, waiting: 0, fail: 0, success: 0, loading: 0, cancel: 0' in command_result:
        cdata_info("删除选择升级的ONU成功")
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("删除选择升级的ONU失败")
        cdata_info("===============ERROR!!!===================")
        return False
    tn.write(b"interface epon 0/0" + b"\n")
    tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)

    # 删除当前ONU
    command_write = 'ont del %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')

    # 判断ONU是否删除成功
    command_write = 'show ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
    if 'Error: There is no ONT available' in command_result:
        cdata_info("ONU在OLT上删除成功")
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU在OLT上删除失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 判断ONU是否可以重新被发现
    for i in range(1, 60):
        command_write = 'show ont autofind %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2).decode('ascii')
        if SN in command_result:
            cdata_info("ONU在OLT上被重新被发现。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU在OLT上不能被重新被发现")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
        
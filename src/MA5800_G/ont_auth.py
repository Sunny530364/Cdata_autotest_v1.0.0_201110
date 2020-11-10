import getpass
import telnetlib
import os
import sys
import time
import re
from src.config.initialization_config import *
from src.config.telnet_client_MA5800 import *
from os.path import dirname, abspath
from src.config.Cdata_loggers import *

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)

# 解决pon_id和onu_id不为个位数的时候，非升级测试用例判断失败的问题
def ttt(pon_id, onu_id):
    command = ''
    if len(pon_id) == 1:
        if len(onu_id) == 1:
            command = '0/ 1/%s    %s  ' % (pon_id, onu_id)
        else:
            command = '0/ 1/%s   %s  ' % (pon_id, onu_id)
    else:
        if len(onu_id) == 1:
            command = '0/ 1/%s   %s  ' % (pon_id, onu_id)
        else:
            command = '0/ 1/%s  %s  ' % (pon_id, onu_id)
    return command

# 解决pon_id和onu_id不为个位数的时候，升级测试用例判断失败的问题
def ttt1(pon_id, onu_id):
    command = ''
    if len(pon_id) == 1:
        if len(onu_id) == 1:
            command = '0/1/%s               %s            ' % (pon_id, onu_id)
        else:
            command = '0/1/%s              %s            ' % (pon_id, onu_id)
    else:
        if len(onu_id) == 1:
            command = '0/1/%s              %s            ' % (pon_id, onu_id)
        else:
            command = '0/1/%s             %s            ' % (pon_id, onu_id)
    return command

# 转换成华为显示的MAC地址(如：aa:bb:cc:dd:ee:ff转成aabb-ccdd-eeff)
def SN_12_to_16(SN):
    temp = ''
    if len(SN) == 12:
        temp = str(hex(ord(SN[0])))[2:] + str(hex(ord(SN[1])))[2:] + str(hex(ord(SN[2])))[2:] + str(hex(ord(SN[3])))[2:]
        SN = temp + SN[4:]
    return SN


# 16位的SN号转成12位的SN号
def SN_16_to_12(SN):
    temp = ''
    if len(SN) == 16:
        temp = chr(int('0x' + (SN[0:2]), 16)) + chr(int('0x' + (SN[2:4]), 16)) + chr(int('0x' + (SN[4:6]), 16)) + chr(
            int('0x' + (SN[6:8]), 16))
        SN = temp + SN[8:]
    return SN

# 检测ONU是否可以自动发现
def autofind_onu(tn, PonID, OnuID, SN):
    SN = SN_12_to_16(SN)
    
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

    # 判断ONU是否可以被自动发现
    for i in range(1, 12):
        time.sleep(10)
        command_write = 'display ont autofind %s' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        print(command_result)
        print(SN)
        if SN in command_result:
            cdata_info("ONU在OLT上被重新被发现。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上发现失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

    # 判断当前ONU_ID是否已经被占用
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
    command_write = 'display ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
    print(command_result)
    if 'Failure: The ONT does not exist' in command_result:
        cdata_info("当前ONU_ID没有被占用。")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("当前ONU_ID被占用,请更改ONU_ID或者删除该ONU后再进行测试")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

# 使用MAC认证ONU
def auth_by_sn(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, SN):
    SN = SN_12_to_16(SN)
    
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

    # 以SN的方式添加ONU
    command_write = 'ont add %s %s sn-auth %s omci ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, SN, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)

    # 判断OLT上，ONU是否添加成功
    for i in range(0, 13):
        time.sleep(3)
        command_write = 'display ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        print(ttt(PonID, OnuID) + SN)
        if ttt(PonID, OnuID) + SN in command_result:
            cdata_info("ONU在OLT上添加成功。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上添加失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    time.sleep(30)
    
    # 判断ONU是否认证成功
    for i in range(0, 6):
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        time.sleep(10)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        if 'Run state               : online' in command_result and 'Config state            : normal' in \
                command_result and 'Authentic type          : SN-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("ONU在OLT上通过SN注册成功。")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
        elif 'Run state               : online' in command_result and 'Config state            : failed' in \
                command_result and 'Authentic type          : SN-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("==========================================")
            cdata_error("===============ERROR!!!===================")
            cdata_error("查看ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上通过SN注册失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

def auth_by_sn_password(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, SN_PASSWORD, SN):
    SN = SN_12_to_16(SN)
    
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

    # 以SN的方式添加ONU
    command_write = 'ont add %s %s sn-auth %s password-auth %s omci ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, SN, SN_PASSWORD, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)

    # 判断OLT上，ONU是否添加成功
    for i in range(0, 3):
        time.sleep(3)
        command_write = 'display ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        print(ttt(PonID, OnuID) + SN)
        if ttt(PonID, OnuID) + SN in command_result:
            cdata_info("ONU在OLT上添加成功。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上添加失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    time.sleep(30)
    
    # 判断ONU是否认证成功
    for i in range(0, 6):
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        time.sleep(10)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        if 'Run state               : online' in command_result and 'Config state            : normal' in \
                command_result and 'Authentic type          : SN-auth+password-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("ONU在OLT上通过MAC注册成功。")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
        elif 'Run state               : online' in command_result and 'Config state            : failed' in \
                command_result and 'Authentic type          : SN-auth+password-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("==========================================")
            cdata_error("===============ERROR!!!===================")
            cdata_error("查看ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上通过SN注册失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
        
def auth_by_snpassword(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, SN_PASSWORD, SN):
    SN = SN_12_to_16(SN)
    
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

    # 以SN的方式添加ONU
    command_write = 'ont add %s %s password-auth %s always-on omci ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, SN_PASSWORD, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
    time.sleep(30)
    # 判断OLT上，ONU是否添加成功
    for i in range(0, 3):
        time.sleep(3)
        command_write = 'display ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        print(ttt(PonID, OnuID) + SN)
        if ttt(PonID, OnuID) + SN in command_result:
            cdata_info("ONU在OLT上添加成功。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上添加失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    time.sleep(30)
    
    # 判断ONU是否认证成功
    for i in range(0, 6):
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        time.sleep(10)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        if 'Run state               : online' in command_result and 'Config state            : normal' in \
                command_result and 'Authentic type          : password-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("ONU在OLT上通过MAC注册成功。")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
        elif 'Run state               : online' in command_result and 'Config state            : failed' in \
                command_result and 'Authentic type          : password-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("==========================================")
            cdata_error("===============ERROR!!!===================")
            cdata_error("查看ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上通过SN注册失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

# 使用LOID认证ONU        
def auth_by_loid(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, LOID, SN):
    SN = SN_12_to_16(SN)
    
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

    # 以LOID的方式添加ONU
    command_write = 'ont add %s %s loid-auth %s always-on omci ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, LOID, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
    time.sleep(30)
    
    # 判断OLT上，ONU是否添加成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        if ttt(PonID, OnuID) + SN in command_result:
            cdata_info("ONU在OLT上添加成功。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上添加失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    time.sleep(30)
    
    # 判断ONU是否认证成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        # tn.write(b"display ont info 2 1" + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        if 'Run state               : online' in command_result and 'Config state            : normal' in \
                command_result and 'Authentic type          : loid-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("ONU在OLT上通过MAC注册成功。")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
        elif 'Run state               : online' in command_result and 'Config state            : failed' in \
                command_result and 'Authentic type          : MAC-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("==========================================")
            cdata_error("===============ERROR!!!===================")
            cdata_error("查看ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上通过SN注册失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False        

# 使用LOID+PASSWORD认证ONU              
def auth_by_loid_password(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, LOID, LOID_PASSWORD, SN):
    SN = SN_12_to_16(SN)
    
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

    # 以LOID+PASSWORD的方式添加ONU
    command_write = 'ont add %s %s loid-auth %s checkcode-auth %s always-on omci ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, LOID, LOID_PASSWORD, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
    time.sleep(30)
    
    # 判断OLT上，ONU是否添加成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        print(command_result)
        print(ttt(PonID, OnuID) + SN)
        if ttt(PonID, OnuID) + SN in command_result:
            cdata_info("ONU在OLT上添加成功。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上添加失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    time.sleep(30)
    
    # 判断ONU是否认证成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        # tn.write(b"display ont info 2 1" + b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        if 'Run state               : online' in command_result and 'Config state            : normal' in \
                command_result and 'Authentic type          : loid+checkcode-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("ONU在OLT上通过MAC注册成功。")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
        elif 'Run state               : online' in command_result and 'Config state            : failed' in \
                command_result and 'Authentic type          : MAC-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("==========================================")
            cdata_error("===============ERROR!!!===================")
            cdata_error("查看ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上通过SN注册失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False  

def add_service_port(tn, PonID, OnuID, Gemport_ID, Vlan_list):
    vlan_num = 0

    # 判断当前的视图是否正确。
    tn.write(b"\n")
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
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
    # 批量添加service-port
    for Cvlan in Vlan_list:
        command_write = 'service-port vlan  %s gpon 0/1/%s ont %s gemport %s multi-service   user-vlan  %s' % (
                            str(Cvlan), PonID, OnuID, Gemport_ID, str(Cvlan))
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2)

    # 查看service-port是否添加成功
    command_write = 'display  service-port  port  0/1/%s ont %s gemport %s' % (PonID, OnuID, Gemport_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2).decode('ascii')

    for Cvlan in Vlan_list:
        if str(Cvlan) in command_result:
            vlan_num = vlan_num + 1
    if vlan_num == len(Vlan_list):
        cdata_info('SERVICE-PORT添加成功')
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('SERVICE-PORT添加失败。')
        cdata_info("==========================================")
        return False

# 删除sercice-port
def del_service_port(tn, PonID, OnuID, Gemport_ID):
    # 判断当前的视图是否正确。
    tn.write(b"\n")
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
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
        
    # 删除掉service-port
    command_write = 'undo service-port port  0/1/%s ont %s '% (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    tn.write(b"y"+b"\n")
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    command_write = 'display  service-port port  0/1/%s ont  %s'%(PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2).decode('ascii')
    print(command_result)
    
    # 判断service-port是否删除成功
    if 'Failure: No service virtual port can be operated' in command_result:
        cdata_info('service_port删除成功。')
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('service_port删除失败。')
        cdata_info("==========================================")
        return False

# 添加native-vlan
def ont_native_vlan(tn, PonID, OnuID, Ont_Port_ID, User_vlan):
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
    time.sleep(5)
    
    # 添加native-vlan
    command_write = 'ont port native-vlan  %s %s eth %s vlan %s' % (PonID, OnuID, Ont_Port_ID, User_vlan)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
    
    # 查看NATIVE-VLAN是否添加成功
    time.sleep(5)
    tn.write(b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
    command_write = 'display ont port attribute %s %s eth %s' % (PonID, OnuID, Ont_Port_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
    print(command_result)
    if User_vlan in command_result:
        cdata_info("ONT Native-vlan配置成功")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONT Native-vlan配置失败")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

# 查看ONU的基本信息
def get_onu_info(tn, PonID, OnuID, SN):
    SN = SN_12_to_16(SN)
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
        
    # 查看ONU的基本信息
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
    command_write = 'display ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    get_ont_info = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
    print(get_ont_info)
    
    # 查看ONU上报的能力集信息
    command_write = 'display ont capability %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    get_ont_capability = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
    print(get_ont_capability)
    
    # 查看ONU的光功率信息
    command_write = 'display ont optical-info  %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    get_ont_optical_info = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
    print(get_ont_optical_info)
    
    # 查看ONU的版本信息
    command_write = 'display ont version %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    get_ont_version = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
    print(get_ont_version)
    
    print(SN)
    print(get_ont_info)
    # 获取ONU的关键参数
    if SN in get_ont_info:
        FrameID_SlotID_PonID = re.findall('F/S/P                   : (.*)', get_ont_info)
        ONT_ID = re.findall('ONT-ID                  : (.*)', get_ont_info)
        Control_flag = re.findall('Control flag            : (.*)', get_ont_info)
        Run_state = re.findall('Run state               : (.*)', get_ont_info)
        Config_state = re.findall('Config state            : (.*)', get_ont_info)
        Match_state = re.findall('Match state             : (.*)', get_ont_info)
        Distance = re.findall('ONT distance\(m\)         : (.*)', get_ont_info)
        Authentic_mode = re.findall('Authentic type          : (.*)', get_ont_info)
        MAC_read = re.findall('SN                      : (.*)', get_ont_info)
        
        for result in get_ont_capability.split('\r\n'):
            if 'ONT type' in result:
                ONT_TYPE = result[36:]
            if 'Number of uplink PON ports' in result:
                Number_of_uplink_PON_ports = result[36:]                
            if 'Number of POTS ports' in result:
                Number_of_POTS_ports = result[36:]               
            if 'Number of ETH ports' in result:
                Number_of_ETH_ports = result[36:]
            if 'Number of VDSL ports' in result:
                Number_of_VDSL_ports = result[36:]    
            if 'Number of TDM ports' in result:
                Number_of_TDM_ports = result[36:]
            if 'Number of MOCA ports' in result:
                Number_of_MOCA_ports = result[36:]
            if 'Number of CATV ANI ports' in result:
                Number_of_CATV_ANI_ports = result[36:]
            if 'Number of CATV UNI ports' in result:
                Number_of_CATV_UNI_ports = result[36:]
            if 'Number of GEM ports' in result:
                Number_of_GEM_ports = result[36:]
            if 'IP configuration' in result:
                IP_configuration = result[36:]
            if 'Number of Traffic Schedulers' in result:
                Number_of_Traffic_Schedulers = result[36:]
            if 'Number of T-CONTs' in result:
                Number_of_T_CONTs = result[36:]
            if 'The type of flow control' in result:
                The_type_of_flow_control = result[36:]
                
        Vendor_ID = re.findall('Vendor-ID                : (.*)', get_ont_version)
        ONT_hardware_version = re.findall('ONT Version              : (.*)', get_ont_version)
        Product_ID = re.findall('Product-ID               : (.*)', get_ont_version)
        Equipment_ID = re.findall('Equipment-ID             : (.*)', get_ont_version)
        Main_Software_Version = re.findall('Main Software Version    : (.*)', get_ont_version)
        Standby_Software_Version = re.findall('Standby Software Version : (.*)', get_ont_version)

        Voltage = re.findall('Voltage\(V\)                             : (.*)', get_ont_optical_info)
        Tx_optical_power = re.findall('Tx optical power\(dBm\)                  : (.*)', get_ont_optical_info)
        Rx_optical_power = re.findall('Rx optical power\(dBm\)                  : (.*)', get_ont_optical_info)
        Laser_bias_current = re.findall('Laser bias current\(mA\)                 : (.*)', get_ont_optical_info)
        Temperature = re.findall('Temperature\(C\)                         : (.*)', get_ont_optical_info)  
        CATV_Rx_optical_power = re.findall('OLT Rx ONT optical power\(dBm\)          : (.*)', get_ont_optical_info)
        OLT_Rx_ONT_optical_power = re.findall('CATV Rx optical power\(dBm\)             : (.*)', get_ont_optical_info)

        
        # 打印ONU的关键参数
        cdata_info("==========================================================")
        cdata_info('               ONU的基本信息：')
        cdata_info("==========================================================")
        cdata_info('机箱号和槽位号   ：%s' % (FrameID_SlotID_PonID[0]))
        cdata_info('ONU ID           ：%s' % (ONT_ID[0]))
        cdata_info('控制标志位       ：%s' % (Control_flag[0]))
        cdata_info('运行状态         ：%s' % (Run_state[0]))
        cdata_info('配置状态         ：%s' % (Config_state[0]))
        cdata_info('能力匹配状态     ：%s' % (Match_state[0]))
        cdata_info('测距距离         ：%s' % (Distance[0]))
        cdata_info('认证方式         ：%s' % (Authentic_mode[0]))
        cdata_info('SN号             ：%s' % (MAC_read[0]))
        cdata_info("==========================================================")
        cdata_info('\n') 
        cdata_info("==========================================================")
        cdata_info('               ONU上报的版本信息：')
        cdata_info("==========================================================")
        cdata_info('Vendor_ID        ：%s' % (Vendor_ID[0]))
        cdata_info('硬件版本号       ：%s' % (ONT_hardware_version[0]))
        cdata_info('Product_ID       ：%s' % (Product_ID[0]))        
        cdata_info('Equipment_ID     ：%s' % (Equipment_ID[0]))
        cdata_info('主分区版本号     ：%s' % (Main_Software_Version[0]))
        cdata_info('备分区版本号     ：%s' % (Standby_Software_Version[0]))

        cdata_info("==========================================================")
        cdata_info('\n')
        cdata_info("==========================================================")
        cdata_info('               ONU上报的能力集信息：')
        cdata_info("==========================================================")
        cdata_info('ONU类型           ：%s' % (ONT_TYPE))
        cdata_info('PON口接口数量     ：%s' % (Number_of_uplink_PON_ports))
        cdata_info('以太网口数量      ：%s' % (Number_of_ETH_ports))
        cdata_info('VDSL口数量        ：%s' % (Number_of_VDSL_ports))
        cdata_info('语音口数量        ：%s' % (Number_of_POTS_ports))
        cdata_info('TDM接口数量       ：%s' % (Number_of_TDM_ports))
        cdata_info('MOCA接口数量      ：%s' % (Number_of_TDM_ports))
        cdata_info('CATV_ANI接口数量  ：%s' % (Number_of_CATV_ANI_ports))
        cdata_info('CATV_UNI接口数量  ：%s' % (Number_of_CATV_UNI_ports))
        cdata_info('GEMPORT接口       ：%s' % (Number_of_GEM_ports))
        cdata_info('IP_host数量       ：%s' % (IP_configuration))
        cdata_info('流控队列数量      ：%s' % (Number_of_Traffic_Schedulers))
        cdata_info('T-CONTs数量       ：%s' % (Number_of_T_CONTs))
        cdata_info('是否支持流控      ：%s' % (The_type_of_flow_control)) 
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
        cdata_info('OLT接收光功率       ：%s' % (OLT_Rx_ONT_optical_power[0]))
        cdata_info('CATV接收光功率      ：%s' % (CATV_Rx_optical_power[0]))
        cdata_info("==========================================================")
        cdata_info('\n')
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("查询ONU基本信息失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
        
# 远程重启ONU
def reboot_onu(tn, PonID, OnuID):
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

    # 在OLT上执行重启ONU的命令
    command_write = 'ont reset %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"y"+b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')

    # 判断ONU是否重启
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        if 'Run state               : offline' in command_result and 'Config state            : initial' in command_result and 'Match state             : initial' in command_result:
            cdata_info("ONU正在重启。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU执行重启失败")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    time.sleep(30)
    
    # 判断ONU重启后，是否可以注册成功
    for i in range(1, 12):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Run state               : online' in command_result and 'Config state            : normal' in \
                command_result and 'Control flag            : active' in command_result and 'Match state             : match' in command_result:
            cdata_info("ONU重启完成。")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
        elif 'Run state               : failed' in command_result and 'Config state            : normal' in \
                command_result and 'Control flag            : active' in command_result and 'Match state             : match' in command_result:
            cdata_info("==========================================")
            cdata_error("===============ERROR!!!===================")
            cdata_error("ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU重启后，无法上线")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

# 去激活ONU
def deactive_onu(tn, PonID, OnuID):
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

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont deactivate %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')

    # 判断ONU是否离线
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        if 'Control flag            : deactivated' in command_result and 'Run state               : offline' in command_result and 'Config state            : initial' in command_result and 'Match state             : initial' in command_result:
            cdata_info("ONU去激活成功。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error(" ONU去激活失败")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

    # 在OLT上执行重新开启ONU的TX的命令
    command_write = 'ont activate %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
    time.sleep(30)
    
    # 查看ONU是否可以重新上线
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        # tn.write(b"display ont info 2 1" + b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Run state               : online' in command_result and 'Config state            : normal' in \
                command_result and 'Control flag            : active' in command_result and 'Match state             : match' in command_result:
            cdata_info("ONU激活成功。")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
        elif 'Run state               : online' in command_result and 'Config state            : failed' in \
                command_result and 'Control flag            : active' in command_result and 'Match state             : match' in command_result:

            cdata_info("==========================================")
            cdata_info("===============ERROR!!!===================")
            cdata_error("ONU去激活失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU重新上线失败")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

# OMCI升级ONU
def upgrade_onu(tn, PonID, OnuID, tftp_server_ip, file_name):
    # 判断当前的视图是否正确。
    tn.write(b"diagnose"+b"\n")
    result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

    # OLT上执行omci升级ONU
    command_write = 'ont-load stop'
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2).decode('ascii')
    command_write = 'ont-load info program %s tftp %s ' % (file_name, tftp_server_ip)
    tn.write(command_write.encode('ascii') + b"\n") 
    time.sleep(1)
    tn.write(b"\n")
    command_result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2).decode('ascii')
    command_write = 'ont-load select 0/1 %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2).decode('ascii')
    
    # 判断是否选择升级的ONU成功
    command_write = 'display ont-load select 0/1 %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    command_result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2).decode('ascii')
    if ttt1(PonID, OnuID) + "  Ready" in command_result:
        cdata_info('选择升级的ONU成功')
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('选择升级的ONU失败')
        cdata_info("==========================================")
        return False      
    command_write = 'ont-load start activemode immediate'
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2).decode('ascii')
    time.sleep(30)
    
    # 查看ONU的升级进度
    command_write = 'display ont-load select 0/1 %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    command_result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2).decode('ascii')
    if ttt1(PonID, OnuID) + 'Loading' in command_result:
        cdata_info('ONU正在升级......')
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('ONU进入升级进程失败')
        cdata_info("==========================================")
        return False
        
    # 查看ONU升级完成后是否重启
    tn.write(b"config" + b"\n")
    tn.read_until(b"MA5800-X15(config)#", timeout=2)
    tn.write(b"interface gpon 0/1" + b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
    for i in range(0, 30):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        if 'Run state               : offline' in command_result and 'Config state            : initial' in command_result and 'Match state             : initial' in command_result:
            cdata_info("ONU正在重启。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU执行重启失败")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    time.sleep(30)
    
    # 判断ONU重启后，是否可以注册成功
    for i in range(1, 12):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        print(command_result)
        if 'Run state               : online' in command_result and 'Config state            : normal' in \
                command_result and 'Control flag            : active' in command_result and 'Match state             : match' in command_result:
            cdata_info("ONU重启完成。")
            break
        elif 'Run state               : failed' in command_result and 'Config state            : normal' in \
                command_result and 'Control flag            : active' in command_result and 'Match state             : match' in command_result:
            cdata_info("==========================================")
            cdata_error("===============ERROR!!!===================")
            cdata_error("ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU重启后，无法上线")
        cdata_info("==========================================")
        return False
        
    # 查看ONU在OLT上是否升级完成    
    tn.write(b"quit" + b"\n")
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    tn.write(b"diagnose"+b"\n")
    result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2)
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont-load select 0/1 %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2).decode('ascii')
        if ttt1(PonID, OnuID) + 'Success' in command_result:
            cdata_info("ONU在OLT上升级完成。")
            tn.write(b"config" + b"\n")
            tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
            break
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU升级等待超时，请检查ONU是否异常")
        cdata_info("==========================================")
        tn.write(b"config" + b"\n")
        tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

# 删除ONU
def ont_del(tn, PonID, OnuID, SN):
    SN = SN_12_to_16(SN)
    
    # 判断当前的视图是否正确。
    tn.write(b"interface gpon 0/1" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

    # 删除当前ONU
    command_write = 'ont del %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')

    # 判断ONU是否删除成功
    command_write = 'display ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
    print(command_result)
    if 'The ONT does not exist' in command_result:
        cdata_info("ONU在OLT上删除成功")
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU在OLT上删除失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

    # 判断ONU是否可以重新被发现
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont autofind %s' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        if SN in command_result:
            cdata_info("ONU在OLT上被重新被发现。")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU在OLT上不能被重新被发现")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

# 删除ONU(升级ONU专用)
def ont_del_1(tn, PonID, OnuID, SN):
    SN = SN_12_to_16(SN)

    # 判断当前的视图是否正确。
    tn.write(b"\n")
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("===============ERROR!!!===================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

    # 删除选择的升级ONU
    command_write = 'no ont load select 0/0 %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    tn.write(b"display ont load select 0/0" + b"\n")
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2).decode('ascii')
    if 'There is no ont in the loading list' in command_result \
            or 'Total: 0, waiting: 0, fail: 0, success: 0, loading: 0, cancel: 0' in command_result:
        cdata_info("删除选择升级的ONU成功")
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("删除选择升级的ONU失败")
        cdata_info("===============ERROR!!!===================")
        return False
    tn.write(b"interface gpon 0/1" + b"\n")
    tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2)

    # 删除当前ONU
    command_write = 'ont del %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')

    # 判断ONU是否删除成功
    command_write = 'display ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
    if 'Error: There is no ONT available' in command_result:
        cdata_info("ONU在OLT上删除成功")
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU在OLT上删除失败")
        cdata_info("===============ERROR!!!===================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

    # 判断ONU是否可以重新被发现
    for i in range(1, 60):
        command_write = 'display ont autofind %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"MA5800-X15(config-if-gpon-0/1)#", timeout=2).decode('ascii')
        if SN in command_result:
            cdata_info("ONU在OLT上被重新被发现。")
            tn.write(b"quit" + b"\n")
            result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU在OLT上不能被重新被发现")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
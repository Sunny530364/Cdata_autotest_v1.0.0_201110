#!/usr/bin/python
# -*- coding UTF-8 -*-

import getpass
import telnetlib
import os
import sys
import time
import re
from src.config.telnet_client import *
from os.path import dirname, abspath
from src.config.Cdata_loggers import *

base_path = dirname(dirname(abspath(__file__)))
sys.path.insert(0, base_path)


# 12位的SN号，转成16位的SN号
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


# 解决pon_id和onu_id不为个位数的时候，非升级测试用例判断失败的问题
def ttt(pon_id, onu_id):
    command = ''
    if len(pon_id) == 1:
        if len(onu_id) == 1:
            command = '0/0 %s  %s   ' % (pon_id, onu_id)
        elif len(onu_id) == 2:
            command = '0/0 %s  %s  ' % (pon_id, onu_id)
        else:
            command = '0/0 %s  %s ' % (pon_id, onu_id)

    else:
        if len(onu_id) == 1:
            command = '0/0 %s %s   ' % (pon_id, onu_id)
        elif len(onu_id) == 2:
            command = '0/0 %s %s  ' % (pon_id, onu_id)
        else:
            command = '0/0 %s %s ' % (pon_id, onu_id)
    return command


# 解决pon_id和onu_id不为个位数的时候，升级测试用例判断失败的问题
def ttt1(pon_id, onu_id):
    command = ''
    if len(pon_id) == 1:
        if len(onu_id) == 1:
            command = '0/0 %s   %s   ' % (pon_id, onu_id)
        elif len(onu_id) == 2:
            command = '0/0 %s   %s  ' % (pon_id, onu_id)
        else:
            command = '0/0 %s   %s ' % (pon_id, onu_id)

    else:
        if len(onu_id) == 1:
            command = '0/0 %s  %s   ' % (pon_id, onu_id)
        elif len(onu_id) == 2:
            command = '0/0 %s  %s  ' % (pon_id, onu_id)
        else:
            command = '0/0 %s  %s ' % (pon_id, onu_id)
    return command


# 检测ONU是否可以自动发现
def autofind_onu(tn, PonID, OnuID, SN):
    SN_12_to_16(SN)

    # 判断当前的视图是否正确。
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
    command_write = 'show ont autofind %s all' % (PonID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')

    # 判断ONU是否可以被自动发现
    for i in range(0, 20):
        time.sleep(10)
        command_write = 'show ont autofind %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if SN in command_result:
            cdata_info("ONU在OLT上被重新被发现。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上发现失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 判断当前ONU_ID是否已经被占用
    command_write = 'show ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    print(command_result)
    if 'Error: There is no ONT available' in command_result:
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


# 使用SN认证ONU
def auth_by_sn(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, SN):
    SN = SN_16_to_12(SN)

    # 判断当前的视图是否正确。
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

    # 以SN的方式添加ONU
    command_write = 'ont add %s %s sn-auth %s ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, SN, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)

    # 判断OLT上，ONU是否添加成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if ttt(PonID, OnuID) + SN in command_result:
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

    # 判断ONU是否认证成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        # tn.write(b"show ont info 2 1" + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if 'Run state         : online' in command_result and 'Config state      : success' in \
                command_result and 'Authentic mode    : sn-auth' in command_result:
            cdata_info("ONU在OLT上通过SN注册成功。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state         : online' in command_result and 'Config state      : failed' in \
                command_result and 'Authentic mode    : sn-auth' in command_result:
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


# 使用SN的PASSWORD认证ONU
def auth_by_sn_password(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, SN, SN_PASSWORD):
    SN = SN_16_to_12(SN)

    # 判断当前的视图是否正确。
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

    # 以SN+PASSWORD的方式添加ONU
    command_write = 'ont add %s %s sn-auth %s password-auth %s ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, SN, SN_PASSWORD, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)

    # 判断OLT上，ONU是否添加成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if ttt(PonID, OnuID) + SN in command_result:
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

    # 判断ONU是否认证成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if 'Run state         : online' in command_result and 'Config state      : success' in \
                command_result and 'Authentic mode    : sn-password-auth' in command_result \
                and SN_PASSWORD in command_result:
            cdata_info("ONU在OLT上通过SN_PASSWORD注册成功。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state         : online' in command_result and 'Config state      : failed' in \
                command_result and 'Authentic mode    : sn-auth' in command_result:
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
        cdata_error("ONU在OLT上通过SN_PASSWORD注册失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False


# 使用SN的PASSWORD认证ONU
def auth_by_snpassword(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, SN, SN_PASSWORD):
    SN = SN_16_to_12(SN)

    # 判断当前的视图是否正确。
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

    # 以SN的PASSWORD的方式添加ONU
    command_write = 'ont add %s %s password-auth %s ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, SN_PASSWORD, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)

    # 判断OLT上，ONU是否添加成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if ttt(PonID, OnuID) + SN in command_result:
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

    # 判断ONU是否认证成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if 'Run state         : online' in command_result and 'Config state      : success' in command_result \
                and 'Authentic mode    : password-auth' in command_result and SN_PASSWORD in command_result:
            cdata_info("ONU在OLT上通过SN+PASSWORD注册成功。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state         : online' in command_result and 'Config state      : failed' in \
                command_result and 'Authentic mode    : sn-auth' in command_result:
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
        cdata_error("ONU在OLT上通过SN+PASSWORD注册失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False


# 使用LOID认证ONU
def auth_by_loid(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, LOID, SN):
    SN = SN_16_to_12(SN)

    # 判断当前的视图是否正确。
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

    # 以LOID的方式添加ONU
    command_write = 'ont add %s %s loid-auth %s ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, LOID, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)

    # 判断OLT上，ONU是否添加成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if ttt(PonID, OnuID) + SN in command_result:
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

    # 判断ONU是否认证成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        # tn.write(b"show ont info 2 1" + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if 'Run state         : online' in command_result and 'Config state      : success' \
                in command_result and 'Authentic mode    : loid-auth' in command_result and LOID in command_result:
            cdata_info("ONU在OLT上通过LOID注册成功。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state         : online' in command_result and 'Config state      : failed' in \
                command_result and 'Authentic mode    : sn-auth' in command_result:
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
        cdata_error("ONU在OLT上通过LOID注册失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False


# 使用LOID+PASSWORD认证ONU
def auth_by_loid_password(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, LOID, LOID_PASSWORD, SN):
    SN = SN_16_to_12(SN)

    # 判断当前的视图是否正确。
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

    # 以LOID+PASSWORD的方式添加ONU
    command_write = 'ont add %s %s loid-auth %s password-auth %s ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, LOID, LOID_PASSWORD, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)

    # 判断OLT上，ONU是否添加成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if ttt(PonID, OnuID) + SN in command_result:
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

    # 判断ONU是否认证成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if 'Run state         : online' in command_result and 'Config state      : success' \
                in command_result and 'Authentic mode    : loid-password-auth' in command_result and LOID in command_result and LOID_PASSWORD in command_result:
            cdata_info("ONU在OLT上通过LOID+PASSWORD注册成功。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state         : online' in command_result and 'Config state      : failed' in \
                command_result and 'Authentic mode    : sn-auth' in command_result:
            cdata_info("==========================================")
            cdata_info("===============ERROR!!!===================")
            cdata_error("ONU配置失败,请检查ONU的配置。")
            cdata_info("==========================================")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error("ONU在OLT上通过LOID+PASSWORD注册失败。")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False


# 添加sercice-port，可以使用列表的形式批量添加
def add_service_port(tn, PonID, OnuID, Gemport_ID, Vlan_list):
    vlan_num = 0

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

    for Cvlan in Vlan_list:
        command_write = 'service-port  autoindex vlan %s gpon 0/0 port %s ont %s gemport ' \
                        '%s multi-service user-vlan %s tag-action transparent' % (
                            str(Cvlan), PonID, OnuID, Gemport_ID, str(Cvlan))
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config)#", timeout=2)
    command_result = tn.read_until(b"OLT(config)#", timeout=2)

    command_write = 'show service-port gpon 0/0 port %s ont %s gemport %s' % (PonID, OnuID, Gemport_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')

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

def add_service_port_1(tn, PonID, OnuID, Gemport_ID, Vlan_list):
    vlan_num = 0

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
    command_write = 'no service-port gpon 0/0 port %s ont %s gemport %s '% ( PonID, OnuID, Gemport_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"OLT(config)#", timeout=2)
    for Cvlan in Vlan_list:
        command_write = 'service-port  autoindex vlan %s gpon 0/0 port %s ont %s gemport ' \
                        '%s tag-action default' % (
                            str(Cvlan), PonID, OnuID, Gemport_ID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config)#", timeout=2)
    command_result = tn.read_until(b"OLT(config)#", timeout=2)

    command_write = 'show service-port gpon 0/0 port %s ont %s gemport %s' % (PonID, OnuID, Gemport_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')

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
    command_write = 'no service-port gpon 0/0 port %s ont %s gemport ' \
                    '%s ' % (
                        PonID, OnuID, Gemport_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"OLT(config)#", timeout=2)
    command_write = 'show service-port gpon 0/0 port %s ont %s gemport %s' % (PonID, OnuID, Gemport_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
    if '( up/down      : 0   /0    )' in command_result:
        cdata_info('service_port删除成功。')
        return True
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error('service_port删除失败。')
        cdata_info("==========================================")
        return False

# 添加native-vlan
def ont_native_vlan(tn, PonID, OnuID, Onu_port_ID, User_vlan):
    # 判断当前的视图是否正确。
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

    command_write = 'ont port  native-vlan  %s %s eth %s vlan %s' % (PonID, OnuID, Onu_port_ID, User_vlan)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    # 查看NATIVE-VLAN是否添加成功
    command_write = 'show ont port attribute %s %s eth all' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
    if ttt(PonID, OnuID) + '%s    enable   auto   auto   on     off     %s' % (
    Onu_port_ID, User_vlan) in command_result:
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
def get_onu_info(tn, PonID, OnuID, SN):
    SN = SN_16_to_12(SN)

    # 判断当前的视图是否正确。
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

    command_write = 'show ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    get_ont_info = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')

    # 获取ONU的版本信息
    command_write = 'show ont version %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    get_ont_version = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')

    # 获取ONU的能力集信息
    command_write = 'show ont capability %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    get_ont_capability = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')

    # 获取ONU的光参数信息
    command_write = 'show ont optical-info  %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    get_ont_optical_info = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')

    # 获取ONU的关键参数
    if SN in get_ont_info:
        # 提取ONU的关键参数
        FrameID_SlotID = re.findall('F/S               : (.*)', get_ont_info)
        Port = re.findall('Port              : (.*)', get_ont_info)
        ONT_ID = re.findall('ONT-ID            : (.*)', get_ont_info)
        Control_flag = re.findall('Control flag      : (.*)', get_ont_info)
        Run_state = re.findall('Run state         : (.*)', get_ont_info)
        Config_state = re.findall('Config state      : (.*)', get_ont_info)
        Match_state = re.findall('Match state       : (.*)', get_ont_info)
        DBA_type = re.findall('DBA type          : (.*)', get_ont_info)
        Distance = re.findall('Distance\(m\)       : (.*)', get_ont_info)
        Authentic_mode = re.findall('Authentic mode    : (.*)', get_ont_info)
        SN_read = re.findall('SN                : (.*)', get_ont_info)
        Vendor_ID = re.findall('Vendor-ID                      : (.*)', get_ont_version)
        ONT_Version = re.findall('ONT Version                    : (.*)', get_ont_version)
        Product_ID = re.findall('Product-ID                     : (.*)', get_ont_version)
        Equipment_ID = re.findall('Equipment-ID                   : (.*)', get_ont_version)
        Main_Software_Version = re.findall('Main Software Version          : (.*)', get_ont_version)
        Standby_Software_Version = re.findall('Standby Software Version       : (.*)', get_ont_version)
        ONT_TYPE = re.findall('ONT TYPE                      : (.*)', get_ont_capability)
        OMCC_version = re.findall('OMCC version                  : (.*)', get_ont_capability)
        Number_of_uplink_PON_ports = re.findall('Number of uplink PON ports    : (.*)', get_ont_capability)
        Number_of_POTS_ports = re.findall('Number of POTS ports          : (.*)', get_ont_capability)
        Number_of_IPHOST = re.findall('Number of IPHOST              : (.*)', get_ont_capability)
        Number_of_ETH_ports = re.findall('Number of ETH ports           : (.*)', get_ont_capability)
        Number_of_VEIP = re.findall('Number of VEIP                : (.*)', get_ont_capability)
        Number_of_CATV_UNI_ports = re.findall('Number of CATV UNI ports      : (.*)', get_ont_capability)
        Number_of_GEM_ports = re.findall('Number of GEM ports           : (.*)', get_ont_capability)
        Number_of_TCONTs = re.findall('Number of T-CONTs             : (.*)', get_ont_capability)
        The_type_of_flow_control = re.findall('The type of flow control      : (.*)', get_ont_capability)
        # Voltage = re.findall('Voltage\(V\)                     : (.*)', get_ont_optical_info)
        Voltage = re.findall('Voltage\(V\)\s+: (.*)', get_ont_optical_info)
        Tx_optical_power = re.findall('Tx optical power\(dBm\)\s+: (.*)', get_ont_optical_info)
        Rx_optical_power = re.findall('Rx optical power\(dBm\)\s+: (.*)', get_ont_optical_info)
        Laser_bias_current = re.findall('Laser bias current\(mA\)\s+: (.*)', get_ont_optical_info)
        Temperature = re.findall('Temperature\(C\)\s+: (.*)', get_ont_optical_info)
        CATV_Rx_optical_power = re.findall('CATV Rx optical power\(dBm\)\s+: (.*)', get_ont_optical_info)

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
        cdata_info('DBA类型          ：%s' % (DBA_type[0]))
        cdata_info('测距距离         ：%s' % (Distance[0]))
        cdata_info('认证方式         ：%s' % (Authentic_mode[0]))
        cdata_info('SN号             ：%s' % (SN_read[0]))
        cdata_info("==========================================================")
        cdata_info('\n')
        cdata_info("==========================================================")
        cdata_info('               ONU上报的版本信息：')
        cdata_info("==========================================================")
        cdata_info('硬件版本号       ：%s' % (ONT_Version[0]))
        cdata_info('主分区软件版本号 ：%s' % (Main_Software_Version[0]))
        cdata_info('备分区软件版本号 ：%s' % (Standby_Software_Version[0]))
        cdata_info('Vendor ID        ：%s' % (Vendor_ID[0]))
        cdata_info('Product ID       ：%s' % (Product_ID[0]))
        cdata_info('Equipment ID     ：%s' % (Equipment_ID[0]))
        cdata_info("==========================================================")
        cdata_info('\n')
        cdata_info("==========================================================")
        cdata_info('               ONU上报的能力集信息：')
        cdata_info("==========================================================")
        cdata_info('ONU类型          ：%s' % (ONT_TYPE[0]))
        cdata_info('OMCC版本号       ：%s' % (OMCC_version[0]))
        cdata_info('PON口数量        ：%s' % (Number_of_uplink_PON_ports[0]))
        cdata_info('语音口数量       ：%s' % (Number_of_POTS_ports[0]))
        cdata_info('IP_HOST数量      ：%s' % (Number_of_IPHOST[0]))
        cdata_info('以太网口数量     ：%s' % (Number_of_ETH_ports[0]))
        cdata_info('VEIP口数量       ：%s' % (Number_of_VEIP[0]))
        cdata_info('CATV口数量       ：%s' % (Number_of_CATV_UNI_ports[0]))
        cdata_info('Gemport数量      ：%s' % (Number_of_GEM_ports[0]))
        cdata_info('Tcont数量        ：%s' % (Number_of_TCONTs[0]))
        cdata_info('支持的流控方式   ：%s' % (The_type_of_flow_control[0]))
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
        cdata_info('CATV_RX光功率(dBm)  ：%s' % (CATV_Rx_optical_power[0]))
        cdata_info("==========================================================")
        cdata_info('\n')
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

    # 在OLT上执行重启ONU的命令
    command_write = 'ont reboot %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')

    # 判断ONU是否重启
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if 'Run state         : offline' in command_result and 'Config state      : initial' \
                in command_result and 'Match state       : initial' in command_result:
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

    # 判断ONU重启后，是否可以注册成功
    for i in range(0, 12):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if 'Run state         : online' in command_result and 'Config state      : success' \
                in command_result and 'Match state       : match' in command_result:
            cdata_info("ONU重启完成。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state         : online' in command_result and 'Config state      : failed' in \
                command_result and 'Authentic mode    : sn-auth' in command_result:
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
    command_write = 'ont deactivate %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')

    # 判断ONU是否离线
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if 'Run state         : offline' in command_result and 'Config state      : initial' \
                in command_result and 'Match state       : initial' in command_result and 'Control flag      : deactive' in command_result:
            cdata_info("ONU离线成功。")
            break
    else:
        cdata_info("==========================================")
        cdata_error("===============ERROR!!!===================")
        cdata_error(" ONU离线失败")
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 在OLT上执行重新开启ONU的TX的命令
    command_write = 'ont activate %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')

    # 查看ONU是否可以重新上线
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        # tn.write(b"show ont info 2 1" + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if 'Run state         : online' in command_result and 'Config state      : success' \
                in command_result and 'Match state       : match' in command_result:
            cdata_info("ONU重新上线成功。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state         : online' in command_result and 'Config state      : failed' in \
                command_result and 'Authentic mode    : sn-auth' in command_result:
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

    # 选择需要升级的ONU
    command_write = 'ont load select 0/0 %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
    time.sleep(1)

    # 判断升级的ONU是否选择成功
    tn.write(b"show ont load select 0/0" + b"\n")
    command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
    print(command_result)
    print(ttt1(PonID, OnuID) + '    waiting    0%')
    if ttt1(PonID, OnuID) + '    waiting    0%' in command_result:
        cdata_info('选择升级的ONU成功')
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error('选择升级的ONU失败')
        cdata_info("==========================================")
        return False

    # 开始执行升级ONU的命令
    command_write = 'ont load start 0/0 %s activemode immediate' % (file_name)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
    time.sleep(10)

    # 查看ONU的升级进度
    tn.write(b"show ont load select 0/0" + b"\n")
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
    for i in range(0, 20):
        time.sleep(10)
        tn.write(b"show ont load select 0/0" + b"\n")
        command_result = tn.read_until(b"OLT(config)#", timeout=2).decode('ascii')
        time.sleep(1)
        if ttt1(PonID, OnuID) + '    success    100%' in command_result:
            cdata_info("ONU在OLT上升级完成。")
            break
    else:
        cdata_info("==========================================")
        cdata_info("===============ERROR!!!===================")
        cdata_error("ONU升级等待超时，请检查ONU是否异常")
        cdata_info("==========================================")
        return False

    # 查看ONU升级完成后是否重启
    tn.write(b"interface gpon 0/0" + b"\n")
    tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
    for i in range(0, 12):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if 'Run state         : offline' in command_result and 'Config state      : initial' \
                in command_result and 'Match state       : initial' in command_result:
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
    for i in range(0, 12):
        time.sleep(10)
        command_write = 'show ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        # tn.write(b"show ont info 2 1" + b"\n")
        time.sleep(1)

        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if 'Run state         : online' in command_result and 'Config state      : success' \
                in command_result and 'Match state       : match' in command_result:
            cdata_info("ONU重启后注册完成。")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        elif 'Run state         : online' in command_result and 'Config state      : failed' in \
                command_result and 'Authentic mode    : sn-auth' in command_result:
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


# 删除ONU
def ont_del(tn, PonID, OnuID, SN):
    SN = SN_12_to_16(SN)

    # 判断当前的视图是否正确。
    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
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
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')

    # 判断ONU是否删除成功
    command_write = 'show ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
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
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont autofind %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
        if SN in command_result:
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
    # command_write = 'file delete'
    # tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config)#", timeout=2)    
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
    tn.write(b"interface gpon 0/0" + b"\n")
    tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)

    # 删除当前ONU
    command_write = 'ont del %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')

    # 判断ONU是否删除成功
    command_write = 'show ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
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
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'show ont autofind %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode('ascii')
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
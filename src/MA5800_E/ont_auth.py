import getpass
import telnetlib
import os
import sys
import time
import re
# from src.config.initialization_config import *
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
            command = '0/ 2/%s    %s  ' % (pon_id, onu_id)
        else:
            command = '0/ 2/%s   %s  ' % (pon_id, onu_id)
    else:
        if len(onu_id) == 1:
            command = '0/ 2/%s   %s  ' % (pon_id, onu_id)
        else:
            command = '0/ 2/%s  %s  ' % (pon_id, onu_id)
    return command

# 解决pon_id和onu_id不为个位数的时候，升级测试用例判断失败的问题
def ttt1(pon_id, onu_id):
    command = ''
    if len(pon_id) == 1:
        if len(onu_id) == 1:
            command = '0/2/%s               %s            ' % (pon_id, onu_id)
        else:
            command = '0/2/%s              %s            ' % (pon_id, onu_id)
    else:
        if len(onu_id) == 1:
            command = '0/2/%s              %s            ' % (pon_id, onu_id)
        else:
            command = '0/2/%s             %s            ' % (pon_id, onu_id)
    return command

# 转换成华为显示的MAC地址(如：aa:bb:cc:dd:ee:ff转成aabb-ccdd-eeff)
def turn_to_huawei_mac(ONU_MAC):
    mac_split = ONU_MAC.split(':')
    return mac_split[0]+mac_split[1]+'-'+mac_split[2]+mac_split[3]+'-'+mac_split[4]+mac_split[5]

# 检测ONU是否可以自动发现
def autofind_onu(tn,PonID, OnuID, ONU_MAC):
    ONU_MAC = turn_to_huawei_mac(ONU_MAC)
    
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

    # 判断ONU是否可以被自动发现
    for i in range(1, 12):
        time.sleep(10)
        command_write = 'display ont autofind %s' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        time.sleep(1)
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
        print(command_result)
        if ONU_MAC in command_result:
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
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
    command_write = 'display ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
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
def auth_by_mac(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, ONU_MAC):
    ONU_MAC = turn_to_huawei_mac(ONU_MAC)
    
    # 判断当前的视图是否正确。
    tn.write(b"interface epon 0/2" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=3)
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
    command_write = 'ont add %s %s mac-auth %s oam ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, ONU_MAC, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)

    # 判断OLT上，ONU是否添加成功
    for i in range(0, 3):
        time.sleep(3)
        command_write = 'display ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
        print(ttt(PonID, OnuID) + ONU_MAC)
        if ttt(PonID, OnuID) + ONU_MAC in command_result:
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
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
        if 'Run state               : online' in command_result and 'Config state            : normal' in \
                command_result and 'Authentic type          : MAC-auth' in command_result and 'Match state             : match' in command_result:
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

# 使用LOID认证ONU        
def auth_by_loid(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, LOID, ONU_MAC):
    ONU_MAC = turn_to_huawei_mac(ONU_MAC)
    
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

    # 以LOID的方式添加ONU
    command_write = 'ont add %s %s loid-auth %s always-on oam ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, LOID, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
    time.sleep(30)
    
    # 判断OLT上，ONU是否添加成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
        if ttt(PonID, OnuID) + ONU_MAC in command_result:
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
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
        if 'Run state               : online' in command_result and 'Config state            : normal' in \
                command_result and 'Authentic type          : loid-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("ONU在OLT上通过LOID注册成功。")
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
        cdata_error("ONU在OLT上通过LOID注册失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False        

# 使用LOID+PASSWORD认证ONU


# 使用LOID_PASSWORD认证ONU
def auth_by_loid_password(tn, PonID, OnuID, Ont_Lineprofile_ID, Ont_Srvprofile_ID, LOID, LOID_PASSWORD, ONU_MAC):
    ONU_MAC = turn_to_huawei_mac(ONU_MAC)
    
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

    # 以LOID+PASSWORD的方式添加ONU
    command_write = 'ont add %s %s loid-auth %s checkcode-auth %s always-on oam ont-lineprofile-id %s ont-srvprofile-id %s' \
                    % (PonID, OnuID, LOID, LOID_PASSWORD, Ont_Lineprofile_ID, Ont_Srvprofile_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
    time.sleep(30)
    
    # 判断OLT上，ONU是否添加成功
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s all' % (PonID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
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
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
        if 'Run state               : online' in command_result and 'Config state            : normal' in \
                command_result and 'Authentic type          : loid+checkcode-auth' in command_result and 'Match state             : match' in command_result:
            cdata_info("ONU在OLT上通过LOID_PASSWORD注册成功。")
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
        cdata_error("ONU在OLT上通过LOID_PASSWORD注册失败。")
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False  

#创建service-port
def add_service_port(tn, PonID, OnuID,Vlan_list):
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
        command_write = 'service-port vlan  %s epon 0/2/%s ont %s multi-service user-vlan %s' % (
                            str(Cvlan), PonID, OnuID, str(Cvlan))
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2)

    # 查看service-port是否添加成功
    command_write = 'display  service-port  port  0/2/%s ont %s' % (PonID, OnuID)
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
def del_service_port(tn, PonID, OnuID):
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
    command_write = 'undo service-port port  0/2/%s ont %s ' \
                     % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    tn.write(b"y"+b"\n")
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    command_write = 'display  service-port port  0/2/%s ont  %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b'{ <cr>|e2e<K>|gemport<K>|sort-by<K>||<K> }: ',timeout=2)
    tn.write(b"\n")
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2).decode('ascii')
    print(command_result)
    #Failure: No service virtual port can be operated
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
def ont_native_vlan(tn, PonID, OnuID, Ont_Port_ID, User_Vlan):
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
    time.sleep(5)
    
    # 添加native-vlan
    command_write = 'ont port native-vlan  %s %s eth %s vlan %s' % (PonID, OnuID, Ont_Port_ID, User_Vlan)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
    
    # 查看NATIVE-VLAN是否添加成功
    time.sleep(5)
    tn.write(b"\n")
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
    command_write = 'display ont port attribute %s %s eth %s' % (PonID, OnuID, Ont_Port_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
    print(command_result)
    if User_Vlan in command_result:
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
def get_onu_info(tn, PonID, OnuID, ONU_MAC):
    ONU_MAC = turn_to_huawei_mac(ONU_MAC)
    
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
        
    # 查看ONU的基本信息
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
    command_write = 'display ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    get_ont_info = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
    print(get_ont_info)
    
    # 查看ONU上报的能力集信息
    command_write = 'display ont capability %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    get_ont_capability = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
    print(get_ont_capability)
    
    # 查看ONU的光功率信息
    command_write = 'display ont optical-info  %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    get_ont_optical_info = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
    print(get_ont_optical_info)
    
    # 查看ONU的版本信息
    command_write = 'display ont version %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    time.sleep(1)
    get_ont_version = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
    print(get_ont_version)
    
    
    # 获取ONU的关键参数
    if ONU_MAC in get_ont_info:
        FrameID_SlotID_PonID = re.findall('F/S/P                   : (.*)', get_ont_info)
        ONT_ID = re.findall('ONT-ID                  : (.*)', get_ont_info)
        Control_flag = re.findall('Control flag            : (.*)', get_ont_info)
        Run_state = re.findall('Run state               : (.*)', get_ont_info)
        Config_state = re.findall('Config state            : (.*)', get_ont_info)
        Match_state = re.findall('Match state             : (.*)', get_ont_info)
        Distance = re.findall('ONT distance\(m\)         : (.*)', get_ont_info)
        Authentic_mode = re.findall('Authentic type          : (.*)', get_ont_info)
        MAC_read = re.findall('MAC                     : (.*)', get_ont_info)
        
        for result in get_ont_capability.split('\r\n'):
            if 'ONT type' in result:
                ONT_TYPE = result[36:]
            if 'Number of LLIDs' in result:
                Number_of_LLIDs = result[36:]                
            if 'Number of PON interfaces' in result:
                Number_of_PON_interfaces = result[36:]
            if 'IPv6 aware' in result:
                IPv6_aware = result[36:]               
            if 'GE' in result:
                Number_of_GE = result[36:]
            if 'FE' in result:
                Number_of_FE = result[36:]    
            if 'VoIP' in result:
                Number_of_VoIP = result[36:]
            if 'WLAN' in result:
                Number_of_WLAN = result[36:]
            if 'USB' in result:
                Number_of_USB = result[36:]
            if 'CATV RF' in result:
                Number_of_CATV_RF = result[36:]
                
        Vendor_ID = re.findall('Vendor-ID               : (.*)', get_ont_version)
        ONT_hardware_version = re.findall('ONT hardware version    : (.*)', get_ont_version)
        ONT_model = re.findall('ONT model               : (.*)', get_ont_version)
        Extended_model = re.findall('ONT extended model      : (.*)', get_ont_version)
        ONT_software_version = re.findall('ONT software version    : (.*)', get_ont_version)
        ONT_chipset_vendor_ID = re.findall('ONT chipset vendor ID   : (.*)', get_ont_version)
        ONT_chipset_model = re.findall('ONT chipset model       : (.*)', get_ont_version)
        ONT_chipset_revision = re.findall('ONT chipset revision    : (.*)', get_ont_version)
        ONT_chipset_version = re.findall('ONT chipset version/date: (.*)', get_ont_version)
        ONT_firmware_version = re.findall('ONT firmware version    : (.*)', get_ont_version) 

        Voltage = re.findall('Voltage\(V\)                             : (.*)', get_ont_optical_info)
        Tx_optical_power = re.findall('Tx optical power\(dBm\)                  : (.*)', get_ont_optical_info)
        Rx_optical_power = re.findall('Rx optical power\(dBm\)                  : (.*)', get_ont_optical_info)
        Laser_bias_current = re.findall('Laser bias current\(mA\)                 : (.*)', get_ont_optical_info)
        Temperature = re.findall('Temperature\(C\)                         : (.*)', get_ont_optical_info)  
        OLT_Rx_ONT_optical_power = re.findall('OLT Rx ONT optical power\(dBm\)          : (.*)', get_ont_optical_info)

        
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
        cdata_info('ONU类型          ：%s' % (ONT_TYPE))
        cdata_info('PON口接口数量    ：%s' % (Number_of_PON_interfaces))
        cdata_info('GE口数量     ：%s' % (Number_of_GE))
        cdata_info('FE口数量     ：%s' % (Number_of_FE))
        cdata_info('语音口数量       ：%s' % (Number_of_VoIP))
        cdata_info('CATV接口数量     ：%s' % (Number_of_CATV_RF))
        cdata_info('WIFI接口数量     ：%s' % (Number_of_WLAN))
        cdata_info('USB接口数量     ：%s' % (Number_of_USB))
        cdata_info('LLID数量         ：%s' % (Number_of_LLIDs))
        cdata_info('是否支持IPV6     ：%s' % (IPv6_aware))
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

    # 在OLT上执行重启ONU的命令
    command_write = 'ont reset %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"y"+b"\n")
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')

    # 判断ONU是否重启
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
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
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
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

    # 在OLT上执行关闭ONU的TX的命令
    command_write = 'ont deactivate %s %s ' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')

    # 判断ONU是否离线
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
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
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
    time.sleep(30)
    
    # 查看ONU是否可以重新上线
    for i in range(0, 6):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        # tn.write(b"display ont info 2 1" + b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
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

    # OLT上执行OAM升级ONU
    command_write = 'ont-load stop'
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2).decode('ascii')
    command_write = 'ont-load info program %s tftp %s ' % (file_name, tftp_server_ip)
    tn.write(command_write.encode('ascii') + b"\n") 
    time.sleep(1)
    tn.write(b"\n")
    command_result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2).decode('ascii')
    command_write = 'ont-load select 0/2 %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"MA5800-X15(diagnose)%%", timeout=2).decode('ascii')
    
    # 判断是否选择升级的ONU成功
    command_write = 'display ont-load select 0/2 %s %s' % (PonID, OnuID)
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
    command_write = 'display ont-load select 0/2 %s %s' % (PonID, OnuID)
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
    tn.write(b"interface epon 0/2" + b"\n")
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
    for i in range(0, 30):
        time.sleep(10)
        command_write = 'display ont info %s %s' % (PonID, OnuID)
        tn.write(command_write.encode('ascii') + b"\n")
        time.sleep(1)
        tn.write(b"\n")
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
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
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
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
        command_write = 'display ont-load select 0/2 %s %s' % (PonID, OnuID)
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
def ont_del(tn, PonID, OnuID, ONU_MAC):
    ONU_MAC = turn_to_huawei_mac(ONU_MAC)
    
    # 判断当前的视图是否正确。
    tn.write(b"interface epon 0/2" + b"\n")
    result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)
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
    command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')

    # 判断ONU是否删除成功
    command_write = 'display ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
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
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
        if ONU_MAC in command_result:
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
    tn.write(b"interface epon 0/2" + b"\n")
    tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2)

    # 删除当前ONU
    command_write = 'ont del %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')

    # 判断ONU是否删除成功
    command_write = 'display ont info %s %s' % (PonID, OnuID)
    tn.write(command_write.encode('ascii') + b"\n")
    command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
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
        command_result = tn.read_until(b"MA5800-X15(config-if-epon-0/2)#", timeout=2).decode('ascii')
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
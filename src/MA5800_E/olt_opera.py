#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client_MA5800 import *
import re

def create_epon_ontlineprofile(tn,Ont_Lineprofile_ID, Dba_Profile_ID):
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
    #删除gpon的线路模板200
    tn.write(('undo ont-lineprofile gpon profile-id %s'%Ont_Lineprofile_ID).encode()+b'\n')
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    tn.write(('display ont-lineprofile gpon profile-id %s'%Ont_Lineprofile_ID).encode()+b'\n')
    tn.read_until(b'{ <cr>||<K> }: ', timeout=2)
    tn.write(b'\n')
    result1 = tn.read_until(b"MA5800-X15(config)#", timeout=2).decode()
    if ' Failure: The line profile does not exist' in result1:
        cdata_info('gpon ont-lineprofile %s 删除成功'%Ont_Lineprofile_ID)
    elif 'Failure: The input profile type is incorrect' in result1:
        cdata_info('已存在epon线路模板')
    else:
        cdata_error('gpon ont-lineprofile %s 删除失败'%Ont_Lineprofile_ID)
        return False
    #创建epon的线路模板
    tn.write(('ont-lineprofile epon  profile-id %s'%Ont_Lineprofile_ID).encode()+b'\n')
    tn.read_until(b'{ <cr>|profile-name<K> }:',timeout=2)
    tn.write(b'\n')
    tn.read_until(('MA5800-X15(config-epon-lineprofile-%s)#'%Ont_Lineprofile_ID).encode(),timeout=2)
    #绑定指定的dba
    tn.write(('llid dba-profile-id %s'%Dba_Profile_ID).encode()+b'\n')
    tn.read_until(b'{ <cr>|encrypt<K>|ont-car<K> }: ',timeout=2)
    tn.write(b'\n')
    tn.read_until(('MA5800-X15(config-epon-lineprofile-%s)#' % Ont_Lineprofile_ID).encode(), timeout=2)
    tn.write(b'display ont-lineprofile current \n')
    tn.read_until(b'{ <cr>||<K> }: ',timeout=2)
    tn.write(b'\n')
    result = tn.read_until(('MA5800-X15(config-epon-lineprofile-%s)#'% Ont_Lineprofile_ID).encode() ,timeout=2).decode()

    if 'DBA Profile-ID      :%s'%Dba_Profile_ID in result :
        cdata_info('epon线路模板 %s 绑定dba模板 %s 正常'%(Ont_Lineprofile_ID,Dba_Profile_ID))
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-epon-lineprofile-%s)#' % Ont_Lineprofile_ID).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return True
    else:
        cdata_error('线路模板 %s 绑定dba模板 %s 失败'%(Ont_Lineprofile_ID,Dba_Profile_ID))
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-epon-lineprofile-%s)#' % Ont_Lineprofile_ID).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False

def create_epon_ontsrvprofile(tn, Ont_Srvprofile_ID):
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
    #删除gpon的线路模板200
    tn.write(('undo ont-srvprofile gpon profile-id %s'%Ont_Srvprofile_ID).encode()+b'\n')
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    tn.write(('display ont-srvprofile gpon profile-id %s'%Ont_Srvprofile_ID).encode()+b'\n')
    tn.read_until(b'{ <cr>||<K> }: ',timeout=2)
    tn.write(b'\n')
    result1= tn.read_until(b"MA5800-X15(config)#", timeout=2).decode()
    if ' Failure: The service profile does not exist' in result1:
        cdata_info('gpon服务模板 %s 删除成功'%Ont_Srvprofile_ID)
    elif 'Failure: The access type of the profile mismatch' in result1:
        cdata_info('已存在epon服务模板')
    else:
        cdata_error('gpon服务模板 %s 删除失败'%Ont_Srvprofile_ID)
        return False
    #创建epon的线路模板
    tn.write(('ont-srvprofile epon profile-id %s'%Ont_Srvprofile_ID).encode()+b'\n')
    tn.read_until(b'{ <cr>|profile-name<K> }: ',timeout=2)
    tn.write(b'\n')
    tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#'%Ont_Srvprofile_ID).encode(),timeout=2)
    #配置能力集
    tn.write(b'ont-port eth adaptive pots adaptive'+b'\n')
    tn.read_until(b'{ <cr>|max-pots-port<U><1,32>|tdm<K>|tdm-type<K> }: ',timeout=2)
    tn.write(b'\n')
    tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % Ont_Srvprofile_ID).encode(), timeout=2)

    # cdata_info('服务模板能力集配置正常')
    tn.write(b'commit \n')
    tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % Ont_Srvprofile_ID).encode(), timeout=2)
    tn.write(b'quit \n')
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    return True

def no_shutdown_epon(tn,PonID):
    try:
        tn.write(b'interface epon 0/2'+b'\n')
        result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)#',timeout=2)
        tn.write(('undo  shutdown %s'%PonID).encode()+b'\n')
        result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)', timeout=2)
        tn.write(('display port state %s'%PonID).encode()+b'\n')
        tn.read_until(b'{ <cr>||<K> }: ',timeout=2)
        tn.write(b'\n')
        result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)', timeout=2).decode('utf-8')
        # print(result)
        if 'TX fault                     Normal' in result:
            cdata_info('pon %s 端口使能成功'%PonID)
            tn.write(b'quit \n')
            tn.read_until(b'MA5800-X15(config)# ', timeout=2)
            return True
        else:
            cdata_error('pon %s 端口使能失败'%PonID)
            tn.write(b'quit \n')
            tn.read_until(b'MA5800-X15(config)# ', timeout=2)
            return False
            # raise Exception("OLT_PON %s 端口未使能成功"%PonID)
    except:
        cdata_error('pon %s 端口使能失败')
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)# ', timeout=2)
        return False
        # raise Exception("OLT_PON %s 端口未使能成功" % PonID)

def shutdown_epon(tn,PonID):
    try:
        tn.write(b'interface epon 0/2'+b'\n')
        result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)', timeout=2)
        tn.write(('shutdown %s'%PonID).encode()+b'\n')
        result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)', timeout=2)
        tn.write(('display port state %s'%PonID).encode()+b'\n')
        tn.read_until(b'{ <cr>||<K> }:',timeout=2)
        tn.write(b'\n')
        result = tn.read_until(b'MA5800-X15(config-interface-epon-0/0)# ', timeout=2).decode('utf-8')
        if 'TX fault                     Normal' not in result:
            cdata_info('pon %s 端口去使能成功'%PonID)
            tn.write(b'quit \n')
            tn.read_until(b'MA5800-X15(config)# ', timeout=2)
            return True
        else:
            cdata_error('pon %s 端口去使能失败'%PonID)
            tn.write(b'quit \n')
            tn.read_until(b'MA5800-X15(config)# ', timeout=2)
            return False
    except:
        # raise Exception("OLT_PON %s 端口去使能使能" % PonID)
        cdata_error('pon %s 端口去使能失败' % PonID)
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)# ', timeout=2)
        return False


if __name__ == '__main__':
    tn = telnet_host(host_ip='192.168.5.82', username='test111', password='test123')[0]
    noshutdown_pon(tn, PonID='4')


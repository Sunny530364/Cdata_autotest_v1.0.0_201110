#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client_MA5800 import *

def traffic_table(tn):
    # 判断当前的视图是否正确。
    tn.write(b"\n")
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    if result:
        pass
    else:
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    tn.write(b'display traffic table ip name auto_traffic \n')
    tn.write(b'\n')
    result = tn.read_until(b'MA5800-X15(config)#',timeout=2).decode('utf-8')
    print(result)
    if 'Failure: The traffic table does not exist' in result:
        cdata_debug('模板未创建')
        tn.write('traffic table ip cir %s pir %s priority 0  priority-policy local-Setting '%(cir,pir))

def dba_profile_type4(tn,Dba_Profile_ID,max='1000000'):
    # 判断当前的视图是否正确。
    tn.write(b"\n")
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    if result:
        pass
    else:
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    tn.write(("dba-profile modify profile-id %s"%Dba_Profile_ID).encode() + b"\n")
    result = tn.read_until(b"The type of the DBA-profile (1~5)", timeout=2)
    tn.write(b'4 \n')
    result = tn.read_until(b"The maximum bandwidth of the DBA-profile(128~10000000kbps)", timeout=2)
    tn.write(max.encode()+b'\n ')
    tn.read_until(b'The priority of the DBA-profile(0~3)',timeout =2)
    tn.write(b'\n')
    tn.read_until(b'The weight of the DBA-profile(1~10000)',timeout =2 )
    tn.write(b'\n')
    tn.read_until(b'MA5800-X15(config)#',timeout=2)
    result = tn.write(('display dba-profile profile-id %s'%Dba_Profile_ID).encode()+b'\n')
    tn.read_until(b'{ <cr>||<K> }: ',timeout=2)
    tn.write(b'\n')
    result = tn.read_until(b"MA5800-X15(config)#", timeout=5).decode('utf-8')
    if 'Max(kbps):                %s'%max in result:

        cdata_info('dba配置type4正常')
        return True
    else:
        cdata_error("===============ERROR!!!===================")
        cdata_error('dba配置type4失败')
        cdata_info("==========================================")
        return False

def dba_profile_type5(tn,Dba_Profile_ID,fix= '10240',assure = '20480',max='51200'):
    # 判断当前的视图是否正确。
    # 判断当前的视图是否正确。
    tn.write(b"\n")
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    if result:
        pass
    else:
        cdata_error("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"quit" + b"\n")
        result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
        return False
    tn.write(("dba-profile modify profile-id %s"%Dba_Profile_ID).encode() + b"\n")
    result = tn.read_until(b"The type of the DBA-profile (1~5)", timeout=2)
    tn.write(b'5 \n')
    result = tn.read_until(b"The fixed bandwidth of the DBA-profile(128~10000000kbps)", timeout=2)
    tn.write(fix.encode()+b'\n')
    result = tn.read_until(b"The assured bandwidth of the DBA-profile(128~10000000kbps)", timeout=2)
    tn.write(assure.encode()+b'\n ')
    result = tn.read_until(b"The maximum bandwidth of the DBA-profile(128~10000000kbps)", timeout=2)
    tn.write(max.encode()+b'\n ')
    tn.read_until(b'The additional bandwidth of the DBA-profile(0:non-assure  1: best-effort)',timeout=2)
    tn.write(b'\n')
    tn.read_until(b'The priority of the DBA-profile(0~3)',timeout =2)
    tn.write(b'\n')
    tn.read_until(b'The weight of the DBA-profile(1~10000)',timeout =2 )
    tn.write(b'\n')
    tn.read_until(b'MA5800-X15(config)#',timeout=2)
    result = tn.write(('display dba-profile profile-id %s'%Dba_Profile_ID).encode()+b'\n')
    tn.read_until(b'{ <cr>||<K> }: ', timeout=2)
    tn.write(b'\n')
    result = tn.read_until(b"MA5800-X15(config)#", timeout=2).decode('utf-8')
    if 'Fix(kbps):                %s'%fix in result and 'Assure(kbps):             %s'%assure in result and \
            'Max(kbps):                %s'%max in result:

        cdata_info('dba配置type5正常')
        return True
    else:
        cdata_error("===============ERROR!!!===================")
        cdata_error('dba配置type5失败')
        cdata_error("===============ERROR!!!===================")
        return False

def ont_port_limitrate_inbound(tn,Traffic_Profile_ID_inbound,PonID,OnuID,Ont_Port_ID):

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
    # 配置onu端口入口限速
    tn.write(('ont  port attribute %s %s eth %s up-policing %s '%(PonID, OnuID, Ont_Port_ID,Traffic_Profile_ID_inbound)).encode() + b'\n')
    tn.read_until(b'{ <cr>|ds-policing<K> }: ',timeout=2)
    tn.write(b'\n')
    tn.read_until(b'MA5800-X15(config-if-epon-0/2)#', timeout=2)
    # 查看onu的端口限速
    tn.write(('display ont port attribute %s %s eth %s '%(PonID, OnuID,Ont_Port_ID)).encode() + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ',timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)#', timeout=2).decode()
    print(command_result)
    try:
        result = ((((command_result.split('---------------------------------------------------------------------------'))[2].split('\r\n'))[1]).split())
        print(result)
        if str(Traffic_Profile_ID_inbound) == result[7]:
            cdata_info("ONT端口入口绑定流量模板%s成功" % Traffic_Profile_ID_inbound)
            # 退出gpon视图下
            tn.write(b"quit" + b"\n")
            tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
        else:
            cdata_error("ONT端口入口绑定流量模板%s失败" % Traffic_Profile_ID_inbound)
            tn.write(b"quit" + b"\n")
            tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return False
    except IndexError:
        cdata_error('获取onu端口限速情况错误')

def ont_port_limitrate_outbound(tn,Traffic_Profile_ID_outbound,PonID,OnuID,Ont_Port_ID):
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
    # 配置onu端口入口限速
    tn.write(('ont  port attribute %s %s eth %s ds-policing %s ' % (
    PonID, OnuID, Ont_Port_ID, Traffic_Profile_ID_outbound)).encode() + b'\n')
    tn.read_until(b'{ <cr>|up-policing<K> }: ', timeout=2)
    tn.write(b'\n')
    tn.read_until(b'MA5800-X15(config-if-epon-0/2)#', timeout=2)
    # 查看onu的端口限速
    tn.write(('display ont port attribute %s %s eth %s ' % (PonID, OnuID, Ont_Port_ID)).encode() + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ', timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)#', timeout=2).decode()
    print(command_result)
    try:
        result = (((
            (command_result.split('---------------------------------------------------------------------------'))[2].split(
                '\r\n'))[1]).split())
        print(result)
        if str(Traffic_Profile_ID_outbound) == result[8]:
            cdata_info("ONT端口出口绑定流量模板%s成功" % Traffic_Profile_ID_outbound)
            # 退出gpon视图下
            tn.write(b"quit" + b"\n")
            tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
        else:
            cdata_error("ONT端口出口绑定流量模板%s失败" % Traffic_Profile_ID_outbound)
            tn.write(b"quit" + b"\n")
            tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return False
    except IndexError:
        cdata_error('获取onu端口限速情况错误')

def ont_port_limitrate_del(tn,PonID, OnuID, Ont_Port_ID):
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
    #删除onu端口限速
    tn.write(('ont  port attribute %s %s eth %s up-policing unconcern ds-policing unconcern'%(PonID, OnuID, Ont_Port_ID)).encode()+b'\n')
    tn.read_until(b'MA5800-X15(config-if-epon-0/2)#', timeout=2)
    # 查看onu的端口限速
    tn.write(('display ont port attribute %s %s eth %s ' % (PonID, OnuID, Ont_Port_ID)).encode() + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ', timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)#', timeout=2).decode()
    print(command_result)
    try:
        #获取onu的端口限速情况
        result = (((
            (command_result.split('---------------------------------------------------------------------------'))[2].split(
                '\r\n'))[1]).split())
        print(result)
        if  result[7]=='Unconcern' and result[8]=='Unconcern':
            cdata_info("ONT端口删除绑定流量模板成功" )
            # 退出gpon视图下
            tn.write(b"quit" + b"\n")
            tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return True
        else:
            cdata_error("ONT端口删除绑定流量模板失败")
            tn.write(b"quit" + b"\n")
            tn.read_until(b"MA5800-X15(config)#", timeout=2)
            return False
    except IndexError:
        cdata_error('获取onu端口限速情况错误')

if __name__ == '__main__':

    tn = telnet_host(host_ip='192.168.5.82', username='test111', password='test123')[0]
    # ont_port_limitrate_outbound(tn, Traffic_Profile_ID_outbound='100', PonID='4', OnuID='40', Ont_Port_ID='1')
    # test_ont_port_limitrate_del(tn,  PonID='4', OnuID='40', Ont_Port_ID='1')
    dba_profile_type4(tn, Dba_Profile_ID='100', max='1000000')
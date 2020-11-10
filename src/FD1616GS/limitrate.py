#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
from src.config.Cdata_loggers import *


def check_ont_capability(tn,PonID,OnuID,Ont_Port_ID):
    tn.write(b"interface gpon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode()
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
    for i in range(20):
        time.sleep(1)
        #查看onu端口的速率
        tn.write("show ont port state {} {} eth all ".format(PonID,OnuID).encode() + b'\n')
        result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode()
        cdata_debug(result)
        if "%s    GE"%Ont_Port_ID in result :
            cdata_info("onu端口%s速率为1000M"%Ont_Port_ID)
            # 退出gpon视图下
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return "GE"
        elif "%s    FE"%Ont_Port_ID in result :
            cdata_info("onu端口%s速率为100M"%Ont_Port_ID)
            # 退出gpon视图下
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return "FE"
        else :
            continue
    tn.write(b"exit" + b"\n")
    tn.read_until(b"OLT(config)#", timeout=2)

def dba_limitrate_type5(tn,Dba_Profile_ID,fix= '10240',assure = '20480',max='51200'):
    try:
        #进入dba视图下
        tn.read_until(b'OLT(config)# ', timeout=2)
        tn.write('dba-profile profile-id {}'.format(Dba_Profile_ID).encode()+b'\n')
        #配置dba为type5
        tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(),timeout=2)
        tn.write(('type5 fix %s assure %s max %s '%(fix,assure,max)).encode()+b'\n')
        tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
        tn.write(b'show dba-profile  current'+b'\n')
        time.sleep(0.5)
        command_result = tn.read_very_eager().decode('utf-8')
        cdata_debug(command_result)
        if "Fix(kbps)     :  %s"%fix  in command_result and  "Assure(kbps)  :  %s"%assure in command_result \
                and "Max(kbps)     :  %s"%max in command_result:
            cdata_info('dba模板配置type5成功')
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return True
        else:
            cdata_error('dba模板配置type5失败')
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    except:
        cdata_error("dba模板配置失败")
        return False

def dba_limitrate_type4(tn,Dba_Profile_ID,max='1024000'):
    try:
        # 进入dba视图下
        tn.read_until(b'OLT(config)# ', timeout=2)
        tn.write('dba-profile profile-id {}'.format(Dba_Profile_ID).encode() + b'\n')
        # 配置dba为type4
        tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
        tn.write(('type4 max %s '%max).encode() + b'\n')
        tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
        tn.write(b'show dba-profile current ' + b'\n')
        time.sleep(0.5)
        command_result = tn.read_very_eager().decode('utf-8')

        if "Max(kbps)     :  %s"%max in command_result:
            cdata_info('dba模板配置type4成功')
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return True
        else:
            cdata_error('dba模板配置type4失败')
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    except:
        cdata_error("dba模板配置失败")
        return False

def ont_port_limitrate_inbound(tn,Traffic_Profile_ID_inbound,PonID,OnuID,Ont_Port_ID):
    try:
        # 进入gpon视图下
        # 判断当前的视图是否正确。
        tn.write(b"interface gpon 0/0" + b"\n")
        result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2)
        if result:
            pass
        else:
            cdata_info("===============ERROR!!!===================")
            cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
            cdata_info("==========================================")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
        # 配置onu端口入口限速
        tn.write(
            'ont port car {} {} eth {} inbound {} '.format(PonID, OnuID, Ont_Port_ID,
                                                            Traffic_Profile_ID_inbound).encode() + b'\n')
        tn.read_until(b'OLT(config-interface-gpon-0/0)#', timeout=2)
        # 查看onu的端口限速
        tn.write('show ont port car {} {} eth all '.format(PonID, OnuID).encode() + b'\n')
        command_result = tn.read_until(b'OLT(config-interface-gpon-0/0)#', timeout=2).decode()
        print(command_result)
        # 获取onu端口1的car
        result = (
            ((command_result.split(
                '-----------------------------------------------------------------------------'))[1].
             split('----------------------------------------------------------------------------'))[1].split(
                '\r\n')[
                int(Ont_Port_ID)].split())
        print(result)
        if str(Traffic_Profile_ID_inbound) == result[4]:
            cdata_info("ONT端口入口绑定流量模板%s成功" % Traffic_Profile_ID_inbound)
            # 退出gpon视图下
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return True
        else:
            cdata_error("ONT端口入口绑定流量模板%s失败" % Traffic_Profile_ID_inbound)
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return False
    except:
        cdata_error("ont入口绑定流量模板失败")
        tn.write(b"exit" + b"\n")
        return False

def ont_port_limitrate_outbound(tn,Traffic_Profile_ID_outbound,PonID,OnuID,Ont_Port_ID):
    try:
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
        # 配置onu端口出口限速
        tn.write(
            'ont port car {} {} eth {} outbound {} '.format(PonID, OnuID, Ont_Port_ID, Traffic_Profile_ID_outbound).encode() + b'\n')
        tn.read_until(b'OLT(config-interface-gpon-0/0)#', timeout=2)
        # 查看onu的端口限速
        tn.write('show ont port car {} {} eth all '.format(PonID, OnuID).encode() + b'\n')
        command_result = tn.read_until(b'OLT(config-interface-gpon-0/0)#', timeout=2).decode()
        #获取onu端口1的car
        result = (
            ((command_result.split('-----------------------------------------------------------------------------'))[1].
             split('----------------------------------------------------------------------------'))[1].split('\r\n')[
                int(Ont_Port_ID)].split())
        if str(Traffic_Profile_ID_outbound) == result[5]:
            cdata_info("ONT端口出口绑定流量模板%s成功" % Traffic_Profile_ID_outbound)
            # 退出gpon视图下
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return True
        else:
            cdata_error("ONT端口出口绑定流量模板%s失败" % Traffic_Profile_ID_outbound)
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return False
    except:
        cdata_error("ont出口绑定流量模板失败")
        tn.write(b"exit" + b"\n")
        return False

def ont_port_limitrate_del(tn,PonID=16,OnuID=2,Ont_Port_ID=1):
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
    tn.read_until(b'OLT(config-interface-gpon-0/0)#')
    tn.write('no ont port car {} {} eth {} inbound outbound '.format(PonID,OnuID,Ont_Port_ID).encode()+b'\n')
    tn.read_until(b'OLT(config-interface-gpon-0/0)#')
    # 退出gpon视图下
    tn.write(b'exit' + b'\n')


if __name__ == '__main__':
    tn = telnet_host(host_ip='192.168.0.181', username='root', password='admin')[0]
    dba_limitrate_type5(tn, Dba_Profile_ID='100', fix='10240', assure='20480', max='51200')

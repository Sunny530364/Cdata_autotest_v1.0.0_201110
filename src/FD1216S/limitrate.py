#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI
from src.config.telnet_client import *
from src.config.Cdata_loggers import *

#onu端口绑定入口限速
def ont_port_limitrate_inbound(tn,PonID,OnuID,Ont_Port_ID,cir='10240'):
    try:
        # 进入gpon视图下
        # 判断当前的视图是否正确。
        tn.write(b"interface epon 0/0" + b"\n")
        result = tn.read_until(b"OLT(config-interface-epon-0/0)# ", timeout=2)
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
            ' ont port attribute {} {} eth {} up-policing cir {} cbs 2000 ebs 2000 '.format(PonID, OnuID, Ont_Port_ID,cir  ).encode() + b'\n')
        tn.read_until(b'OLT(config-interface-epon-0/0)#', timeout=2)
        # 查看onu的端口限速
        tn.write('show ont  port attribute {} {} eth {} policing '.format(PonID, OnuID,Ont_Port_ID).encode() + b'\n')
        time.sleep(0.5)
        command_result = tn.read_until(b'OLT(config-interface-epon-0/0)#', timeout=2).decode("utf-8")
        print(command_result)
        if 'UP policing cir(kbps)  : 10240' in command_result:
            cdata_info("ONT端口{}入口配置cir {}正常".format(Ont_Port_ID,cir))
            # 退出epon视图下
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return True
        else:
            cdata_error("ONT端口{}入口配置cir{}失败".format(Ont_Port_ID,cir))
            # 退出epon视图下
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return False
    except:
        cdata_error('onu入口配置端口限速失败')
        # 退出epon视图下
        tn.write(b"exit" + b"\n")
        tn.read_until(b"OLT(config)#", timeout=2)
        return False

#onu端口绑定出口限速
def ont_port_limitrate_outbound(tn,PonID,OnuID,Ont_Port_ID,cir='10240' ,pir='20480'):

    #进入epon视图，并判断视图是否正确
    tn.write(b"interface epon 0/0" + b"\n")
    result = tn.read_until(b"OLT(config-interface-epon-0/0)#", timeout=2)
    if result:
        pass
    else:
        cdata_info("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        cdata_info("==========================================")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False
    # 配置onu端口出口限速
    tn.write(
        'ont port attribute {} {} eth {} ds-policing cir {} pir  {} '.format(PonID, OnuID, Ont_Port_ID, cir,pir).encode() + b'\n')
    tn.read_until(b'OLT(config-interface-epon-0/0)#', timeout=2)
    # 查看onu的端口限速
    tn.write('show ont  port attribute {} {} eth {} policing'.format(PonID, OnuID,Ont_Port_ID).encode() + b'\n')
    command_result = tn.read_until(b'OLT(config-interface-epon-0/0)#', timeout=2).decode()
    print(command_result)
    if 'DN policing cir(kbps)  : 10240' in command_result and 'DN policing pir(kbps)  : 20480' in command_result:
        cdata_info("ONT端口{}出口配置 cir:{} pir:{} 成功".format(Ont_Port_ID,cir,pir))
        # 退出gpon视图下
        tn.write(b"exit" + b"\n")
        tn.read_until(b"OLT(config)#", timeout=2)
        return True
    else:
        cdata_error("ONT端口{}出口配置 cir:{} pir:{} 成功".format(Ont_Port_ID,cir,pir))
        tn.write(b"exit" + b"\n")
        tn.read_until(b"OLT(config)#", timeout=2)
        return False


#onu端口删除入口限速
def ont_port_limitrate_inbound_del(tn,PonID,OnuID,Ont_Port_ID):
    try:
        # 进入gpon视图下
        # 判断当前的视图是否正确。
        tn.write(b"interface epon 0/0" + b"\n")
        result = tn.read_until(b"OLT(config-interface-epon-0/0)# ", timeout=2)
        if result:
            pass
        else:
            cdata_info("===============ERROR!!!===================")
            cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
            cdata_info("==========================================")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
        #删除onu端口入口限速
        tn.write('no ont  port attribute {} {} eth {} up-policing'.format(PonID,OnuID,Ont_Port_ID).encode()+b'\n')
        result = tn.read_until(b"OLT(config-interface-epon-0/0)# ", timeout=2)
        tn.write('show ont port attribute {} {} eth {} policing'.format(PonID,OnuID,Ont_Port_ID).encode()+b'\n')
        result = tn.read_until(b"OLT(config-interface-epon-0/0)# ", timeout=2).decode()
        if ' UP policing            : unconcern' in result:
            cdata_info('删除onu入口限速正常')
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        else:
            cdata_info('删除onu入口限速失败')
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
    except:
        cdata_error('onu入口删除端口限速失败')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

#onu端口删除出口限速
def ont_port_limitrate_outbound_del(tn,PonID,OnuID,Ont_Port_ID):
    try:
        # 进入gpon视图下
        # 判断当前的视图是否正确。
        tn.write(b"interface epon 0/0" + b"\n")
        result = tn.read_until(b"OLT(config-interface-epon-0/0)# ", timeout=2)
        if result:
            pass
        else:
            cdata_info("===============ERROR!!!===================")
            cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
            cdata_info("==========================================")
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
        #删除onu端口入口限速
        tn.write('no ont  port attribute {} {} eth {} ds-policing'.format(PonID,OnuID,Ont_Port_ID).encode()+b'\n')
        result = tn.read_until(b"OLT(config-interface-epon-0/0)# ", timeout=2)
        tn.write('show ont port attribute {} {} eth {} policing'.format(PonID,OnuID,Ont_Port_ID).encode()+b'\n')
        result = tn.read_until(b"OLT(config-interface-epon-0/0)# ", timeout=2).decode()
        if 'DN policing            : unconcern' in result:
            cdata_info('删除onu出口限速正常')
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
        else:
            cdata_info('删除onu出口限速失败')
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return True
    except:
        cdata_error('删除onu出口限速失败')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

#dba模板配置typy5
def dba_limitrate_type5(tn,Dba_Profile_ID,fix='10240',assure='20480',max='51200'):
    try:
        #进入dba视图下
        tn.read_until(b'OLT(config)# ', timeout=2)
        tn.write('dba-profile profile-id {}'.format(Dba_Profile_ID).encode()+b'\n')
        #配置dba为type5
        tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(),timeout=2)
        tn.write(('type5 fix %s assure %s max %s '%(fix,assure,max)).encode()+b'\n')
        tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
        #保存配置并退出dba模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        tn.write(('show dba-profile profile-id {} '.format(Dba_Profile_ID)).encode() + b'\n')
        time.sleep(0.5)
        command_result = tn.read_very_eager().decode('utf-8')
        if "Fix(kbps)     :  %s"%fix  in command_result and  "Assure(kbps)  :  %s"%assure in command_result \
                and "Max(kbps)     :  %s"%max in command_result:
            cdata_info('dba模板配置type5成功')
            return True
        else:
            cdata_error('dba模板配置type5失败')
            return False
    except:
        cdata_error("dba模板配置失败")
        return False

#dba模板配置type4
def dba_limitrate_type4(tn,Dba_Profile_ID,max='1000000'):

    # 进入dba视图下
    tn.read_until(b'OLT(config)# ', timeout=2)
    tn.write('dba-profile profile-id {}'.format(Dba_Profile_ID).encode() + b'\n')
    # 配置dba为type4
    tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
    tn.write(('type4 max %s '%max).encode() + b'\n')
    tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
    # 保存配置，退出线路模板
    tn.write(b'commit' + b'\n')
    tn.read_until('OLT(config-dba-profile-{})# '.format(Dba_Profile_ID).encode(), timeout=2)
    tn.write(b'exit' + b'\n')
    tn.write(('show dba-profile profile-id {} '.format(Dba_Profile_ID)).encode() + b'\n')
    time.sleep(0.5)
    command_result = tn.read_very_eager().decode('utf-8')

    if "Max(kbps)     :  %s"%max in command_result:
        cdata_info('dba模板配置type4成功')
        return True
    else:
        cdata_error('dba模板配置type4失败')
        return False



if __name__ == '__main__':
    tn = telnet_host(host_ip='192.168.3.140', username='root', password='admin')[0]
    # dba_limitrate_type4(tn, Dba_Profile_ID, max='1000000')
    dba_limitrate_type5(tn, Dba_Profile_ID, fix='10240', assure='20480', max='51200')

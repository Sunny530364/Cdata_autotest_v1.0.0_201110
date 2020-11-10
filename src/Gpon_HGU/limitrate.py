#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

from src.config.telnet_client import *
from src.config.Cdata_loggers import *


def check_ont_capability(tn,ponid=16,ontid=2,ethid=1):
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
        tn.write("show ont port state {} {} eth all ".format(ponid,ontid).encode() + b'\n')
        result = tn.read_until(b"OLT(config-interface-gpon-0/0)#", timeout=2).decode()
        if "%s    GE"%ethid in result :
            cdata_info("onu端口%s速率为1000M"%ethid)
            # 退出gpon视图下
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return "GE"
        elif "%s    FE"%ethid in result :
            cdata_info("onu端口%s速率为100M"%ethid)
            # 退出gpon视图下
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return "FE"
        else :
            continue
    tn.write(b"exit" + b"\n")
    tn.read_until(b"OLT(config)#", timeout=2)

def dba_limitrate_type5(tn,dba_profile_id=100,):
    try:
        #进入dba视图下
        tn.read_until(b'OLT(config)# ', timeout=2)
        tn.write('dba-profile profile-id {}'.format(dba_profile_id).encode()+b'\n')
        #配置dba为type5
        tn.read_until('OLT(config-dba-profile-{})# '.format(dba_profile_id).encode(),timeout=2)
        tn.write(b'type5 fix 10240 assure 20480 max 51200 '+b'\n')
        tn.read_until('OLT(config-dba-profile-{})# '.format(dba_profile_id).encode(), timeout=2)
        tn.write(b'show dba-profile  current'+b'\n')
        time.sleep(0.5)
        command_result = tn.read_very_eager().decode('utf-8')
        if "Fix(kbps)     :  10240"  in command_result and  "Assure(kbps)  :  20480" in command_result \
                and "Max(kbps)     :  51200" in command_result:
            cdata_info('dba模板配置type5成功')
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-dba-profile-{})# '.format(dba_profile_id).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return True
        else:
            cdata_error('dba模板配置type5失败')
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-dba-profile-{})# '.format(dba_profile_id).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    except:
        cdata_error("dba模板配置失败")
        return False

def dba_limitrate_type4(tn,dba_profile_id=100):
    try:
        # 进入dba视图下
        tn.read_until(b'OLT(config)# ', timeout=2)
        tn.write('dba-profile profile-id {}'.format(dba_profile_id).encode() + b'\n')
        # 配置dba为type4
        tn.read_until('OLT(config-dba-profile-{})# '.format(dba_profile_id).encode(), timeout=2)
        tn.write(b'type4 max 1024000 ' + b'\n')
        tn.read_until('OLT(config-dba-profile-{})# '.format(dba_profile_id).encode(), timeout=2)
        tn.write(b'show dba-profile current ' + b'\n')
        time.sleep(0.5)
        command_result = tn.read_very_eager().decode('utf-8')

        if "Max(kbps)     :  1024000" in command_result:
            cdata_info('dba模板配置type4成功')
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-dba-profile-{})# '.format(dba_profile_id).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return True
        else:
            cdata_error('dba模板配置type4失败')
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-dba-profile-{})# '.format(dba_profile_id).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    except:
        cdata_error("dba模板配置失败")
        return False

def ont_port_limitrate_inbound(tn,traffic_profile_id=1,ponid=16,ontid=2,ethid=1):
    try:
        # 进入gpon视图下
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
        # 配置onu端口入口限速
        tn.write(
            ' ont port car {} {} eth {} inbound {} '.format(ponid, ontid, ethid, traffic_profile_id).encode() + b'\n')
        tn.read_until(b'OLT(config-interface-gpon-0/0)#', timeout=2)
        # 查看onu的端口限速
        tn.write('show ont port car {} {} eth all '.format(ponid, ontid).encode() + b'\n')
        time.sleep(0.5)
        command_result = tn.read_until(b'OLT(config-interface-gpon-0/0)#', timeout=2).decode("utf-8")
        print(command_result)
        result = (((command_result.split('-----------------------------------------------------------------------------'))[1].
              split('----------------------------------------------------------------------------'))[1].split('\r\n')[int(ethid)].split())
        if str(traffic_profile_id) == result[4] :
            cdata_info("ONT端口出口绑定流量模板%s成功" % traffic_profile_id)
            # 退出gpon视图下
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return True
        else:
            cdata_error("ONT端口出口绑定流量模板%s失败" % traffic_profile_id)
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return False
    except:
        cdata_error('onu入口绑定流量模板失败')
        return False

def ont_port_limitrate_outbound(tn,traffic_profile_id=1,ponid=16,ontid=2,ethid=1):
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
            'ont port car {} {} eth {} outbound {} '.format(ponid, ontid, ethid, traffic_profile_id).encode() + b'\n')
        tn.read_until(b'OLT(config-interface-gpon-0/0)#', timeout=2)
        # 查看onu的端口限速
        tn.write('show ont port car {} {} eth all '.format(ponid, ontid).encode() + b'\n')
        command_result = tn.read_until(b'OLT(config-interface-gpon-0/0)#', timeout=2).decode()
        #获取onu端口1的car
        result = (
            ((command_result.split('-----------------------------------------------------------------------------'))[1].
             split('----------------------------------------------------------------------------'))[1].split('\r\n')[
                int(ethid)].split())
        if str(traffic_profile_id) == result[5]:
            cdata_info("ONT端口出口绑定流量模板%s成功" % traffic_profile_id)
            # 退出gpon视图下
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return True
        else:
            cdata_error("ONT端口出口绑定流量模板%s失败" % traffic_profile_id)
            tn.write(b"exit" + b"\n")
            tn.read_until(b"OLT(config)#", timeout=2)
            return False
    except:
        cdata_error("ont出口绑定流量模板失败")
        return False

def ont_port_limitrate_del(tn,ponid=16,ontid=2,ethid=1):
    # 进入gpon视图下
    tn.read_until(b'OLT(config)# ', timeout=2)
    tn.write(b'interface gpon 0/0 ' + b'\n')
    tn.read_until(b'OLT(config-interface-gpon-0/0)#')
    tn.write('no ont port car {} {} eth {} inbound outbound '.format(ponid,ontid,ethid).encode()+b'\n')
    tn.read_until(b'OLT(config-interface-gpon-0/0)#')
    # 退出gpon视图下
    tn.write(b'exit' + b'\n')


if __name__ == '__main__':
    tn = telnet_host(host_ip='192.168.5.164', username='root', password='admin')[0]
    ont_port_limitrate_inbound(tn)

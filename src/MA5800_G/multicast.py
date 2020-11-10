#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI


from src.config.telnet_client_MA5800 import *
import re


def olt_igmp(tn):
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
    #创建组播vlan
    tn.write(b'vlan  3000'+b'\n')
    tn.read_until(b'{ <cr>|to<K>|vlantype<E><mux,standard,smart,super> }:',timeout=2)
    tn.write(b'\n')
    #进入组播vlan模式
    tn.write('multicast-vlan 3000 ')
    tn.read_until(b'MA5800-X15(config-mvlan3000)#',timeout=2)
    #配置igmp版本号
    tn.write(b'igmp version v2'+b'\n')
    tn.read_until(b'MA5800-X15(config-mvlan3000)#', timeout=2)
    #配置组播节目组
    tn.write(b'igmp program add ip 239.1.1.1'+b'\n')
    tn.read_until(b'MA5800-X15(config-mvlan3000)#', timeout=2)
    #配置组播路由端口
    tn.write(b'igmp uplink-port 0/8/2')
    tn.read_until(b'MA5800-X15(config-mvlan3000)#', timeout=2)
    #配置组播模式
    tn.write('igmp mode snooping ')
    tn.read_until(b'MA5800-X15(config-mvlan3000)#', timeout=2)
def add_service_port(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID,mvlan):

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

    command_write = 'service-port vlan  %s gpon 0/1/%s ont %s gemport %s multi-service   user-vlan  %s' % (
                        str(mvlan), Gpon_PonID, Gpon_OnuID, Gemport_ID, str(mvlan))
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2)

    # 查看service-port是否添加成功
    command_write = 'display  service-port  port  0/1/%s ont %s gemport %s' % (Gpon_PonID, Gpon_OnuID, Gemport_ID)
    tn.write(command_write.encode('ascii') + b"\n")
    time.sleep(1)
    tn.write(b"\n")
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2).decode('ascii')
    vp = ((command_result.split('-----------------------------------------------------------------------------'))[2].split('\r\n'))
    for i in range(len(vp)):
        if re.search(r'%s(\s+)common(\s+)gpon(\s+)0/1(\s+)/%s(\s+)%s(\s+)1(\s+)vlan(\s+)%s'%(mvlan,Gpon_PonID, Gpon_OnuID,mvlan),vp[i]):
        # if '3000 common   gpon 0/1 4  40   1     vlan  3000' in vp[i]:
            print((vp[i].split()[0]))
            return (vp[i].split()[0])

    return False


def onu_imgp_transparent(tn,Ont_Srvprofile_ID,Gpon_PonID, Gpon_OnuID, Gemport_ID,Mvlan, User_Vlan):
    add_multicast_member(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID, Mvlan,User_Vlan)
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
    try:
        tn.write(('ont-srvprofile gpon profile-id %s '% (Ont_Srvprofile_ID)).encode() + b'\n')
        tn.read_until(b'{ <cr>|profile-name<K> }:', timeout=2)
        tn.write(b'\n')
        tn.read_until(('MA5800-X15(config-gpon-srvprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    except:
        raise Exception("该线路模板视图可能有其他人的在使用")
    tn.write(b'multicast mode unconcern '+b'\n')
    tn.read_until(('MA5800-X15(config-gpon-srvprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    tn.write(b'display ont-srvprofile  current'+b'\n')
    tn.read_until(b'{ <cr>||<K> }:  ',timeout=2)
    tn.write(b'\n')
    result = tn.read_until(('MA5800-X15(config-gpon-srvprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2).decode()
    if 'Multicast forward mode            : Unconcern' in result:
        cdata_info('onu组播模式配置透传正常')
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-gpon-srvprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        return True
    else:
        cdata_error('onu组播模式配置透传失败')
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-gpon-srvprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        return False


def ont_igmp_snooping(tn,Ont_Srvprofile_ID,Gpon_PonID, Gpon_OnuID, Gemport_ID, Mvlan,User_Vlan):
    add_multicast_member(tn, Gpon_PonID, Gpon_OnuID, Gemport_ID,Mvlan, User_Vlan)
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
    try:
        tn.write(('ont-srvprofile gpon profile-id %s ' % (Ont_Srvprofile_ID)).encode() + b'\n')
        tn.read_until(b'{ <cr>|profile-name<K> }:', timeout=2)
        tn.write(b'\n')
        tn.read_until(('MA5800-X15(config-gpon-srvprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    except:
        raise Exception("该线路模板视图可能有其他人的在使用")
    tn.write(b'multicast mode igmp-snooping ' + b'\n')
    tn.read_until(('MA5800-X15(config-gpon-srvprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
    tn.write(b'display ont-srvprofile  current' + b'\n')
    tn.read_until(b'{ <cr>||<K> }:  ', timeout=2)
    tn.write(b'\n')
    result = tn.read_until(('MA5800-X15(config-gpon-srvprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2).decode()
    if 'Multicast mode                    : IGMP-Snooping' in result:
        cdata_info('onu组播模式配置snooping正常')
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-gpon-srvprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        return True
    else:
        cdata_error('onu组播模式配置snooping失败')
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-gpon-srvprofile-%s)#' % (Ont_Lineprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        return False


def add_multicast_member(tn,Gpon_PonID, Gpon_OnuID, Gemport_ID,Mvlan, User_Vlan):
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
    try:
        # 进入btv下增加用户
        tn.write(b'btv' + b'\n')
        tn.read_until(b'MA5800-X15(config-btv)#', timeout=2)
        tn.write(('igmp user  add port 0/1/%s ontid %s gemport-index %s user-vlan %s'%(Gpon_PonID, Gpon_OnuID, Gemport_ID, User_Vlan)).encode() + b'\n')
        tn.read_until(b'{ <cr>|auth<K>|globalleave<K>|igmp-version<K>|log<K>|max-bandwidth<K>|max-program<K>|no-auth<K>|quickleave<K> }:',timeout=2)
        tn.write(b'\n')
        tn.read_until(b'MA5800-X15(config-btv)#', timeout=2)
        # 进入组播vlan视图
        tn.write(('multicast-vlan %s'%Mvlan).encode() + b'\n')
        tn.read_until(('MA5800-X15(config-mvlan%s)#'%Mvlan).encode(), timeout=2)
        #添加用户
        tn.write(('igmp multicast-vlan member port 0/1/%s ontid %s gemport-index %s user-vlan %s'%(Gpon_PonID, Gpon_OnuID, Gemport_ID, User_Vlan)).encode()+b'\n')
        tn.read_until(('MA5800-X15(config-mvlan%s)#' % Mvlan).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b"MA5800-X15(config)#", timeout=2)
        cdata_info('添加组播用户正常')
        return True
    except:
        cdata_error('添加组播用户失败')
        return False


def del_multicast_member(tn,Gpon_PonID, Gpon_OnuID, Gemport_ID):
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
    try:
        # 进入btv下删除用户
        tn.write(b'btv' + b'\n')
        tn.read_until(b'MA5800-X15(config-btv)#', timeout=2)
        tn.write(('igmp user delete port 0/1/%s ontid %s gemport-index %s'%(Gpon_PonID, Gpon_OnuID, Gemport_ID)).encode() + b'\n')
        tn.read_until(b'Are you sure to delete user? (y/n)[n]:',timeout=2)
        tn.write(b'y \n')
        tn.read_until(b'MA5800-X15(config-btv)#', timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b"MA5800-X15(config)#", timeout=2)
        cdata_info('删除组播用户正常')
        return True
    except:
        cdata_error('删除组播用户失败')
        return False


if __name__ == '__main__':
    tn = telnet_host(host_ip='192.168.5.82', username='test111', password='test123')[0]
    # add_multicast_member(tn, Gpon_PonID='4', Gpon_OnuID='40', Gemport_ID='1', User_Vlan='3000')
    ont_igmp_snooping(tn, Ont_Srvprofile_ID='200',Gpon_PonID='4', Gpon_OnuID='40', Gemport_ID='1', User_Vlan='3000')
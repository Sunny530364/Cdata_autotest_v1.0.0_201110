#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI


from src.config.telnet_client_MA5800 import *
import re

#获取onu的虚端口索引号
def get_service_port(tn, PonID, OnuID,User_Vlan):

    # # 判断当前的视图是否正确。
    # tn.write(b"\n")
    # result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    # if result:
    #     pass
    # else:
    #     cdata_info("==========================================")
    #     cdata_error("===============ERROR!!!===================")
    #     cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
    #     cdata_info("==========================================")
    #     tn.write(b"quit" + b"\n")
    #     result = tn.read_until(b"MA5800-X15(config)#", timeout=2)
    #     return False
    #
    # command_write = 'service-port vlan  %s gpon 0/1/%s ont %s gemport %s multi-service   user-vlan  %s' % (
    #                     str(mvlan), PonID, OnuID, Gemport_ID, str(mvlan))
    # tn.write(command_write.encode('ascii') + b"\n")
    # time.sleep(1)
    # tn.write(b"\n")
    # command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2)

    # 查看service-port是否添加成功

    tn.read_until(b"MA5800-X15(config)#", timeout=2)
    command_write = 'display  service-port  port  0/2/%s ont %s ' % (PonID, OnuID)
    tn.write(command_write.encode() + b"\n")
    tn.read_until(b'{ <cr>|e2e<K>|gemport<K>|sort-by<K>||<K> }: ',timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(b"MA5800-X15(config)#", timeout=2).decode()
    cdata_debug(command_result)
    vp = ((command_result.split('-----------------------------------------------------------------------------'))[2].split('\r\n'))
    for i in range(len(vp)):
        if re.search(r'%s(\s+)common(\s+)epon(\s+)0/2(\s+)/%s(\s+)%s(\s+)-(\s+)vlan(\s+)%s'%(User_Vlan,PonID, OnuID,User_Vlan),vp[i]):
        # if '32 3000 common   epon 0/2 /4  40   -     vlan  3000       -    -    up' in vp[i]:
            cdata_debug((vp[i].split()[0]))
            return (vp[i].split()[0])

#配置onu组播模式为透传
def ont_imgp_transparent(tn,PonID,OnuID,Mvlan,User_Vlan):
    #增加组播成员
    add_multicast_member(tn, PonID, OnuID, Mvlan,User_Vlan)
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

    tn.write(b'interface epon 0/2' + b'\n')
    result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)# ', timeout=2)
    tn.write(('ont multicast-mode %s %s transparent '%(PonID,OnuID)).encode() + b'\n')
    tn.read_until(b' This command will force all the multicast users offline on this ONT Are you sure to execute this command? (y/n)[n]: ',timeout=2)
    tn.write(b'y \n')
    result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)#', timeout=2)
    tn.write(('display ont info %s %s'%(PonID,OnuID)).encode()+b'\n')
    tn.read_until(b'{ <cr>||<K> }: ',timeout=2)
    tn.write(b'\n')
    result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)# ', timeout=2).decode('utf-8')
    if 'Multicast mode          : Transparent' in result :
        cdata_info('onu配置组播模式为transparent正常')
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#',timeout=2)
        return True
    else:
        cdata_error('onu配置组播模式为transparent失败')
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#', timeout=2)
        return False

#配置onu组播模式为snooping
def ont_imgp_snooping(tn,PonID,OnuID, Mvlan,User_Vlan):
    # 增加组播成员
    add_multicast_member(tn, PonID, OnuID, Mvlan,User_Vlan)
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
    tn.write(b'interface epon 0/2' + b'\n')
    result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)#', timeout=2)
    tn.write(('ont  multicast-mode %s %s igmp-snooping  '%(PonID,OnuID)).encode() + b'\n')
    tn.read_until(b'This command will force all the multicast users offline on this ONT Are you sure to execute this command? (y/n)[n]: ',timeout=2)
    tn.write(b'y \n')
    result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)#', timeout=2)
    tn.write(('display ont info %s %s' % (PonID, OnuID)).encode() + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ', timeout=2)
    tn.write(b'\n')
    result = tn.read_until(b'MA5800-X15(config-if-epon-0/2)# ', timeout=2).decode('utf-8')
    if 'Multicast mode          : IGMP-Snooping' in result :
        cdata_info('onu配置组播模式为imgp-snooping正常')
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#', timeout=2)
        return True

    else:
        cdata_error('onu配置组播模式为igmp_snooping失败')
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#', timeout=2)
        return False

#配置组播
def ont_multicast_tagstrip(tn,Ont_Srvprofile_ID,Ont_Port_ID,tagstrip):

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
        tn.write(('ont-srvprofile epon profile-id %s ' % (Ont_Srvprofile_ID)).encode() + b'\n')
        tn.read_until(b'{ <cr>|profile-name<K> }:', timeout=2)
        tn.write(b'\n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
    except:
        raise Exception("该线路模板视图可能有其他人的在使用")
    tn.write(('port eth %s multicast-tagstrip %s '%(Ont_Port_ID,tagstrip)).encode() + b'\n')
    result = tn.read_until(b'{ <cr>|ds-policing<K>|group-num-max<K>|max-mac-count<K>|up-policing<K> }:', timeout=2)
    tn.write(b'\n')
    tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
    tn.write(('display ont-srvprofile  current ').encode() + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ', timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(),timeout=2).decode()
    ' ETH  1       -                -                Tag         Unlimited'
    if re.search(r"ETH(\s+)%s(.*)%s" % (Ont_Port_ID,tagstrip), command_result,re.I):
        cdata_info('端口%s 配置下行组播vlan %s成功'%(Ont_Port_ID,tagstrip))
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#', timeout=2)
        return True
    else:
        cdata_info('端口%s 配置下行组播vlan %s失败' % ( Ont_Port_ID, tagstrip))
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#', timeout=2)
        return False

def ont_multicast_tagstrip_translation(tn,Ont_Srvprofile_ID,Ont_Port_ID,Svlan,Cvlan):
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
        tn.write(('ont-srvprofile epon profile-id %s ' % (Ont_Srvprofile_ID)).encode() + b'\n')
        tn.read_until(b'{ <cr>|profile-name<K> }:', timeout=2)
        tn.write(b'\n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
    except:
        raise Exception("该线路模板视图可能有其他人的在使用")
    tn.write(('port eth %s multicast-tagstrip translation %s %s ' % (Ont_Port_ID, Svlan,Cvlan)).encode() + b'\n')
    tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
    tn.write(('display ont-srvprofile  current ').encode() + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ', timeout=2)
    tn.write(b'\n')
    command_result = tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(),
                                   timeout=2).decode()
    ' ETH  1       3000             200              Translation Unlimited'
    if re.search(r"ETH(\s+)%s(\s+)%s(\s+)%s(\s+)Translation" % (Ont_Port_ID, Svlan,Cvlan), command_result, re.I):
        cdata_info('端口%s 配置下行组播vlan %s转%s成功' % (Ont_Port_ID,  Svlan,Cvlan))
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#', timeout=2)
        return True
    else:
        cdata_info('端口%s 配置下行组播vlan %s转%s失败' % (Ont_Port_ID,  Svlan,Cvlan))
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#', timeout=2)
        return False

def ont_igmp_mvlan(tn,Ont_Srvprofile_ID,Ont_Port_ID,Mvlan):
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
        tn.write(('ont-srvprofile epon profile-id %s ' % (Ont_Srvprofile_ID)).encode() + b'\n')
        tn.read_until(b'{ <cr>|profile-name<K> }:', timeout=2)
        tn.write(b'\n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
    except:
        raise Exception("该线路模板视图可能有其他人的在使用")
    tn.write(('port multicast-vlan eth %s %s ' % ( Ont_Port_ID, Mvlan)).encode() + b'\n')
    tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
    tn.write(('port eth %s multicast-tagstrip untag'%Ont_Port_ID).encode()+b'\n')
    tn.read_until(b'{ <cr>|ds-policing<K>|group-num-max<K>|max-mac-count<K>|up-policing<K> }: ',timeout=2)
    tn.write(b'\n')
    tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
    tn.write(('display ont-srvprofile  current ').encode() + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ',timeout=2)
    tn.write(b'\n')
    result = tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2).decode()
    if re.search(r'ETH(\s+)%s(\s+)%s(.*)'%(Ont_Port_ID,Mvlan), result, re.I):
    #if ' ETH  %s       %s             -                Untag       Unlimited'%(Ont_Port_ID,Mvlan) in result:
        cdata_info('onu端口配置组播mvlan正常')
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#', timeout=2)
        return True
    else:
        cdata_error('onu端口配置组播mvlan失败')
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#', timeout=2)
        return False

def del_ont_igmp_mvlan(tn,Ont_Srvprofile_ID,Ont_Port_ID,Mvlan):
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
        tn.write(('ont-srvprofile epon profile-id %s ' % (Ont_Srvprofile_ID)).encode() + b'\n')
        tn.read_until(b'{ <cr>|profile-name<K> }:', timeout=2)
        tn.write(b'\n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
    except:
        raise Exception("该线路模板视图可能有其他人的在使用")
    tn.write(('undo port multicast-vlan eth %s %s ' % ( Ont_Port_ID, Mvlan)).encode() + b'\n')
    tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
    tn.write(('display ont-srvprofile  current ').encode() + b'\n')
    tn.read_until(b'{ <cr>||<K> }: ', timeout=2)
    tn.write(b'\n')
    result = tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(),timeout=2).decode()
    # 'ETH  1       -                -                Untag       Unlimited'
    if re.search(r'ETH(\s+)%s(\s+)-(.*)'%(Ont_Port_ID),result,re.I):
    #if ' ETH  %s       -                -                Untag       Unlimited'%(Ont_Port_ID) in result:
        cdata_info('onu端口删除组播mvlan正常')
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#', timeout=2)
        return True
    else:
        cdata_error('onu端口删除组播mvlan失败')
        tn.write(b'commit \n')
        tn.read_until(('MA5800-X15(config-epon-srvprofile-%s)#' % (Ont_Srvprofile_ID)).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b'MA5800-X15(config)#', timeout=2)
        return False

def add_multicast_member(tn,PonID, OnuID,Mvlan,User_Vlan):
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
        #获取虚端口的index
        vp_index = get_service_port(tn, PonID, OnuID, User_Vlan)
        # 进入btv下增加用户
        tn.write(b'btv' + b'\n')
        tn.read_until(b'MA5800-X15(config-btv)#', timeout=2)
        tn.write(('igmp user add service-port %s '%(vp_index)).encode() + b'\n')
        tn.read_until(b'{ <cr>|auth<K>|globalleave<K>|igmp-ipv6-version<K>|igmp-version<K>|log<K>|max-bandwidth<K>|max-program<K>|no-auth<K>|quickleave<K>|video<K> }: ',timeout=2)
        tn.write(b'\n')
        tn.read_until(b'MA5800-X15(config-btv)#', timeout=2)
        # 进入组播vlan视图
        tn.write(('multicast-vlan %s'%Mvlan).encode() + b'\n')
        tn.read_until(('MA5800-X15(config-mvlan%s)#'%Mvlan).encode(), timeout=2)
        #添加用户
        tn.write(('igmp multicast-vlan member service-port %s '%(vp_index)).encode()+b'\n')
        tn.read_until(('MA5800-X15(config-mvlan%s)#' % Mvlan).encode(), timeout=2)
        tn.write(b'quit \n')
        tn.read_until(b"MA5800-X15(config)#", timeout=2)
        cdata_info('添加组播用户正常')
        return True
    except:
        cdata_error('添加组播用户失败')
        return False

def del_multicast_member(tn,PonID, OnuID,User_Vlan):
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
        # 获取虚端口的index
        vp_index = get_service_port(tn, PonID, OnuID,User_Vlan)
        # 进入btv下删除用户
        tn.write(b'btv' + b'\n')
        tn.read_until(b'MA5800-X15(config-btv)#', timeout=2)
        tn.write(('igmp user delete service-port %s'%(vp_index)).encode() + b'\n')
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
    # add_multicast_member(tn, PonID='4', OnuID='40', Gemport_ID='1', User_Vlan='3000')
    # ont_igmp_snooping(tn, Ont_Srvprofile_ID='200',PonID='4', OnuID='40', Gemport_ID='1', User_Vlan='3000')
    # get_service_port(tn, PonID='4', OnuID='40', mvlan='3000')
    #ont_multicast_tagstrip(tn, Ont_Srvprofile_ID='200', Ont_Port_ID='1',tagstrip='Tag')
    #ont_multicast_tagstrip_translation(tn, Ont_Srvprofile_ID='200', Ont_Port_ID='1',Svlan='3000',Cvlan='2000')
    #ont_igmp_mvlan(tn,Ont_Srvprofile_ID='200',Ont_Port_ID='1',Mvlan='3000')
    del_ont_igmp_mvlan(tn,Ont_Srvprofile_ID='200',Ont_Port_ID='1',Mvlan='3000')
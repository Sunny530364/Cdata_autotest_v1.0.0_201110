#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI
import time
from src.config.telnet_client import *
import logging
from src.config.Cdata_loggers import *
# initialize(log_level=logging.INFO)

# def ont_lineprofile_view(tn,ont_lineprofile_id):
#     '''
#     进入线路模板视图
#     '''
#     tn.read_until(b'OLT(config)# ', timeout=2)
#     tn.write('ont-lineprofile gpon profile-id {} '.format(ont_lineprofile_id).encode() + b'\n')

def change_mapping_mode(tn,mapping_mode,ont_lineprofile_id):
    '''
    配置mapping-mode ，可以是（vlan,vlan_pri,pri,port）
    '''
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode()+ b'\n')

def gemport_transparent(tn,ont_lineprofile_id=200,mapping_mode='vlan'):
    '''
    配置mapping-mode为vlan，gem mapping 1 1 为透传
    :param tn: telnet登录对象
    :param mapping_mode: mapping-mode 的模式
    :return: None
    '''
    cdata_info("配置gemport为transparent")
    # 判断当前的视图是否正确。
    # 进入线路模板视图下
    tn.write('ont-lineprofile gpon profile-id {} '.format(ont_lineprofile_id).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    if result:
        pass
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        print("==========================================")
        tn.write(b"commit" + b"\n")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 删除gem mapping 1
    tn.write(b'no gem mapping  1  1 ' + b'\n')
    # 修改mapping-mode为vlan
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    #判断mapping_mode设置是否正常
    tn.write(b'show ont-lineprofile current' + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2).decode("utf-8")
    if "Mapping mode     : VLAN" in result:
        cdata_info("线路模板:mapping_mode设置成vlan正常")
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成vlan失败")
        print("==========================================")
        tn.write(b"commit" + b"\n")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 配置gem mapping 1 为transparent
    tn.write(b'gem mapping  1  1 vlan  transparent' + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    tn.write(b'show ont-lineprofile current' + b'\n')
    command_result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(),timeout=2).decode("utf-8")
    if '1           -         -             -' in command_result:
        cdata_info('线路模板:配置gemport 1为transparent成功')
        # 保存配置，退出线路模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('线路模板:配置gemport 1为transparent失败')
        print("==========================================")
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

def gemport_untag(tn,ont_lineprofile_id=200,mapping_mode='vlan'):
    '''
    配置mapping-mode为vlan，gem mapping 1 1 为透传
    :param tn: telnet登录对象
    :param mapping_mode: mapping-mode 的模式
    :return: None
    '''
    cdata_info("配置gemport为transparent")
    # 判断当前的视图是否正确。
    # 进入线路模板视图下
    tn.write('ont-lineprofile gpon profile-id {} '.format(ont_lineprofile_id).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    if result:
        pass
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        print("==========================================")
        tn.write(b"commit" + b"\n")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 删除gem mapping 1
    tn.write(b'no gem mapping  1  1 ' + b'\n')
    # 修改mapping-mode为vlan
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    #判断mapping_mode设置是否正常
    tn.write(b'show ont-lineprofile current' + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2).decode("utf-8")
    if "Mapping mode     : VLAN" in result:
        cdata_info("线路模板:mapping_mode设置成vlan正常")
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成vlan失败")
        print("==========================================")
        tn.write(b"commit" + b"\n")
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 配置gem mapping 1 为untag
    tn.write(b'gem mapping  1  1 vlan  untag' + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    tn.write(b'show ont-lineprofile current' + b'\n')
    command_result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(),timeout=2).decode("utf-8")
    if '1           untagged' in command_result:
        cdata_info('线路模板:配置gemport 1为transparent成功')
        # 保存配置，退出线路模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('线路模板:配置gemport 1为transparent失败')
        print("==========================================")
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False



def gemport_vlan(tn,ont_lineprofile_id=200,mapping_mode='vlan'):
    '''
        配置mapping-mode为vlan，gem mapping 1 vlan 2000 为透传
        :param tn: telnet登录对象
        :param mapping_mode: mapping-mode 的模式
        :return: None
        '''
    cdata_info("配置mapping_mode为vlan")
    try:
        # 判断当前的视图是否正确。
        # 进入线路模板视图下
        tn.write('ont-lineprofile gpon profile-id {} '.format(ont_lineprofile_id).encode() + b'\n')
        result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        if result:
            pass
        else:
            print("==========================================")
            print("===============ERROR!!!===================")
            cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
            print("==========================================")
            tn.write(b"commit"+b'\n')
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False

        #删除gem mapping 1
        tn.write(b'no gem mapping  1  1 '+ b'\n')
        #修改mapping-mode is vlan
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        # 判断mapping_mode设置是否正常
        tn.write(b'show ont-lineprofile current' + b'\n')
        result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(),
                               timeout=2).decode("utf-8")
        if "Mapping mode     : VLAN" in result:
            cdata_info("线路模板:mapping_mode设置成vlan正常")
        else:
            print("==========================================")
            print("===============ERROR!!!===================")
            cdata_error("线路模板:mapping_mode设置成vlan失败")
            print("==========================================")
            tn.write(b"commit" + b'\n')
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
        #配置gem mapping 为vlan2000
        tn.write(b'gem mapping 1 1 vlan 2000'+b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(b'show ont-lineprofile current' + b'\n')
        command_result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(),
                                       timeout=2).decode("utf-8")
        if '1           2000      -             - ' in command_result:
            cdata_info('线路模板:配置gem mapping 为2000成功')
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return True
        else:
            print("==========================================")
            print("===============ERROR!!!===================")
            cdata_error('线路模板:配置gem mapping 为vlan失败')
            print("==========================================")
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    except:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('线路模板:配置gem mapping 为vlan失败')
        print("==========================================")

        return False

def gemport_vlan_pri(tn,ont_lineprofile_id=200,mapping_mode='vlan-priority '):
    '''
    配置mapping-mode为vlan-priority，gem mapping 1 1 vlan 2000 pri 2为透传
    :param tn: telnet登录对象
    :param mapping_mode: mapping-mode 的模式
    '''
    cdata_info("配置mapping_mode为vlan+pri")
    # 判断当前的视图是否正确。
    # 进入线路模板视图下
    tn.write('ont-lineprofile gpon profile-id {} '.format(ont_lineprofile_id).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    if result:
        pass
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    #删除gem mapping 1
    tn.write(b'no gem mapping  1  1 ' + b'\n')
    #修改mapping-mode is vlan-priority
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    # 判断mapping_mode设置是否正常
    tn.write(b'show ont-lineprofile current' + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(),
                           timeout=2).decode("utf-8")
    if " Mapping mode     : VLAN + 802.1p PRI" in result:
        cdata_info("线路模板:mapping_mode设置成vlan+pri正常")
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成vlan+pri失败")
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    #配置gem mapping 为vlan 2000+pri 7
    tn.write(b' gem mapping  1 1 vlan 2000 priority 7 ' + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    tn.write(b'show ont-lineprofile current' + b'\n')
    command_result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2).decode("utf-8")
    if '1           2000      7             - ' in command_result:
        cdata_info('线路模板:配置gem mapping 为vlan 2000+pri2成功')

        # 保存配置，退出线路模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error('线路模板:配置gem mapping 为vlan 2000+pri2失败')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        # 保存配置，退出线路模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

def gemport_pri(tn,ont_lineprofile_id=200,mapping_mode='priority'):

    # 判断当前的视图是否正确。
    # 进入线路模板视图下
    cdata_info("配置mapping_mode为pri")
    tn.write('ont-lineprofile gpon profile-id {} '.format(ont_lineprofile_id).encode() + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    if result:
        pass
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 删除gem mapping 1
    tn.write(b'no gem mapping  1  1 ' + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    # 修改mapping-mode is priority
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    # 判断mapping_mode设置是否正常
    tn.write(b'show ont-lineprofile current' + b'\n')
    result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(),
                           timeout=2).decode("utf-8")
    if " Mapping mode     : 802.1p PRI" in result:
        cdata_info("线路模板:mapping_mode设置成pri正常")
    else:
        print("==========================================")
        print("===============ERROR!!!===================")
        cdata_error("线路模板:mapping_mode设置成pri失败")
        print("==========================================")
        tn.write(b"commit" + b'\n')
        tn.write(b"exit" + b"\n")
        result = tn.read_until(b"OLT(config)#", timeout=2)
        return False

    # 配置gem mapping 为pri 7
    tn.write(b' gem mapping 1 1 priority 7  ' + b'\n')
    tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
    tn.write(b'show ont-lineprofile current' + b'\n')
    command_result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(),
                                   timeout=2).decode("utf-8")
    if '1           -         7             - ' in command_result:
        cdata_info('线路模板配置gem mapping 为pri2成功')
        # 保存配置，退出线路模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return True
    else:
        cdata_error('线路模板配置gem mapping pri2失败')
        # 保存配置，退出线路模板
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False

def gemport_port(tn,ont_lineprofile_id=200,ethid='1',mapping_mode='port'):
    # 判断当前的视图是否正确。
    # 进入线路模板视图下
    cdata_info("配置mapping-mode为port")
    try:
        tn.write('ont-lineprofile gpon profile-id {} '.format(ont_lineprofile_id).encode() + b'\n')
        result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        if result:
            pass
        else:
            print("==========================================")
            print("===============ERROR!!!===================")
            cdata_error('当前OLT所在的视图不正确，请检查上一个模块的代码。')
            print("==========================================")
            tn.write(b"commit" + b'\n')
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
        # 删除gem mapping 1
        tn.write(b'no gem mapping  1  1 ' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        # 修改mapping-mode is port
        tn.write(' mapping-mode {0}'.format(mapping_mode).encode() + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        # 判断mapping_mode设置是否正常
        tn.write(b'show ont-lineprofile current' + b'\n')
        result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(),
                               timeout=2).decode("utf-8")
        if " Mapping mode     : PORT" in result:
            cdata_info("线路模板:mapping_mode设置成port正常")
        else:
            print("==========================================")
            print("===============ERROR!!!===================")
            cdata_error("线路模板:mapping_mode设置成port失败")
            print("==========================================")
            tn.write(b"commit" + b'\n')
            tn.write(b"exit" + b"\n")
            result = tn.read_until(b"OLT(config)#", timeout=2)
            return False
        # 配置gem mapping 为port 2
        tn.write(('gem mapping 1 1 eth %s '%ethid).encode() + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(b'show ont-lineprofile current' + b'\n')
        command_result = tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(),
                                       timeout=2).decode("utf-8")
        if '1           -         -             %s '%(ethid) in command_result:
            cdata_info('线路模板配置gem mapping 为port %s成功'%ethid)
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return True
        else:
            cdata_error('线路模板配置gem mapping 为port %s失败'%ethid)
            # 保存配置，退出线路模板
            tn.write(b'commit' + b'\n')
            tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
            tn.write(b'exit' + b'\n')
            return False
    except:
        tn.write(b'commit' + b'\n')
        tn.read_until('OLT(config-ont-lineprofile-{})# '.format(ont_lineprofile_id).encode(), timeout=2)
        tn.write(b'exit' + b'\n')
        return False


if __name__ == '__main__':
    host_ip = '192.168.5.164'
    username = 'root'
    password = 'admin'
    tn = telnet_host(host_ip, username, password)[0]
    gemport_transparent(tn)
    gemport_port(tn)
    # gemport_vlan(tn)
    # gemport_pri(tn)
#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI

#导入telnetlib模块
from telnetlib import Telnet
import time
import logging
import sys
from  src.config.Cdata_loggers import *
# from  src.config.initialization_config import *

def telnet_host(host_ip,username,password):
    '''
    :param host_ip: 被测设备的管理
    :param username: 被测设备登录的用户名
    :param password: 被测设备登录的密码
    :return: telnet的连接对象或者布尔值
    '''
    try:
        tn = Telnet(host_ip,port=23)
        #设置调试级别，debuglevel的值越高，得到的调试输出就越多(在sys.stdout上)
        Telnet.set_debuglevel(tn,debuglevel=1)
    except:
        cdata_warn('%s 设备连接失败' % host_ip)
        return False,
    # 等待login出现后输入用户名，最多等待5秒
    tn.read_until(b'>>User name: ', timeout=5)
    tn.write(username.encode() + b'\n')
    # 等待Password出现后输入用户名，最多等待5秒
    tn.read_until(b'>>User password: ', timeout=5)
    tn.write(password.encode() + b'\n')
    # 延时1秒再收取返回结果，给服务端足够响应时间
    time.sleep(2)
    # 获取登录结果
    # read_very_eager()获取到的是的是上次获取之后本次获取之前的所有输出
    command_result = tn.read_very_eager().decode('utf-8')
    print(command_result)
    if 'Huawei Integrated Access Software' in command_result:
        cdata_info('%s 登录成功' % host_ip)
        tn.read_until(b'MA5800-X15>', timeout=2)
        tn.write('enable'.encode() + b'\n')
        # self.tn.read_until(b'OLT# ', timeout=10)
        tn.write('config'.encode() + b'\n')
        tn.read_until(b'MA5800-X15(config)# ', timeout=5)
        tn.write('idle-timeout  255'.encode() + b'\n')
        tn.read_until(b'MA5800-X15(config)# ', timeout=5)
        tn.write('scroll  512'.encode() + b'\n')
        tn.read_until(b'MA5800-X15(config)# ', timeout=5)
        tn.write('undo event output all'.encode() + b'\n')
        tn.read_until(b'MA5800-X15(config)# ', timeout=5)
        tn.write('undo  alarm  output all'.encode() + b'\n')
        tn.read_until(b'MA5800-X15(config)# ', timeout=5)
        return tn,True
    else:
        cdata_info('%s 登录失败，用户名或密码错误' % host_ip)
        return False,

#关闭telnet连接
def logout_host(tn):
    tn.close()

# 此函数实现执行传过来的命令，并输出其执行结果
def execute_some_command(tn):
    with open('init.txt','r',encoding='UTF-8') as f:
        lines = f.readlines()
        for line in lines:
            if '#' in line:
                print(line)
            else:
                # 执行命令
                tn.write(line.encode()+b'\n')
                time.sleep(1)
                # 获取命令结果
                command_result = tn.read_very_eager().decode('utf-8')
                logging.warning('命令执行结果：\n%s' % command_result)



if __name__ == '__main__':
    olt_mgt_ip = '192.168.5.82'
    olt_username = 'root123'
    olt_password = 'admin123'
    tn = telnet_host(host_ip=olt_mgt_ip, username=olt_username, password=olt_password)[0]
    if tn == False:
        raise Exception("设备登录失败")
    # execute_some_command(tn)
    logout_host(tn)


#
# if __name__ == '__main__':
#     olt_mgt_ip = '192.168.5.164'
#     olt_username = 'root'
#     olt_password = 'admin'
#
#     tn = telnet_host(host_ip=olt_mgt_ip, username=olt_username, password=olt_password)[0]
#     if tn == False:
#         raise Exception("设备登录失败")
#     print('继续测试')
#     print(tn)
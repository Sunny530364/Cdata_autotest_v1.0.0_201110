import sys
print(sys.path)
import getpass
import telnetlib
import os
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
import datetime
import requests
import shlex
import subprocess
import wmi
import psutil
from src.config.Cdata_loggers import *

'''
打开谷歌浏览器，使用公司的speedtest服务器进行测速。
需要将谷歌浏览器的驱动chromedriver.exe放入系统的环境变量中。
'''


def speedtest_test():
    try:
        text5 = 'xxx'
        num = 1
        browser = webdriver.Chrome()
        browser.get('http://192.168.6.253:10080/speedtest.html')
        wait = WebDriverWait(browser, 10, 1)
        submit1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#startStopBtn')))
        submit1.click()

        # 测试过程中，数据会一致跳动，等待数据连续三次一样以后，再取结果。
        while 1:
            text2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ulText'))).text
            time.sleep(1)
            if text2 != '' and text2 != '...':
                if text2 == text5:
                    num = num + 1
                    if num == 3:
                        break
                else:
                    text5 = text2

        # 读取SPEEDTEST测试的结果
        text1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#dlText'))).text
        text2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ulText'))).text
        text3 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#pingText'))).text
        text4 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#jitText'))).text
        text5 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ip'))).text

        # 打印SPEEDTEST的测试结果
        cdata_info("==============================")
        cdata_info("下行速率为         ：%sMbps" % (text1))
        cdata_info("上行速率为         ：%sMbps" % (text2))
        cdata_info("Ping时延为         ：%sms" % (text3))
        cdata_info("Jitter抖动时延为   ：%sms" % (text4))
        cdata_info("当前电脑的IP地址为 ：%s" % (text5))
        cdata_info("==============================")

        # 判断SPEEDTEST的测试结果是否通过(判断条件上行和下行的速率大于60Mbps)
        if float(text1) > 60 or float(text2) > 60:
            cdata_info("SPEEDTEST测速成功")
            return True
        else:
            cdata_error("SPEEDTEST测速失败")
            return False
    except:
        cdata_error("Speedtest测速失败")
        return False
    finally:
        browser.quit()


# 执行PING测试
def ping(Ping_test_addr):
    for i in range(0, 3):
        s1 = ""
        shell_cmd = 'ping ' + Ping_test_addr
        cmd = shlex.split(shell_cmd)
        p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while p.poll() is None:
            line = p.stdout.readline()
            line = line.strip()
            if line:
                s1 = s1 + str(line, encoding='gbk')
        if p.returncode == 0:
            cdata_info('ping成功了。')
            return True
    else:
        cdata_error('ping失败了.')
        return False


# 测试电脑的上网方式为DHCP
def dhcp_test(Network_car_name):
    try:
        c = wmi.WMI()
        # 获取电脑网卡DHCP开关状态，如果是关闭状态就开启
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if Network_car_name in interface.Caption:
                if interface.DHCPEnabled:
                    cdata_info('当前DHCP为开启状态。')
                    break
                else:
                    cdata_info('当前DHCP为关闭状态，需要等待程序重新开启。')
                    time.sleep(1)
                    returnValues1 = interface.EnableDHCP()
                    time.sleep(1)
                    returnValues2 = interface.SetDNSServerSearchOrder()
                    print(returnValues1[0],returnValues2[0])
                    if returnValues1[0] == 0 and returnValues2[0] == 0:
                        cdata_info("DHCP和DNS修改成为自动获取成功")
                        break
                    else:
                        cdata_error("DHCP和DNS修改成为自动获取失败")
                        return False
                    break
        else:
            cdata_error('当前网卡不存在，请检查网卡配置')
            return False

        # 重新获取IP地址
        os.system("ipconfig/release")
        os.system("ipconfig/renew")

        # 读取重新获取后的IPv4的地址
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if Network_car_name in interface.Caption:
                print(interface)
                ipv4_addr = interface.IPAddress[0]
                default_gw = interface.DefaultIPGateway[0]
                networkmask = interface.IPSubnet[0]
                dns1 = interface.DNSServerSearchOrder[0]
                dns2 = interface.DNSServerSearchOrder[1]

                # 读取电脑网卡的IPv4的地址信息
                cdata_info("=======================================")
                cdata_info("当前的IP地址信息")
                cdata_info("=======================================")
                cdata_info('当前的网卡名称为     ：%s' % ('Broadcom NetLink (TM) Gigabit Etherne'))
                cdata_info('PC获取到的IP地址为   ：%s' % (ipv4_addr))
                cdata_info('PC获取到的网关地址为 ：%s' % (default_gw))
                cdata_info('PC获取到的子网掩码为 ：%s' % (networkmask))
                cdata_info('PC获取到的主DNS为    ：%s' % (dns1))
                cdata_info('PC获取到的备DNS为    ：%s' % (dns2))
                return True
        else:
            cdata_error('当前网卡不存在，请检查网卡配置')
            return False
    except:
        return False

    # 修改PC上网的方式为静态IP


# 测试电脑的上网方式为静态IP
def static_ip_test(Network_car_name):
    try:
        c = wmi.WMI()

        # 获取电脑网卡DHCP开关状态，如果是关闭状态就开启
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if Network_car_name in interface.Caption:
                if interface.DHCPEnabled:
                    cdata_info('当前DHCP为开启状态。')
                    break
                else:
                    cdata_info('当前DHCP为关闭状态，需要等待程序重新开启。')
                    time.sleep(1)
                    returnValues1 = interface.EnableDHCP()
                    time.sleep(1)
                    returnValues2 = interface.SetDNSServerSearchOrder()
                    print(returnValues1[0],returnValues2[0])
                    if returnValues1[0] == 0 and returnValues2[0] == 0:
                        cdata_info("DHCP和DNS修改成为自动获取成功")
                        break
                    else:
                        cdata_error("DHCP和DNS修改成为自动获取失败")
                        return False
        else:
            cdata_error('当前网卡不存在，请检查网卡配置')
            return False

        # 重新获取IP地址
        os.system("ipconfig/release")
        os.system("ipconfig/renew")

        # 获取当前动态获取的IP地址，然后将动态IP获取的地址设置PC的静态IP地址
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if Network_car_name in interface.Caption:
                ipv4_addr = interface.IPAddress[0]
                default_gw = interface.DefaultIPGateway[0]
                networkmask = interface.IPSubnet[0]
                dns1 = interface.DNSServerSearchOrder[0]
                dns2 = interface.DNSServerSearchOrder[1]
                if interface.DHCPEnabled:
                    cdata_info('当前DHCP为开启状态，需要等待程序设置成静态IP。')
                    for i in range(0, 3):
                        time.sleep(1)
                        returnValues1 = interface.EnableStatic(IPAddress=[ipv4_addr], SubnetMask=[networkmask])
                        time.sleep(1)
                        returnValues2 = interface.SetGateways(DefaultIPGateway=[default_gw])
                        time.sleep(1)
                        returnValues3 = interface.SetDNSServerSearchOrder(DNSServerSearchOrder=[dns1, dns2])
                        print(returnValues1[0],returnValues2[0],returnValues3[0])
                        if returnValues1[0] == 0 and returnValues2[0] == 0 and returnValues3[0] == 0:
                            cdata_info("静态IP地址配置成功")
                            break
                    else:
                        cdata_error("静态IP地址配置失败")
                        return False
                    break
        else:
            cdata_error('当前网卡不存在，请检查网卡配置')
            return False

        # 读取电脑网卡的IPv4的地址信息
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if Network_car_name in interface.Caption:
                current_ipv4_addr = interface.IPAddress[0]
                current_default_gw = interface.DefaultIPGateway[0]
                current_networkmask = interface.IPSubnet[0]
                current_dns1 = interface.DNSServerSearchOrder[0]
                current_dns2 = interface.DNSServerSearchOrder[1]
                if ipv4_addr == current_ipv4_addr and default_gw == current_default_gw and networkmask == current_networkmask and dns1 == current_dns1 and dns2 == current_dns2:
                    cdata_info("获取到的IP信息与配置的一致")
                    cdata_info("=======================================")
                    cdata_info("当前的IP地址信息")
                    cdata_info("=======================================")
                    cdata_info('当前的网卡名称为     ：%s' % (Network_car_name))
                    cdata_info('PC获取到的IP地址为   ：%s' % (ipv4_addr))
                    cdata_info('PC获取到的网关地址为 ：%s' % (default_gw))
                    cdata_info('PC获取到的子网掩码为 ：%s' % (networkmask))
                    cdata_info('PC获取到的主DNS为    ：%s' % (current_dns1))
                    cdata_info('PC获取到的备DNS为    ：%s' % (current_dns2))
                    return True
                else:
                    cdata_error("获取到的IP信息与配置的不一致")
                    return False
            else:
                cdata_error("无法获取到电脑当前网卡的IP地址")
        else:
            cdata_error('当前网卡不存在，请检查网卡配置')
            return False
    except:
        return False

    # 修改PC上网的方式为DHCP


# 将电脑的上网方式从静态IP修改成DHCP
def static_turn_to_dhcp(Network_car_name):
    try:
        c = wmi.WMI()

        # 修改PC的上网方式为DHCP
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if Network_car_name in interface.Caption:
                time.sleep(1)
                returnValues1 = interface.EnableDHCP()
                time.sleep(1)
                returnValues2 = interface.SetDNSServerSearchOrder()
                if returnValues1[0] == 0 and returnValues2[0] == 0:
                    cdata_info("DHCP和DNS修改成为自动获取成功")
                    break
                else:
                    cdata_error("DHCP和DNS修改成为自动获取失败")
                    return False
        else:
            cdata_error('当前网卡不存在，请检查网卡配置')
            return False

        time.sleep(1)

        # 重新获取IP地址
        os.system("ipconfig/release")
        time.sleep(1)
        os.system("ipconfig/renew")

        # 读取当前网卡的IPv4地址信息
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if Network_car_name in interface.Caption:
                ipv4_addr = interface.IPAddress[0]
                default_gw = interface.DefaultIPGateway[0]
                networkmask = interface.IPSubnet[0]
                dns1 = interface.DNSServerSearchOrder[0]
                dns2 = interface.DNSServerSearchOrder[1]
                cdata_info("=======================================")
                cdata_info("当前的IP地址信息")
                cdata_info("=======================================")
                cdata_info('当前的网卡名称为     ：%s' % (Network_car_name))
                cdata_info('PC获取到的IP地址为   ：%s' % (ipv4_addr))
                cdata_info('PC获取到的网关地址为 ：%s' % (default_gw))
                cdata_info('PC获取到的子网掩码为 ：%s' % (networkmask))
                cdata_info('PC获取到的主DNS为    ：%s' % (dns1))
                cdata_info('PC获取到的备DNS为    ：%s' % (dns2))
                return True
        else:
            cdata_error('当前网卡不存在，请检查网卡配置')
            return False
    except:
        return False


# 配置电脑的上网方式为PPPoE拨号
def pppoe_connect(pppoe_client, pppoe_name, pppoe_password):
    # 判断当前是否已经成功拨号
    if pppoe_client in psutil.net_if_addrs():
        cdata_info("当前已经成功拨号，程序会先帮您断开连接后再进行拨号")
        pppoe_disconnect(pppoe_client)

    # 开始拨号
    cmd_str = "rasdial %s %s %s" % (pppoe_client, pppoe_name, pppoe_password)
    res = os.system(cmd_str)
    if res == 0:
        cdata_info("=======================================")
        cdata_info("拨号成功")
        cdata_info('当前拨号成功后获取到的IP地址为：%s' % (psutil.net_if_addrs()['宽带连接'][0].address))
        cdata_info("=======================================")
        return True
    else:
        cdata_info("=======================================")
        cdata_error("拨号失败")
        cdata_info("=======================================")
        return False


# 断开PPPoE拨号
def pppoe_disconnect(pppoe_client):
    # 判断当前是否拨号成功
    if pppoe_client in psutil.net_if_addrs():

        # 执行断开拨号操作
        cmd_str = "rasdial %s /disconnect" % (pppoe_client)
        res = os.system(cmd_str)
        if res == 0:
            cdata_info("=======================================")
            cdata_info("拨号断开成功")
            cdata_info("=======================================")
            return True
        else:
            cdata_info("=======================================")
            cdata_error("拨号断开失败")
            cdata_info("=======================================")
            return False
    else:
        print("=======================================")
        cdata_error("当前未拨号，无需断开连接。")
        print("=======================================")


# if __name__ == '__main__':
#     speedtest_test()

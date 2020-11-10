#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI


import xlrd
import os
import sys
import json


# 获取当前目录路径
curent_path = os.path.abspath('.')
# update_file = ''
# updatefile_path = os.path.join(curent_path,update_file)

#pc放置文件的路径
dir_pc = 'E:\Cdata_part11_my20201029'
#jenkins创建任务的名称
work_name = 'GPON_SFU_FD1616GS_1'

# 清除data目录下的升级文件
dir_data = os.path.join(dir_pc,'data')
# print(dir_data)
os.chdir(dir_data)
os.system('del .\*.bin  .\*.tar')
os.chdir(curent_path)
# 从个人文件夹中把升级文件复制到data目录下
os.system('copy .\*.bin  %s'%dir_data)
os.system('copy .\*.tar  %s'%dir_data)
test_case_list = []
test_case_id = []
command = ''
# 打开文件夹
filename = sys.argv[1]
data = xlrd.open_workbook(filename)
# data = xlrd.open_workbook('E:\\CDATA\\自动化测试\\Cdata_part11\\execute\\EPON_SFU_FD1216S\\自动化测试用例.xlsx')

# 查看工作表
data.sheet_names()

#获取变量的表格
table  = data.sheet_by_name('Parameters')
#获取对接测试的onu类型
olt_types = table.row_values(2)[3]


#从变量表格中获取所有的参数
vars = []
for rowNum in range(1, table.nrows):
    if rowNum == 1 :
        vars.append(table.row_values(rowNum)[2] + " = " + (table.row_values(rowNum)[3]) + "\n")
        # print(1,(table.row_values(rowNum)[3]))
    elif isinstance(table.row_values(rowNum)[3], float):
        vars.append(table.row_values(rowNum)[2] + " = " + '"' + str(int(table.row_values(rowNum)[3])) + '"' + "\n")
        # print(2, (table.row_values(rowNum)[3]))
    else:
        vars.append(table.row_values(rowNum)[2] + " = " + '"' + str(table.row_values(rowNum)[3]) + '"' + "\n")
        # print(3, (table.row_values(rowNum)[3]))

#将变量写入初始配置文件中
file_initconfig = os.path.join(dir_pc,'tests\\FD1616GS\\initialization_config.py')
# f = open(file_initconfig, "w",encoding='utf-8')
# f.writelines(vars)
# f.close()
# if not os.path.exists(file_initconfig):
#     os
# mode = 'a' if os.path.exists(file_initconfig) else 'w'
with open(file_initconfig, 'w',encoding='utf-8') as f:
    f.writelines(vars)

print('对接测试的olt:%s'%olt_types.split(','))

# 通过文件名获得工作表,获取工作表1
for i in range(len(olt_types.split(','))):
    olt_type=(olt_types.split(',')[i])
    table = data.sheet_by_name(olt_type)
    # 读取需要执行的用例
    for rowNum in range(table.nrows):
        if table.row_values(rowNum)[3] == '是':
            script = olt_type+'//'+(table.row_values(rowNum)[2])
            test_case_list.append(script)
            test_case_id.append(int(table.row_values(rowNum)[0]))

# 输出需要执行用例的数量
print('执行的用例数量为%s个' % (len(test_case_list)))

# 生成pytest的命令行
for case_name in test_case_list:
    command = command + case_name + ' '

# 进入测试用例的目录
dir_test = os.path.join(dir_pc,'tests')
#os.chdir('E:\\CDATA\\自动化测试\\Cdata_part11\\tests')
os.chdir(dir_test)

dir_allure = os.path.join(os.path.join(os.path.join(dir_pc,'tests\\workspace'),work_name),'allure-results')
#pytest_command = 'pytest  '+ command + ' -s  --alluredir ' 'E:\\CDATA\\自动化测试\\Cdata_part11\\tests\\workspace\\EPON_SFU_FD1216S\\allure-results'
pytest_command = 'pytest  '+ command + ' -s  --alluredir  '+dir_allure
os.system(pytest_command)

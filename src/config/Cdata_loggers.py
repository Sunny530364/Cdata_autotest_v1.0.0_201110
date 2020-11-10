#!/usr/bin/python
# -*- coding UTF-8 -*-

#author: ZHONGQI


import logging
import enum
import os,sys
import datetime

# print(sys.argv[0])
# print(os.path.abspath(sys.argv[0]))

logger = None

class LogHandle(enum.Enum):
    LOG_FILE = 0
    LOG_CONSOLE = 1
    LOG_FILE_AND_CONSOLE = 2

def initialize(log=True, log_level=logging.INFO, log_handle=LogHandle.LOG_FILE_AND_CONSOLE):
    """
    Do some initialization work,such as initialize log file and connect to CL
    :param log: record renix api logs to file if log is True
    :param log_level: log level ,info by default
    :param log_handle: write log to file or console, or both
    :param host: the ip address of CL is running
    :param port: the listen port connected to CL
    :param timeout: the time waiting for connect CL successfully
    :return: the time waiting for connect CL successfully
    """
    print('CDATA Test Begin')
    # try:
    if log:
        init_log(log_level, log_handle)

    # except Exception as err:
    #     # test_error(traceback.format_exc())
    #     raise "初始化失败"

def init_log(log_level, log_handle):
    """
    crate log file and set log level
    :param log_level:
    :param log_handle:
    :return:
    """
    log_fmt = logging.Formatter("[%(levelname)s] %(asctime)s  %(message)s")
    # current_path = 'c:\\renix_py_api'
    # current_file_name = 'script'
    # create logs in user script folder, sys.argv[0] is the script path
    # script_path = os.path.abspath(sys.argv[0])
    current_path = 'c:\\CDATA_AUTOTEST_LOG'
    current_file_name = "Test"
    # script_path = (os.path.abspath(__file__))
    #当前文件的绝对路径
    script_path = os.path.abspath(sys.argv[0])

    if os.path.isfile(script_path):
        current_path, current_file_name_ext = os.path.split(script_path)
        current_file_name, extention_name = current_file_name_ext.split('.')
        print(current_file_name)
    global logger
    #创建日志器
    logger = logging.getLogger( "CDATA")
    #设置日志等级
    logger.setLevel(log_level)

    if log_handle == LogHandle.LOG_FILE or log_handle == LogHandle.LOG_FILE_AND_CONSOLE:
        log_folder_path = os.path.join(current_path, "logs")
        #如果不存在logs文件夹，则在当前目录下创建logs文件夹
        if not os.path.exists(log_folder_path):
            os.makedirs(log_folder_path)

        #log的文件名称
        file_name = "%s_%s_%s.log" % ('Cdata',current_file_name, datetime.datetime.now().strftime('%b_%d_%y_%H_%M_%S'))
        log_file_path = os.path.join(log_folder_path, file_name)
        print('log path: {}'.format(log_file_path))

        # log_file_handler = logging.handlers.RotatingFileHandler(log_file_path,
        #                                                         maxBytes=10 * 1024 * 1024,
        #                                                         backupCount=5)
        # log_file_handler.setLevel(log_level)
        log_file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        log_file_handler.setLevel(log_level)
        log_file_handler.setFormatter(log_fmt)
        logger.addHandler(log_file_handler)

    if log_handle == LogHandle.LOG_CONSOLE or log_handle == LogHandle.LOG_FILE_AND_CONSOLE:
        control_handler = logging.StreamHandler()
        control_handler.setFormatter(log_fmt)

        logger.addHandler(control_handler)

def cdata_error(message):
    if logger:
        logger.error(message)

def cdata_warn(message):
    if logger:
        logger.warning(message)

def cdata_info(message):
    if logger:
        logger.info(message)

def cdata_debug(message):
    if logger:
        logger.debug(message)

initialize(log_level=logging.DEBUG)

# cdata_warn("debug")

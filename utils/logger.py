# -*- coding: utf-8 -*-
import logging
import os.path
import time

logpath = os.path.dirname(os.path.abspath('.')) + '/log/'


class Logger(object):
    def __init__(self, logger=None):
        '''''
            指定保存日志的文件路径，日志级别，以及调用文件
            将日志存入到指定的文件中
        '''
        # 创建一个logger

        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # 为了避免日志 handlers 重复的问题，先检测 handlers 是否存在。若不创建一个handler，用于写入日志文件
            rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
            log_name = logpath + rq + '.log'

            fh = logging.FileHandler(log_name)
            fh.setLevel(logging.INFO)

        # 再创建一个handler，用于输出到控制台
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)

        # 定义handler的输出格式
            formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)

        # 给logger添加handler
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)


    def getlog(self):
        return self.logger

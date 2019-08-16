# -*- coding: utf-8 -*-
import unittest
from HTMLTestRunnerCN import HTMLTestReportCN
import os
import time
from testsuites.keys import test_flag_required_memo
from testsuites.issue import test_issue_create

# 定义输出的文件位置和名字
report_path = os.path.dirname(os.path.abspath('.')) + '/report/'
now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
HtmlFile = report_path + now + "report.html"
fp = open(HtmlFile, "wb")


def run_all():
    suite = unittest.TestLoader().discover("testsuites")
    return suite


def run_case(class_name, case_name):

    suite = unittest.TestSuite()

    if class_name.strip() == "test_flag_required_memo":
        suite.addTest(test_flag_required_memo.FlagRequiredTest(case_name))
        return suite

    if class_name.strip() == "test_issue_create":
        suite.addTest(test_issue_create.CreateIssueTest(case_name))
        return suite

def run_suite(module):
    suite = unittest.TestLoader().loadTestsFromModule(module)
    return suite


if __name__ == '__main__':
    suite = run_case("test_issue_create", "test_normal_01")
    runner = HTMLTestReportCN(stream=fp, title=u'测试报告', description=u'执行情况', tester=u'zhaoyi')
    runner.run(suite)

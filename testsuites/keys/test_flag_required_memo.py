# -*- coding: utf-8 -*-

import unittest
import time
from node import selfcheck
from client import common
from utils import logger
from client import keyapi

log = logger.Logger().getlog()
com = common.ClientCommmon()
check = selfcheck.SelfCheck(netname="testnet")
api = keyapi.KeysApi()


class FlagRequiredTest(unittest.TestCase):
    """ 设置 memo 测试套件 """
    net = None
    walletname = "memotest"

    @classmethod
    def setUpClass(cls):
        network, latest_height = check.rest_environment()
        cls.net = network
        check.init_local_testnet(chainid=network, monkier='wind')
        com.wait_network_status()
        com.wait_network_height(5)

    def setUp(self):
        log.info("===============用例开始运行===============")

    def tearDown(self):
        com.delete_account(self.walletname)
        status = check.start_until_synchronization_node()
        self.assertTrue(status)
        log.info("===============用例运行结束===============")

    def test_normal_01(self):
        """设置memo为true，转账失败 """
        address, memo_result = api.newaccount_memo(self.walletname, 'true')
        result = com.transfer(from_account="wind", to_address=address, amount="10gard")
        self.assertIn("Memo is required to transfer to address " + address, result)

    def test_normal_02(self):
        """将memo 改为 false 成功转账 """
        address, memo_result = api.newaccount_memo(self.walletname, 'true')
        result = com.transfer(from_account="wind", to_address=address, amount="10gard")
        self.assertIn("Memo is required to transfer to address " + address, result)
        com.must_memo('false', self.walletname)
        result = com.transfer(from_account="wind", to_address=address, amount="10gard")
        self.assertIn("success", result)

    def test_normal_03(self):
        """memo 限制入，不限制转出 """
        address, memo_result = api.newaccount_memo(self.walletname, 'true')
        test_address, memo_result = api.newaccount_memo("03", 'true')
        result = com.transfer(from_account=self.walletname, to_address=test_address, amount="10gard")
        self.assertIn("success", result)
        com.delete_account("03")

    def test_normal_04(self):
        """查询地址设置了 memo"""
        address, memo_result = api.newaccount_memo(self.walletname, 'true')
        result = api.flag_required_query_memo(address)
        self.assertTrue(result)

    def test_normal_05(self):
        """查询地址未设置 memo"""
        address, memo_result = api.newaccount_memo(self.walletname, 'false')
        result = api.flag_required_query_memo(address)
        self.assertFalse(result)

    def test_abnormal_06(self):
        """无效的传入参数 """
        address, memo_result = api.newaccount_memo(self.walletname, '111111111111111111', normal="abnormal")
        self.assertIn("invalid syntax", memo_result)
        result = com.transfer(from_account="wind", to_address=address, amount="10gard")
        self.assertIn("success", result)

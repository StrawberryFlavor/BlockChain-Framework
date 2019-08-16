# -*- coding: utf-8 -*-

import unittest
import time
import json
from node import selfcheck
from client import common
from utils import logger
from client import issueapi

log = logger.Logger().getlog()
com = common.ClientCommmon()
check = selfcheck.SelfCheck(netname="testnet")
api = issueapi.IssueApi()


class CreateIssueTest(unittest.TestCase):
    """ 创建 issue 测试套件"""
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
        """ 正常创建 issue """
        address, pubkey = com.add_account(self.walletname)
        com.faucet_send(address)
        issue_id = api.create_issue('test', "WIND", "1000000", "18", self.walletname)
        result = api.issue_query(issue_id)
        owner = json.loads(result)['value']['owner']
        self.assertEqual(address, owner)

    def test_normal_02(self):
        """ 创建两个同名的 issue """
        address, pubkey = com.add_account(self.walletname)
        com.faucet_send(address)
        issue_id = api.create_issue('test', "WIND", "1000000", "18", self.walletname)
        result = api.issue_query(issue_id)
        owner = json.loads(result)['value']['owner']
        self.assertEqual(address, owner)
        issue_id = api.create_issue('test', "WIND", "1000000", "18", self.walletname)
        result = api.issue_query(issue_id)
        owner = json.loads(result)['value']['owner']
        self.assertEqual(address, owner)


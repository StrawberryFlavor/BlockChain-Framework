import unittest
import time
from tools import selfcheck
from client import common
from utils import logger
from testsuites.keys import keyapi

log = logger.Logger().getlog()
com = common.ClientCommmon()
check = selfcheck.SelfCheck(netname="testnet")
api = keyapi.KeysApi()


class FlagRequiredTest(unittest.TestCase):
    net = None

    def setUp(self):
        network, latest_height = check.rest_environment()
        self.net = network
        check.init_local_testnet(chainid=network, monkier='wind')
        while com.network_status():
            time.sleep(10)
            log.info("等待同步中")

    def tearDown(self):
        com.delete_account("test")
        status = check.start_until_synchronization_node()
        self.assertEqual(True, status)

    def test_normal_01(self):
        address = api.newaccount_memo('test', 'true')
        result = com.transfer(from_account="wind", to_address=address, amount="10gard")
        self.assertIn("Memo is required to transfer to address " + address, result)

# -*- coding: utf-8 -*-

from client import common
import time

com = common.ClientCommmon()


class KeysApi(object):

    def newaccount_memo(self, account_name, true_false):
        (address, pubkey) = com.add_account(account_name)
        result = com.faucet_send(address)
        if "Internal error: Timed out waiting for tx to be included in a block " in result:
            time.sleep(10)
            com.faucet_send(address)
        com.must_memo(true_false, account_name)
        return address


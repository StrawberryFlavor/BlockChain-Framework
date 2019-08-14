# -*- coding: utf-8 -*-

from client import common
import time
import json
from utils import logger
import os

com = common.ClientCommmon()

log = logger.Logger().getlog()
config_json = os.path.dirname(os.path.abspath('.')) + '/utils/config.json'
f = open(config_json)
config = json.loads(f.read())
cli_local_path = config['localpath']

class KeysApi(object):

    def newaccount_memo(self, account_name, true_false, normal="normal"):
        (address, pubkey) = com.add_account(account_name)
        com.faucet_send(address)
        # if "Internal error: Timed out waiting for tx to be included in a block ".strip() in result:
        #     time.sleep(10)
        memo_result = com.must_memo(true_false, account_name, normal=normal)
        return address, memo_result

    def flag_required_query_memo(self, address, normal="normal"):
        get_address_memo = cli_local_path + "hashgardcli keys flag-required-query memo " + address
        result = com.subcommand(get_address_memo)
        if normal == "normal":
            result_json = json.loads(result)
            return result_json['memo_required']
        return result
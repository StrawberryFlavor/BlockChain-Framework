# -*- coding: utf-8 -*-
import datetime
from client import common
import time
import json
from utils import logger, command
import os

com = common.ClientCommmon()
log = logger.Logger().getlog()
config_json = os.path.dirname(os.path.abspath('.')) + '/utils/config.json'
f = open(config_json)
config = json.loads(f.read())
cli_local_path = config['localpath']


class IssueApi(object):
    def create_issue(self, name, symbol, total_supply, decimals, from_account, normal="normal"):
        """
        创建 issue
        :param name:
        :param symbol:
        :param total_supply:
        :param from_account:
        :param normal:
        :return:
        """
        issue_create_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli issue create " + name + " " + symbol + " " + total_supply + " --decimals " + decimals + " --from " + from_account + " -y"
        result = command.subcommand(issue_create_cmd)
        com.wait_network_height()
        if normal == "normal":
            result_json = json.loads(result)
            tx = result_json['txhash']
            log.info("交易成功，txhash为 %s" % tx)
            for item in result_json['tags']:
                if item['key'] == "issue-id":
                    issue_id = item['value']
                    log.info("创建的 issue id 为 %s" % issue_id)
                    return issue_id
        log.info("交易失败")
        return result

    def issue_mint(self, issue_id, amount, to_address, from_account, normal="normal"):
        """
        issue 增发
        :param issue_id:
        :param amount:
        :param to_address:
        :param from_account:
        :param normal:
        :return:
        """
        issue_mint_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli issue mint " + issue_id + " " + amount + " --to " + to_address + " --from " + from_account + " -y"
        result = com.is_normal(issue_mint_cmd, normal=normal)
        com.wait_network_height()
        return result

    def issue_transfer_ownership(self, issue_id, to_address, from_account, normal="normal"):
        """
        issue 转移owner权限
        :param issue_id:
        :param to_address:
        :param from_account:
        :param normal:
        :return:
        """
        issue_transfer_ownership_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli issue transfer-ownership " + issue_id + " " + to_address + " --from " + from_account + " -y"
        result = com.is_normal(issue_transfer_ownership_cmd, normal=normal)
        com.wait_network_height()
        return result

    def issue_freeze(self, freeze_type, issue_id, acc_address, end_time, from_account, normal="normal"):
        """
        issue 冻结
        :param freeze_type:
        :param issue_id:
        :param acc_address:
        :param end_time:
        :param from_account:
        :param normal:
        :return:
        """
        issue_freeze_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli issue freeze " + freeze_type  + " " + issue_id + " " + acc_address + " " + end_time + " --from " + from_account + " -y"
        result = com.is_normal(issue_freeze_cmd, normal=normal)
        com.wait_network_height()
        return result

    def issue_unfreeze(self,freeze_type, issue_id, acc_address, from_account, normal="normal"):
        """
        issue 解冻
        :param freeze_type:
        :param issue_id:
        :param acc_address:
        :param from_account:
        :param normal:
        :return:
        """
        issue_unfreeze_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli issue unfreeze " + freeze_type + " " + issue_id + " " + acc_address + " --from " + from_account + " -y"
        result = com.is_normal(issue_unfreeze_cmd, normal)
        com.wait_network_height()
        return result

    def issue_burn(self, issue_id, amount, from_account,normal="normal"):
        """
        持有者销毁自身持有的代币
        :param issue_id:
        :param amount:
        :param from_account:
        :param normal:
        :return:
        """
        issue_burn_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli issue burn " + issue_id + " " + amount + " --from " + from_account + " -y"
        result = com.is_normal(issue_burn_cmd, normal)
        com.wait_network_height()
        return result

    def issue_burn_from(self, issue_id, from_address, amount, from_account, normal="normal"):
        issue_burn_from_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli issue burn-from " + issue_id + " " + from_address + " " + amount + " --from " + from_account + " -y"

        result = com.is_normal(issue_burn_from_cmd, normal)
        com.wait_network_height()
        return result

    def issue_disable(self, issue_id, feature, from_account, normal="normal"):
        """
        对代币的高级功能进行关闭，且该关闭不可逆
        :param issue_id:
        :param feature:
        :param from_account:
        :param normal:
        :return:
        """
        issue_disable_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli issue disable " + issue_id + " " + feature + " --from " + from_account + " -y"

        result = com.is_normal(issue_disable_cmd, normal)
        com.wait_network_height()
        return result

    def issue_describe(self,issue_id, description_json_path, from_account,  normal="normal"):
        issue_describe_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli issue describe " + issue_id + " " + description_json_path + " --from " + from_account + " -y"

        result = com.is_normal(issue_describe_cmd, normal)
        com.wait_network_height()
        return result

    def issue_query(self, issue_id):
        issue_query_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli issue query " + issue_id
        result = command.subcommand(issue_query_cmd)
        return result

    def issue_search(self, symbol):
        issue_search_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli issue search " + symbol
        result = command.subcommand(issue_search_cmd)
        return result

# -*- coding: utf-8 -*-
from utils import logger
import os
import json
import time
from utils import command

log = logger.Logger().getlog()
config_json = os.path.dirname(os.path.abspath('.')) + '/utils/config.json'
f = open(config_json)
config = json.loads(f.read())
cli_local_path = config['localpath']


class ClientCommmon(object):

    def add_account(self, name="test"):
        """
        添加账户
        :param name:
        :return:
        """
        try:
            keys_add = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli keys add " + name
            log.info("创建地址 %s" % name)
            result = command.subcommand(keys_add)
            result_json = json.loads(result)
            address = result_json['address']
            pubkey = result_json['pubkey']
            log.info("创建完成，地址为 %s" % address)
            self.wait_network_height()
            return address, pubkey
        except Exception as e:
            log.info(e)

    def delete_account(self, name):
        """
        删除账户
        :param name:
        :return:
        """
        try:
            keys_delete = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli keys delete " + name
            log.info("删除地址 %s" % name)
            result = command.subcommand(keys_delete)
            if "Key deleted forever" in result:
                log.info("删除成功")
            self.wait_network_height()
        except Exception as e:
            log.info(e)

    def transfer(self, from_account, to_address, amount):
        """
        转账
        :return:
        """
        log.info("本地 %s 账户转账 %s 到 %s地址" % (from_account, amount, to_address))
        send = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli bank send " + to_address + " " + amount + " --from " + from_account + " -y"
        result = command.subcommand(send)
        self.wait_network_height()
        return result

    def faucet_send(self, address):
        """
        领取水龙头代币
        :param address:
        :return:
        """
        faucet_send = cli_local_path + "hashgardcli faucet send " + address
        log.info("%s 地址领取水龙头" % address)
        result = command.subcommand(faucet_send)
        self.wait_network_height()
        return result

    def create_validator(self, from_account, amount, moniker, normal="normal"):
        """
        创建验证人
        :param from_account:
        :param amount:
        :param moniker:
        :return:
        """
        show_tendermint_validator = cli_local_path + "hashgard tendermint show-validator"
        validator_pubkey = self.subcommand(show_tendermint_validator).strip()
        log.info("节点的pubkey为 %s" % validator_pubkey)
        create_validator_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli stake create-validator " + " --pubkey " + validator_pubkey + " --commission-max-change-rate=0.01  --commission-rate=0.1  --commission-max-rate=0.2 --amount=" + amount + " --moniker=" + moniker + " --min-self-delegation=10  --fees=2gard " + "--from " + from_account + " -y"
        result = command.subcommand(create_validator_cmd)
        self.wait_network_height()
        if normal == "normal":
            result_json = json.loads(result)
            txhash = result_json['txhash']
            log.info("交易hash为 %s" % txhash)
            for items in result_json['tags']:
                if items['key'] == "destination-validator":
                    validator_address = items['value']
                    log.info("创建验证人地址为 %s" % validator_address)
                    return validator_address, txhash
        else:
            return result

    def wait_network_status(self):
        # 等待区块同步完成
        result_json = self.network_status()
        status = result_json['sync_info']['catching_up']
        # 如果为真
        while str(status) == "true":
            time.sleep(10)
            if str(self.network_status()['sync_info']['catching_up']) == "false":
                break
            log.info("当前正在同步，请等待区块同步完成")
        log.info("当前已经同步完成")

    def wait_network_height(self, num=1):
        result_json = self.network_status()
        latest_height = result_json['sync_info']['latest_block_height']
        wait_height = int(latest_height) + int(num)
        log.info("需要等待高度到 %s" % str(wait_height))
        while True:
            now_height = self.network_status()['sync_info']['latest_block_height']
            if int(now_height) >= int(wait_height):
                log.info("当前已经等待到 %s 高度" % str(wait_height))
                break
            log.info("当前高度 %s 还未达到指定高度 %s，请等待" % (str(now_height), str(wait_height)))
            time.sleep(5)

    def network_status(self):
        """
        查看当前同步状态，若未同步完，返回true，同步完，返回false
        :return:
        """
        cli_status = cli_local_path + "hashgardcli status"
        result = command.subcommand(cli_status)
        result_json = json.loads(result)
        return result_json

    def delegate(self, validator_address, amount, from_account):
        """
        委托给验证人
        :param validator_address:
        :param amount:
        :param from_account:
        :return:
        """
        delegate_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli stake delegate " + validator_address + " " + amount + " --from " + from_account + " -y"
        result = command.subcommand(delegate_cmd)
        result_json = json.loads(result)
        txhash = result_json['txhash']
        log.info("抵押到验证人地址 %s 成功，交易hash为 %s" % (validator_address, txhash))
        self.wait_network_height()
        return txhash

    def unbond(self, validator_address, amount, from_account):
        """
        对指定的验证人节点解绑委托
        :param validator_address:
        :param amount:
        :param from_account:
        :return:
        """
        unbond_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli stake unbond " + validator_address + " " + amount + " --from " + from_account + " -y"
        result = command.subcommand(unbond_cmd)
        result_json = json.loads(result)
        txhash = result_json['txhash']
        log.info("对验证人地址 %s 解绑，交易hash为 %s" % (validator_address, txhash))
        self.wait_network_height()
        return txhash

    def redelegate(self, src_validator_address, dst_validator_address, amount, from_account):
        """
        转移委托
        :param src_validator_address:
        :param dst_validator_address:
        :param amount:
        :param from_account:
        :return:
        """
        redelegate_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli stake redelegate " + src_validator_address + " " + dst_validator_address + " " + amount + " --from " + from_account + " -y"
        result = command.subcommand(redelegate_cmd)
        result_json = json.loads(result)
        txhash = result_json['txhash']
        log.info("从验证人 %s 转移 %s 委托至验证人地址 %s 解绑，交易hash为 %s" % (src_validator_address, amount, dst_validator_address, txhash))
        self.wait_network_height()
        return txhash

    def get_balances(self, address, coin=None):
        """
        查询指定地址的余额
        :param address:
        :param coin:
        :return:
        """
        balances_cmd = cli_local_path + "hashgardcli bank account " + address
        result = command.subcommand(balances_cmd)
        result_json = json.loads(result)
        if coin != None:
            for item in result_json['value']['coins']:
                if item['denom'] == coin:
                    amount = item['amount']
                    log.info("该{address}地址中，存在 {amount}个{coin}".format(address=address, amount=amount, coin=coin))
        return result_json

    def keys_list(self):
        """
        查询本地地址列表
        :return:
        """
        keys_list_cmd = cli_local_path + "hashgardcli keys list"
        result = command.subcommand(keys_list_cmd)
        result_json = json.loads(result)
        return result_json

    def must_memo(self, true_or_false, from_account, normal="normal"):
        must_memo_cmd = "echo " + config['walletpassword'] + "|" + cli_local_path + "hashgardcli keys flag-required memo " + true_or_false + " --from " + from_account + " -y"
        result = command.subcommand(must_memo_cmd)

        self.wait_network_height()

        if normal == "normal":
            result_json = json.loads(result)
            txhash = result_json['txhash']
            log.info("设置成功，交易hash为 %s" % txhash)
            for item in result_json['tags']:
                if item['key'] == "sender":
                    sender = item['value']
                    log.info("%s 地址对其转账时，必须加入备注" % sender)
            return result
        return result

    def remove_keys(self):
        rm_rf = "rm -rf " + config['defaultpath'] + '.hashgardcli/keys/' + "\n"
        log.info('清空本地所有账户')
        command.ossystem(rm_rf)

    def is_normal(self, command, normal):
        result = command.subcommand(command)
        if normal == "normal":
            result_json = json.loads(result)
            tx = result_json['txhash']
            log.info("交易成功，txhash为 %s" % tx)
            return result
        log.info("交易失败")
        return result


if __name__ == "__main__":
    common = ClientCommmon()

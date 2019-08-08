# -*- coding: utf-8 -*-
from utils import sshoperation
from utils import logger
from utils import getmd5
import os
import json
import time

log = logger.Logger().getlog()
keypath = os.path.dirname(os.path.abspath(".")) + "/ShellResources/sshkey/id_rsa_github"
config_json = os.path.dirname(os.path.abspath('.')) + '/utils/config.json'
f = open(config_json)
config = json.loads(f.read())


class SelfCheck(object):
    """
    自检代码，控制dev或者线上的节点运行
    """

    # 先指定环境,默认为dev
    def __init__(self, netname="testnet"):
        self.net = netname

    def cmd(self, host, port, username):
        ssh = sshoperation.SSHConnection(host=host, port=port, username=username)
        return ssh

    def stop_node(self, node_name="local"):
        # 停止单个节点
        log.info("停止节点 %s" % node_name)
        if node_name != "local":
            log.info("启动本地节点")
            ssh = self.cmd(host=config[self.net][node_name]['ip'], port=config[self.net][node_name]['port'],
                           username="root")
            ssh.exec_command("pkill hashgard")
        os.system("pkill hashgard" + "\n")

    def stop_nodes(self):
        # 停止所有节点
        for node in config[self.net]:
            log.info("停止节点 %s" % node)
            ssh = self.cmd(host=config[self.net][node]['ip'], port=config[self.net][node]['port'], username="root")
            ssh.exec_command("pkill hashgard")

    def start_node(self, node_name="local"):
        # 开始单个节点
        log.info("启动节点 %s" % node_name)
        if node_name != "local":
            log.info("启动本地节点")
            ssh = self.cmd(host=config[self.net][node_name]['ip'], port=config[self.net][node_name]['port'],
                           username="root")
            ssh.exec_command("hashgard start >/root/hashgard/hashgard.log &")
        else:
            start_cmd = config['localpath'] + "hashgard start > /home/wind/Hashgard_Log/hashgard.log &" + "\n"
            os.system(start_cmd)

    def start_nodes(self):
        # 开始所有节点
        for node in config[self.net]:
            log.info("启动节点 %s" % node)
            ssh = self.cmd(host=config[self.net][node]['ip'], port=config[self.net][node]['port'], username="root")
            ssh.exec_command("hashgard start >/root/hashgard/hashgard.log &")

    def start_node_lcd(self, net, node_name):
        # 开始 lcd 服务
        log.info("启动 %s 节点的 lcd 服务" % node_name)
        ssh = self.cmd(host=config[self.net][node_name]['ip'], port=config[self.net][node_name]['port'],
                       username="root")
        # 关闭 先关闭lcd服务，避免冲突
        ssh.exec_command("pkill -9 hashgardlcd")
        ssh.exec_command("hashgardlcd start --chain-id=%s --laddr=tcp://0.0.0.0:1317 > /root/hashgard/lcd.log &" % net)

    def update_dev_version(self, branch="master"):
        """
        编译线上dev的版本
        :param branch:
        :return:
        """
        log.info("更新dev代码至最新版本并编译")
        ssh = self.cmd(host=config[self.net]['dev']['ip'], port=config[self.net]['dev']['port'],
                       username="root")
        if branch != "master":
            ssh.exec_command("git checkout %s" % branch)
        data = ssh.exec_command("cd /root/go/src/github.com/hashgard/hashgard;git pull origin %s" % branch)
        if data != "Already up-to-date.":
            ssh.exec_command("cd /root/go/src/github.com/hashgard/hashgard;make install")
            ssh.exec_command("cd /root/go/bin/;./hashgard version --long")
        else:
            log.info("当前处于 %s 分支，已经是最新版，无需编译" % branch)

    def check_local(self):
        """
        比对本地环境和dev编译环境下的md5是否一致
        若不一致，则拷贝下来替换
        :return:
        """
        log.info("更新本地版本至最新")
        self.update_dev_version()
        ssh = self.cmd(host=config[self.net]['dev']['ip'], port=config[self.net]['dev']['port'],
                       username="root")
        md5_remote_hashgard = ssh.exec_command("cd /root/go/bin/;md5sum hashgard").split()[0]
        md5_remote_hashgardcli = ssh.exec_command("cd /root/go/bin/;md5sum hashgardcli").split()[0]
        md5_remote_hashgardlcd = ssh.exec_command("cd /root/go/bin/;md5sum hashgardlcd").split()[0]

        hashgard_path = config['localpath'] + 'hashgard'
        hashgardcli_path = config['localpath'] + 'hashgardcli'
        hashgardlcd_path = config['localpath'] + 'hashgardlcd'

        md5_local_hashgard = getmd5.GetMd5().calc_md5_for_file(hashgard_path)
        md5_local_hashgardcli = getmd5.GetMd5().calc_md5_for_file(hashgardcli_path)
        md5_local_hashgardlcd = getmd5.GetMd5().calc_md5_for_file(hashgardlcd_path)

        if md5_local_hashgard != md5_remote_hashgard or md5_local_hashgardcli != md5_remote_hashgardcli or md5_local_hashgardlcd != md5_remote_hashgardlcd:
            os.system("pkill hashgard")
            ssh.downloaddir(remotepath="/root/go/bin/", localpath=hashgardcli_path)
        else:
            log.info("当前本地版本和 dev git环境版本一致")

    def check_remote_all(self):
        """
        将本地版本传输到相应的网络环境
        :return:
        """
        log.info("更新版本至环境 %s" % self.net)
        for node in config[self.net]:
            log.info("更新节点 %s" % node)
            ssh = self.cmd(host=config[self.net][node]['ip'], port=config[self.net][node]['port'], username="root")
            ssh.putdir(localpath=config['localpath'], remotepath='/usr/local/bin/')

    def init_local_hashgard(self, chainid, monkier):
        log.info("部署同步环境")
        kill = "pkill hashgard" + "\n"
        rm = "rm -rf " + config['defaultpath'] + ".hashgard" + "\n"
        init = config['localpath'] + "hashgard init --chain-id {net} --moniker {monkier}".format(net=chainid, monkier=monkier) + "\n"
        config_toml = "curl https://raw.githubusercontent.com/hashgard/testnets/develop/sif/{net}/config/config.toml > ".format(net=chainid) + config['defaultpath'] + ".hashgard/config/config.toml" + "\n"
        genesis = "curl https://raw.githubusercontent.com/hashgard/testnets/develop/sif/{net}/config/genesis.json > ".format(net=chainid) + config['defaultpath'] + ".hashgard/config/genesis.json" + "\n"
        cli_config_chainid = config['localpath'] + "hashgardcli config chain-id %s" % chainid + "\n"
        cli_config_trust = config['localpath'] + "hashgardcli config trust-node true" + "\n"
        cli_config_json = config['localpath'] + "hashgardcli config output json" + "\n"
        cli_config_indent = config['localpath'] + "hashgardcli config indent true" + "\n"
        init_cmd = kill + rm + init
        log.info(init_cmd)
        os.system(init_cmd)
        time.sleep(3)
        install_config = config_toml + genesis
        log.info(install_config)
        os.system(install_config)
        time.sleep(3)
        cli_config = cli_config_chainid + cli_config_trust + cli_config_json + cli_config_indent
        log.info(cli_config)
        os.system(cli_config)


if __name__ == "__main__":
    check = SelfCheck(netname="testnet")
    # check.stop_node()
    # check.check_local()
    check.init_local_hashgard("sif-7000", "wind")
    check.start_node()

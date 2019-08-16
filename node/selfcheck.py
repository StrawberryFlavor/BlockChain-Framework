# -*- coding: utf-8 -*-
from utils import sshoperation
from utils import logger
from utils import getmd5
from utils import command
import os
import json
import time

log = logger.Logger().getlog()
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


    def stop_node(self, node_name="local"):
        # 停止单个节点
        if node_name != "local":
            log.info("停止节点 %s" % node_name)
            ssh = command.sshcmd(host=config[self.net][node_name]['ip'], port=config[self.net][node_name]['port'], username="root")
            ssh.exec_command("pkill hashgard")
        log.info("停止本地节点")
        os.system("pkill hashgard" + "\n")
        time.sleep(3)

    def stop_nodes(self):
        # 停止所有节点
        for node in config[self.net]:
            log.info("停止节点 %s" % node)
            ssh = command.sshcmd(host=config[self.net][node]['ip'], port=config[self.net][node]['port'], username="root")
            ssh.exec_command("pkill hashgard")
            result = ssh.exec_command("hashgardcli status")
            if "connection refused".strip() in result:
                log.info("成功停止")
            else:
                ssh.exec_command("pkill hashgard")

    def start_node(self, node_name="local"):
        # 开始单个节点
        if node_name != "local":
            log.info("启动节点 %s" % node_name)
            ssh = command.sshcmd(host=config[self.net][node_name]['ip'], port=config[self.net][node_name]['port'],
                           username="root")
            ssh.exec_command("hashgard start >/root/hashgard/hashgard.log &")
        else:
            log.info("启动本地节点")
            start_cmd = config['localpath'] + "hashgard start > /home/wind/Hashgard_Log/hashgard.log &" + "\n"
            os.system(start_cmd)
        time.sleep(3)

    def start_nodes(self):
        # 开始所有节点
        for node in config[self.net]:
            log.info("启动节点 %s" % node)
            ssh = command.sshcmd(host=config[self.net][node]['ip'], port=config[self.net][node]['port'], username="root")
            ssh.exec_command("hashgard start >/root/hashgard/hashgard.log &")
            time.sleep(2)

    def start_node_lcd(self, net, node_name):
        # 开始 lcd 服务
        log.info("启动 %s 节点的 lcd 服务" % node_name)
        ssh = command.sshcmd(host=config[self.net][node_name]['ip'], port=config[self.net][node_name]['port'], username="root")
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
        ssh = command.sshcmd(host=config[self.net]['dev']['ip'], port=config[self.net]['dev']['port'], username="root")
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
        ssh = command.sshcmd(host=config[self.net]['dev']['ip'], port=config[self.net]['dev']['port'], username="root")
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
            ssh = command.sshcmd(host=config[self.net][node]['ip'], port=config[self.net][node]['port'], username="root")
            ssh.putdir(localpath=config['localpath'], remotepath='/usr/local/bin/')

    def init_local_sif_hashgard(self, chainid, monkier):
        """
        部署本地sif网络
        :param chainid:
        :param monkier:
        :return:
        """
        log.info("部署本地sif网络")
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
        command.ossystem(init_cmd)
        time.sleep(3)
        install_config = config_toml + genesis
        log.info(install_config)
        command.ossystem(install_config)
        time.sleep(3)
        cli_config = cli_config_chainid + cli_config_trust + cli_config_json + cli_config_indent
        log.info(cli_config)
        command.ossystem(cli_config)
        self.start_node()

    def init_local_testnet(self, chainid="test", monkier="wind"):
        log.info("部署本地测试网络")
        kill = "pkill hashgard" + "\n"
        unsafe_reset_all = "hashgard unsafe-reset-all" + "\n"
        rm = "rm -rf " + config['defaultpath'] + ".hashgard" + "\n"
        init = config['localpath'] + "hashgard init --chain-id {net} --moniker {monkier}".format(net=chainid, monkier=monkier) + "\n"

        cli_config_chainid = config['localpath'] + "hashgardcli config chain-id %s" % chainid + "\n"
        cli_config_trust = config['localpath'] + "hashgardcli config trust-node true" + "\n"
        cli_config_json = config['localpath'] + "hashgardcli config output json" + "\n"
        cli_config_indent = config['localpath'] + "hashgardcli config indent true" + "\n"

        init_cmd = kill + unsafe_reset_all + rm + init
        log.info(init_cmd)
        command.ossystem(init_cmd)

        time.sleep(3)
        ssh = command.sshcmd(host=config[self.net]['dev']['ip'], port=config[self.net]['dev']['port'], username="root")
        ssh.downloadfile(localpath=config['defaultpath'] + ".hashgard/config/config.toml", remotepath=config['configpath'] + "config.toml")
        ssh.downloadfile(localpath=config['defaultpath'] + ".hashgard/config/genesis.json", remotepath=config['configpath'] + "genesis.json")

        time.sleep(3)
        cli_config = cli_config_chainid + cli_config_trust + cli_config_json + cli_config_indent
        log.info(cli_config)
        command.ossystem(cli_config)
        self.start_node()
        time.sleep(10)

    def rest_environment(self):
        """
        重置测试环境
        :return:
        """
        log.info("重置测试环境")
        # 先清空同步节点，避免数据以同步节点为准
        ssh = command.sshcmd(host=config['synchronization']['robot']['ip'], port=config['synchronization']['robot']['port'], username='root')

        ssh.exec_command("pkill hashgard")
        time.sleep(2)
        ssh.exec_command("hashgard unsafe-reset-all")

        kill_cmd = "pkill hashgard" + "\n"
        unsafe_cmd = config['localpath'] + "hashgard unsafe-reset-all" + "\n"
        log.info(kill_cmd + unsafe_cmd)
        command.ossystem(kill_cmd + unsafe_cmd)

        self.stop_nodes()

        hashgard_unsafe_rest_all = "hashgard unsafe-reset-all"
        for node in config[self.net]:
            ssh = command.sshcmd(host=config[self.net][node]['ip'], port=config[self.net][node]['port'], username="root")
            ssh.exec_command(hashgard_unsafe_rest_all)
            log.info("对 %s 节点执行重置" % config[self.net][node])

        time.sleep(5)
        # 启动所有节点
        self.start_nodes()

        ssh = command.sshcmd(host=config[self.net]['dev']['ip'], port=config[self.net]['dev']['port'], username="root")
        result = ssh.exec_command("hashgardcli status")
        result_json = json.loads(result)
        network = result_json['node_info']['network']
        latest_height = result_json['sync_info']['latest_block_height']
        time.sleep(10)
        return network, latest_height

    def start_until_synchronization_node(self):
        log.info("启动节点同步数据")
        kill_cmd = "pkill hashgard"
        hashgard_unsafe_rest_all = "hashgard unsafe-reset-all"

        ssh = command.sshcmd(host=config['synchronization']['robot']['ip'], port=config['synchronization']['robot']['port'], username="root")
        # 杀死程序
        ssh.exec_command(kill_cmd)
        # 替换版本
        ssh.putfile(localpath=config['localpath'] + "hashgard", remotepath="/usr/local/bin/hashgard")
        ssh.putfile(localpath=config['localpath'] + "hashgardcli", remotepath="/usr/local/bin/hashgardcli")

        ssh.exec_command(hashgard_unsafe_rest_all)

        time.sleep(3)
        # 重置环境
        ssh.exec_command("hashgard start > /root/hashgard/hashgard.log &")

        time.sleep(5)

        status_cmd = "hashgardcli status"

        while True:
            if str(json.loads(ssh.exec_command(status_cmd))['sync_info']['catching_up']) == "False":
                break
            else:
                log.info("当前还未同步完成，请等待")
                time.sleep(10)
        log.info("当前已经同步完成")

        now_height = int(json.loads(ssh.exec_command(status_cmd))['sync_info']['latest_block_height'])
        time.sleep(10)
        next_height = now_height + 1
        if int(json.loads(ssh.exec_command(status_cmd))['sync_info']['latest_block_height']) >= int(next_height):
            status = ssh.exec_command('ps -ef|grep hashgard  |grep -v "grep"|wc -l')
            if status == 0:
                log.info("程序中断")
                return False
            else:
                log.info("程序运行正常")
                return True
        else:
            log.info("超过10秒都未增加高度")
            return False


if __name__ == "__main__":
    check = SelfCheck(netname="testnet")
    # network, latest_height = check.rest_environment()
    # check.init_local_testnet(chainid=network,monkier='wind')
    status = check.start_until_synchronization_node()
    print(status)


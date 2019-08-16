import subprocess
import os
from utils.logger import Logger
from utils import sshoperation

log = Logger().getlog()


def subcommand(command):

    log.info("执行命令：\n%s" % command)

    p = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    stout = p.stdout.read()

    if len(stout) > 0:
        result = stout.strip().decode()
        log.info("返回结果：\n%s" % result)
        return result

    stderr = p.stderr.read()

    if len(stderr) > 0:
        err = stderr.strip().decode()
        log.info("报错信息：\n%s" % err)
        return err


def ossystem(command):
    log.info("执行命令：\n%s" % command)
    os.system(command)


def sshcmd(host, port, username):
    ssh = sshoperation.SSHConnection(host=host, port=port, username=username)
    return ssh

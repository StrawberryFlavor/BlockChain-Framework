# -*- coding: utf-8 -*-
import paramiko
import os
from utils import logger

log = logger.Logger().getlog()


class SSHConnection(object):
    """
    由于环境上都是指定了私钥登陆，就在基础上写死了
    每次实例化都建立连接
    """

    def __init__(self, host, port, username):
        self._host = host
        self._port = port
        self._username = username
        self._transport = None
        self._sftp = None
        self._client = None
        keypath = os.path.dirname(os.path.abspath(".")) + "/tools/sshkey/id_rsa_github"
        self.privatepath = paramiko.RSAKey.from_private_key_file(keypath)
        self._connect()  # 建立连接

    def _connect(self):
        try:
            transport = paramiko.Transport((self._host, 22))
            transport.connect(username=self._username, pkey=self.privatepath)
            sftp = paramiko.SFTPClient.from_transport(transport)

            self._sftp = sftp
            self._transport = transport
            log.info("SSH 连接到服务器：%s,端口为：%s,用户名为：%s" % (self._host, self._port, self._username))
        except Exception as e:
            log.info(e)

    # 下载文件
    def downloadfile(self, remotepath, localpath):
        try:
            if self._sftp is None:
                self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._sftp.get(remotepath, localpath)
            log.info("已经将 %s 下载到 %s" % (remotepath, localpath))
        except Exception as e:
            log.info(e)

    # 下载文件夹
    def downloaddir(self, remotepath, localpath):
        try:
            if self._sftp is None:
                self._sftp = paramiko.SFTPClient.from_transport(self._transport)

            try:
                os.mkdir(localpath)
            except:
                pass

            for item in self._sftp.listdir(remotepath):
                self._sftp.get((remotepath + "/" + item), localpath + "/" + item)
                log.info("%s 文件 已经从%s 已经下载到 %s " % (item, remotepath, localpath))
        except Exception as e:
            log.info(e)

    # 上传文件
    def putfile(self, localpath, remotepath):
        try:
            if self._sftp is None:
                self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._sftp.put(localpath, remotepath)
            log.info("已经将 %s 上传到 %s" % (localpath, remotepath))
        except Exception as e:
            log.info(e)

    def putdir(self, localpath, remotepath):
        try:
            if self._sftp is None:
                self._sftp = paramiko.SFTPClient.from_transport(self._transport)

            try:
                self._sftp.mkdir(remotepath)
            except:
                pass

            for item in os.listdir(localpath):
                self._sftp.put(localpath=localpath + "/" + item, remotepath=remotepath + "/" + item)
                log.info("%s 文件 已经从%s 已经上传到 %s " % (item, localpath, remotepath))
        except Exception as e:
            log.info(e)

    # 执行命令
    def exec_command(self, command):
        try:
            if self._client is None:
                self._client = paramiko.SSHClient()
                self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self._client._transport = self._transport
            stdin, stdout, stderr = self._client.exec_command(command)
            log.info("输入命令： %s" % command)
            data = stdout.read()
            if len(data) > 0:
                log.info("返回结果：\n%s" % data.strip().decode())  # 打印正确结果
                return data.strip().decode()
            err = stderr.read()
            if len(err) > 0:
                log.info("报错信息：\n%s" % err.strip().decode())  # 输出错误结果
                return err.strip().decode()
        except Exception as e:
            log.info(e)

    def close(self):
        if self._transport:
            self._transport.close()
            log.info("文件传输服务关闭")
        if self._client:
            self._client.close()
            log.info("SSH 命令服务关闭")


if __name__ == "__main__":
    ssh = SSHConnection(host="172.16.6.9", port="22", username="root")
    ssh.exec_command("/root/go/bin/hashgard version")
    status = "status"
    ssh.exec_command("cd /root/go/src/github.com/hashgard/hashgard;git %s" % status)
    ssh.exec_command("cd /root/go/src/github.com/hashgard/hashgard;pwd")
    cd = ssh.exec_command("cd /root/go/bin/;md5sum hashgard").split()[0]
    print(cd)
    ssh.exec_command('pwd')
    ssh.close()

# @Author: Richerd
# @Create: 2023/10/18 11:03
# coding: utf-8

import yaml
import datetime
import json

import paramiko

PATH = r"test.yaml"
LOG = open("log.txt", "a+")
# EXC_CMD = "cd && cd /root/temp/  && "
EXC_CMD = "cd && cd /root/temp/chaosblade-0.6.0 && "


class SSHClient():
    def __init__(self, ip, port, username, pwd):
        self.ip = ip
        self.port = port
        self.username = username
        self.pwd = pwd

    def connect(self):
        ssh = paramiko.SSHClient()
        # 允许连接不在know_hosts文件中的主机(固定)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接服务器 参数 hostname='10.0.0.200', port=22, username='root', password='123'
        ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.pwd)
        return ssh

    def exe_cmd(self, ssh, cmd):
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30000, get_pty=True)
        result = stdout.read().decode('utf8')
        return result

    def closed(self, ssh):
        ssh.close()


def read_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
        result = yaml.load(data, Loader=yaml.FullLoader)
    return result


def write_yaml(yaml_path, data):
    with open(yaml_path, encoding="utf-8", mode="w") as f:
        yaml.dump(data, stream=f, allow_unicode=True)


def add_key(key, result_id, action):
    cmd = "./blade {} {}".format(action, result_id)
    res = read_yaml(PATH)
    val = {"command": cmd}
    res[key] = val
    write_yaml(PATH, res)
def get_cur_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def exec_cmd(key, res):
    # res = read_yaml(PATH)
    command = res[key]['command']
    if key != "安装命令":
        command = r"{}{}".format(EXC_CMD, res[key]['command'])
        print("============" + command)
    # command = r"{}{}".format(EXC_CMD, res[key]['command'])
    print("======command======" + command)
    ssh_obj = SSHClient(res['ip'], res['port'], res['username'], res['pwd'])

    try:
        ssh = ssh_obj.connect()
    except Exception as ex:
        string = "{} IP:{}, 连接服务器失败, {}\n".format(get_cur_time(), res['ip'], str(ex))
        LOG.write(string)
        return
    try:
        print("----操作类型---: " + key)
        print("----command----: ", command.split("&&")[-1])
        response = ssh_obj.exe_cmd(ssh, command)
        print("----操作返回信息------: ", response)
        if key in ["执行命令", "挂载命令", "销毁命令", "卸载命令"]:
            string = "{} IP:{}, 返回信息如下, {}\n".format(get_cur_time(), res['ip'], str(res))
            LOG.write(string)

        if key in ["执行命令", "挂载命令"]:
            result_id = json.loads(response).get("result")
            if result_id and key == "执行命令":
                add_key("销毁命令", result_id, "destroy")
            elif result_id and key == "挂载命令":
                add_key("卸载命令", result_id, "revoke")
            else:
                string = "{} IP:{}, 无法获取result_id \n".format(get_cur_time(), res['ip'])
                LOG.write(string)
    except Exception as ex:
        string = "{} IP:{}, 执行Linux命令失败，信息如下, {}\n".format(get_cur_time(), res['ip'], str(ex))
        LOG.write(string)
    finally:
        ssh_obj.closed(ssh)


if __name__ == '__main__':
    # "安装命令", "执行命令", "挂载命令", "销毁命令", "卸载命令"
    key = "执行命令"
    res = read_yaml(PATH)
    if key == "安装命令":
        exec_cmd(key, res)
    if key == "挂载命令" and "卸载命令" not in res:
        #     执行挂载命令 需要生成销毁命令key
        exec_cmd(key, res)
    elif key == "挂载命令" and "卸载命令" in res:
        print("在运行'" + key + "'前，需要将文件中的元素'卸载命令'删除，以便生成新的'卸载命令'")
        string = "{} 配置文件中存在卸载命令，请删除后在重新执行\n".format(get_cur_time())
        LOG.write(string)
    # 执行 执行命令，需要生成销毁命令key
    if key == "执行命令" and "销毁命令" not in res:
        exec_cmd(key, res)
    elif key == "执行命令" and "销毁命令" in res:
        print("在运行'" + key + "'前，需要将文件中的元素'销毁命令'删除，以便生成新的'销毁命令'")
        string = "{} 配置文件中存在销毁命令，请删除后在重新执行\n".format(get_cur_time())
        LOG.write(string)
    if key == "销毁命令" and "销毁命令" in res:
        # 执行销毁命令 需要删除销毁命令key
        exec_cmd(key, res)
        del res["销毁命令"]
    if key == "卸载命令" and "卸载命令" in res:
        # 执行卸载命令 需要删除卸载命令key
        exec_cmd(key, res)
        del res["卸载命令"]

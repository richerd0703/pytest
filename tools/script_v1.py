import paramiko
import yaml
from concurrent.futures import ThreadPoolExecutor
import datetime
import json

PATH = r"output.yaml"
LOG = open("pool_log.txt", "a+")
# EXC_CMD = "cd && cd /root/temp/  && "
EXC_CMD = "cd && cd /root/temp/chaosblade-0.6.0 && "


def create_ssh_client(host):
    server_ip = host['ip']
    server_port = host['port']
    server_pwd = host['pwd']
    server_username = host['username']

    try:
        # 创建SSH客户端
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接到服务器
        ssh_client.connect(server_ip, port=server_port, username=server_username, password=server_pwd)
        return ssh_client

    except Exception as ex:
        string = "{} IP:{}, 连接服务器失败, {}\n".format(get_cur_time(), server_ip, str(ex))
        LOG.write(string)
        return


def execute_command(ssh_client, command):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode('utf-8')
        print(output)
        return output

    except Exception as ex:
        string = "{}, 命令'{}'执行失败, {}\n".format(get_cur_time(), command, str(ex))
        LOG.write(string)
        return


def closed(ssh):
    ssh.close()


def read_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
        result = yaml.load(data, Loader=yaml.FullLoader)
    return result


def write_yaml(yaml_path, data):
    with open(yaml_path, encoding="utf-8", mode="w") as f:
        yaml.dump(data, stream=f, allow_unicode=True)


def get_cur_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_key(res, key, server_name, result_id, action):
    cmd = "./blade {} {}".format(action, result_id)
    # res = read_yaml(PATH)
    # val = {server_name: cmd}
    # print(id(val))
    if key not in res:
        res[key] = {}
    res[key][server_name] = cmd


def exec_cmd(key, res):
    with ThreadPoolExecutor(max_workers=len(res['hosts'])) as executor:
        ssh_clients = []
        for host_info in res['hosts'].values():
            ssh_client = create_ssh_client(host_info)
            ssh_clients.append(ssh_client)

        for server_id, command in res[key].items():
            if key != "安装命令":
                command = r"{}{}".format(EXC_CMD, res[key][server_id])
                print("============" + command)
            ssh_client = ssh_clients.pop(0)
            try:
                response = executor.submit(execute_command, ssh_client, command).result()
                print("----操作返回信息------: ", response)
                if key in ["执行命令", "挂载命令", "销毁命令", "卸载命令"]:
                    string = "{} IP:{}, 返回信息如下, {}\n".format(get_cur_time(), res['hosts'][server_id]['ip'], str(res))
                    LOG.write(string)

                if key in ["执行命令", "挂载命令"]:
                    result_id = json.loads(response).get("result")
                    # result_id = response
                    if result_id and key == "执行命令":
                        add_key(res, "销毁命令", server_id, result_id, "destroy")
                    elif result_id and key == "挂载命令":
                        add_key(res, "卸载命令", server_id, result_id, "revoke")
                    else:
                        string = "{} IP:{}, 无法获取result_id \n".format(get_cur_time(), res['hosts'][server_id]['ip'])
                        LOG.write(string)
            except Exception as ex:
                string = "{} IP:{}, 执行Linux命令失败，信息如下, {}\n".format(get_cur_time(), res['hosts'][server_id]['ip'], str(ex))
                LOG.write(string)

            write_yaml(PATH, res)
        for ssh_client in ssh_clients:
            if ssh_client:
                ssh_client.close()

if __name__ == '__main__':
    # "安装命令", "执行命令", "挂载命令", "销毁命令", "卸载命令"
    key = "销毁命令"
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
        del res['销毁命令']
        write_yaml(PATH, res)
    if key == "卸载命令" and "卸载命令" in res:
        # 执行卸载命令 需要删除卸载命令key
        exec_cmd(key, res)
        del res['卸载命令']
        write_yaml(PATH, res)
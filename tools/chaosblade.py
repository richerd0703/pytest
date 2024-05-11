import paramiko
import yaml
from concurrent.futures import ThreadPoolExecutor

def execute_command(host_info, command):
    server_ip = host_info['ip']
    server_port = host_info['port']
    server_pwd = host_info['pwd']
    server_username = host_info['username']

    try:
        # 创建SSH客户端
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接到服务器
        ssh_client.connect(server_ip, port=server_port, username=server_username, password=server_pwd)

        # 执行命令
        stdin, stdout, stderr = ssh_client.exec_command(command)

        # 读取命令输出
        output = stdout.read().decode('utf-8').strip()
        print(output)
        return output

    except Exception as e:
        return str(e)

    finally:
        # 关闭SSH连接
        ssh_client.close()

def main():
    # 读取服务器信息和命令
    with open('new_test.yaml', 'r', encoding='utf-8') as yaml_file:
        data = yaml.safe_load(yaml_file)

    # 存储命令结果
    results = data

    with ThreadPoolExecutor(max_workers=len(data['command'])) as executor:
        futures = []
        for server, command in data['command'].items():
            future = executor.submit(execute_command, data['hosts'][server], command)
            futures.append((server, future))

        for server, future in futures:
            result = future.result()
            results['command'][server] = result

    # 将结果写入新的YAML文件
    with open('output.yaml', 'w', encoding='utf-8') as output_file:
        yaml.dump(results, output_file, allow_unicode=True)

if __name__ == "__main__":
    main()
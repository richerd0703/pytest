import yaml
import json

def read_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
        result = yaml.load(data, Loader=yaml.FullLoader)
    return result


def write_yaml(yaml_path, data):
    with open(yaml_path, encoding="utf-8", mode="w") as f:
        yaml.dump(data, stream=f, allow_unicode=True)


if __name__ == '__main__':
    PATH = r"output.yaml"
    res = read_yaml(PATH)
    print(res)
    del res['销毁命令']
    print(res)
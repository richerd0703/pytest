

import random

# 读取文件内容
with open(r"D:\download\chrome\ZIKU.txt", 'r',encoding='utf-8') as f:
    lines = f.readlines()
    s = lines[0]

    # print(type(lines))
    s1 = set(s)
    print(s1)
    print("l = ", len(s), "s = ", len(s1))

# s = '哈哈哈哈你'
# res = set(s)
# print(res)
# print(len(res))

# 打乱行的顺序
# shuffled_lines = random.sample(lines, len(lines))
#
# # 将打乱后的行写入新文件
# with open(r"D:\download\chrome\new_ZIKU.txt", 'w',encoding='utf-8') as f:
#     f.writelines(shuffled_lines)
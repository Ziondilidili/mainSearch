import time

from pyrogram import Client, filters, emoji
import logging
import configparser
from mysql import UsingMysql
from tqdm import tqdm

# 日志等级
logging.basicConfig(level=logging.INFO)

# 配置文件
config = configparser.ConfigParser()  # 类实例化
config_path = "config.ini"
config.read(config_path, encoding="UTF-8")
no_group_title = config.get('pyrogram', 'no_group_title')

# 脚本配置
zion_app = Client(
    "Zion",
    api_id=15906508,
    api_hash='87dfc1059f90780e8480cc2d42d781d1',
    proxy=dict(
        hostname="127.0.0.1",
        port=10808,
    )
)


def get_config():
    with zion_app:
        for dialog in tqdm(zion_app.iter_dialogs()):
            # time.sleep(2)
            id = str(dialog['chat']['id'])
            username = str(dialog['chat']['username'])
            if username == "":
                continue
            if id not in config.sections():
                config.add_section(id)
                config.set(id, 'limit', "1")
            title = str(dialog['chat']['title'])
            limit = config.get(id, 'limit')
            count = zion_app.get_history_count(dialog['chat']['id'])
            if limit == count:
                continue
            config.set(id, 'title', title)
            config.set(id, 'count', str(count))
            config.set(id, 'username', username)
            config.set(id, 'first_name', str(dialog['chat']['first_name']))
            config.write(open(config_path, "w+",encoding="UTF-8"))


def select_one(cursor):
    cursor.execute("select * from media")
    data = cursor.fetchone()
    # print("-- 单条记录: {0} ".format(data))


def fetch_list_by_filter(cursor, pk):
    sql = 'select * from media where width > %d' % pk
    cursor.execute(sql)
    data_list = cursor.fetchall()
    print('-- 总数: %d' % len(data_list))
    return data_list


# 查找
def fetch_list():
    with UsingMysql(log_time=True) as um:
        # 查找id 大于800的记录
        data_list = fetch_list_by_filter(um.cursor, 0)


# 新增单条记录
def create_one(i):
    with UsingMysql(log_time=False) as um:
        sql = "insert into media(title,url,type) values(%s, %s, %s)"
        try:
            title = i['caption']
        except:
            return
        try:
            url = "https://t.me/" + i['sender_chat']['username'] + "/" + str(i['message_id'])
        except:
            try:
                url = "https://t.me/" + i['chat']['username'] + "/" + str(i['message_id'])
            except:
                print(i)
                print("url error")
        if 'photo' in i['media']:
            type = "photo"
        if 'video' in i['media']:
            type = "video"
        params = (title, url, type)
        um.cursor.execute(sql, params)
        # 查看结果
        select_one(um.cursor)


def get_medio():
    with zion_app:
        for l in config.sections():
            if l == "pyrogram":
                continue
            if config.get(l, 'limit') == config.get(l, 'count'):
                continue
            if config.get(l, "title") in no_group_title or l[0] != "-" or config.get(l, "username") == "None":
                continue
            count = zion_app.get_history_count(l)
            config.set(l, 'count', str(count))
            limit = int(config.get(l, "limit"))
            for j in range(limit, int(count), 100):
                history = zion_app.get_history(l, offset=j, reverse=True)
                for i in tqdm(history):
                    if i['caption'] == "":
                        continue
                    try:
                        if 'video' in i['media'] or 'photo' in i['media']:
                            create_one(i)
                        else:
                            continue
                    except:
                        continue
                config.set(l, 'limit', str(j))
                config.write(open(config_path, "w+", encoding="UTF-8"))
                print(l + ": " + str(j) + " over")


# @zion_app.on_message(filters.video or filters.media_group)
# def get_update(client,message):
#     if 'video' in message['media'] or 'photo' in message['media']:
#         create_one(message)


def get_parsent():
    sum_count = 0
    now_count = 0
    for i in config.sections():
        if i == "pyrogram":
            continue
        if config.get(i, 'limit') == config.get(i, 'count'):
            continue
        if config.get(i, "title") in no_group_title or i[0] != "-" or config.get(i, "username") == "None":
            continue
        sum_count = sum_count + int(config.get(i, 'count'))
        now_count = now_count + int(config.get(i, 'limit'))
    print(
        "总数 -- " + str(sum_count) + "\n" + "已完成 -- " + str(now_count) + "\n" + "百分比 -- " + str(
            (round(now_count / sum_count, 2)) * 100) + "%\n")


if __name__ == "__main__":
    # try:
    #     zion_app.run(get_config())
    # except:
    # get_parsent()
    # zion_app.run(get_medio())
    zion_app.run(get_config())

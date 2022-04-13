import configparser
from pyrogram import Client, filters, emoji
from mysql import UsingMysql
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import (InlineQueryResultArticle, InputTextMessageContent,
                            InlineKeyboardMarkup, InlineKeyboardButton)
import logging.handlers
import tornado.web
import tornado.ioloop
from tornado.web import RequestHandler, Application
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import define, options
import json
import tqdm

define('port', default=8044, type=int)
# 配置文件
config = configparser.ConfigParser()  # 类实例化
config_path = "config.ini"
config.read(config_path, encoding="UTF-8")
# 日志等级
logging.basicConfig(level=logging.INFO)
# 脚本配置
no_group_title = config.get('pyrogram', 'no_group_title')
bot_app = Client(
    "Douyinnn_bot",
    bot_token="5334963669:AAEFOj2VCaEl-ScqWJXeWDlEQLTPS_LVepo",
    # bot_token='5111025743:AAH-pAHXppygEAdVq_ugk9g7LoEKkrcdlyw',
    proxy=dict(
        hostname="127.0.0.1",
        port=1080,
    )
)


def search(pk, limit):
    # select * from 表名 where 字段名 like 对应值（子串）
    with UsingMysql(log_time=True) as um:
        # 查找id 大于800的记录
        sql = "select * from media where title like '%" + pk + "%' limit " + str((limit - 1) * 20) + "," + "20"
        um.cursor.execute(sql)
        data_list = um.cursor.fetchall()
        print('-- 总数: %d' % len(data_list))
        return data_list


def sum(pk):
    with UsingMysql(log_time=False) as um:
        sql = "SELECT COUNT(*) FROM media WHERE title LIKE '%" + pk + "%'"
        um.cursor.execute(sql)
        return um.cursor.fetchall()[0]['COUNT(*)']


@bot_app.on_callback_query()
def callback(client, message):
    callback_data = message['data']
    message_id = message['message']['message_id']
    chat_id = message['message']['chat']['id']
    data = callback_data.split("/")
    limit = int(data[0].replace("/", ""))
    search_key = data[1].replace("/", "")
    reply_markup = message['message']['reply_markup']
    key_sum = sum(search_key)
    data_list = search(search_key, limit)
    num = (limit - 1) * 20
    res = ''
    for i in data_list:
        num = num + 1
        # res = res + str(num) + ". " + i['type'] + " - " + i['title'][0:26] + " - " + i['url'] + '\n\n'
        if len(i['title']) > 50:
            res = res + '<a href="' + i['url'] + '">' + str(num) + ". " + i['type'] + " - " + i['title'][
                                                                                              0:50].replace("\n",
                                                                                                            "") + '...\n\n' + '</a>\n'
        else:
            res = res + '<a href="' + i['url'] + '">' + str(num) + ". " + i['type'] + " - " + i['title'].replace("\n",
                                                                                                                 "") + '\n\n' + '</a>\n'
    res = res + '<a>' + " - 结果总数：" + str(key_sum) + '</a>' + "\n" + '<a> - 当前页：' + str(
        limit) + '</a>' + "\n"
    bot_app.edit_message_text(chat_id, message_id, res,
                              reply_markup=InlineKeyboardMarkup(
                                  [
                                      [
                                          InlineKeyboardButton(  # Generates a callback query when pressed
                                              "上一页",
                                              callback_data=str(limit - 1) + '/' + search_key,
                                          ),
                                          InlineKeyboardButton(  # Generates a callback query when pressed
                                              "下一页",
                                              callback_data=str(limit + 1) + "/" + search_key,
                                          )
                                      ]
                                  ]
                              ),
                              parse_mode="html")


@bot_app.on_message(filters.private)
def main(client, message):
    user_id = message['from_user']['id']
    message_id = message['message_id']
    search_key = message.text
    key_sum = sum(search_key)
    limit = 1
    data_list = search(search_key, limit)
    num = (limit - 1) * 20
    res = ''
    for i in data_list:
        num = num + 1
        if len(i['title']) > 50:
            res = res + '<a href="' + i['url'] + '">' + str(num) + ". " + i['type'] + " - " + i['title'][
                                                                                              0:50].replace("\n",
                                                                                                            "") + '...\n\n' + '</a>\n'
        else:
            res = res + '<a href="' + i['url'] + '">' + str(num) + ". " + i['type'] + " - " + i['title'].replace(
                "\n",
                "") + '\n\n' + '</a>\n'
    res = res + '<a> - 搜索内容：' + search_key + '</a>' + "\n" + '<a>' + " - 结果总数：" + str(
        key_sum) + '</a>' + "\n" + '<a> - 当前页：' + str(
        1) + '</a>' + "\n"
    bot_app.send_message(user_id, res, parse_mode='html',
                         reply_markup=InlineKeyboardMarkup(
                             [
                                 [
                                     InlineKeyboardButton(  # Generates a callback query when pressed
                                         "上一页",
                                         callback_data=str(limit - 1) + '/' + search_key,
                                     ),
                                     InlineKeyboardButton(  # Generates a callback query when pressed
                                         "下一页",
                                         callback_data=str(limit + 1) + "/" + search_key,
                                     )
                                 ]
                             ]
                         )
                         )


if __name__ == "__main__":
    bot_app.run()

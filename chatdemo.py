# -*- coding: utf-8 -*-

import tornado.web
import tornado.options
import tornado.ioloop
import os.path
from tornado.options import define,options
import tornado.websocket
import logging
from tornado.escape import json_encode
import uuid

# 定义启动端口
define("port", default=8888, help="run on the given port", type=int)

# Tornado 应用类
class Application(tornado.web.Application):
    # URL 映射
    def __init__(self):
        handlers = [
            (r"/",MainHandler),
            (r"/chatsocket", ChatSocketHandler),
        ]
        # 初始化参数设置
        settings = dict(
            cookie_secret = "YOU_CANT_GUEST_MY_SECRET",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies = True,
        )

# 主页响应器
class MainHandler():
    def get(self):
        self.render("index.html")   # 渲染模板

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()         # 保存所有在线 WebSocket 连接

    def open(self):         # WebSocket 建立时调用
        ChatSocketHandler.waiters.add(self)

    def on_close(self):     # WebSocket 断开连接后调用
        ChatSocketHandler.waiters.remove(self)

    def on_message(self, message):      # 收到 WebSocket 消息时调用
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        self.username = parsed["username"]
        chat = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
            "type": "message",
        }
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html",message=chat)
        )
        ChatSocketHandler.send_updates(chat)

    @classmethod
    def send_updates(cls, chat):        # 向所有客户端发送消息
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

# 监听端口，并启动IOLoop
def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
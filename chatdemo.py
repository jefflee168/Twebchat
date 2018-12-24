# -*- coding: utf-8 -*-

import tornado.web
import tornado.options
import tornado.ioloop
import os.path
from tornado.options import define,options

# 定义启动端口
define("port", default=8888, help="run on the given port", type=int)

# Tornado 应用类
class Application(tornado.web.Application):
    # URL 映射
    def __init__(self):
        handlers = [
            (r"/",MainHandler),
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

# 监听端口，并启动IOLoop
def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
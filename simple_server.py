# 导入 Python 自带的网络服务器模块
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# 1. 定义一个“接待员”，专门处理别人发来的请求
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 如果别人在浏览器访问了我们的网站
        self.send_response(200) # 告诉浏览器：一切正常
        self.send_header('Content-type', 'application/json') # 告诉他我返回的是 JSON 数据
        self.end_headers()
        
        # 准备要返回的数据
        data = {"status": "success", "message": "我的AI助手准备就绪！"}
        
        # 把数据打包发给浏览器
        self.wfile.write(json.dumps(data).encode('utf-8'))

# 2. 开启服务器（就是饭店开门营业）
if __name__ == "__main__":
    server_address = ('', 8000) # 在 8000 端口开门
    httpd = HTTPServer(server_address, MyHandler)
    print("🚀 服务器已启动，请在浏览器打开 http://localhost:8000")
    httpd.serve_forever() # 让服务器一直运行，不要停
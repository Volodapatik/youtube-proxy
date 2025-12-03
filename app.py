from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
import json

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Главная страница
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>YouTube Proxy для России</title>
                    <style>
                        body { font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px; }
                        input { width: 70%; padding: 10px; font-size: 16px; }
                        button { padding: 10px 20px; font-size: 16px; }
                        #video { margin-top: 20px; width: 100%; height: 500px; }
                    </style>
                </head>
                <body>
                    <h1>🎬 YouTube Proxy для России</h1>
                    <p>Вставь ссылку на YouTube видео:</p>
                    <input type="text" id="url" placeholder="https://www.youtube.com/watch?v=...">
                    <button onclick="loadVideo()">Смотреть</button>
                    
                    <div id="video">
                        <iframe width="100%" height="500" 
                            src="https://www.youtube.com/embed/dQw4w9WgXcQ" 
                            frameborder="0" allowfullscreen>
                        </iframe>
                    </div>
                    
                    <script>
                    function loadVideo() {
                        let url = document.getElementById('url').value;
                        let videoId = extractVideoId(url);
                        if (videoId) {
                            let iframe = '<iframe width="100%" height="500" ' +
                                        'src="https://www.youtube.com/embed/' + videoId + '" ' +
                                        'frameborder="0" allowfullscreen></iframe>';
                            document.getElementById('video').innerHTML = iframe;
                        }
                    }
                    
                    function extractVideoId(url) {
                        let regExp = /^.*((youtu.be\\/)|(v\\/)|(\\/u\\/\\w\\/)|(embed\\/)|(watch\\?))\\??v?=?([^#&?]*).*/;
                        let match = url.match(regExp);
                        return (match && match[7].length==11) ? match[7] : false;
                    }
                    </script>
                </body>
                </html>
                """
                self.wfile.write(html.encode('utf-8'))
                return
                
            # API для получения информации о видео
            elif self.path.startswith('/api/'):
                video_id = self.path.split('/')[-1]
                api_url = f"https://www.youtube.com/youtubei/v1/player?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
                
                # Эмулируем запрос как мобильное устройство
                data = {
                    "videoId": video_id,
                    "context": {
                        "client": {
                            "clientName": "ANDROID",
                            "clientVersion": "17.31.35",
                            "androidSdkVersion": 30
                        }
                    }
                }
                
                req = urllib.request.Request(api_url, 
                    data=json.dumps(data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'})
                
                with urllib.request.urlopen(req) as response:
                    video_data = response.read()
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(video_data)
                return
                
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
    
    def do_POST(self):
        self.do_GET()
    
    def log_message(self, format, *args):
        pass  # Отключаем логи

def run_server():
    port = int(os.environ.get('PORT', 3000))
    server = HTTPServer(('0.0.0.0', port), ProxyHandler)
    print(f'🚀 YouTube Proxy запущен на порту {port}')
    print(f'📡 Открой: http://localhost:{port}')
    server.serve_forever()

if __name__ == '__main__':
    import os
    run_server()

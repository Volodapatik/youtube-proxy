from flask import Flask, render_template, request, jsonify, redirect
import requests
import json
import re
from urllib.parse import quote

app = Flask(__name__)

# YouTube API ключ (публичный, для поиска)
YOUTUBE_API_KEY = "AIzaSyCSeZzG1u99LqcTpm78P3-XSg4poOQEVCo"

@app.route('/')
def index():
    """Главная страница как YouTube"""
    return render_template('index.html')

@app.route('/search')
def search():
    """Поиск видео на YouTube"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Введите запрос'}), 400
    
    try:
        # Поиск через YouTube API
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=20&q={quote(query)}&type=video&key={YOUTUBE_API_KEY}"
        response = requests.get(search_url)
        data = response.json()
        
        if 'items' not in data:
            return jsonify({'error': 'Не найдено'}), 404
        
        # Получаем детали видео
        video_ids = [item['id']['videoId'] for item in data['items'] if 'videoId' in item['id']]
        
        if not video_ids:
            return jsonify({'error': 'Нет видео'}), 404
        
        # Детали видео
        videos_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={','.join(video_ids)}&key={YOUTUBE_API_KEY}"
        videos_response = requests.get(videos_url)
        videos_data = videos_response.json()
        
        videos = []
        for video in videos_data.get('items', []):
            videos.append({
                'id': video['id'],
                'title': video['snippet']['title'],
                'channel': video['snippet']['channelTitle'],
                'thumbnail': video['snippet']['thumbnails']['medium']['url'],
                'views': format_views(video['statistics'].get('viewCount', '0')),
                'duration': format_duration(video['contentDetails']['duration']),
                'published': format_date(video['snippet']['publishedAt'])
            })
        
        return jsonify({'videos': videos, 'query': query})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/watch/<video_id>')
def watch(video_id):
    """Страница просмотра видео"""
    return render_template('watch.html', video_id=video_id)

@app.route('/api/stream/<video_id>')
def get_stream_url(video_id):
    """Получение ссылки на видео (через сторонний сервис)"""
    try:
        # Используем публичный прокси для получения ссылки
        proxy_url = f"https://pipedapi.kavin.rocks/streams/{video_id}"
        response = requests.get(proxy_url, timeout=10)
        data = response.json()
        
        # Ищем лучшее качество
        if 'videoStreams' in data and data['videoStreams']:
            # Сортируем по качеству
            streams = sorted(data['videoStreams'], 
                           key=lambda x: x.get('quality', ''), 
                           reverse=True)
            
            # Предпочитаем mp4
            for stream in streams:
                if 'url' in stream:
                    return jsonify({
                        'url': stream['url'],
                        'quality': stream.get('quality', 'unknown'),
                        'format': stream.get('format', 'mp4')
                    })
        
        # Альтернативный метод через yt-dlp (если установлен)
        return jsonify({
            'url': f"https://www.youtube.com/embed/{video_id}",
            'quality': '720p',
            'format': 'iframe'
        })
        
    except Exception as e:
        # Фолбэк на стандартный embed
        return jsonify({
            'url': f"https://www.youtube.com/embed/{video_id}",
            'quality': '720p',
            'format': 'iframe'
        })

# Вспомогательные функции
def format_views(view_count):
    """Форматирование количества просмотров"""
    try:
        count = int(view_count)
        if count >= 1000000:
            return f"{count/1000000:.1f}M"
        elif count >= 1000:
            return f"{count/1000:.1f}K"
        return str(count)
    except:
        return "0"

def format_duration(duration):
    """Форматирование длительности"""
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)
    if not match:
        return "--:--"
    
    hours = match.group(1)[:-1] if match.group(1) else "0"
    minutes = match.group(2)[:-1] if match.group(2) else "0"
    seconds = match.group(3)[:-1] if match.group(3) else "0"
    
    if int(hours) > 0:
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    else:
        return f"{int(minutes):02d}:{int(seconds):02d}"

def format_date(published_at):
    """Форматирование даты"""
    from datetime import datetime, timezone
    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    diff = now - pub_date
    
    days = diff.days
    if days < 1:
        return "Сегодня"
    elif days == 1:
        return "Вчера"
    elif days < 7:
        return f"{days} дней назад"
    elif days < 30:
        weeks = days // 7
        return f"{weeks} недель назад"
    elif days < 365:
        months = days // 30
        return f"{months} месяцев назад"
    else:
        years = days // 365
        return f"{years} лет назад"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

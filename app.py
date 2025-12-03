from flask import Flask, render_template, request, jsonify
import requests
import json
import re
import os
from urllib.parse import quote

app = Flask(__name__)

YOUTUBE_API_KEY = "AIzaSyCSeZzG1u99LqcTpm78P3-XSg4poOQEVCo"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    page_token = request.args.get('page', '')
    
    if not query:
        return jsonify({'error': 'Введите запрос'}), 400
    
    try:
        # Формируем URL с пагинацией
        base_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=20&q={quote(query)}&type=video&key={YOUTUBE_API_KEY}"
        
        if page_token:
            base_url += f"&pageToken={page_token}"
        
        response = requests.get(base_url)
        data = response.json()
        
        if 'items' not in data:
            return jsonify({'error': 'Не найдено'}), 404
        
        # Получаем ID видео для деталей
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
        
        return jsonify({
            'videos': videos,
            'query': query,
            'nextPageToken': data.get('nextPageToken', ''),
            'totalResults': data.get('pageInfo', {}).get('totalResults', 0)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/watch/<video_id>')
def watch(video_id):
    return render_template('watch.html', video_id=video_id)

# Вспомогательные функции
def format_views(view_count):
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

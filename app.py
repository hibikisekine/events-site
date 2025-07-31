from flask import Flask, render_template, request, jsonify, make_response
import sqlite3
import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from weather_api import WeatherAPI
from weather_simple import WeatherSimple
from event_scraper import EventScraper
from event_filter import EventFilter
from logger import setup_logger, log_user_action, log_error
from config import config

load_dotenv()

# 環境設定
env = os.getenv('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[env])

# ログ設定
if env == 'production':
    setup_logger(app)

# 静的ファイルのキャッシュ無効化
@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# データベース初期化
def init_db():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            time TEXT,
            location TEXT,
            category TEXT,
            is_indoor BOOLEAN DEFAULT 0,
            is_free BOOLEAN DEFAULT 0,
            has_parking BOOLEAN DEFAULT 0,
            child_friendly BOOLEAN DEFAULT 0,
            weather_dependent BOOLEAN DEFAULT 0,
            rain_cancellation TEXT,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            weather_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    response = make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content

@app.route('/api/events')
def get_events():
    try:
        # 天気予報を取得（WeatherAPI.com使用）
        weather_api = WeatherSimple()
        weather_data = weather_api.get_weather_forecast()
        
        # イベントを取得
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM events 
            WHERE date >= date('now') 
            ORDER BY date ASC, time ASC
        ''')
        events = cursor.fetchall()
        conn.close()
        
        # イベントをフィルタリング
        event_filter = EventFilter()
        filtered_events = event_filter.filter_events_by_weather(events, weather_data)
        
        return jsonify({
            'events': filtered_events,
            'weather': weather_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather')
def get_weather():
    try:
        # WeatherAPI.comを使用
        weather_api = WeatherSimple()
        weather_data = weather_api.get_weather_forecast()
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scrape-events')
def scrape_events():
    try:
        # スクレイピングを無効化（サンプルデータを使用）
        return jsonify({'message': 'スクレイピングは無効化されています。サンプルデータを使用しています。'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """ヘルスチェックエンドポイント"""
    try:
        # データベース接続チェック
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM events')
        event_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'events_count': event_count,
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/filter')
def filter_events():
    try:
        # パラメータ取得
        category = request.args.get('category', '')
        city = request.args.get('city', '')
        indoor_only = request.args.get('indoor_only', '')
        outdoor_only = request.args.get('outdoor_only', '')
        free_only = request.args.get('free_only', '')
        parking_required = request.args.get('parking_required', '')
        child_friendly = request.args.get('child_friendly', '')

        filters = {
            'category': category,
            'city': city,
            'indoor_only': indoor_only,
            'outdoor_only': outdoor_only,
            'free_only': free_only,
            'parking_required': parking_required,
            'child_friendly': child_friendly
        }

        print(f"🔍 フィルター適用: {filters}")  # デバッグ情報

        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()

        query = 'SELECT * FROM events WHERE 1=1'
        params = []

        if filters.get('indoor_only'):
            query += ' AND is_indoor = 1'
        if filters.get('outdoor_only'):
            query += ' AND is_indoor = 0'
        if filters.get('free_only'):
            query += ' AND is_free = 1'
        if filters.get('parking_required'):
            query += ' AND has_parking = 1'
        if filters.get('child_friendly'):
            query += ' AND child_friendly = 1'
        if filters.get('category'):
            query += ' AND category = ?'
            params.append(filters['category'])
        if filters.get('city'):
            query += ' AND (location LIKE ? OR location LIKE ?)'
            params.append(f'%{filters["city"]}%')
            params.append(f'%（{filters["city"]}）%')

        print(f"🔍 SQLクエリ: {query}")  # デバッグ情報
        print(f"🔍 パラメータ: {params}")  # デバッグ情報

        cursor.execute(query, params)
        events = cursor.fetchall()
        conn.close()

        print(f"🔍 結果件数: {len(events)}")  # デバッグ情報

        response = jsonify({'events': events})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response
    except Exception as e:
        print(f"❌ フィルターエラー: {e}")  # デバッグ情報
        error_response = jsonify({'error': str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        error_response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        error_response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return error_response, 500

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=8080) 
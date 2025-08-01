import json
import sqlite3
from datetime import datetime, timedelta
import os

def handler(event, context):
    """Netlify Function handler"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    # Handle preflight requests
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    path = event.get('path', '').split('/')[-1]
    
    try:
        if path == 'events':
            return get_events(event, headers)
        elif path == 'weather':
            return get_weather(event, headers)
        elif path == 'stats':
            return get_stats(event, headers)
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Endpoint not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def get_events(event, headers):
    """スクレイピングされたイベントデータを取得"""
    try:
        # データベースファイルのパス
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'events.db')
        
        # データベースに接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # アクティブなイベントを取得
        cursor.execute('''
            SELECT id, title, description, date, time, location, category,
                   is_indoor, is_free, has_parking, child_friendly,
                   weather_dependent, rain_cancellation, source_url, source_city
            FROM events 
            WHERE is_active = 1 
            ORDER BY date ASC, created_at DESC
        ''')
        
        events = []
        for row in cursor.fetchall():
            event = {
                'id': row[0],
                'title': row[1],
                'description': row[2] or '',
                'date': row[3],
                'time': row[4] or '',
                'location': row[5] or '',
                'category': row[6] or 'その他',
                'is_indoor': bool(row[7]) if row[7] is not None else None,
                'is_free': bool(row[8]) if row[8] is not None else None,
                'has_parking': bool(row[9]) if row[9] is not None else False,
                'child_friendly': bool(row[10]) if row[10] is not None else False,
                'weather_dependent': bool(row[11]) if row[11] is not None else False,
                'rain_cancellation': row[12] or None,
                'source_url': row[13] or '',
                'source_city': row[14] or ''
            }
            events.append(event)
        
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'events': events,
                'count': len(events),
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Database error: {str(e)}'})
        }

def get_weather(event, headers):
    """天気データを取得（WeatherAPI.comを使用）"""
    try:
        import requests
        
        # WeatherAPI.comのキー
        API_KEY = '88ed0e701cfc4c7fb0d13301253107'
        
        # 複数都市の天気データを取得
        cities = [
            {'name': 'つくば市', 'query': 'Tsukuba,Japan'},
            {'name': 'つくばみらい市', 'query': 'Tsukubamirai,Japan'},
            {'name': '取手市', 'query': 'Toride,Japan'},
            {'name': '守谷市', 'query': 'Moriya,Japan'}
        ]
        
        weather_data = {}
        
        for city in cities:
            try:
                response = requests.get(
                    f'https://api.weatherapi.com/v1/current.json',
                    params={
                        'key': API_KEY,
                        'q': city['query'],
                        'aqi': 'no'
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    weather_data[city['name']] = {
                        'temperature': round(data['current']['temp_c']),
                        'condition': data['current']['condition']['text'],
                        'humidity': data['current']['humidity'],
                        'rain_probability': round(data['current']['precip_mm'] * 10) if data['current']['precip_mm'] > 0 else 0,
                        'icon': data['current']['condition']['icon']
                    }
                else:
                    weather_data[city['name']] = {
                        'temperature': '--',
                        'condition': 'データ取得中',
                        'humidity': '--',
                        'rain_probability': 0,
                        'icon': '113'
                    }
                    
            except Exception as e:
                weather_data[city['name']] = {
                    'temperature': '--',
                    'condition': 'データ取得中',
                    'humidity': '--',
                    'rain_probability': 0,
                    'icon': '113'
                }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'weather': weather_data,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Weather API error: {str(e)}'})
        }

def get_stats(event, headers):
    """スクレイピング統計を取得"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'events.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 統計データを取得
        cursor.execute("SELECT COUNT(*) FROM events WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM events WHERE created_at >= date('now', '-7 days')")
        recent_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT source_city, COUNT(*) FROM events WHERE is_active = 1 GROUP BY source_city")
        city_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'active_events': active_count,
                'recent_events': recent_count,
                'city_stats': city_stats,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Stats error: {str(e)}'})
        } 
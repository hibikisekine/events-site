import requests
import json
import sqlite3
from datetime import datetime, timedelta
import os

class WeatherAPI:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
        self.city = 'Tsukubamirai'  # つくばみらい市
        self.country_code = 'JP'
        self.base_url = 'http://api.openweathermap.org/data/2.5'
        
    def get_weather_forecast(self):
        """3日間の天気予報を取得"""
        try:
            # キャッシュをチェック
            cached_data = self._get_cached_weather()
            if cached_data:
                return cached_data
            
            # APIから天気データを取得
            url = f"{self.base_url}/forecast"
            params = {
                'q': f"{self.city},{self.country_code}",
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ja'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            weather_data = response.json()
            processed_data = self._process_weather_data(weather_data)
            
            # キャッシュに保存
            self._cache_weather_data(processed_data)
            
            return processed_data
            
        except Exception as e:
            print(f"天気予報取得エラー: {e}")
            return self._get_default_weather_data()
    
    def _process_weather_data(self, raw_data):
        """天気データを処理して必要な情報を抽出"""
        processed = {
            'city': raw_data['city']['name'],
            'forecast': []
        }
        
        for item in raw_data['list']:
            date = datetime.fromtimestamp(item['dt'])
            weather_info = {
                'datetime': date.isoformat(),
                'date': date.strftime('%Y-%m-%d'),
                'time': date.strftime('%H:%M'),
                'temperature': round(item['main']['temp']),
                'feels_like': round(item['main']['feels_like']),
                'humidity': item['main']['humidity'],
                'description': item['weather'][0]['description'],
                'main': item['weather'][0]['main'],
                'icon': item['weather'][0]['icon'],
                'rain_probability': item.get('pop', 0) * 100,
                'is_rainy': self._is_rainy(item['weather'][0]['main']),
                'is_sunny': self._is_sunny(item['weather'][0]['main'])
            }
            processed['forecast'].append(weather_info)
        
        return processed
    
    def _is_rainy(self, weather_main):
        """雨かどうかを判定"""
        rainy_conditions = ['Rain', 'Drizzle', 'Thunderstorm']
        return weather_main in rainy_conditions
    
    def _is_sunny(self, weather_main):
        """晴れかどうかを判定"""
        sunny_conditions = ['Clear']
        return weather_main in sunny_conditions
    
    def _get_cached_weather(self):
        """キャッシュされた天気データを取得"""
        try:
            conn = sqlite3.connect('events.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT weather_data FROM weather_cache 
                WHERE date = date('now') 
                AND created_at > datetime('now', '-1 hour')
                ORDER BY created_at DESC LIMIT 1
            ''')
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            print(f"キャッシュ取得エラー: {e}")
            return None
    
    def _cache_weather_data(self, weather_data):
        """天気データをキャッシュに保存"""
        try:
            conn = sqlite3.connect('events.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO weather_cache (date, weather_data)
                VALUES (date('now'), ?)
            ''', (json.dumps(weather_data),))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"キャッシュ保存エラー: {e}")
    
    def _get_default_weather_data(self):
        """デフォルトの天気データ（APIエラー時のフォールバック）"""
        return {
            'city': 'つくばみらい市',
            'forecast': [
                {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'time': '12:00',
                    'temperature': 20,
                    'description': '晴れ',
                    'main': 'Clear',
                    'is_rainy': False,
                    'is_sunny': True,
                    'rain_probability': 0
                }
            ]
        }
    
    def get_weather_for_date(self, target_date):
        """特定の日付の天気を取得"""
        forecast = self.get_weather_forecast()
        target_date_str = target_date.strftime('%Y-%m-%d')
        
        for item in forecast['forecast']:
            if item['date'] == target_date_str:
                return item
        
        return None 
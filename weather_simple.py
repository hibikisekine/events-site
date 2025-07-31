import requests
import sqlite3
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class WeatherSimple:
    """シンプルな天気API（WeatherAPI.com使用）"""
    
    def __init__(self):
        self.api_key = os.getenv('WEATHERAPI_KEY', '88ed0e701cfc4c7fb0d13301253107')
        self.base_url = 'http://api.weatherapi.com/v1'
        self.db_path = 'events.db'
    
    def get_weather_forecast(self, city='Tsukubamirai'):
        """3日間の天気予報を取得"""
        
        # キャッシュをチェック
        cached_data = self._get_cached_weather()
        if cached_data:
            return cached_data
        
        try:
            # WeatherAPI.comから天気予報を取得
            url = f"{self.base_url}/forecast.json"
            params = {
                'key': self.api_key,
                'q': f"{city},Japan",
                'days': 3,
                'lang': 'ja'
            }
            
            print(f"🌤️ 天気予報を取得中... (APIキー: {self.api_key[:10]}...)")
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 天気予報の取得に成功しました！")
                
                # 天気データを処理
                weather_data = self._process_weather_data(data)
                
                # キャッシュに保存
                self._cache_weather(weather_data)
                
                return weather_data
            else:
                print(f"❌ APIエラー: {response.status_code}")
                print(f"レスポンス: {response.text}")
                return self._get_fallback_weather()
                
        except requests.exceptions.RequestException as e:
            print(f"❌ リクエストエラー: {e}")
            return self._get_fallback_weather()
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
            return self._get_fallback_weather()
    
    def _get_sample_forecast(self):
        """サンプル予報データを生成"""
        from datetime import datetime, timedelta
        
        forecast = []
        today = datetime.now()
        
        for i in range(3):
            date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
            
            # ランダムな天気パターン
            if i == 0:
                condition = "晴れ"
                is_sunny = True
                is_rainy = False
            elif i == 1:
                condition = "曇り"
                is_sunny = False
                is_rainy = False
            else:
                condition = "小雨"
                is_sunny = False
                is_rainy = True
            
            forecast.append({
                'date': date,
                'condition': condition,
                'temp_max': 25 + i,
                'temp_min': 18 + i,
                'humidity': 60 + (i * 5),
                'precipitation': 0 if i < 2 else 5,
                'is_rainy': is_rainy,
                'is_sunny': is_sunny
            })
        
        return forecast
    
    def _process_weather_data(self, data):
        """天気データを処理"""
        forecast = []
        
        # APIレスポンスの構造を確認して処理
        if 'forecast' in data and 'forecastday' in data['forecast']:
            for day in data['forecast']['forecastday']:
                date = day['date']
                day_data = day['day']
                
                # 天気の判定
                condition = day_data['condition']['text'].lower()
                is_rainy = any(word in condition for word in ['雨', 'rain', 'shower', 'storm'])
                is_sunny = any(word in condition for word in ['晴', 'sunny', 'clear'])
                
                forecast.append({
                    'date': date,
                    'condition': day_data['condition']['text'],
                    'temp_max': day_data['maxtemp_c'],
                    'temp_min': day_data['mintemp_c'],
                    'humidity': day_data['avghumidity'],
                    'precipitation': day_data['totalprecip_mm'],
                    'is_rainy': is_rainy,
                    'is_sunny': is_sunny
                })
        else:
            # APIレスポンスが期待と異なる場合、サンプルデータを使用
            print("⚠️ APIレスポンス構造が期待と異なります。サンプルデータを使用します。")
            forecast = self._get_sample_forecast()
        
        return {
            'location': data.get('location', {}).get('name', 'つくばみらい市'),
            'forecast': forecast,
            'current': {
                'temp': data.get('current', {}).get('temp_c', 20),
                'condition': data.get('current', {}).get('condition', {}).get('text', '晴れ'),
                'humidity': data.get('current', {}).get('humidity', 60)
            }
        }
    
    def _get_cached_weather(self):
        """キャッシュされた天気データを取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT data, timestamp FROM weather_cache 
                WHERE timestamp > datetime('now', '-30 minutes')
                ORDER BY timestamp DESC LIMIT 1
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                import json
                return json.loads(result[0])
            
        except Exception as e:
            print(f"キャッシュ取得エラー: {e}")
        
        return None
    
    def _cache_weather(self, weather_data):
        """天気データをキャッシュに保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            import json
            data_json = json.dumps(weather_data)
            
            cursor.execute('''
                INSERT OR REPLACE INTO weather_cache (data, timestamp)
                VALUES (?, datetime('now'))
            ''', (data_json,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"キャッシュ保存エラー: {e}")
    
    def _get_fallback_weather(self):
        """フォールバック用の天気データ"""
        today = datetime.now()
        
        return {
            'location': 'つくばみらい市',
            'forecast': [
                {
                    'date': today.strftime('%Y-%m-%d'),
                    'condition': '晴れ',
                    'temp_max': 25,
                    'temp_min': 15,
                    'humidity': 60,
                    'precipitation': 0,
                    'is_rainy': False,
                    'is_sunny': True
                },
                {
                    'date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'condition': '曇り',
                    'temp_max': 23,
                    'temp_min': 14,
                    'humidity': 70,
                    'precipitation': 5,
                    'is_rainy': False,
                    'is_sunny': False
                },
                {
                    'date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'condition': '雨',
                    'temp_max': 20,
                    'temp_min': 12,
                    'humidity': 85,
                    'precipitation': 15,
                    'is_rainy': True,
                    'is_sunny': False
                }
            ],
            'current': {
                'temp': 22,
                'condition': '晴れ',
                'humidity': 60
            }
        }
    
    def is_weather_suitable_for_event(self, event_type, weather_data):
        """イベントタイプと天気の適合性を判定"""
        if not weather_data or 'forecast' not in weather_data:
            return True
        
        # 今日の天気を取得
        today_forecast = weather_data['forecast'][0] if weather_data['forecast'] else None
        
        if not today_forecast:
            return True
        
        # 屋内イベントは天気に関係なく開催可能
        if event_type == 'indoor':
            return True
        
        # 屋外イベントは雨の日は不適切
        if event_type == 'outdoor':
            return not today_forecast.get('is_rainy', False)
        
        return True
    
    def get_weather_score(self, event_type, weather_data):
        """天気とイベントの適合度スコアを計算"""
        if not weather_data or 'forecast' not in weather_data:
            return 50
        
        today_forecast = weather_data['forecast'][0] if weather_data['forecast'] else None
        
        if not today_forecast:
            return 50
        
        # 屋内イベントは常に高スコア
        if event_type == 'indoor':
            return 90
        
        # 屋外イベントは天気に応じてスコア調整
        if event_type == 'outdoor':
            if today_forecast.get('is_rainy', False):
                return 20
            elif today_forecast.get('is_sunny', False):
                return 95
            else:
                return 70
        
        return 50 
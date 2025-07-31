#!/usr/bin/env python3
from weather_simple import WeatherSimple

def test_weather():
    """新しい天気APIの動作テスト"""
    
    print("🌤️ 新しい天気APIをテスト中...")
    
    try:
        weather_api = WeatherSimple()
        weather_data = weather_api.get_weather_forecast()
        
        print("✅ 天気データの取得に成功しました！")
        
        # 現在の天気
        current = weather_data.get('current', {})
        print(f"📍 場所: {weather_data.get('location', 'N/A')}")
        print(f"🌡️ 現在の気温: {current.get('temp', 'N/A')}°C")
        print(f"☁️ 天気: {current.get('condition', 'N/A')}")
        
        # 3日間の予報
        print("\n📅 3日間の予報:")
        for day in weather_data.get('forecast', []):
            print(f"  {day['date']}: {day['condition']} "
                  f"({day['temp_min']}°C - {day['temp_max']}°C)")
        
        # イベント適合性テスト
        print("\n🎯 イベント適合性テスト:")
        indoor_score = weather_api.get_weather_score('indoor', weather_data)
        outdoor_score = weather_api.get_weather_score('outdoor', weather_data)
        
        print(f"  屋内イベント適合度: {indoor_score}%")
        print(f"  屋外イベント適合度: {outdoor_score}%")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == '__main__':
    test_weather() 
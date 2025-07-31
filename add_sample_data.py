import sqlite3
from datetime import datetime, timedelta

def add_sample_events():
    """サンプルイベントデータを追加"""
    
    # サンプルイベントデータ
    sample_events = [
        {
            'title': 'つくばみらい市 夏祭り',
            'description': '地域の夏祭りです。盆踊り、屋台、花火大会があります。',
            'date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'time': '18:00',
            'location': 'つくばみらい市中央公園（つくばみらい市）',
            'category': '地域',
            'is_indoor': False,
            'is_free': True,
            'has_parking': True,
            'child_friendly': True,
            'weather_dependent': True,
            'rain_cancellation': '小雨決行',
            'source_url': 'https://example.com'
        },
        {
            'title': '守谷市 図書館講座',
            'description': '読書感想文の書き方講座です。小学生向け。',
            'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'time': '14:00',
            'location': '守谷市立図書館（守谷市）',
            'category': '教育',
            'is_indoor': True,
            'is_free': True,
            'has_parking': True,
            'child_friendly': True,
            'weather_dependent': False,
            'rain_cancellation': '',
            'source_url': 'https://example.com'
        },
        {
            'title': '取手市 スポーツフェスティバル',
            'description': '各種スポーツ体験ができるイベントです。',
            'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'location': '取手市総合運動公園（取手市）',
            'category': 'スポーツ',
            'is_indoor': False,
            'is_free': True,
            'has_parking': True,
            'child_friendly': True,
            'weather_dependent': True,
            'rain_cancellation': '雨天中止',
            'source_url': 'https://example.com'
        },
        {
            'title': 'つくば市 科学実験教室',
            'description': '子供向けの科学実験教室です。',
            'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'time': '13:30',
            'location': 'つくば市科学館（つくば市）',
            'category': '教育',
            'is_indoor': True,
            'is_free': False,
            'has_parking': True,
            'child_friendly': True,
            'weather_dependent': False,
            'rain_cancellation': '',
            'source_url': 'https://example.com'
        },
        {
            'title': '常総市 農業体験',
            'description': '稲刈り体験と農産物直売会です。',
            'date': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'time': '09:00',
            'location': '常総市農業センター（常総市）',
            'category': '地域',
            'is_indoor': False,
            'is_free': True,
            'has_parking': True,
            'child_friendly': True,
            'weather_dependent': True,
            'rain_cancellation': '雨天順延',
            'source_url': 'https://example.com'
        },
        {
            'title': '龍ケ崎市 音楽コンサート',
            'description': '地域の音楽家によるクラシックコンサートです。',
            'date': (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d'),
            'time': '19:00',
            'location': '龍ケ崎市文化会館（龍ケ崎市）',
            'category': '文化',
            'is_indoor': True,
            'is_free': False,
            'has_parking': True,
            'child_friendly': False,
            'weather_dependent': False,
            'rain_cancellation': '',
            'source_url': 'https://example.com'
        },
        {
            'title': '古河市 歴史散歩',
            'description': '古河の歴史を学ぶ散歩ツアーです。',
            'date': (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d'),
            'time': '14:00',
            'location': '古河市役所前（古河市）',
            'category': '文化',
            'is_indoor': False,
            'is_free': True,
            'has_parking': True,
            'child_friendly': True,
            'weather_dependent': True,
            'rain_cancellation': '小雨決行',
            'source_url': 'https://example.com'
        },
        {
            'title': '坂東市 子育てサロン',
            'description': '0-3歳児と保護者向けの子育てサロンです。',
            'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'location': '坂東市子育て支援センター（坂東市）',
            'category': '子育て',
            'is_indoor': True,
            'is_free': True,
            'has_parking': True,
            'child_friendly': True,
            'weather_dependent': False,
            'rain_cancellation': '',
            'source_url': 'https://example.com'
        }
    ]
    
    # データベースに接続
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    
    # サンプルデータを追加
    for event in sample_events:
        cursor.execute('''
            INSERT OR REPLACE INTO events 
            (title, description, date, time, location, category,
             is_indoor, is_free, has_parking, child_friendly,
             weather_dependent, rain_cancellation, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event['title'], event['description'], event['date'],
            event['time'], event['location'], event['category'],
            event['is_indoor'], event['is_free'], event['has_parking'],
            event['child_friendly'], event['weather_dependent'],
            event['rain_cancellation'], event['source_url']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"{len(sample_events)}件のサンプルイベントを追加しました。")

if __name__ == '__main__':
    add_sample_events() 
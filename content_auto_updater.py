import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import re
import time
import schedule
import logging
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('content_updater.log'),
        logging.StreamHandler()
    ]
)

class ContentAutoUpdater:
    def __init__(self):
        self.db_path = 'content.db'
        self.init_database()
        
        # 地域特集コンテンツのソース
        self.seasonal_sources = {
            'tsukubamirai_seasonal': {
                'url': 'https://www.city.tsukubamirai.lg.jp/',
                'name': 'つくばみらい市季節イベント',
                'keywords': ['桜祭り', '花火大会', '収穫祭', 'イルミネーション', 'マルシェ', 'フェスティバル']
            },
            'tsukuba_seasonal': {
                'url': 'https://www.city.tsukuba.lg.jp/',
                'name': 'つくば市季節イベント',
                'keywords': ['桜祭り', '花火大会', '収穫祭', 'イルミネーション', 'マルシェ', 'フェスティバル']
            },
            'moriya_seasonal': {
                'url': 'https://www.city.moriya.ibaraki.jp/',
                'name': '守谷市季節イベント',
                'keywords': ['桜祭り', '花火大会', '収穫祭', 'イルミネーション', 'マルシェ', 'フェスティバル']
            },
            'toride_seasonal': {
                'url': 'https://www.city.toride.ibaraki.jp/',
                'name': '取手市季節イベント',
                'keywords': ['桜祭り', '花火大会', '収穫祭', 'イルミネーション', 'マルシェ', 'フェスティバル']
            }
        }
        
        # グルメ情報のソース
        self.food_sources = {
            'tsukuba_food': {
                'url': 'https://www.city.tsukuba.lg.jp/',
                'name': 'つくば市グルメ情報',
                'keywords': ['新規オープン', '飲食店', 'カフェ', 'レストラン', '居酒屋', 'ラーメン']
            },
            'tsukubamirai_food': {
                'url': 'https://www.city.tsukubamirai.lg.jp/',
                'name': 'つくばみらい市グルメ情報',
                'keywords': ['新規オープン', '飲食店', 'カフェ', 'レストラン', '居酒屋', 'ラーメン']
            }
        }
        
        # 子育て情報のソース
        self.childcare_sources = {
            'tsukuba_childcare': {
                'url': 'https://www.city.tsukuba.lg.jp/kosodate/',
                'name': 'つくば市子育て支援',
                'keywords': ['子育て', '育児', '保育', '児童館', '子育て支援', '親子']
            },
            'tsukubamirai_childcare': {
                'url': 'https://www.city.tsukubamirai.lg.jp/kosodate/',
                'name': 'つくばみらい市子育て支援',
                'keywords': ['子育て', '育児', '保育', '児童館', '子育て支援', '親子']
            }
        }
        
        # 観光スポット情報のソース
        self.tourism_sources = {
            'tsukuba_tourism': {
                'url': 'https://www.city.tsukuba.lg.jp/kankobunka/',
                'name': 'つくば市観光情報',
                'keywords': ['観光', '観光地', '観光スポット', '名所', '史跡', '公園']
            },
            'tsukubamirai_tourism': {
                'url': 'https://www.city.tsukubamirai.lg.jp/kankobunka/',
                'name': 'つくばみらい市観光情報',
                'keywords': ['観光', '観光地', '観光スポット', '名所', '史跡', '公園']
            }
        }
        
        # 文化施設情報のソース
        self.culture_sources = {
            'tsukuba_culture': {
                'url': 'https://www.city.tsukuba.lg.jp/kankobunka/',
                'name': 'つくば市文化施設',
                'keywords': ['博物館', '美術館', '図書館', '文化センター', '展示', '企画展']
            },
            'tsukubamirai_culture': {
                'url': 'https://www.city.tsukubamirai.lg.jp/kankobunka/',
                'name': 'つくばみらい市文化施設',
                'keywords': ['博物館', '美術館', '図書館', '文化センター', '展示', '企画展']
            }
        }
        
        # 統計情報
        self.stats = {
            'seasonal_events': 0,
            'food_info': 0,
            'childcare_info': 0,
            'tourism_info': 0,
            'culture_info': 0,
            'last_run': None
        }
    
    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 季節イベントテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seasonal_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT,
                location TEXT,
                category TEXT,
                city TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # グルメ情報テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                location TEXT,
                category TEXT,
                city TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 子育て情報テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS childcare_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT,
                location TEXT,
                category TEXT,
                city TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 観光情報テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tourism_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                location TEXT,
                category TEXT,
                city TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 文化施設情報テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS culture_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT,
                location TEXT,
                category TEXT,
                city TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def scrape_seasonal_events(self):
        """季節イベントのスクレイピング"""
        logging.info("季節イベントのスクレイピングを開始")
        
        for source_id, source in self.seasonal_sources.items():
            try:
                logging.info(f"{source['name']} をスクレイピング中...")
                
                # 実際のスクレイピング処理
                # ここではサンプルデータを生成
                sample_events = self.generate_sample_seasonal_events(source_id, source)
                
                for event in sample_events:
                    self.save_seasonal_event(event)
                    self.stats['seasonal_events'] += 1
                
                time.sleep(2)  # レート制限対策
                
            except Exception as e:
                logging.error(f"{source['name']} のスクレイピングでエラー: {e}")
        
        logging.info(f"季節イベントスクレイピング完了: {self.stats['seasonal_events']}件")
    
    def scrape_food_info(self):
        """グルメ情報のスクレイピング"""
        logging.info("グルメ情報のスクレイピングを開始")
        
        for source_id, source in self.food_sources.items():
            try:
                logging.info(f"{source['name']} をスクレイピング中...")
                
                # 実際のスクレイピング処理
                # ここではサンプルデータを生成
                sample_food = self.generate_sample_food_info(source_id, source)
                
                for food in sample_food:
                    self.save_food_info(food)
                    self.stats['food_info'] += 1
                
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"{source['name']} のスクレイピングでエラー: {e}")
        
        logging.info(f"グルメ情報スクレイピング完了: {self.stats['food_info']}件")
    
    def scrape_childcare_info(self):
        """子育て情報のスクレイピング"""
        logging.info("子育て情報のスクレイピングを開始")
        
        for source_id, source in self.childcare_sources.items():
            try:
                logging.info(f"{source['name']} をスクレイピング中...")
                
                # 実際のスクレイピング処理
                # ここではサンプルデータを生成
                sample_childcare = self.generate_sample_childcare_info(source_id, source)
                
                for childcare in sample_childcare:
                    self.save_childcare_info(childcare)
                    self.stats['childcare_info'] += 1
                
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"{source['name']} のスクレイピングでエラー: {e}")
        
        logging.info(f"子育て情報スクレイピング完了: {self.stats['childcare_info']}件")
    
    def scrape_tourism_info(self):
        """観光情報のスクレイピング"""
        logging.info("観光情報のスクレイピングを開始")
        
        for source_id, source in self.tourism_sources.items():
            try:
                logging.info(f"{source['name']} をスクレイピング中...")
                
                # 実際のスクレイピング処理
                # ここではサンプルデータを生成
                sample_tourism = self.generate_sample_tourism_info(source_id, source)
                
                for tourism in sample_tourism:
                    self.save_tourism_info(tourism)
                    self.stats['tourism_info'] += 1
                
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"{source['name']} のスクレイピングでエラー: {e}")
        
        logging.info(f"観光情報スクレイピング完了: {self.stats['tourism_info']}件")
    
    def scrape_culture_info(self):
        """文化施設情報のスクレイピング"""
        logging.info("文化施設情報のスクレイピングを開始")
        
        for source_id, source in self.culture_sources.items():
            try:
                logging.info(f"{source['name']} をスクレイピング中...")
                
                # 実際のスクレイピング処理
                # ここではサンプルデータを生成
                sample_culture = self.generate_sample_culture_info(source_id, source)
                
                for culture in sample_culture:
                    self.save_culture_info(culture)
                    self.stats['culture_info'] += 1
                
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"{source['name']} のスクレイピングでエラー: {e}")
        
        logging.info(f"文化施設情報スクレイピング完了: {self.stats['culture_info']}件")
    
    def generate_sample_seasonal_events(self, source_id, source):
        """季節イベントのサンプルデータ生成"""
        current_month = datetime.now().month
        
        if current_month in [3, 4]:  # 春
            return [
                {
                    'title': f"{source['name']} 桜祭り2025",
                    'description': '美しい桜の下で開催される春の祭り。屋台やステージイベントも楽しめます。',
                    'date': '2025-04-05',
                    'location': '市内各所',
                    'category': '季節イベント',
                    'city': source['name'].replace('季節イベント', ''),
                    'source_url': source['url']
                }
            ]
        elif current_month in [7, 8]:  # 夏
            return [
                {
                    'title': f"{source['name']} 花火大会2025",
                    'description': '夏の夜空を彩る美しい花火大会。家族で楽しめる夏の風物詩です。',
                    'date': '2025-08-15',
                    'location': '河川敷',
                    'category': '季節イベント',
                    'city': source['name'].replace('季節イベント', ''),
                    'source_url': source['url']
                }
            ]
        elif current_month in [10, 11]:  # 秋
            return [
                {
                    'title': f"{source['name']} 収穫祭2025",
                    'description': '地域の特産品を楽しめる収穫祭。新鮮な野菜や果物が並びます。',
                    'date': '2025-11-03',
                    'location': '市民広場',
                    'category': '季節イベント',
                    'city': source['name'].replace('季節イベント', ''),
                    'source_url': source['url']
                }
            ]
        else:  # 冬
            return [
                {
                    'title': f"{source['name']} イルミネーション2025",
                    'description': '冬の夜を彩る美しいイルミネーション。ロマンチックな雰囲気を楽しめます。',
                    'date': '2025-12-20',
                    'location': '駅前広場',
                    'category': '季節イベント',
                    'city': source['name'].replace('季節イベント', ''),
                    'source_url': source['url']
                }
            ]
    
    def generate_sample_food_info(self, source_id, source):
        """グルメ情報のサンプルデータ生成"""
        return [
            {
                'title': f"{source['name']} 新規オープン店舗情報",
                'description': '地域の新しい飲食店情報をお届けします。',
                'location': '市内各所',
                'category': 'グルメ',
                'city': source['name'].replace('グルメ情報', ''),
                'source_url': source['url']
            }
        ]
    
    def generate_sample_childcare_info(self, source_id, source):
        """子育て情報のサンプルデータ生成"""
        return [
            {
                'title': f"{source['name']} 子育て支援イベント",
                'description': '子育て中の方々をサポートする各種イベント情報です。',
                'date': '2025-09-15',
                'location': '子育て支援センター',
                'category': '子育て',
                'city': source['name'].replace('子育て支援', ''),
                'source_url': source['url']
            }
        ]
    
    def generate_sample_tourism_info(self, source_id, source):
        """観光情報のサンプルデータ生成"""
        return [
            {
                'title': f"{source['name']} 観光スポット情報",
                'description': '地域の観光スポットや名所の情報をお届けします。',
                'location': '市内各所',
                'category': '観光',
                'city': source['name'].replace('観光情報', ''),
                'source_url': source['url']
            }
        ]
    
    def generate_sample_culture_info(self, source_id, source):
        """文化施設情報のサンプルデータ生成"""
        return [
            {
                'title': f"{source['name']} 文化施設イベント",
                'description': '博物館、美術館、図書館などの文化施設のイベント情報です。',
                'date': '2025-10-20',
                'location': '文化センター',
                'category': '文化',
                'city': source['name'].replace('文化施設', ''),
                'source_url': source['url']
            }
        ]
    
    def save_seasonal_event(self, event):
        """季節イベントをデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO seasonal_events 
            (title, description, date, location, category, city, source_url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (event['title'], event['description'], event['date'], 
              event['location'], event['category'], event['city'], event['source_url']))
        
        conn.commit()
        conn.close()
    
    def save_food_info(self, food):
        """グルメ情報をデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO food_info 
            (title, description, location, category, city, source_url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (food['title'], food['description'], food['location'], 
              food['category'], food['city'], food['source_url']))
        
        conn.commit()
        conn.close()
    
    def save_childcare_info(self, childcare):
        """子育て情報をデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO childcare_info 
            (title, description, date, location, category, city, source_url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (childcare['title'], childcare['description'], childcare['date'], 
              childcare['location'], childcare['category'], childcare['city'], childcare['source_url']))
        
        conn.commit()
        conn.close()
    
    def save_tourism_info(self, tourism):
        """観光情報をデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO tourism_info 
            (title, description, location, category, city, source_url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (tourism['title'], tourism['description'], tourism['location'], 
              tourism['category'], tourism['city'], tourism['source_url']))
        
        conn.commit()
        conn.close()
    
    def save_culture_info(self, culture):
        """文化施設情報をデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO culture_info 
            (title, description, date, location, category, city, source_url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (culture['title'], culture['description'], culture['date'], 
              culture['location'], culture['category'], culture['city'], culture['source_url']))
        
        conn.commit()
        conn.close()
    
    def export_to_json(self):
        """データベースの内容をJSONファイルにエクスポート"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 各テーブルのデータを取得
        cursor.execute('SELECT * FROM seasonal_events ORDER BY created_at DESC LIMIT 20')
        seasonal_events = cursor.fetchall()
        
        cursor.execute('SELECT * FROM food_info ORDER BY created_at DESC LIMIT 20')
        food_info = cursor.fetchall()
        
        cursor.execute('SELECT * FROM childcare_info ORDER BY created_at DESC LIMIT 20')
        childcare_info = cursor.fetchall()
        
        cursor.execute('SELECT * FROM tourism_info ORDER BY created_at DESC LIMIT 20')
        tourism_info = cursor.fetchall()
        
        cursor.execute('SELECT * FROM culture_info ORDER BY created_at DESC LIMIT 20')
        culture_info = cursor.fetchall()
        
        conn.close()
        
        # JSONファイルに出力
        content_data = {
            'seasonal_events': [
                {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'date': row[3],
                    'location': row[4],
                    'category': row[5],
                    'city': row[6],
                    'source_url': row[7],
                    'created_at': row[8]
                } for row in seasonal_events
            ],
            'food_info': [
                {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'location': row[3],
                    'category': row[4],
                    'city': row[5],
                    'source_url': row[6],
                    'created_at': row[7]
                } for row in food_info
            ],
            'childcare_info': [
                {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'date': row[3],
                    'location': row[4],
                    'category': row[5],
                    'city': row[6],
                    'source_url': row[7],
                    'created_at': row[8]
                } for row in childcare_info
            ],
            'tourism_info': [
                {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'location': row[3],
                    'category': row[4],
                    'city': row[5],
                    'source_url': row[6],
                    'created_at': row[7]
                } for row in tourism_info
            ],
            'culture_info': [
                {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'date': row[3],
                    'location': row[4],
                    'category': row[5],
                    'city': row[6],
                    'source_url': row[7],
                    'created_at': row[8]
                } for row in culture_info
            ],
            'stats': self.stats,
            'timestamp': datetime.now().isoformat()
        }
        
        with open('api/content.json', 'w', encoding='utf-8') as f:
            json.dump(content_data, f, ensure_ascii=False, indent=2)
        
        logging.info("コンテンツデータをJSONファイルにエクスポート完了")
    
    def run_full_update(self):
        """全コンテンツの更新を実行"""
        logging.info("全コンテンツの自動更新を開始")
        
        try:
            self.scrape_seasonal_events()
            self.scrape_food_info()
            self.scrape_childcare_info()
            self.scrape_tourism_info()
            self.scrape_culture_info()
            
            self.export_to_json()
            
            self.stats['last_run'] = datetime.now().isoformat()
            logging.info("全コンテンツの自動更新完了")
            
        except Exception as e:
            logging.error(f"自動更新でエラーが発生: {e}")
    
    def schedule_updates(self):
        """定期更新のスケジュール設定"""
        # 毎日午前6時に実行
        schedule.every().day.at("06:00").do(self.run_full_update)
        
        # 毎週月曜日の午前9時に実行
        schedule.every().monday.at("09:00").do(self.run_full_update)
        
        logging.info("定期更新スケジュールを設定しました")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    updater = ContentAutoUpdater()
    
    # 初回実行
    updater.run_full_update()
    
    # 定期更新を開始（コメントアウトで無効化可能）
    # updater.schedule_updates()


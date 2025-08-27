import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import re
import time
import logging
import json
import os
from urllib.parse import urljoin, urlparse
import random

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_content_scraper_v2.log'),
        logging.StreamHandler()
    ]
)

class RealContentScraperV2:
    def __init__(self):
        self.db_path = 'real_content_v2.db'
        self.init_database()
        
        # 実際のスクレイピング対象サイト（正しいURL構造）
        self.scraping_sources = {
            'tsukuba_city': {
                'base_url': 'https://www.city.tsukuba.lg.jp/',
                'name': 'つくば市',
                'event_url': 'https://www.city.tsukuba.lg.jp/kankobunka/event/',
                'culture_url': 'https://www.city.tsukuba.lg.jp/kankobunka/',
                'childcare_url': 'https://www.city.tsukuba.lg.jp/kosodate/',
                'tourism_url': 'https://www.city.tsukuba.lg.jp/kankobunka/'
            },
            'tsukubamirai_city': {
                'base_url': 'https://www.city.tsukubamirai.lg.jp/',
                'name': 'つくばみらい市',
                'event_url': 'https://www.city.tsukubamirai.lg.jp/miraidaira-shimin-center/machidukuri/event-kouza/',
                'culture_url': 'https://www.city.tsukubamirai.lg.jp/',
                'childcare_url': 'https://www.city.tsukubamirai.lg.jp/',
                'tourism_url': 'https://www.city.tsukubamirai.lg.jp/'
            },
            'moriya_city': {
                'base_url': 'https://www.city.moriya.ibaraki.jp/',
                'name': '守谷市',
                'event_url': 'https://www.city.moriya.ibaraki.jp/',
                'culture_url': 'https://www.city.moriya.ibaraki.jp/',
                'childcare_url': 'https://www.city.moriya.ibaraki.jp/',
                'tourism_url': 'https://www.city.moriya.ibaraki.jp/'
            },
            'toride_city': {
                'base_url': 'https://www.city.toride.ibaraki.jp/',
                'name': '取手市',
                'event_url': 'https://www.city.toride.ibaraki.jp/',
                'culture_url': 'https://www.city.toride.ibaraki.jp/',
                'childcare_url': 'https://www.city.toride.ibaraki.jp/',
                'tourism_url': 'https://www.city.toride.ibaraki.jp/'
            }
        }
        
        # ヘッダー設定（ブロック回避）
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
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
    
    def get_page_content(self, url):
        """ページコンテンツを取得"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            logging.error(f"ページ取得エラー {url}: {e}")
            return None
    
    def extract_seasonal_events(self, city_id, source):
        """季節イベントを抽出"""
        logging.info(f"{source['name']} の季節イベントをスクレイピング中...")
        
        try:
            content = self.get_page_content(source['event_url'])
            if not content:
                return []
            
            soup = BeautifulSoup(content, 'html.parser')
            events = []
            
            # イベントリンクを検索
            event_links = soup.find_all('a', href=True)
            
            for link in event_links:
                href = link.get('href')
                title = link.get_text(strip=True)
                
                # 季節イベントのキーワードでフィルタリング
                seasonal_keywords = ['桜', '花火', '祭り', 'フェスティバル', 'マルシェ', '収穫祭', 'イルミネーション', 'イベント']
                
                if any(keyword in title for keyword in seasonal_keywords) and len(title) > 5:
                    # 詳細ページを取得
                    detail_url = urljoin(source['base_url'], href)
                    detail_content = self.get_page_content(detail_url)
                    
                    if detail_content:
                        detail_soup = BeautifulSoup(detail_content, 'html.parser')
                        
                        # 日付を抽出
                        date_text = self.extract_date(detail_soup)
                        
                        # 場所を抽出
                        location = self.extract_location(detail_soup)
                        
                        # 説明を抽出
                        description = self.extract_description(detail_soup)
                        
                        event = {
                            'title': title,
                            'description': description or f"{source['name']}で開催される{title}です。",
                            'date': date_text,
                            'location': location or '市内各所',
                            'category': '季節イベント',
                            'city': source['name'],
                            'source_url': detail_url
                        }
                        
                        events.append(event)
                        self.stats['seasonal_events'] += 1
                        
                        # レート制限対策
                        time.sleep(random.uniform(1, 2))
            
            return events
            
        except Exception as e:
            logging.error(f"{source['name']} の季節イベント抽出でエラー: {e}")
            return []
    
    def extract_food_info(self, city_id, source):
        """グルメ情報を抽出"""
        logging.info(f"{source['name']} のグルメ情報をスクレイピング中...")
        
        try:
            # 飲食店関連のページを検索
            food_events = []
            
            # イベントページから飲食関連の情報を抽出
            content = self.get_page_content(source['event_url'])
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                
                food_keywords = ['飲食', 'グルメ', 'カフェ', 'レストラン', '居酒屋', 'ラーメン', '新規オープン', '店舗']
                
                for link in soup.find_all('a', href=True):
                    title = link.get_text(strip=True)
                    
                    if any(keyword in title for keyword in food_keywords) and len(title) > 5:
                        detail_url = urljoin(source['base_url'], link.get('href'))
                        
                        food_info = {
                            'title': title,
                            'description': f"{source['name']}の新しいグルメ情報です。",
                            'location': '市内各所',
                            'category': 'グルメ',
                            'city': source['name'],
                            'source_url': detail_url
                        }
                        
                        food_events.append(food_info)
                        self.stats['food_info'] += 1
            
            return food_events
            
        except Exception as e:
            logging.error(f"{source['name']} のグルメ情報抽出でエラー: {e}")
            return []
    
    def extract_childcare_info(self, city_id, source):
        """子育て情報を抽出"""
        logging.info(f"{source['name']} の子育て情報をスクレイピング中...")
        
        try:
            content = self.get_page_content(source['childcare_url'])
            if not content:
                return []
            
            soup = BeautifulSoup(content, 'html.parser')
            childcare_events = []
            
            # 子育て関連のリンクを検索
            childcare_links = soup.find_all('a', href=True)
            
            for link in childcare_links:
                title = link.get_text(strip=True)
                href = link.get('href')
                
                childcare_keywords = ['子育て', '育児', '保育', '児童館', '子育て支援', '親子', '子ども']
                
                if any(keyword in title for keyword in childcare_keywords) and len(title) > 5:
                    detail_url = urljoin(source['base_url'], href)
                    detail_content = self.get_page_content(detail_url)
                    
                    if detail_content:
                        detail_soup = BeautifulSoup(detail_content, 'html.parser')
                        
                        date_text = self.extract_date(detail_soup)
                        location = self.extract_location(detail_soup)
                        description = self.extract_description(detail_soup)
                        
                        childcare_info = {
                            'title': title,
                            'description': description or f"{source['name']}の子育て支援情報です。",
                            'date': date_text,
                            'location': location or '子育て支援センター',
                            'category': '子育て',
                            'city': source['name'],
                            'source_url': detail_url
                        }
                        
                        childcare_events.append(childcare_info)
                        self.stats['childcare_info'] += 1
                        
                        time.sleep(random.uniform(1, 2))
            
            return childcare_events
            
        except Exception as e:
            logging.error(f"{source['name']} の子育て情報抽出でエラー: {e}")
            return []
    
    def extract_tourism_info(self, city_id, source):
        """観光情報を抽出"""
        logging.info(f"{source['name']} の観光情報をスクレイピング中...")
        
        try:
            content = self.get_page_content(source['tourism_url'])
            if not content:
                return []
            
            soup = BeautifulSoup(content, 'html.parser')
            tourism_events = []
            
            # 観光関連のリンクを検索
            tourism_links = soup.find_all('a', href=True)
            
            for link in tourism_links:
                title = link.get_text(strip=True)
                href = link.get('href')
                
                tourism_keywords = ['観光', '観光地', '観光スポット', '名所', '史跡', '公園', '見学']
                
                if any(keyword in title for keyword in tourism_keywords) and len(title) > 5:
                    detail_url = urljoin(source['base_url'], href)
                    detail_content = self.get_page_content(detail_url)
                    
                    if detail_content:
                        detail_soup = BeautifulSoup(detail_content, 'html.parser')
                        
                        location = self.extract_location(detail_soup)
                        description = self.extract_description(detail_soup)
                        
                        tourism_info = {
                            'title': title,
                            'description': description or f"{source['name']}の観光スポット情報です。",
                            'location': location or '市内各所',
                            'category': '観光',
                            'city': source['name'],
                            'source_url': detail_url
                        }
                        
                        tourism_events.append(tourism_info)
                        self.stats['tourism_info'] += 1
                        
                        time.sleep(random.uniform(1, 2))
            
            return tourism_events
            
        except Exception as e:
            logging.error(f"{source['name']} の観光情報抽出でエラー: {e}")
            return []
    
    def extract_culture_info(self, city_id, source):
        """文化施設情報を抽出"""
        logging.info(f"{source['name']} の文化施設情報をスクレイピング中...")
        
        try:
            content = self.get_page_content(source['culture_url'])
            if not content:
                return []
            
            soup = BeautifulSoup(content, 'html.parser')
            culture_events = []
            
            # 文化施設関連のリンクを検索
            culture_links = soup.find_all('a', href=True)
            
            for link in culture_links:
                title = link.get_text(strip=True)
                href = link.get('href')
                
                culture_keywords = ['博物館', '美術館', '図書館', '文化センター', '展示', '企画展', '講座', 'セミナー']
                
                if any(keyword in title for keyword in culture_keywords) and len(title) > 5:
                    detail_url = urljoin(source['base_url'], href)
                    detail_content = self.get_page_content(detail_url)
                    
                    if detail_content:
                        detail_soup = BeautifulSoup(detail_content, 'html.parser')
                        
                        date_text = self.extract_date(detail_soup)
                        location = self.extract_location(detail_soup)
                        description = self.extract_description(detail_soup)
                        
                        culture_info = {
                            'title': title,
                            'description': description or f"{source['name']}の文化施設情報です。",
                            'date': date_text,
                            'location': location or '文化センター',
                            'category': '文化',
                            'city': source['name'],
                            'source_url': detail_url
                        }
                        
                        culture_events.append(culture_info)
                        self.stats['culture_info'] += 1
                        
                        time.sleep(random.uniform(1, 2))
            
            return culture_events
            
        except Exception as e:
            logging.error(f"{source['name']} の文化施設情報抽出でエラー: {e}")
            return []
    
    def extract_date(self, soup):
        """日付を抽出"""
        # 日付パターンを検索
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{1,2})月(\d{1,2})日',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{1,2})/(\d{1,2})'
        ]
        
        text = soup.get_text()
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 3:
                    year, month, day = match.groups()
                    if len(year) == 2:
                        year = '2025'  # 年が2桁の場合は2025年と仮定
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                elif len(match.groups()) == 2:
                    month, day = match.groups()
                    return f"2025-{month.zfill(2)}-{day.zfill(2)}"
        
        return None
    
    def extract_location(self, soup):
        """場所を抽出"""
        # 場所を示すキーワードを検索
        location_keywords = ['場所', '会場', '所在地', '住所']
        
        for keyword in location_keywords:
            elements = soup.find_all(string=re.compile(keyword))
            for element in elements:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    # 場所の情報を抽出
                    location_match = re.search(r'[場所|会場|所在地|住所][：:]\s*(.+)', text)
                    if location_match:
                        return location_match.group(1).strip()
        
        return None
    
    def extract_description(self, soup):
        """説明を抽出"""
        # 説明文を検索
        description_selectors = [
            'p',
            '.description',
            '.content',
            '.text'
        ]
        
        for selector in description_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 20 and len(text) < 500:  # 適切な長さの説明文
                    return text
        
        return None
    
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
        
        logging.info("実際のコンテンツデータをJSONファイルにエクスポート完了")
    
    def run_real_scraping(self):
        """実際のスクレイピングを実行"""
        logging.info("実際の最新情報のスクレイピングを開始")
        
        try:
            for city_id, source in self.scraping_sources.items():
                logging.info(f"=== {source['name']} の情報を取得中 ===")
                
                # 季節イベント
                seasonal_events = self.extract_seasonal_events(city_id, source)
                for event in seasonal_events:
                    self.save_seasonal_event(event)
                
                # グルメ情報
                food_info = self.extract_food_info(city_id, source)
                for food in food_info:
                    self.save_food_info(food)
                
                # 子育て情報
                childcare_info = self.extract_childcare_info(city_id, source)
                for childcare in childcare_info:
                    self.save_childcare_info(childcare)
                
                # 観光情報
                tourism_info = self.extract_tourism_info(city_id, source)
                for tourism in tourism_info:
                    self.save_tourism_info(tourism)
                
                # 文化施設情報
                culture_info = self.extract_culture_info(city_id, source)
                for culture in culture_info:
                    self.save_culture_info(culture)
                
                # 都市間の待機時間
                time.sleep(random.uniform(3, 5))
            
            self.export_to_json()
            
            self.stats['last_run'] = datetime.now().isoformat()
            logging.info(f"実際のスクレイピング完了: 季節イベント{self.stats['seasonal_events']}件, グルメ{self.stats['food_info']}件, 子育て{self.stats['childcare_info']}件, 観光{self.stats['tourism_info']}件, 文化{self.stats['culture_info']}件")
            
        except Exception as e:
            logging.error(f"実際のスクレイピングでエラーが発生: {e}")

if __name__ == "__main__":
    scraper = RealContentScraperV2()
    scraper.run_real_scraping()


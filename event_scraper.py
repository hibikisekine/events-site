import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import re
import time
import schedule
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import json
import os

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class EventScraper:
    def __init__(self):
        self.db_path = 'events.db'
        self.init_database()
        
        # スクレイピング対象サイト
        self.sources = {
            'tsukubamirai_city': {
                'url': 'https://www.city.tsukubamirai.lg.jp/',
                'name': 'つくばみらい市役所',
                'event_page': 'https://www.city.tsukubamirai.lg.jp/soshiki/1/event.html',
                'keywords': ['イベント', '行事', '催し', '講座', 'セミナー']
            },
            'tsukuba_city': {
                'url': 'https://www.city.tsukuba.lg.jp/',
                'name': 'つくば市役所',
                'event_page': 'https://www.city.tsukuba.lg.jp/soshiki/1/event.html',
                'keywords': ['イベント', '行事', '催し', '講座', 'セミナー']
            },
            'moriya_city': {
                'url': 'https://www.city.moriya.ibaraki.jp/',
                'name': '守谷市役所',
                'event_page': 'https://www.city.moriya.ibaraki.jp/soshiki/1/event.html',
                'keywords': ['イベント', '行事', '催し', '講座', 'セミナー']
            },
            'toride_city': {
                'url': 'https://www.city.toride.ibaraki.jp/',
                'name': '取手市役所',
                'event_page': 'https://www.city.toride.ibaraki.jp/soshiki/1/event.html',
                'keywords': ['イベント', '行事', '催し', '講座', 'セミナー']
            },
            'joso_city': {
                'url': 'https://www.city.joso.lg.jp/',
                'name': '常総市役所',
                'event_page': 'https://www.city.joso.lg.jp/soshiki/1/event.html',
                'keywords': ['イベント', '行事', '催し', '講座', 'セミナー']
            },
            'ryugasaki_city': {
                'url': 'https://www.city.ryugasaki.ibaraki.jp/',
                'name': '龍ケ崎市役所',
                'event_page': 'https://www.city.ryugasaki.ibaraki.jp/soshiki/1/event.html',
                'keywords': ['イベント', '行事', '催し', '講座', 'セミナー']
            },
            'koga_city': {
                'url': 'https://www.city.koga.ibaraki.jp/',
                'name': '古河市役所',
                'event_page': 'https://www.city.koga.ibaraki.jp/soshiki/1/event.html',
                'keywords': ['イベント', '行事', '催し', '講座', 'セミナー']
            },
            'bando_city': {
                'url': 'https://www.city.bando.ibaraki.jp/',
                'name': '坂東市役所',
                'event_page': 'https://www.city.bando.ibaraki.jp/soshiki/1/event.html',
                'keywords': ['イベント', '行事', '催し', '講座', 'セミナー']
            }
        }
        
        # スクレイピング統計
        self.stats = {
            'total_events': 0,
            'new_events': 0,
            'updated_events': 0,
            'errors': 0,
            'last_run': None
        }
    
    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT,
                time TEXT,
                location TEXT,
                category TEXT,
                is_indoor BOOLEAN,
                is_free BOOLEAN,
                has_parking BOOLEAN,
                child_friendly BOOLEAN,
                weather_dependent BOOLEAN,
                rain_cancellation TEXT,
                source_url TEXT,
                source_city TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_city TEXT,
                events_found INTEGER,
                events_added INTEGER,
                events_updated INTEGER,
                errors INTEGER,
                duration_seconds REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("データベース初期化完了")
    
    def schedule_scraping(self):
        """スクレイピングスケジュール設定"""
        # 毎日午前6時に実行
        schedule.every().day.at("06:00").do(self.daily_scraping)
        
        # 週1回（日曜日）に全データ更新
        schedule.every().sunday.at("03:00").do(self.weekly_full_update)
        
        # 毎時間に軽量チェック
        schedule.every().hour.do(self.hourly_check)
        
        logging.info("スクレイピングスケジュール設定完了")
    
    def daily_scraping(self):
        """毎日のスクレイピング実行"""
        logging.info("毎日スクレイピング開始")
        start_time = time.time()
        
        try:
            all_events = []
            
            for source_id, source_info in self.sources.items():
                try:
                    logging.info(f"{source_info['name']}からイベント情報を取得中...")
                    events = self.scrape_city_website(source_id, source_info)
                    all_events.extend(events)
                    
                    # サーバーに負荷をかけないよう待機
                    time.sleep(3)
                    
                except Exception as e:
                    logging.error(f"{source_info['name']}のスクレイピングエラー: {e}")
                    self.stats['errors'] += 1
            
            # データベースに保存
            self.save_events_to_db(all_events)
            
            duration = time.time() - start_time
            self.log_scraping_run(duration)
            
            logging.info(f"毎日スクレイピング完了: {len(all_events)}件のイベントを処理")
            
        except Exception as e:
            logging.error(f"毎日スクレイピングエラー: {e}")
    
    def weekly_full_update(self):
        """週1回の全データ更新"""
        logging.info("週次フルアップデート開始")
        
        try:
            # 古いイベントを非アクティブ化
            self.deactivate_old_events()
            
            # 全ソースから最新データを取得
            self.daily_scraping()
            
            # データベースの最適化
            self.optimize_database()
            
            logging.info("週次フルアップデート完了")
            
        except Exception as e:
            logging.error(f"週次フルアップデートエラー: {e}")
    
    def hourly_check(self):
        """毎時間の軽量チェック"""
        logging.info("時間次チェック実行")
        
        try:
            # 最新のイベントのみをチェック
            for source_id, source_info in list(self.sources.items())[:3]:  # 最初の3都市のみ
                try:
                    events = self.scrape_city_website(source_id, source_info, limit=5)
                    if events:
                        self.save_events_to_db(events)
                        logging.info(f"{source_info['name']}: {len(events)}件の新規イベント")
                    
                    time.sleep(1)
                    
                except Exception as e:
                    logging.warning(f"{source_info['name']}の時間次チェックエラー: {e}")
            
        except Exception as e:
            logging.error(f"時間次チェックエラー: {e}")
    
    def scrape_city_website(self, source_id, source_info, limit=None):
        """市役所ウェブサイトからイベント情報をスクレイピング"""
        events = []
        
        try:
            # Selenium設定
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            
            # メインページからイベントリンクを探す
            event_links = self.find_event_links(driver, source_id, source_info)
            
            if limit:
                event_links = event_links[:limit]
            
            for link in event_links:
                try:
                    event_data = self.extract_event_data(driver, link, source_id, source_info)
                    if event_data and self.validate_event_data(event_data):
                        events.append(event_data)
                        
                except Exception as e:
                    logging.warning(f"イベントデータ抽出エラー: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logging.error(f"スクレイピングエラー ({source_info['name']}): {e}")
            self.stats['errors'] += 1
        
        return events
    
    def find_event_links(self, driver, source_id, source_info):
        """イベントページへのリンクを探す"""
        links = []
        
        try:
            # メインページにアクセス
            driver.get(source_info['url'])
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # ページ内のリンクを取得
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.lower()
                    
                    if href and any(keyword in text for keyword in source_info['keywords']):
                        links.append(href)
                        
                except Exception as e:
                    continue
            
            # イベント専用ページも試す
            if source_info.get('event_page'):
                try:
                    driver.get(source_info['event_page'])
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    event_page_links = driver.find_elements(By.TAG_NAME, 'a')
                    for link in event_page_links:
                        try:
                            href = link.get_attribute('href')
                            if href and href not in links:
                                links.append(href)
                        except Exception:
                            continue
                            
                except Exception as e:
                    logging.warning(f"イベントページアクセスエラー: {e}")
            
        except Exception as e:
            logging.error(f"リンク検索エラー: {e}")
        
        return list(set(links))  # 重複を除去
    
    def extract_event_data(self, driver, url, source_id, source_info):
        """イベントページからデータを抽出"""
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # ページのHTMLを取得
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # イベント情報を抽出
            event_data = {
                'title': self.extract_title(soup),
                'description': self.extract_description(soup),
                'date': self.extract_date(soup),
                'time': self.extract_time(soup),
                'location': self.extract_location(soup),
                'category': self.determine_category(soup),
                'is_indoor': self.determine_indoor(soup),
                'is_free': self.determine_free(soup),
                'has_parking': self.determine_parking(soup),
                'child_friendly': self.determine_child_friendly(soup),
                'weather_dependent': self.determine_weather_dependent(soup),
                'rain_cancellation': self.extract_rain_cancellation(soup),
                'source_url': url,
                'source_city': source_info['name']
            }
            
            return event_data if event_data['title'] else None
            
        except Exception as e:
            logging.warning(f"データ抽出エラー: {e}")
            return None
    
    def validate_event_data(self, event_data):
        """イベントデータの検証"""
        if not event_data.get('title'):
            return False
        
        # 日付の妥当性チェック
        if event_data.get('date'):
            try:
                datetime.strptime(event_data['date'], '%Y-%m-%d')
            except ValueError:
                return False
        
        return True
    
    def extract_title(self, soup):
        """タイトルを抽出"""
        selectors = [
            'h1', 'h2', '.title', '.event-title', '.page-title',
            '[class*="title"]', '[class*="event"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.text.strip():
                return element.text.strip()
        
        return None
    
    def extract_description(self, soup):
        """説明を抽出"""
        selectors = [
            '.description', '.content', '.event-description',
            '[class*="description"]', '[class*="content"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.text.strip():
                return element.text.strip()
        
        return ""
    
    def extract_date(self, soup):
        """日付を抽出"""
        # 日付パターンを検索
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{1,2})月(\d{1,2})日',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})'
        ]
        
        text = soup.get_text()
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 3:
                    if len(match.group(1)) == 4:  # 年が含まれている
                        year, month, day = match.groups()
                    else:  # 年が含まれていない
                        month, day, year = match.groups()
                else:
                    month, day = match.groups()
                    year = datetime.now().year
                
                return f"{year}-{int(month):02d}-{int(day):02d}"
        
        return None
    
    def extract_time(self, soup):
        """時間を抽出"""
        time_patterns = [
            r'(\d{1,2}):(\d{2})',
            r'(\d{1,2})時(\d{2})分'
        ]
        
        text = soup.get_text()
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                hour, minute = match.groups()
                return f"{int(hour):02d}:{minute}"
        
        return None
    
    def extract_location(self, soup):
        """場所を抽出"""
        location_keywords = ['場所', '会場', '所在地', 'address', 'location']
        
        for keyword in location_keywords:
            elements = soup.find_all(text=re.compile(keyword))
            for element in elements:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    if keyword in text:
                        # 場所情報を抽出
                        location_match = re.search(f'{keyword}[：:]\s*(.+)', text)
                        if location_match:
                            return location_match.group(1).strip()
        
        return ""
    
    def determine_category(self, soup):
        """カテゴリを判定"""
        text = soup.get_text().lower()
        
        categories = {
            '文化': ['文化', '芸術', '美術', '音楽', '演劇', 'コンサート'],
            'スポーツ': ['スポーツ', '運動', '体育', 'フィットネス', 'ジム'],
            '教育': ['教育', '講座', 'セミナー', '学習', '勉強'],
            '子育て': ['子育て', '育児', '子供', '親子', 'ベビー'],
            '地域': ['地域', 'コミュニティ', '交流', '祭り', 'フェス']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'その他'
    
    def determine_indoor(self, soup):
        """屋内/屋外を判定"""
        text = soup.get_text().lower()
        
        indoor_keywords = ['屋内', '室内', '会館', 'ホール', 'センター', '施設']
        outdoor_keywords = ['屋外', '野外', '公園', '広場', '屋上']
        
        if any(keyword in text for keyword in outdoor_keywords):
            return False
        elif any(keyword in text for keyword in indoor_keywords):
            return True
        
        return None
    
    def determine_free(self, soup):
        """無料/有料を判定"""
        text = soup.get_text().lower()
        
        free_keywords = ['無料', '参加費無料', '入場無料', 'free']
        paid_keywords = ['有料', '参加費', '入場料', '料金', 'チケット']
        
        if any(keyword in text for keyword in free_keywords):
            return True
        elif any(keyword in text for keyword in paid_keywords):
            return False
        
        return None
    
    def determine_parking(self, soup):
        """駐車場の有無を判定"""
        text = soup.get_text().lower()
        
        parking_keywords = ['駐車場', 'パーキング', 'parking', '車で']
        
        return any(keyword in text for keyword in parking_keywords)
    
    def determine_child_friendly(self, soup):
        """子連れ対応を判定"""
        text = soup.get_text().lower()
        
        child_keywords = ['子供', '親子', '子連れ', 'お子様', 'ベビー', 'キッズ']
        
        return any(keyword in text for keyword in child_keywords)
    
    def determine_weather_dependent(self, soup):
        """天候依存を判定"""
        text = soup.get_text().lower()
        
        weather_keywords = ['雨天', '天候', '天気', '雨', '晴れ', '曇り']
        
        return any(keyword in text for keyword in weather_keywords)
    
    def extract_rain_cancellation(self, soup):
        """雨の場合の対応を抽出"""
        text = soup.get_text().lower()
        
        if '雨天中止' in text or '雨で中止' in text:
            return '雨天中止'
        elif '雨天順延' in text or '雨で順延' in text:
            return '雨天順延'
        elif '雨天時' in text or '雨の場合' in text:
            return '雨天時要確認'
        
        return None
    
    def save_events_to_db(self, events):
        """イベントをデータベースに保存"""
        if not events:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_events = 0
        updated_events = 0
        
        for event in events:
            try:
                # 既存のイベントをチェック
                cursor.execute('''
                    SELECT id FROM events 
                    WHERE title = ? AND source_url = ?
                ''', (event['title'], event['source_url']))
                
                existing = cursor.fetchone()
                
                if existing:
                    # 既存イベントを更新
                    cursor.execute('''
                        UPDATE events SET
                            description = ?, date = ?, time = ?, location = ?,
                            category = ?, is_indoor = ?, is_free = ?, has_parking = ?,
                            child_friendly = ?, weather_dependent = ?, rain_cancellation = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (
                        event['description'], event['date'], event['time'], event['location'],
                        event['category'], event['is_indoor'], event['is_free'], event['has_parking'],
                        event['child_friendly'], event['weather_dependent'], event['rain_cancellation'],
                        existing[0]
                    ))
                    updated_events += 1
                else:
                    # 新規イベントを追加
                    cursor.execute('''
                        INSERT INTO events (
                            title, description, date, time, location, category,
                            is_indoor, is_free, has_parking, child_friendly,
                            weather_dependent, rain_cancellation, source_url, source_city
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event['title'], event['description'], event['date'], event['time'],
                        event['location'], event['category'], event['is_indoor'], event['is_free'],
                        event['has_parking'], event['child_friendly'], event['weather_dependent'],
                        event['rain_cancellation'], event['source_url'], event['source_city']
                    ))
                    new_events += 1
                
            except Exception as e:
                logging.error(f"イベント保存エラー: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        self.stats['new_events'] += new_events
        self.stats['updated_events'] += updated_events
        self.stats['total_events'] += len(events)
        
        logging.info(f"イベント保存完了: 新規{new_events}件, 更新{updated_events}件")
    
    def deactivate_old_events(self):
        """古いイベントを非アクティブ化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 30日以上前のイベントを非アクティブ化
        cursor.execute('''
            UPDATE events SET is_active = 0 
            WHERE date < date('now', '-30 days')
        ''')
        
        deactivated_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logging.info(f"古いイベントを非アクティブ化: {deactivated_count}件")
    
    def optimize_database(self):
        """データベースの最適化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('VACUUM')
        cursor.execute('ANALYZE')
        
        conn.close()
        logging.info("データベース最適化完了")
    
    def log_scraping_run(self, duration):
        """スクレイピング実行ログを記録"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scraping_log (
                source_city, events_found, events_added, events_updated, 
                errors, duration_seconds
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'all_cities', self.stats['total_events'], 
            self.stats['new_events'], self.stats['updated_events'],
            self.stats['errors'], duration
        ))
        
        conn.commit()
        conn.close()
    
    def get_active_events(self):
        """アクティブなイベントを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM events 
            WHERE is_active = 1 
            ORDER BY date ASC, created_at DESC
        ''')
        
        events = cursor.fetchall()
        conn.close()
        
        return events
    
    def run_scheduler(self):
        """スケジューラーを実行"""
        logging.info("スクレイピングスケジューラー開始")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1分ごとにチェック
            except KeyboardInterrupt:
                logging.info("スクレイピングスケジューラー停止")
                break
            except Exception as e:
                logging.error(f"スケジューラーエラー: {e}")
                time.sleep(300)  # エラー時は5分待機

if __name__ == "__main__":
    scraper = EventScraper()
    scraper.schedule_scraping()
    scraper.run_scheduler() 
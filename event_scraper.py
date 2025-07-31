import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EventScraper:
    def __init__(self):
        self.sources = {
            'tsukubamirai_city': {
                'url': 'https://www.city.tsukubamirai.lg.jp/',
                'name': 'つくばみらい市役所'
            },
            'tsukuba_city': {
                'url': 'https://www.city.tsukuba.lg.jp/',
                'name': 'つくば市役所'
            },
            'moriya_city': {
                'url': 'https://www.city.moriya.ibaraki.jp/',
                'name': '守谷市役所'
            },
            'joso_city': {
                'url': 'https://www.city.joso.lg.jp/',
                'name': '常総市役所'
            },
            'toride_city': {
                'url': 'https://www.city.toride.ibaraki.jp/',
                'name': '取手市役所'
            },
            'ryugasaki_city': {
                'url': 'https://www.city.ryugasaki.ibaraki.jp/',
                'name': '龍ケ崎市役所'
            },
            'koga_city': {
                'url': 'https://www.city.koga.ibaraki.jp/',
                'name': '古河市役所'
            },
            'bando_city': {
                'url': 'https://www.city.bando.ibaraki.jp/',
                'name': '坂東市役所'
            }
        }
        
    def scrape_all_sources(self):
        """全てのソースからイベント情報をスクレイピング"""
        all_events = []
        
        for source_id, source_info in self.sources.items():
            try:
                print(f"{source_info['name']}からイベント情報を取得中...")
                events = self.scrape_city_website(source_id, source_info)
                all_events.extend(events)
                time.sleep(2)  # サーバーに負荷をかけないよう待機
            except Exception as e:
                print(f"{source_info['name']}のスクレイピングエラー: {e}")
        
        # データベースに保存
        self.save_events_to_db(all_events)
        
        return all_events
    
    def scrape_city_website(self, source_id, source_info):
        """市役所ウェブサイトからイベント情報をスクレイピング"""
        events = []
        
        try:
            # Seleniumを使用してJavaScriptで動的に生成されるコンテンツを取得
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(source_info['url'])
            
            # イベントページへのリンクを探す
            event_links = self.find_event_links(driver, source_id)
            
            for link in event_links[:10]:  # 最初の10件を処理
                try:
                    event_data = self.extract_event_data(driver, link, source_id)
                    if event_data:
                        events.append(event_data)
                except Exception as e:
                    print(f"イベントデータ抽出エラー: {e}")
            
            driver.quit()
            
        except Exception as e:
            print(f"スクレイピングエラー: {e}")
        
        return events
    
    def find_event_links(self, driver, source_id):
        """イベントページへのリンクを探す"""
        links = []
        
        # 共通のイベント関連キーワード
        event_keywords = ['イベント', 'event', '行事', '催し', 'お知らせ', '講座', 'セミナー', 'ワークショップ', '体験', '見学会', '説明会']
        
        try:
            # ページ内のリンクを取得
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            
            for link in all_links:
                href = link.get_attribute('href')
                text = link.text.lower()
                
                if href and any(keyword in text for keyword in event_keywords):
                    links.append(href)
            
        except Exception as e:
            print(f"リンク検索エラー: {e}")
        
        return links
    
    def extract_event_data(self, driver, url, source_id):
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
                'source_url': url
            }
            
            return event_data if event_data['title'] else None
            
        except Exception as e:
            print(f"データ抽出エラー: {e}")
            return None
    
    def extract_title(self, soup):
        """タイトルを抽出"""
        # 様々なセレクタでタイトルを探す
        selectors = ['h1', 'h2', '.title', '.event-title', '.page-title']
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.text.strip():
                return element.text.strip()
        
        return "イベント"
    
    def extract_description(self, soup):
        """説明を抽出"""
        # 説明文を探す
        selectors = ['.description', '.content', '.event-description', 'p']
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.text.strip()
                if len(text) > 20:  # 十分な長さのテキスト
                    return text[:200]  # 200文字まで
        
        return ""
    
    def extract_date(self, soup):
        """日付を抽出"""
        # 日付パターンを探す
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
                        year = '20' + year
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                elif len(match.groups()) == 2:
                    month, day = match.groups()
                    current_year = datetime.now().year
                    return f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # デフォルトは今日
        return datetime.now().strftime('%Y-%m-%d')
    
    def extract_time(self, soup):
        """時間を抽出"""
        time_patterns = [
            r'(\d{1,2}):(\d{2})',
            r'(\d{1,2})時(\d{1,2})分'
        ]
        
        text = soup.get_text()
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                if ':' in pattern:
                    hour, minute = match.groups()
                else:
                    hour, minute = match.groups()
                return f"{hour.zfill(2)}:{minute.zfill(2)}"
        
        return ""
    
    def extract_location(self, soup):
        """場所を抽出"""
        location_keywords = ['場所', '会場', 'location', 'venue', '開催場所']
        
        text = soup.get_text()
        
        # 市名を検索
        city_names = ['つくばみらい市', 'つくば市', '守谷市', '常総市', '取手市', '龍ケ崎市', '古河市', '坂東市']
        found_city = None
        
        for city in city_names:
            if city in text:
                found_city = city
                break
        
        # 具体的な場所を検索
        for keyword in location_keywords:
            if keyword in text:
                # キーワードの前後のテキストを取得
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if keyword in line:
                        # 次の行や前の行から場所を特定
                        for j in range(max(0, i-2), min(len(lines), i+3)):
                            if lines[j].strip() and len(lines[j].strip()) > 3:
                                location = lines[j].strip()
                                # 市名が含まれている場合はそのまま返す
                                if found_city and found_city in location:
                                    return location
                                # 市名が見つかった場合は市名を付加
                                elif found_city:
                                    return f"{location}（{found_city}）"
                                else:
                                    return location
        
        # 市名が見つかった場合は市名を返す
        if found_city:
            return found_city
        
        return "未定"
    
    def determine_category(self, soup):
        """カテゴリを判定"""
        text = soup.get_text().lower()
        
        categories = {
            '文化': ['文化', '芸術', '美術', '音楽', 'コンサート'],
            'スポーツ': ['スポーツ', '運動', '体育', 'マラソン'],
            '子育て': ['子育て', '子供', '親子', '育児'],
            '教育': ['教育', '学習', '講座', 'セミナー'],
            '地域': ['地域', 'コミュニティ', '町内会'],
            'その他': []
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'その他'
    
    def determine_indoor(self, soup):
        """屋内イベントかどうかを判定"""
        text = soup.get_text().lower()
        indoor_keywords = ['屋内', '室内', '会館', 'ホール', '公民館', '図書館']
        outdoor_keywords = ['屋外', '野外', '公園', '広場', '運動場']
        
        if any(keyword in text for keyword in outdoor_keywords):
            return False
        elif any(keyword in text for keyword in indoor_keywords):
            return True
        
        return True  # デフォルトは屋内
    
    def determine_free(self, soup):
        """無料イベントかどうかを判定"""
        text = soup.get_text().lower()
        free_keywords = ['無料', '参加費無料', '入場無料']
        paid_keywords = ['有料', '参加費', '入場料', '料金']
        
        if any(keyword in text for keyword in free_keywords):
            return True
        elif any(keyword in text for keyword in paid_keywords):
            return False
        
        return True  # デフォルトは無料
    
    def determine_parking(self, soup):
        """駐車場の有無を判定"""
        text = soup.get_text().lower()
        parking_keywords = ['駐車場', 'parking', '車で']
        
        return any(keyword in text for keyword in parking_keywords)
    
    def determine_child_friendly(self, soup):
        """子連れOKかどうかを判定"""
        text = soup.get_text().lower()
        child_keywords = ['子供', '親子', '子育て', '家族', 'お子様']
        
        return any(keyword in text for keyword in child_keywords)
    
    def determine_weather_dependent(self, soup):
        """天候に依存するイベントかどうかを判定"""
        text = soup.get_text().lower()
        weather_keywords = ['雨天中止', '雨天順延', '天候', '雨の日']
        
        return any(keyword in text for keyword in weather_keywords)
    
    def extract_rain_cancellation(self, soup):
        """雨天時の対応を抽出"""
        text = soup.get_text().lower()
        
        if '雨天中止' in text:
            return '雨天中止'
        elif '雨天順延' in text:
            return '雨天順延'
        elif '小雨決行' in text:
            return '小雨決行'
        elif '雨でも開催' in text:
            return '雨でも開催'
        
        return ""
    
    def save_events_to_db(self, events):
        """イベントをデータベースに保存"""
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        
        for event in events:
            try:
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
            except Exception as e:
                print(f"イベント保存エラー: {e}")
        
        conn.commit()
        conn.close() 
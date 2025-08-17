import tweepy
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import re
import logging
from typing import List, Dict, Optional
from config import X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET, RESTAURANTS_DB

class RestaurantScraper:
    def __init__(self, db_path: str = RESTAURANTS_DB):
        self.db_path = db_path
        self.setup_logging()  # ログ設定を最初に実行
        self.init_database()
        
        # 検索キーワード（つくば市周辺）
        self.search_keywords = [
            "つくば 新規オープン",
            "つくば 開店",
            "つくばみらい 新規オープン", 
            "つくばみらい 開店",
            "守谷 新規オープン",
            "守谷 開店",
            "取手 新規オープン",
            "取手 開店",
            "常総 新規オープン",
            "常総 開店",
            "龍ヶ崎 新規オープン",
            "龍ヶ崎 開店"
        ]
        
        # 地域マッピング
        self.city_mapping = {
            "つくば": "つくば市",
            "つくばみらい": "つくばみらい市", 
            "守谷": "守谷市",
            "取手": "取手市",
            "常総": "常総市",
            "龍ヶ崎": "龍ヶ崎市"
        }

    def setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('restaurant_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                city TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                category TEXT,
                opening_date TEXT,
                source_url TEXT,
                source_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info("データベース初期化完了")

    def scrape_twitter_restaurants(self) -> List[Dict]:
        """Twitterから飲食店開店情報を取得"""
        try:
            # API認証情報の確認
            if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
                self.logger.error("X API認証情報が不完全です。config.pyを確認してください。")
                return []
            
            # Twitter API認証
            auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
            auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            
            restaurants = []
            
            for keyword in self.search_keywords:
                self.logger.info(f"キーワード検索中: {keyword}")
                
                try:
                    # 過去7日間のツイートを検索
                    tweets = api.search_tweets(
                        q=keyword,
                        lang="ja",
                        count=100,
                        tweet_mode="extended"
                    )
                    
                    for tweet in tweets:
                        restaurant_info = self.extract_restaurant_info(tweet.full_text, keyword)
                        if restaurant_info:
                            restaurant_info['source_url'] = f"https://twitter.com/user/status/{tweet.id}"
                            restaurant_info['source_type'] = 'twitter'
                            restaurants.append(restaurant_info)
                            self.logger.info(f"飲食店情報を抽出: {restaurant_info['name']}")
                
                except Exception as e:
                    self.logger.error(f"キーワード '{keyword}' の検索でエラー: {e}")
                    continue
            
            self.logger.info(f"合計 {len(restaurants)} 件の飲食店情報を取得")
            return restaurants
            
        except Exception as e:
            self.logger.error(f"Twitter取得エラー: {e}")
            return []

    def extract_restaurant_info(self, text: str, keyword: str) -> Optional[Dict]:
        """ツイートから飲食店情報を抽出"""
        try:
            # 店舗名の抽出パターン
            name_patterns = [
                r'「([^」]+)」.*(?:オープン|開店)',
                r'([^、。\s]+店).*(?:オープン|開店)',
                r'([^、。\s]+レストラン).*(?:オープン|開店)',
                r'([^、。\s]+カフェ).*(?:オープン|開店)',
                r'([^、。\s]+居酒屋).*(?:オープン|開店)'
            ]
            
            # 住所の抽出パターン
            address_patterns = [
                r'([^、。\s]+市[^、。\s]+)',
                r'([^、。\s]+県[^、。\s]+)',
                r'([^、。\s]+駅[^、。\s]+)'
            ]
            
            # 開店日の抽出パターン
            date_patterns = [
                r'(\d{1,2}月\d{1,2}日).*(?:オープン|開店)',
                r'(\d{4}年\d{1,2}月\d{1,2}日).*(?:オープン|開店)',
                r'(\d{1,2}/\d{1,2}).*(?:オープン|開店)'
            ]
            
            # 店舗名を抽出
            restaurant_name = None
            for pattern in name_patterns:
                match = re.search(pattern, text)
                if match:
                    restaurant_name = match.group(1)
                    break
            
            if not restaurant_name:
                return None
            
            # 住所を抽出
            address = None
            for pattern in address_patterns:
                match = re.search(pattern, text)
                if match:
                    address = match.group(1)
                    break
            
            # 開店日を抽出
            opening_date = None
            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    opening_date = match.group(1)
                    break
            
            # 地域を特定
            city = self.extract_city(keyword)
            
            # カテゴリを推定
            category = self.estimate_category(text)
            
            return {
                'name': restaurant_name,
                'description': text[:200] + '...' if len(text) > 200 else text,
                'city': city,
                'address': address,
                'category': category,
                'opening_date': opening_date
            }
            
        except Exception as e:
            self.logger.error(f"情報抽出エラー: {e}")
            return None

    def extract_city(self, keyword: str) -> str:
        """キーワードから地域を抽出"""
        for city_key, city_name in self.city_mapping.items():
            if city_key in keyword:
                return city_name
        return "その他"

    def estimate_category(self, text: str) -> str:
        """テキストからカテゴリを推定"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['カフェ', 'コーヒー', 'ティー']):
            return 'カフェ'
        elif any(word in text_lower for word in ['居酒屋', 'バー', '酒場']):
            return '居酒屋・バー'
        elif any(word in text_lower for word in ['ラーメン', 'うどん', 'そば']):
            return '麺類'
        elif any(word in text_lower for word in ['寿司', '刺身', '和食']):
            return '和食'
        elif any(word in text_lower for word in ['イタリアン', 'パスタ', 'ピザ']):
            return 'イタリアン'
        elif any(word in text_lower for word in ['中華', '餃子', '麻婆']):
            return '中華'
        elif any(word in text_lower for word in ['焼肉', '韓国', 'キムチ']):
            return '焼肉・韓国料理'
        else:
            return 'その他'

    def save_restaurants(self, restaurants: List[Dict]):
        """飲食店情報をデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_count = 0
        updated_count = 0
        
        for restaurant in restaurants:
            # 既存の店舗かチェック
            cursor.execute('''
                SELECT id FROM restaurants 
                WHERE name = ? AND city = ?
            ''', (restaurant['name'], restaurant['city']))
            
            existing = cursor.fetchone()
            
            if existing:
                # 既存の店舗を更新
                cursor.execute('''
                    UPDATE restaurants SET
                        description = ?,
                        address = ?,
                        phone = ?,
                        category = ?,
                        opening_date = ?,
                        source_url = ?,
                        source_type = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    restaurant.get('description'),
                    restaurant.get('address'),
                    restaurant.get('phone'),
                    restaurant.get('category'),
                    restaurant.get('opening_date'),
                    restaurant.get('source_url'),
                    restaurant.get('source_type'),
                    existing[0]
                ))
                updated_count += 1
            else:
                # 新規店舗を追加
                cursor.execute('''
                    INSERT INTO restaurants (
                        name, description, city, address, phone,
                        category, opening_date, source_url, source_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    restaurant['name'],
                    restaurant.get('description'),
                    restaurant['city'],
                    restaurant.get('address'),
                    restaurant.get('phone'),
                    restaurant.get('category'),
                    restaurant.get('opening_date'),
                    restaurant.get('source_url'),
                    restaurant.get('source_type')
                ))
                new_count += 1
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"飲食店情報保存完了: 新規{new_count}件, 更新{updated_count}件")

    def get_active_restaurants(self) -> List[Dict]:
        """アクティブな飲食店情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, city, address, phone,
                   category, opening_date, source_url, source_type
            FROM restaurants 
            WHERE is_active = 1 
            ORDER BY opening_date DESC, created_at DESC
        ''')
        
        restaurants = []
        for row in cursor.fetchall():
            restaurant = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'city': row[3],
                'address': row[4],
                'phone': row[5],
                'category': row[6],
                'opening_date': row[7],
                'source_url': row[8],
                'source_type': row[9]
            }
            restaurants.append(restaurant)
        
        conn.close()
        return restaurants

# 使用例
if __name__ == "__main__":
    scraper = RestaurantScraper()
    
    # Twitter API認証情報（実際の値に置き換え）
    # api_key = "your_api_key"
    # api_secret = "your_api_secret"
    # access_token = "your_access_token"
    # access_token_secret = "your_access_token_secret"
    
    # restaurants = scraper.scrape_twitter_restaurants(
    #     api_key, api_secret, access_token, access_token_secret
    # )
    # scraper.save_restaurants(restaurants)
    
    # アクティブな飲食店情報を表示
    active_restaurants = scraper.get_active_restaurants()
    print(f"アクティブな飲食店: {len(active_restaurants)}件")
    for restaurant in active_restaurants[:5]:
        print(f"- {restaurant['name']} ({restaurant['city']})") 
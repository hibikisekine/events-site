#!/usr/bin/env python3
"""
API v2を使用した飲食店スクレイパー
"""

import sqlite3
import logging
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import tweepy
from config import RESTAURANTS_DB, LOG_LEVEL, LOG_FILE

# ログ設定
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class RestaurantScraperV2:
    def __init__(self, db_path: str = RESTAURANTS_DB):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Bearer TokenをURLデコード
        self.bearer_token = urllib.parse.unquote(
            "AAAAAAAAAAAAAAAAAAAAAHNr3QEAAAAA8noVrOaYdxumWQ8fpFC09RBrosQ%3D9SuQoXs4wBcS9Ww0fej30rSNiWRSpxn2gvMmNIl5CCzxCdGV8J"
        )
        
        # 検索キーワード
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
            "常総 開店"
        ]
        
        self.init_database()

    def init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                location TEXT,
                opening_date TEXT,
                category TEXT,
                source_url TEXT,
                source_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info("データベース初期化完了")

    def scrape_twitter_restaurants_v2(self) -> List[Dict]:
        """API v2を使用してTwitterから飲食店開店情報を取得"""
        try:
            # API v2クライアントを作成
            client = tweepy.Client(bearer_token=self.bearer_token)
            
            restaurants = []
            
            for keyword in self.search_keywords:
                self.logger.info(f"キーワード検索中: {keyword}")
                
                try:
                    # API v2でツイートを検索
                    response = client.search_recent_tweets(
                        query=keyword,
                        max_results=100,
                        tweet_fields=['created_at', 'author_id'],
                        expansions=['author_id']
                    )
                    
                    if response.data:
                        for tweet in response.data:
                            restaurant_info = self.extract_restaurant_info_v2(tweet.text, keyword)
                            if restaurant_info:
                                restaurant_info['source_url'] = f"https://twitter.com/user/status/{tweet.id}"
                                restaurant_info['source_type'] = 'twitter_v2'
                                restaurants.append(restaurant_info)
                                self.logger.info(f"飲食店情報を抽出: {restaurant_info['name']}")
                    else:
                        self.logger.info(f"キーワード '{keyword}' の検索結果が0件でした")
                
                except Exception as e:
                    self.logger.error(f"キーワード '{keyword}' の検索でエラー: {e}")
                    continue
            
            self.logger.info(f"合計 {len(restaurants)} 件の飲食店情報を取得")
            return restaurants
            
        except Exception as e:
            self.logger.error(f"Twitter API v2での取得でエラー: {e}")
            return []

    def extract_restaurant_info_v2(self, text: str, keyword: str) -> Optional[Dict]:
        """API v2のツイートから飲食店情報を抽出"""
        try:
            # 基本的な情報抽出
            restaurant_info = {
                'name': '',
                'description': text[:200],  # 最初の200文字
                'location': '',
                'opening_date': '',
                'category': '飲食店',
                'source_url': ''
            }
            
            # 店舗名の抽出（キーワードに基づく）
            if 'つくば' in keyword:
                restaurant_info['location'] = 'つくば市周辺'
            elif 'つくばみらい' in keyword:
                restaurant_info['location'] = 'つくばみらい市周辺'
            elif '守谷' in keyword:
                restaurant_info['location'] = '守谷市周辺'
            elif '取手' in keyword:
                restaurant_info['location'] = '取手市周辺'
            elif '常総' in keyword:
                restaurant_info['location'] = '常総市周辺'
            
            # 店舗名の推定（テキストから抽出）
            words = text.split()
            for i, word in enumerate(words):
                if '店' in word or 'レストラン' in word or 'カフェ' in word:
                    restaurant_info['name'] = word
                    break
                elif i < len(words) - 1 and ('新規' in word or 'オープン' in word):
                    # 前後の単語を店舗名として使用
                    if i > 0:
                        restaurant_info['name'] = words[i-1] + word
                    else:
                        restaurant_info['name'] = word
                    break
            
            # 店舗名が見つからない場合はデフォルト名
            if not restaurant_info['name']:
                restaurant_info['name'] = f"新規店舗 ({keyword})"
            
            # 開店日の推定
            today = datetime.now()
            restaurant_info['opening_date'] = today.strftime('%Y-%m-%d')
            
            return restaurant_info
            
        except Exception as e:
            self.logger.error(f"情報抽出でエラー: {e}")
            return None

    def save_restaurants(self, restaurants: List[Dict]):
        """飲食店情報をデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for restaurant in restaurants:
            cursor.execute('''
                INSERT OR REPLACE INTO restaurants 
                (name, description, location, opening_date, category, source_url, source_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                restaurant['name'],
                restaurant['description'],
                restaurant['location'],
                restaurant['opening_date'],
                restaurant['category'],
                restaurant['source_url'],
                restaurant['source_type']
            ))
        
        conn.commit()
        conn.close()
        self.logger.info(f"{len(restaurants)}件の飲食店情報を保存しました")

    def run_scraper(self):
        """スクレイパーを実行"""
        self.logger.info("飲食店スクレイパー開始")
        
        # Twitterから飲食店情報を取得
        restaurants = self.scrape_twitter_restaurants_v2()
        
        if restaurants:
            # データベースに保存
            self.save_restaurants(restaurants)
            self.logger.info("スクレイピング完了")
        else:
            self.logger.warning("取得した飲食店情報が0件でした")

def main():
    """メイン関数"""
    scraper = RestaurantScraperV2()
    scraper.run_scraper()

if __name__ == '__main__':
    main() 
#!/usr/bin/env python3
"""
控えめなレート制限対応の飲食店スクレイパー
"""

import sqlite3
import logging
import urllib.parse
import time
import random
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

class ConservativeRestaurantScraper:
    def __init__(self, db_path: str = RESTAURANTS_DB):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Bearer TokenをURLデコード
        self.bearer_token = urllib.parse.unquote(
            "AAAAAAAAAAAAAAAAAAAAAHNr3QEAAAAA8noVrOaYdxumWQ8fpFC09RBrosQ%3D9SuQoXs4wBcS9Ww0fej30rSNiWRSpxn2gvMmNIl5CCzxCdGV8J"
        )
        
        # 検索キーワード（最小限に絞る）
        self.search_keywords = [
            "つくば 新規オープン"
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

    def scrape_single_keyword(self, keyword: str) -> List[Dict]:
        """単一キーワードでスクレイピング（控えめな方法）"""
        try:
            # API v2クライアントを作成
            client = tweepy.Client(bearer_token=self.bearer_token)
            
            self.logger.info(f"キーワード検索中: {keyword}")
            
            # ランダムな待機時間（1-3秒）
            wait_time = random.uniform(1, 3)
            self.logger.info(f"{wait_time:.1f}秒待機...")
            time.sleep(wait_time)
            
            # API v2でツイートを検索（結果数を最小限に）
            response = client.search_recent_tweets(
                query=keyword,
                max_results=10,  # 最小値は10
                tweet_fields=['created_at', 'author_id'],
                expansions=['author_id']
            )
            
            restaurants = []
            
            if response.data:
                for tweet in response.data:
                    restaurant_info = self.extract_restaurant_info(tweet.text, keyword)
                    if restaurant_info:
                        restaurant_info['source_url'] = f"https://twitter.com/user/status/{tweet.id}"
                        restaurant_info['source_type'] = 'twitter_v2_conservative'
                        restaurants.append(restaurant_info)
                        self.logger.info(f"飲食店情報を抽出: {restaurant_info['name']}")
            else:
                self.logger.info(f"キーワード '{keyword}' の検索結果が0件でした")
            
            return restaurants
            
        except tweepy.errors.TooManyRequests as e:
            self.logger.warning(f"レート制限に達しました: {e}")
            return []
            
        except Exception as e:
            self.logger.error(f"キーワード '{keyword}' の検索でエラー: {e}")
            return []

    def extract_restaurant_info(self, text: str, keyword: str) -> Optional[Dict]:
        """ツイートから飲食店情報を抽出"""
        try:
            # 基本的な情報抽出
            restaurant_info = {
                'name': '',
                'description': text[:200],  # 最初の200文字
                'location': 'つくば市周辺',
                'opening_date': datetime.now().strftime('%Y-%m-%d'),
                'category': '飲食店',
                'source_url': ''
            }
            
            # 店舗名の推定
            words = text.split()
            for i, word in enumerate(words):
                if '店' in word or 'レストラン' in word or 'カフェ' in word:
                    restaurant_info['name'] = word
                    break
                elif i < len(words) - 1 and ('新規' in word or 'オープン' in word):
                    if i > 0:
                        restaurant_info['name'] = words[i-1] + word
                    else:
                        restaurant_info['name'] = word
                    break
            
            # 店舗名が見つからない場合はデフォルト名
            if not restaurant_info['name']:
                restaurant_info['name'] = f"新規店舗 ({keyword})"
            
            return restaurant_info
            
        except Exception as e:
            self.logger.error(f"情報抽出でエラー: {e}")
            return None

    def save_restaurants(self, restaurants: List[Dict]):
        """飲食店情報をデータベースに保存"""
        if not restaurants:
            return
            
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
        self.logger.info("控えめな飲食店スクレイパー開始")
        
        all_restaurants = []
        
        # 1つのキーワードのみでテスト
        for keyword in self.search_keywords:
            restaurants = self.scrape_single_keyword(keyword)
            all_restaurants.extend(restaurants)
            
            # 次のキーワードの前に長めの待機
            if len(self.search_keywords) > 1:
                self.logger.info("次のキーワードの前に10秒待機...")
                time.sleep(10)
        
        if all_restaurants:
            self.save_restaurants(all_restaurants)
            self.logger.info("スクレイピング完了")
        else:
            self.logger.warning("取得した飲食店情報が0件でした")

def main():
    """メイン関数"""
    scraper = ConservativeRestaurantScraper()
    scraper.run_scraper()

if __name__ == '__main__':
    main() 
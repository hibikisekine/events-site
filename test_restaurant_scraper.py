#!/usr/bin/env python3
"""
飲食店スクレイパーのテスト実行スクリプト
"""

import sys
import os
from restaurant_scraper import RestaurantScraper
from config import X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET

def test_restaurant_scraper():
    """飲食店スクレイパーのテスト実行"""
    print("🍽️ 飲食店開店情報スクレイパーのテスト開始")
    print("=" * 50)
    
    # 設定確認
    print("📋 設定確認:")
    print(f"  X API Key: {'✅ 設定済み' if X_API_KEY else '❌ 未設定'}")
    print(f"  X API Secret: {'✅ 設定済み' if X_API_SECRET else '❌ 未設定'}")
    print(f"  X Access Token: {'✅ 設定済み' if X_ACCESS_TOKEN else '❌ 未設定'}")
    print(f"  X Access Token Secret: {'✅ 設定済み' if X_ACCESS_TOKEN_SECRET else '❌ 未設定'}")
    
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        print("\n❌ X API認証情報が不完全です。")
        print("config.pyで以下の情報を設定してください:")
        print("  - X_API_SECRET")
        print("  - X_ACCESS_TOKEN") 
        print("  - X_ACCESS_TOKEN_SECRET")
        return False
    
    print("\n✅ 設定確認完了")
    
    # スクレイパー初期化
    print("\n🔧 スクレイパー初期化中...")
    scraper = RestaurantScraper()
    
    # Twitterから飲食店情報を取得
    print("\n🐦 Twitterから飲食店情報を取得中...")
    restaurants = scraper.scrape_twitter_restaurants()
    
    if restaurants:
        print(f"\n✅ {len(restaurants)}件の飲食店情報を取得しました:")
        for i, restaurant in enumerate(restaurants[:5], 1):
            print(f"  {i}. {restaurant['name']} ({restaurant['city']})")
            print(f"     カテゴリ: {restaurant.get('category', '未分類')}")
            print(f"     開店日: {restaurant.get('opening_date', '未定')}")
            print(f"     住所: {restaurant.get('address', '未定')}")
            print()
        
        if len(restaurants) > 5:
            print(f"  ... 他 {len(restaurants) - 5}件")
        
        # データベースに保存
        print("💾 データベースに保存中...")
        scraper.save_restaurants(restaurants)
        
        # 保存されたデータを確認
        print("\n📊 保存されたデータを確認:")
        active_restaurants = scraper.get_active_restaurants()
        print(f"  アクティブな飲食店: {len(active_restaurants)}件")
        
        return True
    else:
        print("\n❌ 飲食店情報を取得できませんでした。")
        print("可能な原因:")
        print("  - API認証情報が間違っている")
        print("  - ネットワーク接続の問題")
        print("  - 検索キーワードに該当するツイートがない")
        return False

def main():
    """メイン関数"""
    try:
        success = test_restaurant_scraper()
        if success:
            print("\n🎉 テスト完了！飲食店スクレイパーが正常に動作しています。")
        else:
            print("\n💡 設定を確認してから再実行してください。")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
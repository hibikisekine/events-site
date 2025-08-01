#!/usr/bin/env python3
"""
イベントスクレイピング管理スクリプト
"""

import sys
import time
import logging
from event_scraper import EventScraper

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python manage_scraper.py start     # スケジューラー開始")
        print("  python manage_scraper.py run       # 1回実行")
        print("  python manage_scraper.py test      # テスト実行")
        print("  python manage_scraper.py stats     # 統計表示")
        return
    
    command = sys.argv[1]
    scraper = EventScraper()
    
    if command == "start":
        print("🚀 スクレイピングスケジューラーを開始します...")
        scraper.schedule_scraping()
        scraper.run_scheduler()
        
    elif command == "run":
        print("📊 スクレイピングを1回実行します...")
        start_time = time.time()
        scraper.daily_scraping()
        duration = time.time() - start_time
        print(f"✅ スクレイピング完了 (実行時間: {duration:.2f}秒)")
        
    elif command == "test":
        print("🧪 テストスクレイピングを実行します...")
        # 最初の2都市のみでテスト
        test_sources = dict(list(scraper.sources.items())[:2])
        
        for source_id, source_info in test_sources.items():
            print(f"テスト: {source_info['name']}")
            events = scraper.scrape_city_website(source_id, source_info, limit=3)
            print(f"  取得イベント数: {len(events)}")
            for event in events:
                print(f"    - {event.get('title', 'No title')}")
        
    elif command == "stats":
        print("📈 スクレイピング統計:")
        print(f"  総イベント数: {scraper.stats['total_events']}")
        print(f"  新規イベント: {scraper.stats['new_events']}")
        print(f"  更新イベント: {scraper.stats['updated_events']}")
        print(f"  エラー数: {scraper.stats['errors']}")
        
        # データベースから実際の統計を取得
        conn = scraper.db_path
        import sqlite3
        conn = sqlite3.connect(scraper.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM events WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM events WHERE created_at >= date('now', '-7 days')")
        recent_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT source_city, COUNT(*) FROM events WHERE is_active = 1 GROUP BY source_city")
        city_stats = cursor.fetchall()
        
        conn.close()
        
        print(f"  アクティブイベント: {active_count}")
        print(f"  過去7日間の新規: {recent_count}")
        print("  都市別統計:")
        for city, count in city_stats:
            print(f"    {city}: {count}件")
    
    else:
        print(f"❌ 不明なコマンド: {command}")

if __name__ == "__main__":
    main() 
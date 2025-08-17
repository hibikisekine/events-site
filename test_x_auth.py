#!/usr/bin/env python3
"""
X API認証テストスクリプト
"""

import tweepy
from config import X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET

def test_x_auth():
    """X API認証をテスト"""
    print("🔐 X API認証テスト開始")
    print("=" * 40)
    
    # 認証情報の表示（一部マスク）
    print("📋 認証情報確認:")
    print(f"  API Key: {X_API_KEY[:10]}...")
    print(f"  API Secret: {X_API_SECRET[:10]}...")
    print(f"  Access Token: {X_ACCESS_TOKEN[:10]}...")
    print(f"  Access Token Secret: {X_ACCESS_TOKEN_SECRET[:10]}...")
    
    try:
        # 認証設定
        auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
        auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
        
        # APIオブジェクト作成
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # 認証テスト（自分のアカウント情報を取得）
        print("\n🔍 認証テスト中...")
        me = api.verify_credentials()
        print(f"✅ 認証成功！ユーザー: @{me.screen_name}")
        
        # 簡単な検索テスト
        print("\n🔍 検索テスト中...")
        tweets = api.search_tweets(q="つくば", lang="ja", count=1)
        if tweets:
            print(f"✅ 検索成功！ツイート数: {len(tweets)}")
            print(f"   最初のツイート: {tweets[0].text[:50]}...")
        else:
            print("⚠️ 検索結果が0件でした")
        
        return True
        
    except tweepy.TweepError as e:
        print(f"\n❌ 認証エラー: {e}")
        print("\n💡 考えられる原因:")
        print("  1. API認証情報が間違っている")
        print("  2. API権限が不足している")
        print("  3. アプリの設定が不完全")
        return False
        
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        return False

def main():
    """メイン関数"""
    success = test_x_auth()
    if success:
        print("\n🎉 認証テスト完了！X APIが正常に動作しています。")
    else:
        print("\n💡 X Developer Portalで設定を確認してください。")
        print("  - App permissions: Read")
        print("  - User authentication settings: OAuth 1.0a")

if __name__ == "__main__":
    main() 
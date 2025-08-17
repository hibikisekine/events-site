#!/usr/bin/env python3
"""
X API認証情報修正スクリプト
"""

import os
from dotenv import load_dotenv
import tweepy

load_dotenv()

def check_auth_info():
    """認証情報をチェック"""
    print("🔐 X API認証情報チェック")
    print("=" * 40)
    
    # 環境変数から認証情報を取得
    api_key = os.getenv('X_API_KEY')
    api_secret = os.getenv('X_API_SECRET')
    access_token = os.getenv('X_ACCESS_TOKEN')
    access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')
    
    print("📋 環境変数から取得した認証情報:")
    print(f"  X_API_KEY: {'✅ 設定済み' if api_key else '❌ 未設定'}")
    print(f"  X_API_SECRET: {'✅ 設定済み' if api_secret else '❌ 未設定'}")
    print(f"  X_ACCESS_TOKEN: {'✅ 設定済み' if access_token else '❌ 未設定'}")
    print(f"  X_ACCESS_TOKEN_SECRET: {'✅ 設定済み' if access_token_secret else '❌ 未設定'}")
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("\n❌ 認証情報が不完全です。")
        print("\n💡 解決方法:")
        print("1. .envファイルを作成し、以下の形式で認証情報を設定してください:")
        print("   X_API_KEY=your_api_key_here")
        print("   X_API_SECRET=your_api_secret_here")
        print("   X_ACCESS_TOKEN=your_access_token_here")
        print("   X_ACCESS_TOKEN_SECRET=your_access_token_secret_here")
        print("\n2. X Developer Portal (https://developer.twitter.com/) で認証情報を確認してください")
        return False
    
    return True

def test_auth(api_key, api_secret, access_token, access_token_secret):
    """認証テスト"""
    try:
        print("\n🔍 認証テスト中...")
        
        # 認証設定
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        
        # APIオブジェクト作成
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # 認証テスト
        me = api.verify_credentials()
        print(f"✅ 認証成功！ユーザー: @{me.screen_name}")
        
        # 簡単な検索テスト
        print("\n🔍 検索テスト中...")
        tweets = api.search_tweets(q="つくば", lang="ja", count=1)
        if tweets:
            print(f"✅ 検索成功！ツイート数: {len(tweets)}")
        else:
            print("⚠️ 検索結果が0件でした")
        
        return True
        
    except tweepy.errors.Unauthorized as e:
        print(f"\n❌ 認証エラー (401 Unauthorized): {e}")
        print("\n💡 考えられる原因:")
        print("  1. API認証情報が間違っている")
        print("  2. API権限が不足している")
        print("  3. アプリの設定が不完全")
        print("  4. API Secretが正しくない形式")
        return False
        
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        return False

def create_env_template():
    """環境変数テンプレートを作成"""
    env_content = """# X (Twitter) API認証情報
# X Developer Portal (https://developer.twitter.com/) から取得してください
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# その他の設定
SECRET_KEY=your_secret_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
"""
    
    with open('.env.template', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("\n📝 .env.templateファイルを作成しました")
    print("このファイルを参考に.envファイルを作成してください")

def main():
    """メイン関数"""
    print("🔧 X API認証情報修正ツール")
    print("=" * 40)
    
    # 認証情報チェック
    if not check_auth_info():
        create_env_template()
        return
    
    # 環境変数から認証情報を取得
    api_key = os.getenv('X_API_KEY')
    api_secret = os.getenv('X_API_SECRET')
    access_token = os.getenv('X_ACCESS_TOKEN')
    access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')
    
    # 認証テスト
    success = test_auth(api_key, api_secret, access_token, access_token_secret)
    
    if success:
        print("\n✅ 認証が正常に動作しています！")
    else:
        print("\n❌ 認証に問題があります。")
        create_env_template()

if __name__ == '__main__':
    main() 
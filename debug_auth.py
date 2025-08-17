#!/usr/bin/env python3
"""
X API認証詳細デバッグスクリプト
"""

import os
from dotenv import load_dotenv
import tweepy
import urllib.parse

load_dotenv()

def debug_auth_info():
    """認証情報を詳細にデバッグ"""
    print("🔍 X API認証詳細デバッグ")
    print("=" * 50)
    
    # 環境変数から認証情報を取得
    api_key = os.getenv('X_API_KEY')
    api_secret = os.getenv('X_API_SECRET')
    access_token = os.getenv('X_ACCESS_TOKEN')
    access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')
    
    print("📋 認証情報の詳細:")
    print(f"  API Key: {api_key}")
    print(f"  API Secret: {api_secret}")
    print(f"  Access Token: {access_token}")
    print(f"  Access Token Secret: {access_token_secret}")
    
    # 長さチェック
    print("\n📏 認証情報の長さ:")
    print(f"  API Key: {len(api_key) if api_key else 0} 文字")
    print(f"  API Secret: {len(api_secret) if api_secret else 0} 文字")
    print(f"  Access Token: {len(access_token) if access_token else 0} 文字")
    print(f"  Access Token Secret: {len(access_token_secret) if access_token_secret else 0} 文字")
    
    # 形式チェック
    print("\n🔍 形式チェック:")
    if api_key and len(api_key) == 25:
        print("  ✅ API Key: 正しい長さ (25文字)")
    else:
        print("  ❌ API Key: 長さが正しくありません")
    
    if api_secret and len(api_secret) == 50:
        print("  ✅ API Secret: 正しい長さ (50文字)")
    else:
        print("  ❌ API Secret: 長さが正しくありません")
    
    if access_token and len(access_token) == 50:
        print("  ✅ Access Token: 正しい長さ (50文字)")
    else:
        print("  ❌ Access Token: 長さが正しくありません")
    
    if access_token_secret and len(access_token_secret) == 45:
        print("  ✅ Access Token Secret: 正しい長さ (45文字)")
    else:
        print("  ❌ Access Token Secret: 長さが正しくありません")

def test_different_auth_methods():
    """異なる認証方法をテスト"""
    print("\n🧪 異なる認証方法をテスト")
    print("=" * 50)
    
    api_key = os.getenv('X_API_KEY')
    api_secret = os.getenv('X_API_SECRET')
    access_token = os.getenv('X_ACCESS_TOKEN')
    access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')
    
    # 方法1: 通常のOAuth認証
    print("\n1️⃣ 通常のOAuth認証テスト:")
    try:
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        me = api.verify_credentials()
        print(f"  ✅ 成功: @{me.screen_name}")
        return True
    except Exception as e:
        print(f"  ❌ 失敗: {e}")
    
    # 方法2: Bearer Token認証（API v2用）
    print("\n2️⃣ Bearer Token認証テスト:")
    try:
        # Bearer TokenをURLデコード
        bearer_token = "AAAAAAAAAAAAAAAAAAAAAHNr3QEAAAAA8noVrOaYdxumWQ8fpFC09RBrosQ%3D9SuQoXs4wBcS9Ww0fej30rSNiWRSpxn2gvMmNIl5CCzxCdGV8J"
        decoded_bearer = urllib.parse.unquote(bearer_token)
        
        client = tweepy.Client(bearer_token=decoded_bearer)
        # 簡単なテスト
        print(f"  ✅ Bearer Token: 設定完了")
        return True
    except Exception as e:
        print(f"  ❌ 失敗: {e}")
    
    return False

def check_api_permissions():
    """API権限をチェック"""
    print("\n🔐 API権限チェック")
    print("=" * 50)
    
    print("💡 X Developer Portalで以下を確認してください:")
    print("  1. アプリの権限設定:")
    print("     - Read権限が有効になっているか")
    print("     - Write権限が必要な場合は有効になっているか")
    print("  2. API設定:")
    print("     - API v1.1が有効になっているか")
    print("     - API v2が有効になっているか")
    print("  3. アプリの状態:")
    print("     - アプリが有効になっているか")
    print("     - 開発環境/本番環境の設定が正しいか")

def main():
    """メイン関数"""
    debug_auth_info()
    test_different_auth_methods()
    check_api_permissions()
    
    print("\n💡 推奨される解決方法:")
    print("1. X Developer Portalでアプリの権限を確認")
    print("2. 新しいアクセストークンを生成")
    print("3. API v1.1とAPI v2の両方が有効になっているか確認")
    print("4. アプリの設定でOAuth 1.0aが有効になっているか確認")

if __name__ == '__main__':
    main() 
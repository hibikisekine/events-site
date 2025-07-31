import os
from dotenv import load_dotenv

load_dotenv()

class ProductionConfig:
    """本番環境設定"""
    
    # Flask設定
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    DEBUG = False
    TESTING = False
    
    # データベース設定
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'events.db')
    
    # 天気API設定
    WEATHERAPI_KEY = os.environ.get('WEATHERAPI_KEY', '88ed0e701cfc4c7fb0d13301253107')
    
    # サーバー設定
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 8080))
    
    # ログ設定
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'production.log'
    
    # セキュリティ設定
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # キャッシュ設定
    CACHE_TIMEOUT = 1800  # 30分
    
    # スクレイピング設定
    SCRAPING_ENABLED = False  # 本番では無効化
    MAX_EVENTS_PER_CITY = 50
    
    # パフォーマンス設定
    MAX_CONNECTIONS = 100
    REQUEST_TIMEOUT = 10 
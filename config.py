import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """アプリケーション設定"""
    
    # 基本設定
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # データベース設定
    DATABASE_URL = os.getenv('DATABASE_URL', 'events.db')
    
    # API設定
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
    OPENWEATHER_CITY = os.getenv('OPENWEATHER_CITY', 'Tsukubamirai')
    OPENWEATHER_COUNTRY = os.getenv('OPENWEATHER_COUNTRY', 'JP')
    
    # スクレイピング設定
    SCRAPING_DELAY = int(os.getenv('SCRAPING_DELAY', '2'))  # 秒
    MAX_EVENTS_PER_SOURCE = int(os.getenv('MAX_EVENTS_PER_SOURCE', '10'))
    
    # キャッシュ設定
    WEATHER_CACHE_DURATION = int(os.getenv('WEATHER_CACHE_DURATION', '3600'))  # 1時間
    
    # ログ設定
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # セキュリティ設定
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # パフォーマンス設定
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    
    # 地域設定
    TARGET_CITIES = [
        'つくばみらい市',
        'つくば市', 
        '守谷市',
        '常総市',
        '取手市',
        '龍ケ崎市',
        '古河市',
        '坂東市'
    ]

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """テスト環境設定"""
    TESTING = True
    DATABASE_URL = 'test_events.db'
    WTF_CSRF_ENABLED = False

# 設定の選択
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 
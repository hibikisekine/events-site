import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(app):
    """ログ設定をセットアップ"""
    
    # ログディレクトリを作成
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # ログファイル名
    log_file = os.path.join(log_dir, 'app.log')
    
    # ログレベル
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    
    # フォーマッター
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # ファイルハンドラー（ローテーション付き）
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # ルートロガーを設定
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Flaskアプリケーションロガー
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    return app.logger

def log_event_scraping(city_name, event_count, success=True):
    """イベントスクレイピングのログ"""
    logger = logging.getLogger('event_scraper')
    if success:
        logger.info(f"{city_name}から{event_count}件のイベントを取得しました")
    else:
        logger.error(f"{city_name}からのイベント取得に失敗しました")

def log_weather_api(city_name, success=True, error_message=None):
    """天気APIのログ"""
    logger = logging.getLogger('weather_api')
    if success:
        logger.info(f"{city_name}の天気予報を取得しました")
    else:
        logger.error(f"{city_name}の天気予報取得に失敗: {error_message}")

def log_user_action(action, user_ip=None, details=None):
    """ユーザーアクションのログ"""
    logger = logging.getLogger('user_actions')
    message = f"アクション: {action}"
    if user_ip:
        message += f", IP: {user_ip}"
    if details:
        message += f", 詳細: {details}"
    logger.info(message)

def log_error(error_type, error_message, stack_trace=None):
    """エラーログ"""
    logger = logging.getLogger('errors')
    message = f"エラー種別: {error_type}, メッセージ: {error_message}"
    if stack_trace:
        message += f", スタックトレース: {stack_trace}"
    logger.error(message) 
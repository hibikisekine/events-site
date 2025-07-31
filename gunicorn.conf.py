# Gunicorn設定ファイル

import multiprocessing
import os

# サーバー設定
bind = "0.0.0.0:8080"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# タイムアウト設定
timeout = 30
keepalive = 2
graceful_timeout = 30

# ログ設定
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# プロセス設定
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None

# セキュリティ設定
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 環境変数
raw_env = [
    "FLASK_ENV=production",
    "FLASK_APP=wsgi_production.py"
] 
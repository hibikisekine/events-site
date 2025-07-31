#!/usr/bin/env python3
"""
本番環境用WSGIエントリーポイント
"""

import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import app
from production import ProductionConfig

# 本番設定を適用
app.config.from_object(ProductionConfig)

if __name__ == "__main__":
    app.run(
        host=ProductionConfig.HOST,
        port=ProductionConfig.PORT,
        debug=ProductionConfig.DEBUG
    ) 
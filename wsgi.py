#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
import sys

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import app

if __name__ == "__main__":
    app.run() 
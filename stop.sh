#!/bin/bash

# 今日行けるイベントサイト 停止スクリプト

echo "🛑 今日行けるイベントサイトを停止します..."

# 既存のプロセスを停止
pkill -f "python app.py" 2>/dev/null

# 停止確認
sleep 2
if pgrep -f "python app.py" > /dev/null; then
    echo "⚠️ プロセスが残っています。強制停止します..."
    pkill -9 -f "python app.py" 2>/dev/null
else
    echo "✅ アプリケーションが正常に停止しました"
fi

echo "🔧 ポート8080の確認:"
lsof -i :8080 2>/dev/null || echo "   ポート8080は使用されていません" 
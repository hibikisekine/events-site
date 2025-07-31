#!/bin/bash

# 今日行けるイベントサイト 起動スクリプト

echo "🚀 今日行けるイベントサイトを起動します..."

# 現在のディレクトリを確認
if [ ! -f "app.py" ]; then
    echo "❌ app.pyが見つかりません。正しいディレクトリに移動してください。"
    exit 1
fi

# 既存のプロセスを停止
echo "🛑 既存のプロセスを停止中..."
pkill -f "python app.py" 2>/dev/null
sleep 2

# データベースの確認
if [ ! -f "events.db" ]; then
    echo "📊 データベースを初期化中..."
    python init_db.py
    python add_sample_data.py
fi

# アプリケーションを起動
echo "🚀 Flaskアプリケーションを起動中..."
python app.py &

# 起動待機
echo "⏳ アプリケーションの起動を待機中..."
sleep 5

# ヘルスチェック
echo "🏥 ヘルスチェック中..."
for i in {1..10}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ アプリケーションが正常に起動しました！"
        echo ""
        echo "📱 アクセスURL:"
        echo "   http://localhost:8080"
        echo ""
        echo "🔧 停止するには:"
        echo "   pkill -f 'python app.py'"
        echo ""
        break
    else
        echo "⏳ 起動待機中... ($i/10)"
        sleep 2
    fi
done

if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "❌ アプリケーションの起動に失敗しました"
    echo "ログを確認してください:"
    echo "ps aux | grep python"
    exit 1
fi 
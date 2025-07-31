#!/bin/bash

# 今日行けるイベントサイト デプロイメントスクリプト

set -e

echo "🚀 今日行けるイベントサイト デプロイメント開始"

# 環境変数ファイルの確認
if [ ! -f .env ]; then
    echo "⚠️  .envファイルが見つかりません。env_example.txtをコピーして設定してください。"
    cp env_example.txt .env
    echo "📝 .envファイルを作成しました。APIキーを設定してください。"
    exit 1
fi

# 依存関係のインストール
echo "📦 依存関係をインストール中..."
pip install -r requirements.txt

# データベースの初期化
echo "🗄️ データベースを初期化中..."
python -c "from app import init_db; init_db()"

# ログディレクトリの作成
echo "📁 ログディレクトリを作成中..."
mkdir -p logs

# Dockerイメージのビルド
echo "🐳 Dockerイメージをビルド中..."
docker-compose build

# アプリケーションの起動
echo "🚀 アプリケーションを起動中..."
docker-compose up -d

# ヘルスチェック
echo "🏥 ヘルスチェック中..."
sleep 10
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ アプリケーションが正常に起動しました！"
    echo "🌐 アクセスURL: http://localhost:8000"
else
    echo "❌ アプリケーションの起動に失敗しました。"
    echo "📋 ログを確認してください:"
    docker-compose logs
    exit 1
fi

echo "🎉 デプロイメント完了！"
echo ""
echo "📊 管理コマンド:"
echo "  ログ確認: docker-compose logs -f"
echo "  停止: docker-compose down"
echo "  再起動: docker-compose restart"
echo "  更新: ./deploy.sh" 
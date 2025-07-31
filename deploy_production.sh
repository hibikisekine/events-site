#!/bin/bash

# 本番環境デプロイスクリプト

set -e

echo "🚀 本番環境デプロイを開始します..."

# 環境変数チェック
if [ -z "$WEATHERAPI_KEY" ]; then
    echo "❌ WEATHERAPI_KEYが設定されていません"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEYが設定されていません"
    exit 1
fi

# 必要なディレクトリを作成
echo "📁 ディレクトリを作成中..."
mkdir -p data logs ssl

# SSL証明書を生成（自己署名）
echo "🔐 SSL証明書を生成中..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem -out ssl/cert.pem \
    -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Events/CN=localhost"

# Dockerイメージをビルド
echo "🐳 Dockerイメージをビルド中..."
docker-compose -f docker-compose.production.yml build

# 既存のコンテナを停止・削除
echo "🛑 既存のコンテナを停止中..."
docker-compose -f docker-compose.production.yml down

# データベースを初期化
echo "🗄️ データベースを初期化中..."
python init_db.py

# サンプルデータを追加
echo "📊 サンプルデータを追加中..."
python add_sample_data.py

# コンテナを起動
echo "🚀 コンテナを起動中..."
docker-compose -f docker-compose.production.yml up -d

# ヘルスチェック
echo "🏥 ヘルスチェック中..."
sleep 30

for i in {1..10}; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "✅ アプリケーションが正常に起動しました！"
        break
    else
        echo "⏳ 起動待機中... ($i/10)"
        sleep 10
    fi
done

# 最終チェック
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo ""
    echo "🎉 デプロイが完了しました！"
    echo ""
    echo "📱 アプリケーションURL:"
    echo "   HTTP:  http://localhost"
    echo "   HTTPS: https://localhost"
    echo ""
    echo "📊 監視URL:"
    echo "   ヘルスチェック: http://localhost/health"
    echo "   イベントAPI: http://localhost/api/events"
    echo ""
    echo "🔧 管理コマンド:"
    echo "   ログ確認: docker-compose -f docker-compose.production.yml logs"
    echo "   停止: docker-compose -f docker-compose.production.yml down"
    echo "   再起動: docker-compose -f docker-compose.production.yml restart"
else
    echo "❌ アプリケーションの起動に失敗しました"
    echo "ログを確認してください:"
    echo "docker-compose -f docker-compose.production.yml logs"
    exit 1
fi 
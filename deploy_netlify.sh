#!/bin/bash

# Netlifyデプロイスクリプト

echo "🚀 Netlifyへのデプロイを開始します..."

# 必要なファイルの確認
echo "📁 ファイル確認中..."
if [ ! -f "netlify.toml" ]; then
    echo "❌ netlify.tomlが見つかりません"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txtが見つかりません"
    exit 1
fi

# Netlify CLIの確認
if ! command -v netlify &> /dev/null; then
    echo "📦 Netlify CLIをインストール中..."
    npm install -g netlify-cli
fi

# データベースの準備
echo "📊 データベースを準備中..."
if [ ! -f "events.db" ]; then
    echo "データベースを初期化中..."
    python init_db.py
    python add_sample_data.py
fi

# デプロイ
echo "🚀 デプロイ中..."
netlify deploy --prod

echo "✅ デプロイ完了！"
echo ""
echo "📱 次のステップ:"
echo "1. Google AdSenseアカウントを作成"
echo "2. 広告コードを取得して設定"
echo "3. カスタムドメインを設定（オプション）"
echo ""
echo "🔧 管理コマンド:"
echo "   netlify status        # デプロイ状況確認"
echo "   netlify logs          # ログ確認"
echo "   netlify domains       # ドメイン管理" 
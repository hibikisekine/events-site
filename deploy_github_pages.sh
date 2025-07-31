#!/bin/bash

# GitHub Pagesデプロイスクリプト

echo "🚀 GitHub Pagesへのデプロイを開始します..."

# 必要なファイルの確認
echo "📁 ファイル確認中..."
if [ ! -f "index.html" ]; then
    echo "❌ index.htmlが見つかりません"
    exit 1
fi

if [ ! -f "static/js/app.js" ]; then
    echo "❌ static/js/app.jsが見つかりません"
    exit 1
fi

# GitHubリポジトリの確認
if [ ! -d ".git" ]; then
    echo "❌ Gitリポジトリが見つかりません"
    echo "git init を実行してください"
    exit 1
fi

# リモートリポジトリの確認
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "⚠️ リモートリポジトリが設定されていません"
    echo "GitHubでリポジトリを作成してから以下を実行してください:"
    echo "git remote add origin https://github.com/your-username/events-site.git"
    exit 1
fi

# 変更をコミット
echo "📝 変更をコミット中..."
git add .
git commit -m "Update: 静的サイト対応"

# GitHubにプッシュ
echo "🚀 GitHubにプッシュ中..."
git push origin main

echo "✅ デプロイ完了！"
echo ""
echo "📱 次のステップ:"
echo "1. GitHubリポジトリの設定で「Pages」を有効化"
echo "2. Source を「Deploy from a branch」に設定"
echo "3. Branch を「main」に設定"
echo "4. 数分後にサイトが公開されます"
echo ""
echo "🔧 管理コマンド:"
echo "   git status        # 変更状況確認"
echo "   git log           # コミット履歴"
echo "   git remote -v     # リモートリポジトリ確認" 
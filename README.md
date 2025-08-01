# 今日行けるイベントサイト

天気予報と連携した地域イベント検索サイト

## 🚀 本番デプロイ

### Netlify（推奨）

```bash
# デプロイスクリプト実行
./deploy_netlify.sh
```

### 手動デプロイ

1. **Netlify CLIインストール**
```bash
npm install -g netlify-cli
```

2. **デプロイ**
```bash
netlify deploy --prod
```

## 💰 広告収益化

### Google AdSense設定

1. **AdSenseアカウント作成**
   - [Google AdSense](https://www.google.com/adsense) にアクセス
   - アカウントを作成・審査通過

2. **広告コード取得**
   - 広告ユニットを作成
   - 表示広告コードを取得

3. **コード設定**
   - `index.html` の広告スペースを更新
   - `ca-pub-XXXXXXXXXXXXXXXX` を実際のIDに変更

### その他の収益化オプション

- **Amazonアソシエイト**: イベント関連商品の紹介
- **地域企業の広告**: ローカルビジネスとの提携
- **イベント主催者との提携**: 有料イベントの紹介

## 📊 機能

- ✅ 天気予報連携
- ✅ 地域フィルター
- ✅ カテゴリフィルター
- ✅ 無料/有料フィルター
- ✅ 子連れ対応フィルター
- ✅ 駐車場ありフィルター
- ✅ レスポンシブデザイン
- ✅ 広告表示対応

## 🔧 開発環境

```bash
# 起動
./start.sh

# 停止
./stop.sh

# アクセス
http://localhost:8080
```

## 📱 対応地域

- つくば市
- つくばみらい市
- 守谷市
- 取手市
- 常総市
- 龍ヶ崎市
- 古河市
- 坂東市

## 🎯 収益化戦略

1. **トラフィック増加**
   - SEO最適化
   - SNS拡散
   - 地域メディアとの連携

2. **ユーザーエンゲージメント**
   - イベントレビュー機能
   - お気に入り機能
   - 通知機能

3. **収益最大化**
   - 複数の広告ネットワーク
   - アフィリエイトリンク
   - プレミアム機能

## 🚀 Netlifyの利点

- **無料プラン**: 月100GB、個人プロジェクト無制限
- **自動デプロイ**: GitHub連携
- **カスタムドメイン**: 無料
- **CDN**: 高速配信
- **SSL証明書**: 自動設定 
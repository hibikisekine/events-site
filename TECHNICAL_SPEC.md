# 技術仕様書

## 🔧 システムアーキテクチャ

### 全体構成
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   フロントエンド   │    │   バックエンド     │    │   外部API       │
│                 │    │                 │    │                 │
│ - HTML5         │◄──►│ - Python/Flask  │◄──►│ - WeatherAPI    │
│ - CSS3          │    │ - SQLite        │    │ - X (Twitter)   │
│ - JavaScript    │    │ - BeautifulSoup │    │ - Google Analytics│
│ - Bootstrap 5   │    │ - Selenium      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Netlify CDN   │    │   SQLite DB     │    │   ログファイル    │
│                 │    │                 │    │                 │
│ - 静的ファイル配信 │    │ - events.db      │    │ - scraper.log   │
│ - HTTPS         │    │ - content.db     │    │ - error.log     │
│ - 自動デプロイ   │    │ - weather.db     │    │ - access.log    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 データベース設計

### イベントテーブル (events)
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    date DATE NOT NULL,
    time TEXT,
    location TEXT,
    description TEXT,
    category TEXT,
    is_free BOOLEAN DEFAULT 1,
    has_parking BOOLEAN DEFAULT 0,
    child_friendly BOOLEAN DEFAULT 0,
    is_indoor BOOLEAN DEFAULT 1,
    weather_dependent BOOLEAN DEFAULT 0,
    rain_cancellation TEXT,
    source_url TEXT,
    source_city TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### コンテンツテーブル (content)
```sql
CREATE TABLE seasonal_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    date TEXT,
    location TEXT,
    category TEXT,
    city TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE food_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    location TEXT,
    category TEXT,
    city TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 同様に childcare_info, tourism_info, culture_info テーブル
```

### 天気テーブル (weather)
```sql
CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    temperature REAL,
    humidity INTEGER,
    condition TEXT,
    rain_probability INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔄 スクレイピング仕様

### スクレイピングスクリプト一覧

#### 1. restaurant_scraper.py
- **目的**: X (Twitter) APIを使用した飲食店情報取得
- **実行頻度**: 毎日 午前6時
- **レート制限**: 15分間に100回まで
- **エラーハンドリング**: 429エラー時の自動リトライ

```python
# 主要設定
RATE_LIMIT_DELAY = 60  # 秒
MAX_RESULTS_PER_QUERY = 10
KEYWORDS = ['つくば', '守谷', '取手', '開店', '新店']
```

#### 2. content_auto_updater.py
- **目的**: 地域特集・地域情報の自動更新
- **実行頻度**: 週1回（日曜日）
- **データソース**: 各市の公式サイト
- **出力形式**: JSON

#### 3. real_content_scraper_v2.py
- **目的**: 実際の地域情報をスクレイピング
- **対象サイト**: 各市の観光・文化施設ページ
- **エラーハンドリング**: 404/403エラーの適切な処理

### スクレイピング設定

#### ヘッダー設定
```python
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}
```

#### タイムアウト設定
```python
TIMEOUT = 15  # 秒
RETRY_COUNT = 3
RETRY_DELAY = 5  # 秒
```

## 🌐 API仕様

### WeatherAPI
- **エンドポイント**: `https://api.weatherapi.com/v1/current.json`
- **認証**: APIキー認証
- **レート制限**: 月100万回まで
- **レスポンス形式**: JSON

```json
{
  "location": {
    "name": "Tsukuba",
    "region": "Ibaraki",
    "country": "Japan"
  },
  "current": {
    "temp_c": 25.0,
    "humidity": 65,
    "condition": {
      "text": "Partly cloudy"
    }
  }
}
```

### X (Twitter) API
- **認証方式**: OAuth 1.0a
- **エンドポイント**: `https://api.twitter.com/2/tweets/search/recent`
- **レート制限**: 15分間に100回まで
- **レスポンス形式**: JSON

## 🔐 セキュリティ仕様

### 環境変数管理
```bash
# .env ファイル
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
WEATHER_API_KEY=your_weather_api_key
GA_MEASUREMENT_ID=G-BTJQ4YG2EP
```

### セキュリティヘッダー
```python
# Flask セキュリティ設定
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

### CORS設定
```python
CORS_ORIGINS = [
    "https://tsukuba.netlify.app",
    "http://localhost:8000"
]
```

## 📈 パフォーマンス最適化

### フロントエンド最適化
- **画像最適化**: WebP形式の使用
- **CSS/JS圧縮**: 本番環境での自動圧縮
- **キャッシュ戦略**: ブラウザキャッシュの活用
- **遅延読み込み**: 画像の遅延読み込み

### バックエンド最適化
- **データベースインデックス**: 検索速度の向上
- **クエリ最適化**: N+1問題の回避
- **キャッシュ**: Redis/Memcachedの活用
- **非同期処理**: Celeryによるバックグラウンド処理

### CDN設定
```toml
# netlify.toml
[[headers]]
  for = "/*"
  [headers.values]
    Cache-Control = "public, max-age=3600"
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

## 🚨 エラーハンドリング

### スクレイピングエラー
```python
try:
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error(f"スクレイピングエラー: {url} - {e}")
    return None
```

### API制限エラー
```python
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    time.sleep(retry_after)
    return retry_request()
```

### データベースエラー
```python
try:
    cursor.execute(query, params)
    db.commit()
except sqlite3.Error as e:
    logger.error(f"データベースエラー: {e}")
    db.rollback()
```

## 📊 監視・ログ

### ログ設定
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
```

### 監視項目
- **スクレイピング成功率**: 95%以上を目標
- **API制限エラー**: 月10回以下
- **レスポンス時間**: 平均3秒以下
- **データ更新頻度**: スケジュール通り

### アラート設定
- **スクレイピング失敗**: 連続3回失敗時
- **API制限**: 1時間に5回以上発生時
- **データ不整合**: データ件数が前日比50%減少時

## 🔄 デプロイメントパイプライン

### CI/CD設定
```yaml
# .github/workflows/deploy.yml
name: Deploy to Netlify
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v1.2
        with:
          publish-dir: './'
          production-branch: main
```

### デプロイ前チェック
1. **テスト実行**: ユニットテスト・統合テスト
2. **リンター実行**: コード品質チェック
3. **ビルド確認**: 静的ファイル生成確認
4. **セキュリティスキャン**: 脆弱性チェック

## 📱 レスポンシブデザイン

### ブレークポイント
```css
/* モバイル */
@media (max-width: 768px) { ... }

/* タブレット */
@media (min-width: 769px) and (max-width: 1024px) { ... }

/* デスクトップ */
@media (min-width: 1025px) { ... }
```

### 画像サイズ最適化
- **モバイル**: 最大幅768px
- **タブレット**: 最大幅1024px
- **デスクトップ**: 最大幅1920px

## 🔍 SEO最適化

### メタタグ
```html
<meta name="description" content="茨城県南のイベント情報">
<meta name="keywords" content="つくば,守谷,取手,イベント,天気">
<meta property="og:title" content="茨城県南のイベント情報">
<meta property="og:description" content="今日行けるイベントを探そう">
```

### 構造化データ
```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "茨城県南のイベント情報",
  "description": "今日行けるイベントを探そう",
  "url": "https://tsukuba.netlify.app"
}
```

---

**最終更新**: 2025年1月15日
**バージョン**: 1.0.0

# クイックデプロイガイド

## すぐに使い始める3ステップ

### ステップ1：環境変数を設定

```bash
cd /home/user/webapp
cp .env.example .env
```

`.env`ファイルを編集：
```bash
# 必須：どちらか1つ
OPENAI_API_KEY=sk-...your-key...
# または
GOOGLE_API_KEY=...your-key...

# その他（オプション）
AI_MODEL=gpt-4o
LOG_LEVEL=info
```

### ステップ2：アプリケーション起動

#### 方法A：Docker（推奨）

```bash
docker-compose up -d
```

#### 方法B：手動起動

```bash
# ターミナル1：バックエンド
cd /home/user/webapp
pip install -r requirements.txt
uvicorn api_server:app --host 0.0.0.0 --port 8000

# ターミナル2：フロントエンド
cd /home/user/webapp/frontend
npm install
npm run dev
```

### ステップ3：アクセス

- **フロントエンド**: http://localhost:3000
- **APIドキュメント**: http://localhost:8000/docs

---

## クラウドデプロイ（本番環境）

### Herokuデプロイ（5分）

```bash
# Herokuにログイン
heroku login

# バックエンドをデプロイ
cd /home/user/webapp
heroku create your-app-name-backend
heroku config:set OPENAI_API_KEY=sk-your-key
git push heroku main

# フロントエンドをデプロイ
cd frontend
heroku create your-app-name-frontend
heroku config:set NEXT_PUBLIC_API_URL=https://your-app-name-backend.herokuapp.com
git push heroku main
```

### Renderデプロイ（Web UI）

1. https://render.com にアクセス
2. 「New Web Service」をクリック
3. GitHubリポジトリを接続
4. 環境変数を設定（`OPENAI_API_KEY`）
5. 「Create Web Service」をクリック

### Vercel（フロントエンド）+ Railway（バックエンド）

#### バックエンド（Railway）
1. https://railway.app にアクセス
2. 「New Project」→「Deploy from GitHub repo」
3. 環境変数を設定
4. デプロイ完了後、URLをコピー

#### フロントエンド（Vercel）
```bash
cd /home/user/webapp/frontend
npm install -g vercel
vercel

# プロンプトで入力：
# - Project name: your-app-name
# - NEXT_PUBLIC_API_URL: RailwayのURL
```

---

## 使い方

### 1. Webページにアクセス

http://localhost:3000 または デプロイしたURL

### 2. 出生情報を入力

- 名前
- 生年月日
- 出生時刻
- 都道府県・市区町村

### 3. 鑑定開始

「鑑定を開始」ボタンをクリック

### 4. コンテンツ生成を待つ

15ステップの生成が順次進行（1ステップ約2-5秒）

### 5. PDF をダウンロード

生成完了後、「PDF をダウンロード」ボタンをクリック

---

## トラブルシューティング

### AIが動作しない

**症状**: `ai_generator: False`

**解決策**:
```bash
# APIキーを確認
echo $OPENAI_API_KEY

# 設定されていない場合
export OPENAI_API_KEY=sk-your-key

# サーバーを再起動
docker-compose restart backend
```

### PDF生成エラー

**症状**: PDF ダウンロードが失敗

**解決策**:
```bash
# 日本語フォントをインストール
apt-get update
apt-get install fonts-noto-cjk

# Dockerの場合は既に含まれています
```

### フロントエンドがAPIに接続できない

**症状**: CORS エラー

**解決策**:
```bash
# バックエンドの.envファイルに追加
CORS_ORIGINS=http://localhost:3000,https://your-frontend-url.com

# サーバーを再起動
```

---

## 詳細なドキュメント

より詳しい情報は以下を参照：

- **環境変数**: `ENV_CONFIG.md`
- **本番デプロイ**: `PRODUCTION_DEPLOYMENT.md`
- **PDF生成**: `PDF_GENERATION_GUIDE.md`
- **プロジェクト状況**: `PROJECT_STATUS.md`

---

## サポート

問題が発生した場合：
1. `PROJECT_STATUS.md`の「Known Limitations」を確認
2. `PRODUCTION_DEPLOYMENT.md`の「Troubleshooting」を確認
3. GitHubのIssuesで報告

---

**開発完了日**: 2025-12-18  
**バージョン**: 1.0.0  
**ステータス**: 本番環境対応完了 ✅

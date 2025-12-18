# Google Gemini API セットアップガイド

## ステップ1：APIキーを取得（3分）

### 1. Google AI Studioにアクセス
https://aistudio.google.com/app/apikey

### 2. Googleアカウントでログイン
既存のGmailアカウントでOK

### 3. 「Create API Key」をクリック
- 「Create API key in new project」を選択
- または既存のGoogle Cloud Projectを選択

### 4. APIキーをコピー
`AIza...` で始まる文字列をコピー

---

## ステップ2：環境変数を設定（1分）

```bash
cd /home/user/webapp

# .envファイルを作成
cat > .env << 'EOF'
# Google Gemini API Key
GOOGLE_API_KEY=AIza...your-key-here...

# AI Model Selection
AI_MODEL=gemini-pro

# Logging
LOG_LEVEL=info

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Session Configuration
SESSION_TIMEOUT=3600
EOF
```

または手動で編集：
```bash
nano .env
```

---

## ステップ3：サーバーを再起動（1分）

### 現在のサーバーを停止
```bash
# バックグラウンドで起動しているサーバーを確認
ps aux | grep uvicorn

# PIDを確認してkill（またはCtrl+Cで停止）
pkill -f "uvicorn api_server:app"
```

### 新しい環境変数で再起動
```bash
cd /home/user/webapp
source .env
uvicorn api_server:app --host 0.0.0.0 --port 8000 --log-level info
```

---

## ステップ4：動作確認

### APIの健全性チェック
```bash
curl http://localhost:8000/health
```

期待される出力：
```json
{
  "status": "healthy",
  "service": "Anti-Gravity API",
  "components": {
    "astro_calculator": true,
    "prompt_generator": true,
    "ai_generator": true  ← これがtrueになればOK！
  }
}
```

### テスト鑑定を実行
```bash
cd /home/user/webapp
python3 test_api.py
```

---

## Gemini無料枠の制限

### レート制限
- **60 リクエスト/分** (RPM)
- **1,500 リクエスト/日** (RPD)
- **100万トークン/日**

### 1回の鑑定で使用するトークン数
- 約100,000-150,000トークン（50,000文字生成）
- **1日に約6-10回の鑑定が可能**

### 開発・テストには十分！

---

## トラブルシューティング

### エラー: "API key not found"
```bash
# 環境変数が設定されているか確認
echo $GOOGLE_API_KEY

# 設定されていない場合
export GOOGLE_API_KEY=AIza...your-key...

# サーバー再起動
pkill -f uvicorn
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### エラー: "Rate limit exceeded"
→ 1分間に60リクエストを超えた場合
→ 少し待ってから再試行

### エラー: "Invalid API key"
→ APIキーが間違っている
→ Google AI Studioで再確認

---

## 次のステップ

1. ✅ Gemini APIキー取得
2. ✅ 環境変数設定
3. ✅ サーバー再起動
4. ✅ 動作確認
5. 🚀 フロントエンド起動して使ってみる！

---

## フロントエンド起動

```bash
cd /home/user/webapp/frontend
npm install
npm run dev
```

ブラウザで http://localhost:3000 を開く

---

## Gemini vs GPT-4o 移行

後でGPT-4oに変更する場合：

```bash
# .envファイルを編集
nano .env

# 以下を追加/変更
OPENAI_API_KEY=sk-proj-...
AI_MODEL=gpt-4o

# サーバー再起動
pkill -f uvicorn
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

システムは自動的に `OPENAI_API_KEY` → `GOOGLE_API_KEY` の順で試行します。

---

**作成日**: 2025-12-18  
**対象**: 開発・テスト環境  
**コスト**: 無料（制限あり）

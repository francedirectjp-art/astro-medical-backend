# Anti-Gravity Frontend

Next.js + TypeScript フロントエンド実装

## 技術スタック

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **State Management**: React Hooks

## セットアップ

```bash
# 依存関係のインストール
npm install

# 開発サーバー起動
npm run dev

# 本番ビルド
npm run build
npm start
```

## 環境変数

```.env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## プロジェクト構造

```
frontend/
├── app/
│   ├── layout.tsx              # ルートレイアウト
│   ├── page.tsx                # ホームページ（入力フォーム）
│   ├── globals.css             # グローバルスタイル
│   └── generate/
│       └── [sessionId]/
│           └── page.tsx        # 生成ページ
├── components/
│   └── BirthDataForm.tsx       # 出生データ入力フォーム
├── lib/
│   ├── api.ts                  # APIクライアント
│   └── utils.ts                # ユーティリティ関数
├── types/
│   └── index.ts                # TypeScript型定義
├── public/                     # 静的ファイル
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 主要機能

### 1. 出生データ入力フォーム
- 氏名、生年月日、出生時刻、出生地の入力
- バリデーション機能
- 出生時刻不明オプション

### 2. セッション管理
- セッション作成
- ローカルストレージへの保存
- セッション状態の追跡

### 3. コンテンツ生成UI
- 15ステップの段階的生成
- プログレスバー表示
- 自動生成モード
- リアルタイムコンテンツ表示

### 4. PDFダウンロード
- 生成完了後のPDFダウンロード機能
- ワンクリックダウンロード

## APIエンドポイント統合

```typescript
// セッション作成
await api.createSession(birthData);

// ステップ生成
await api.generateStep(sessionId, stepId);

// ストリーミング生成
for await (const chunk of api.generateStepStream(sessionId, stepId)) {
  console.log(chunk);
}

// PDFダウンロード
const blob = await api.downloadPDF(sessionId);
```

## カスタマイズ

### スタイル変更

`tailwind.config.ts`でカラーテーマを変更:

```typescript
theme: {
  extend: {
    colors: {
      'anti-gravity': {
        dark: '#1a1a1a',
        primary: '#2c3e50',
        secondary: '#34495e',
        accent: '#0ea5e9',
      }
    }
  }
}
```

### APIベースURL変更

`.env.local`ファイルを作成:

```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## デプロイ

### Vercel（推奨）

```bash
# Vercelにデプロイ
vercel

# 本番デプロイ
vercel --prod
```

環境変数を設定:
- `NEXT_PUBLIC_API_URL`: バックエンドAPIのURL

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

```bash
docker build -t anti-gravity-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:8000 anti-gravity-frontend
```

## 今後の拡張

- [ ] ストリーミング表示のタイプライター効果
- [ ] サスペンド/レジューム機能
- [ ] チャート画像の表示
- [ ] ダークモード
- [ ] 多言語対応
- [ ] レスポンシブデザインの強化

# Anti-Gravity Frontend

Next.js 14 + TypeScript + Tailwind CSS による占星術人生経営戦略書システムのフロントエンド

## 技術スタック

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.3
- **Styling**: Tailwind CSS 3.4
- **HTTP Client**: Axios
- **Date Utilities**: date-fns

## 機能

### 1. 出生データ入力
- 氏名、出生日時、出生地の入力フォーム
- バリデーション機能
- 出生時間不明時の処理（正午として計算）
- 都道府県選択

### 2. 進捗表示
- リアルタイムプログレスバー
- 完了ステップ数と総ステップ数
- 累計文字数表示
- 現在処理中のステップ名

### 3. コンテンツ表示
- 静的コンテンツ（理論背景、基礎講義）
- 動的AIコンテンツ（配置分析、シナリオ、提言）
- タイプライター効果（ストリーミング時）
- セクション別カラーコーディング

### 4. PDF生成・ダウンロード
- ワンクリックPDFダウンロード
- 自動ファイル名生成
- ダウンロード進捗表示

### 5. UX機能
- アニメーション（フェードイン、スライドアップ）
- ローディングスピナー
- エラーメッセージ表示
- レスポンシブデザイン

## セットアップ

### 前提条件

- Node.js 18.x 以上
- npm または yarn

### インストール

```bash
cd frontend
npm install
```

### 環境変数

`.env.local` ファイルを作成:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 開発サーバー起動

```bash
npm run dev
```

ブラウザで http://localhost:3000 を開く

### ビルド

```bash
npm run build
npm start
```

## プロジェクト構造

```
frontend/
├── app/
│   ├── layout.tsx          # ルートレイアウト
│   ├── page.tsx            # メインページ
│   └── globals.css         # グローバルスタイル
├── components/
│   ├── BirthDataForm.tsx   # 出生データ入力フォーム
│   ├── ProgressBar.tsx     # 進捗バー
│   └── ContentDisplay.tsx  # コンテンツ表示
├── lib/
│   └── api.ts              # API クライアント
├── types/
│   └── index.ts            # TypeScript型定義
├── public/                 # 静的ファイル
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── README.md
```

## コンポーネント

### BirthDataForm

出生データの入力フォーム

**Props:**
- `onSubmit: (data: BirthData) => void` - フォーム送信時のコールバック
- `loading?: boolean` - ローディング状態

**Features:**
- リアルタイムバリデーション
- エラーメッセージ表示
- 出生時間不明チェックボックス
- 都道府県セレクト

### ProgressBar

生成進捗の表示

**Props:**
- `current: number` - 完了ステップ数
- `total: number` - 総ステップ数
- `currentStep?: string` - 現在のステップ名
- `totalCharacters?: number` - 累計文字数

**Features:**
- アニメーション付きプログレスバー
- パーセンテージ表示
- 文字数カウント

### ContentDisplay

生成されたコンテンツの表示

**Props:**
- `content: StepContent | null` - 表示するコンテンツ
- `streaming?: boolean` - ストリーミングモード
- `streamContent?: string` - ストリーミング中のテキスト

**Features:**
- タイプライター効果
- セクション別スタイリング
- 文字数表示

## API連携

### AntiGravityAPI クラス

```typescript
import api from '@/lib/api';

// セッション作成
const session = await api.createSession(birthData);

// ステップ生成
const content = await api.generateStep(sessionId, stepId);

// ストリーミング生成
for await (const chunk of api.generateStepStream(sessionId, stepId)) {
  console.log(chunk);
}

// PDF ダウンロード
const pdfBlob = await api.downloadPDF(sessionId);
```

### 主要エンドポイント

- `POST /api/session/create` - セッション作成
- `GET /api/session/{id}` - セッション情報取得
- `POST /api/generate/step` - ステップ生成
- `POST /api/generate/step/stream` - ストリーミング生成
- `GET /api/session/{id}/pdf` - PDF ダウンロード
- `GET /api/content/sessions` - セッション構造取得

## スタイリング

### Tailwind CSS カスタム設定

```typescript
// tailwind.config.ts
theme: {
  extend: {
    colors: {
      'anti-gravity': {
        dark: '#1a1a1a',
        primary: '#2c3e50',
        secondary: '#34495e',
        accent: '#0ea5e9',
      }
    },
    animation: {
      'fade-in': 'fadeIn 0.5s ease-in',
      'slide-up': 'slideUp 0.5s ease-out',
    }
  }
}
```

### カスタムアニメーション

- `animate-fade-in` - フェードイン
- `animate-slide-up` - スライドアップ
- `animate-pulse` - 点滅

## デプロイ

### Vercel (推奨)

```bash
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### 環境変数設定

デプロイ時に以下の環境変数を設定:

```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## トラブルシューティング

### API接続エラー

```
Error: Network Error
```

**解決策:**
1. バックエンドAPIが起動しているか確認
2. NEXT_PUBLIC_API_URL が正しく設定されているか確認
3. CORSが正しく設定されているか確認

### ビルドエラー

```
Error: Module not found
```

**解決策:**
```bash
rm -rf node_modules .next
npm install
npm run build
```

### スタイルが反映されない

```bash
# Tailwind CSSの再ビルド
npm run build
```

## 今後の拡張予定

- [ ] ユーザー認証
- [ ] セッション保存・再開機能
- [ ] レスポートプレビュー機能
- [ ] ホロスコープチャート表示
- [ ] ダークモード対応
- [ ] 多言語対応（英語）
- [ ] PWA対応

## ライセンス

Proprietary - Anti-Gravity Project

## サポート

問題が発生した場合は、以下の情報を含めて報告してください:

1. エラーメッセージ
2. ブラウザとバージョン
3. 再現手順
4. コンソールログ

---

**作成日**: 2024年12月17日  
**バージョン**: 1.0.0  
**担当**: Anti-Gravity開発チーム

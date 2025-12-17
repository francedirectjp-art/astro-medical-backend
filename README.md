# Anti-Gravity (アンチグラビティ)
## 占星術人生経営戦略書 自動生成システム

---

## 📋 プロジェクト概要

**Anti-Gravity**は、ユーザーの出生データに基づき、MBAホルダーの「人生経営戦略コンサルタント」というペルソナを持つAIが、約50,000文字の超長編鑑定書（PDF）を自動生成するウェブアプリケーションです。

### コアバリュー
占星術を神秘主義ではなく「経営資源の分析ツール」として提供します。

---

## 📁 ファイル構成

```
/home/user/webapp/
├── README.md                              # このファイル
├── anti_gravity_specification.md          # 詳細仕様書
├── anti_gravity_issues_and_improvements.md # 問題点と改善提案
├── anti_gravity_master_content.json       # マスターコンテンツJSON（77KB）
├── astro_calculator.py                    # 天体計算モジュール（Swiss Ephemeris）
├── api_server.py                          # FastAPI バックエンドサーバー
├── ai_generator.py                        # AI生成モジュール（OpenAI/Gemini）
├── prompt_generator.py                    # AI生成用プロンプトジェネレーター
├── main.py                                # Flask版サーバー（レガシー）
├── requirements.txt                       # Python依存パッケージ
├── swe_data/                              # Swiss Ephemeris天文暦データ
└── Procfile                               # Heroku/Render用
```

---

## 🚀 クイックスタート

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. AI APIキーの設定

```bash
# OpenAI を使用する場合
export OPENAI_API_KEY="your-openai-api-key"

# Gemini を使用する場合
export GOOGLE_API_KEY="your-google-api-key"
```

### 3. APIサーバーの起動

```bash
# FastAPI版（推奨）
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

# Flask版（レガシー）
python main.py
```

### 4. 動作確認

```bash
# ヘルスチェック
curl http://localhost:8000/health

# AI設定状態確認
curl http://localhost:8000/api/ai/status

# ホロスコープ計算テスト
curl -X POST http://localhost:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"name":"テスト","birth_year":1990,"birth_month":1,"birth_day":15,"birth_hour":10,"birth_minute":30,"birth_place":"東京都"}'
```

---

## 📊 主要機能

### 天体計算（astro_calculator.py）
- **Swiss Ephemeris**を使用した高精度計算
- 10主要天体 + カイロン + ドラゴンヘッド/テイル
- 12ハウス（Placidusシステム）
- 4アングル（ASC/MC/IC/DC）
- 主要アスペクト検出
- 4元素・3区分バランス分析
- プログレス計算
- トランジット計算・予測

### AI生成（ai_generator.py）
- **OpenAI GPT-4o / Gemini 1.5 Pro** 対応
- 文字数管理（3段階リカバリーシステム）
- ストリーミング生成
- セッション管理
- ユーザープロファイル自動生成

### APIエンドポイント（api_server.py）

#### 基本
| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/health` | GET | ヘルスチェック |
| `/api/ai/status` | GET | AI設定状態確認 |
| `/api/ai/test` | POST | AI生成テスト |

#### セッション管理
| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/api/session/create` | POST | セッション作成＋計算 |
| `/api/session/{id}` | GET | セッション情報取得 |
| `/api/session/{id}/chart` | GET | ホロスコープデータ取得 |
| `/api/session/{id}/variables/{step}` | GET | ステップ変数取得 |
| `/api/session/{id}/content` | GET | 生成済みコンテンツ取得 |
| `/api/session/{id}/full-text` | GET | 全テキスト結合取得 |

#### AI生成
| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/api/generate/step` | POST | ステップコンテンツ生成 |
| `/api/generate/step/stream` | POST | ストリーミング生成 |
| `/api/generate/status/{id}` | GET | 生成ステータス取得 |

#### 未来予測
| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/api/session/{id}/progressed` | GET | プログレスチャート |
| `/api/session/{id}/transit` | GET | トランジットチャート |
| `/api/session/{id}/forecast` | GET | 3年間予測 |

#### コンテンツ
| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/api/content/master` | GET | マスターコンテンツ取得 |
| `/api/content/step/{step_id}` | GET | ステップコンテンツ取得 |
| `/api/content/sessions` | GET | セッション構造取得 |

---

## 🤖 AI生成フロー

```
1. セッション作成 (/api/session/create)
   └── ホロスコープ計算
   └── 全ステップ変数準備

2. ステップ生成 (/api/generate/step)
   ├── 静的コンテンツ取得（理論背景・基礎講義）
   ├── 動的コンテンツ生成（配置分析・シナリオ・提言）
   │   ├── プロンプト構築
   │   ├── AI生成実行
   │   └── 文字数リカバリー（必要に応じて）
   └── セッション更新

3. ユーザープロファイル生成（Step 2-A完了時）
   └── 以降の全ステップで参照

4. 全テキスト取得 (/api/session/{id}/full-text)
   └── PDF生成（実装予定）
```

---

## 📖 コンテンツ構成

### 全15ステップ・6セッション

| セッション | ステップ | 章 | 内容 |
|-----------|---------|-----|------|
| 1. 基盤スペック | 1-A | 序章/第1章 | 4元素バランス |
| | 1-B | 第2章/第3章 | 3区分/アングル |
| 2. 内なる経営チーム | 2-A | 第4章 | 太陽・月 |
| | 2-B | 第5章 | 水星・金星・火星 |
| 3. 社会との関わり | 3-A | 第6章 | 木星・土星 |
| | 3-B | 第7章 | 天王星・海王星・冥王星 |
| 4. 独自の物語 | 4-A | 第8章 | アスペクト分析 |
| | 4-B | 第9章-1 | カイロン |
| | 4-C | 第9章-2 | ドラゴンヘッド |
| 5. ビジネスモデル | 5-A | 第10章-1 | 2ハウス（財源） |
| | 5-B | 第10章-2 | 6ハウス（働き方） |
| | 5-C | 第10章-3 | 10ハウス（天職） |
| 6. 未来予測 | 6-A | 第12章 | プログレス分析 |
| | 6-B | 第13/14章 | トランジット分析 |
| | 6-C | エピローグ | CEOへの手紙 |

### 6ブロック執筆メソッド

| ブロック | 種類 | 最低文字数 |
|---------|------|-----------|
| 理論背景 (Theory) | 静的 | 400字 |
| 基礎講義 (Lecture) | 静的 | 1,000字 |
| 配置分析 (Analysis) | 動的（AI生成） | 800字 |
| 深層読解 (Symbol) | 動的（AI生成） | 600字 |
| シナリオ (Scenario) | 動的（AI生成） | 1,000字 |
| 提言とワーク (Action) | 動的（AI生成） | 300字 |

---

## ⚙️ 技術スタック

| レイヤー | 技術 |
|---------|------|
| バックエンド | Python (FastAPI) |
| 天体計算 | PySwissEph |
| AI連携 | OpenAI GPT-4o / Google Gemini 1.5 Pro |
| PDF生成 | ReportLab（実装予定） |

---

## 📝 開発ロードマップ

### Phase 1: コアエンジン ✅ 完了
- [x] Swiss Ephemeris実装
- [x] 天体計算モジュール
- [x] JSONマスターデータ

### Phase 2: ハイブリッド生成 ✅ 完了
- [x] プロンプトエンジニアリング
- [x] AI API連携（OpenAI/Gemini）
- [x] 文字数リカバリーロジック
- [x] ストリーミング生成

### Phase 3: UI構築とPDF化 🔄 次のフェーズ
- [ ] フロントエンド実装
- [ ] PDF生成エンジン
- [ ] 進捗表示UI

### Phase 4: テストと最適化
- [ ] 異常系テスト
- [ ] UXテスト
- [ ] パフォーマンス最適化

---

## 📚 ドキュメント

- **仕様書**: `anti_gravity_specification.md`
- **問題点と改善提案**: `anti_gravity_issues_and_improvements.md`
- **マスターコンテンツ**: `anti_gravity_master_content.json`

---

## ⚠️ 注意事項

1. **AI APIキー**: 環境変数 `OPENAI_API_KEY` または `GOOGLE_API_KEY` を設定してください
2. **Swiss Ephemerisデータ**: `swe_data/`ディレクトリに天文暦ファイルが必要です
3. **出生時間不明の場合**: 正午（12:00）を仮定して計算します
4. **カイロン計算**: 一部の天文暦ファイルがない場合、エラーが発生することがあります

---

## 📄 ライセンス

プロジェクト固有

---

*作成日: 2024年*
*バージョン: 1.1.0 (AI連携版)*

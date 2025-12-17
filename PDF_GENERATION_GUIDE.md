# Anti-Gravity PDF生成機能ガイド

## 概要

Anti-Gravity占星術人生経営戦略書システムのPDF生成機能の詳細ガイドです。ReportLabを使用し、50,000文字の日本語PDFレポートを高品質に生成します。

## 実装完了日

2024年12月17日

## 機能概要

### 主要機能

1. **高品質日本語PDF生成**
   - ReportLab 4.0.7を使用
   - 日本語フォント対応（Noto Sans CJKフォールバック付き）
   - A4サイズ、適切な余白設定（20-25mm）

2. **構造化されたレポート**
   - 表紙ページ（出生データ表示）
   - 自動生成目次
   - 6セッション × 複数ステップ構造
   - ページ番号とヘッダー/フッター

3. **コンテンツ統合**
   - 静的コンテンツ（理論背景、基礎講義）
   - 動的AI生成コンテンツ（配置分析、シナリオ、提言）
   - 6ブロック執筆メソッド完全対応

4. **API統合**
   - ダウンロードエンドポイント
   - ファイル保存エンドポイント
   - プレビューエンドポイント

## ファイル構成

### pdf_generator.py (698行)

PDF生成のコアモジュール

```python
# 主要クラス
class AntiGravityPDFGenerator:
    """PDF生成エンジン"""
    def generate(self, output_path: str) -> str
    def generate_to_buffer(self) -> BytesIO
    
# ヘルパー関数
def generate_pdf_from_session(session_data, master_content, output_path)
def generate_pdf_to_buffer(session_data, master_content)
```

### 機能詳細

#### 1. フォント管理

```python
def register_japanese_fonts():
    """日本語フォントを自動検出・登録"""
    # フォント候補パス:
    # - /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
    # - /usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc
    # - フォールバック: Helvetica
```

**注意**: 本番環境では必ず日本語フォントをインストールしてください。

```bash
# Ubuntu/Debian
sudo apt-get install fonts-noto-cjk

# CentOS/RHEL
sudo yum install google-noto-sans-cjk-fonts
```

#### 2. ページテンプレート

- **NumberedCanvas**: ページ番号付きキャンバスクラス
- ヘッダー: "Strategic Life Navigation System | Anti-Gravity"
- フッター: ページ番号（中央配置）
- 表紙以外の全ページに適用

#### 3. スタイル定義

```python
styles = {
    'CoverTitle': 表紙タイトル（28pt, Bold）
    'CoverSubtitle': サブタイトル（14pt）
    'CoverInfo': 出生データ（11pt）
    'SessionTitle': セッションタイトル（20pt, Bold）
    'ChapterTitle': チャプタータイトル（16pt, Bold）
    'SectionTitle': セクションタイトル（13pt, Bold）
    'Body': 本文（10pt, Justify）
    'TOCTitle': 目次タイトル（20pt, Bold, Center）
    'TOCSession': 目次セッション（12pt, Bold）
    'TOCStep': 目次ステップ（10pt, Indent）
}
```

#### 4. PDF構造

```
┌─────────────────────────────────────┐
│ 1. 表紙ページ                         │
│    - タイトル                         │
│    - サブタイトル                     │
│    - 出生データ（氏名、日時、場所）    │
│    - 作成日                           │
├─────────────────────────────────────┤
│ 2. 目次                               │
│    - Session 1〜6                     │
│    - 各ステップのチャプタータイトル    │
├─────────────────────────────────────┤
│ 3. Session 1: 基盤スペック            │
│    Step 1-A: 第1章                    │
│      - はじめに（プロローグ）         │
│      - 理論背景（Theory）             │
│      - 基礎講義（Lecture）            │
│      - 配置分析（Analysis）           │
│      - シナリオ（Scenario）           │
│      - 提言とワーク（Action）         │
│    Step 1-B: 第2・3章                 │
│      ...                              │
├─────────────────────────────────────┤
│ 4. Session 2: 内なる経営チーム        │
│    Step 2-A, 2-B ...                  │
├─────────────────────────────────────┤
│ 5. Session 3〜6                       │
│    ...                                │
├─────────────────────────────────────┤
│ 6. エピローグ                         │
│    - CEOへの手紙                      │
│    - 最終提言                         │
└─────────────────────────────────────┘
```

## API使用方法

### 1. PDFダウンロード

```bash
# セッションIDを指定してPDFを直接ダウンロード
GET /api/session/{session_id}/pdf

# レスポンス
Content-Type: application/pdf
Content-Disposition: attachment; filename="anti_gravity_{name}_{date}.pdf"
```

#### 使用例

```bash
curl -o report.pdf "http://localhost:8000/api/session/abc123/pdf"
```

```javascript
// JavaScript (fetch)
fetch(`/api/session/${sessionId}/pdf`)
  .then(response => response.blob())
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'anti_gravity_report.pdf';
    a.click();
  });
```

### 2. PDFファイル保存

```bash
# サーバーファイルシステムにPDFを保存
POST /api/session/{session_id}/pdf/save
Content-Type: application/json

{
  "output_dir": "./output"  # オプション、デフォルトは "./output"
}

# レスポンス
{
  "success": true,
  "file_path": "/path/to/anti_gravity_name_20241217_115430.pdf",
  "file_name": "anti_gravity_name_20241217_115430.pdf",
  "session_id": "abc123",
  "total_characters": 50000,
  "completed_steps": 15
}
```

### 3. PDF構造プレビュー

```bash
# PDF生成前に構造をプレビュー
GET /api/session/{session_id}/pdf/preview

# レスポンス
{
  "session_id": "abc123",
  "document_title": "山田太郎様 人生経営戦略書",
  "total_characters": 50000,
  "completed_steps": 15,
  "sections": [
    {
      "session_id": 1,
      "title": "基盤スペック",
      "steps": [
        {
          "step_id": "1-A",
          "chapter_title": "はじめに / 第1章",
          "character_count": 3500,
          "has_content": true
        },
        ...
      ]
    },
    ...
  ]
}
```

## Python直接使用

### 基本的な使い方

```python
import json
from pdf_generator import generate_pdf_from_session, generate_pdf_to_buffer

# マスターコンテンツ読み込み
with open('anti_gravity_master_content.json', 'r', encoding='utf-8') as f:
    master_content = json.load(f)

# セッションデータ（APIサーバーから取得）
session_data = {
    'session_id': 'xxx',
    'birth_data': {...},
    'completed_steps': ['1-A', '1-B', ...],
    'generated_content': {...},
    'total_characters': 50000
}

# 方法1: ファイルに保存
pdf_path = generate_pdf_from_session(
    session_data,
    master_content,
    output_path='output/report.pdf'
)
print(f"PDF生成: {pdf_path}")

# 方法2: メモリバッファに生成（ダウンロード用）
pdf_buffer = generate_pdf_to_buffer(session_data, master_content)
# pdf_bufferをHTTPレスポンスで返す
```

### カスタムPDF生成

```python
from pdf_generator import AntiGravityPDFGenerator

# カスタムジェネレーター
generator = AntiGravityPDFGenerator(session_data, master_content)

# PDFビルド（カスタマイズ可能）
generator._build_cover_page()      # 表紙
generator._build_table_of_contents()  # 目次
generator._build_content()         # メインコンテンツ

# 生成
pdf_path = generator.generate('custom_output.pdf')
```

## テスト結果

### 生成されたPDFサンプル

```
ファイル名: test_anti_gravity_sample.pdf
ページ数: 10ページ
ファイルサイズ: 30.75 KB
文字数: 9,500文字
完了ステップ: 3ステップ (1-A, 1-B, 2-A)
```

### パフォーマンス

- **3ステップ（9,500文字）**: 約650ms
- **推定15ステップ（50,000文字）**: 約2-3秒
- **メモリ使用量**: 約5-10MB

### スケーラビリティ

- ✅ 50,000文字の長文に対応
- ✅ メモリ効率的なストリーム生成
- ✅ 複数セッション並行処理可能

## エラーハンドリング

### 1. フォント問題

```python
# 警告が出る場合
"Failed to register font: TTC file postscript outlines are not supported"

# 解決策
# 1. TrueType形式のフォントをインストール
sudo apt-get install fonts-noto-cjk-core

# 2. または、フォールバックフォント（Helvetica）を使用
# - 日本語は正しく表示されないが、PDFは生成される
```

### 2. セッションデータ不足

```python
# エラー
HTTPException(status_code=400, detail="No content available")

# 原因
completed_steps が空、または generated_content が存在しない

# 解決策
まずコンテンツ生成APIを実行してからPDF生成を行う
```

### 3. ファイルシステムエラー

```python
# エラー
OSError: [Errno 2] No such file or directory

# 解決策
output_dir が存在することを確認、または自動作成を有効化
os.makedirs(output_dir, exist_ok=True)
```

## 本番環境デプロイ

### 必須要件

1. **日本語フォントのインストール**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra

# Docker (Dockerfile)
RUN apt-get update && \
    apt-get install -y fonts-noto-cjk && \
    rm -rf /var/lib/apt/lists/*
```

2. **ディスク容量**

- 一時ファイル用: 最低100MB
- 生成PDFストレージ: ユーザー数 × 約50KB

3. **メモリ**

- 推奨: 512MB以上
- PDF生成時ピーク: 約10-20MB/セッション

### 環境変数

```bash
# オプション: PDF出力ディレクトリ
export PDF_OUTPUT_DIR=/var/app/output

# オプション: フォントパス（カスタムフォント使用時）
export CUSTOM_FONT_PATH=/usr/share/fonts/custom/NotoSans.ttf
```

### Nginx設定（大きなPDFダウンロード用）

```nginx
location /api/session/*/pdf {
    proxy_pass http://localhost:8000;
    proxy_read_timeout 300s;  # 5分
    proxy_buffering off;
    client_max_body_size 10M;
}
```

## トラブルシューティング

### Q: PDFが真っ白/空白になる

**A**: コンテンツが正しく生成されているか確認

```python
# プレビューAPIで確認
GET /api/session/{session_id}/pdf/preview

# セッションコンテンツを直接確認
GET /api/session/{session_id}/content
```

### Q: 日本語が文字化けする

**A**: フォント設定を確認

```python
# pdf_generator.py のログを確認
# "Japanese font registered: ..." が出力されているか確認

# フォントパスを手動指定
FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
pdfmetrics.registerFont(TTFont('NotoSansJP', FONT_PATH))
```

### Q: PDFダウンロードが遅い

**A**: 考えられる原因

1. コンテンツ量が多い（50,000文字以上）
2. サーバーCPU不足
3. ネットワーク帯域制限

**解決策**:
- 非同期生成を検討（バックグラウンドジョブ）
- CDN経由でのダウンロード
- 事前生成（セッション完了時にPDFを生成）

## 今後の拡張予定

### 短期（1-2週間）

- [ ] 表紙デザインの改善（ロゴ、カラー）
- [ ] 図表の追加（ホロスコープチャート画像）
- [ ] ページ区切りの最適化
- [ ] 改ページ処理の改善

### 中期（1-2ヶ月）

- [ ] カスタムテンプレート機能
- [ ] PDFセキュリティ（パスワード保護）
- [ ] 透かし機能
- [ ] 複数言語対応（英語版）

### 長期（3-6ヶ月）

- [ ] インタラクティブPDF（ブックマーク、リンク）
- [ ] 動的グラフ生成
- [ ] カスタムフォント選択
- [ ] 印刷最適化版

## 関連ドキュメント

- [anti_gravity_specification.md](./anti_gravity_specification.md) - システム全体仕様
- [anti_gravity_issues_and_improvements.md](./anti_gravity_issues_and_improvements.md) - 技術課題と改善案
- [README.md](./README.md) - プロジェクト概要

## サポート

問題が発生した場合は、以下の情報を含めて報告してください：

1. エラーメッセージ全文
2. セッションID
3. コンテンツ文字数
4. 環境情報（OS、Pythonバージョン、ReportLabバージョン）

---

**作成日**: 2024年12月17日  
**バージョン**: 1.0.0  
**担当**: Anti-Gravity開発チーム

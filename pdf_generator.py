"""
Anti-Gravity PDF Generator
ReportLabを使用した50,000文字日本語PDF生成エンジン
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# フォント設定
# =============================================================================

def register_japanese_fonts():
    """
    日本語フォントを登録
    Noto Sans JPをダウンロードして使用
    """
    try:
        # システムにインストール済みのフォントを試す
        font_paths = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # フォールバック
        ]
        
        # Noto Sans JPフォントがない場合のフォールバック
        # 注意：本番環境では必ず日本語フォントをインストールすること
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('NotoSansJP', font_path))
                    pdfmetrics.registerFont(TTFont('NotoSansJP-Bold', font_path))
                    logger.info(f"Japanese font registered: {font_path}")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to register font {font_path}: {e}")
                    continue
        
        # フォントが見つからない場合はデフォルトを使用
        logger.warning("Japanese fonts not found, using default fonts")
        return False
        
    except Exception as e:
        logger.error(f"Font registration error: {e}")
        return False


# フォント登録
FONT_AVAILABLE = register_japanese_fonts()
BASE_FONT = 'NotoSansJP' if FONT_AVAILABLE else 'Helvetica'
BASE_FONT_BOLD = 'NotoSansJP-Bold' if FONT_AVAILABLE else 'Helvetica-Bold'


# =============================================================================
# ページテンプレートとヘッダー/フッター
# =============================================================================

class NumberedCanvas(canvas.Canvas):
    """ページ番号付きキャンバス"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        """ページ番号を追加して保存"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_page_number(self, page_count):
        """ページ番号を描画"""
        self.setFont(BASE_FONT, 9)
        self.setFillColor(colors.grey)
        
        # フッター
        page_num = self._pageNumber
        text = f"- {page_num} -"
        self.drawCentredString(A4[0] / 2, 15 * mm, text)
        
        # ヘッダー（タイトル）
        if page_num > 1:  # 表紙以外
            self.setFont(BASE_FONT, 8)
            self.drawString(20 * mm, A4[1] - 15 * mm, "Strategic Life Navigation System | Anti-Gravity")


# =============================================================================
# スタイル定義
# =============================================================================

def create_styles() -> Dict[str, ParagraphStyle]:
    """カスタムスタイルを作成"""
    styles = getSampleStyleSheet()
    
    custom_styles = {
        # 表紙用
        'CoverTitle': ParagraphStyle(
            'CoverTitle',
            parent=styles['Heading1'],
            fontName=BASE_FONT_BOLD,
            fontSize=28,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceAfter=20,
            leading=42
        ),
        'CoverSubtitle': ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontName=BASE_FONT,
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=10,
            leading=21
        ),
        'CoverInfo': ParagraphStyle(
            'CoverInfo',
            parent=styles['Normal'],
            fontName=BASE_FONT,
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            alignment=TA_CENTER,
            spaceAfter=6,
            leading=16
        ),
        
        # 本文用
        'SessionTitle': ParagraphStyle(
            'SessionTitle',
            parent=styles['Heading1'],
            fontName=BASE_FONT_BOLD,
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            spaceBefore=24,
            leading=30,
            keepWithNext=True
        ),
        'ChapterTitle': ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading2'],
            fontName=BASE_FONT_BOLD,
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=18,
            leading=24,
            keepWithNext=True
        ),
        'SectionTitle': ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading3'],
            fontName=BASE_FONT_BOLD,
            fontSize=13,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=12,
            leading=19,
            keepWithNext=True
        ),
        'Body': ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName=BASE_FONT,
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            leading=17,
            wordWrap='CJK'
        ),
        'BodyIndent': ParagraphStyle(
            'BodyIndent',
            parent=styles['Normal'],
            fontName=BASE_FONT,
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_JUSTIFY,
            leftIndent=10,
            spaceAfter=6,
            leading=17,
            wordWrap='CJK'
        ),
        
        # 目次用
        'TOCTitle': ParagraphStyle(
            'TOCTitle',
            parent=styles['Heading1'],
            fontName=BASE_FONT_BOLD,
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceAfter=20,
            leading=30
        ),
        'TOCSession': ParagraphStyle(
            'TOCSession',
            parent=styles['Normal'],
            fontName=BASE_FONT_BOLD,
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
            spaceBefore=12,
            leading=18
        ),
        'TOCStep': ParagraphStyle(
            'TOCStep',
            parent=styles['Normal'],
            fontName=BASE_FONT,
            fontSize=10,
            textColor=colors.HexColor('#34495e'),
            leftIndent=15,
            spaceAfter=4,
            leading=15
        ),
    }
    
    return custom_styles


# =============================================================================
# PDF生成メインクラス
# =============================================================================

class AntiGravityPDFGenerator:
    """Anti-Gravity PDF生成エンジン"""
    
    def __init__(self, session_data: Dict[str, Any], master_content: Dict[str, Any]):
        """
        Args:
            session_data: セッションデータ（chart_data, generated_content等）
            master_content: anti_gravity_master_content.json
        """
        self.session_data = session_data
        self.master_content = master_content
        self.styles = create_styles()
        self.story = []  # PDF要素のリスト
        self.toc_entries = []  # 目次エントリ
    
    def generate(self, output_path: str) -> str:
        """
        PDFを生成
        
        Args:
            output_path: 出力ファイルパス
        
        Returns:
            生成されたPDFのパス
        """
        try:
            logger.info(f"Starting PDF generation: {output_path}")
            
            # ドキュメント作成
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=20 * mm,
                rightMargin=20 * mm,
                topMargin=25 * mm,
                bottomMargin=25 * mm,
                title=self._get_document_title(),
                author="Strategic Life Navigation System",
                subject="人生経営戦略書"
            )
            
            # コンテンツ構築
            self._build_cover_page()
            self._build_table_of_contents()
            self._build_content()
            
            # PDF生成
            doc.build(
                self.story,
                onFirstPage=self._on_first_page,
                onLaterPages=self._on_later_pages,
                canvasmaker=NumberedCanvas
            )
            
            logger.info(f"PDF generation completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def generate_to_buffer(self) -> BytesIO:
        """
        PDFをメモリバッファに生成（ダウンロード用）
        
        Returns:
            BytesIO: PDFバイナリデータ
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
            topMargin=25 * mm,
            bottomMargin=25 * mm,
            title=self._get_document_title(),
            author="Strategic Life Navigation System",
            subject="人生経営戦略書"
        )
        
        # コンテンツ構築
        self._build_cover_page()
        self._build_table_of_contents()
        self._build_content()
        
        # PDF生成
        doc.build(
            self.story,
            onFirstPage=self._on_first_page,
            onLaterPages=self._on_later_pages,
            canvasmaker=NumberedCanvas
        )
        
        buffer.seek(0)
        return buffer
    
    def _get_document_title(self) -> str:
        """ドキュメントタイトルを取得"""
        birth_data = self.session_data.get('birth_data', {})
        name = birth_data.get('name', 'ユーザー')
        return f"{name}様 人生経営戦略書"
    
    def _on_first_page(self, canvas, doc):
        """最初のページ（表紙）のコールバック"""
        pass  # 表紙は特別な処理なし
    
    def _on_later_pages(self, canvas, doc):
        """2ページ目以降のコールバック"""
        pass  # NumberedCanvasが処理
    
    # =========================================================================
    # 表紙ページ
    # =========================================================================
    
    def _build_cover_page(self):
        """表紙ページを構築"""
        birth_data = self.session_data.get('birth_data', {})
        name = birth_data.get('name', 'ユーザー')
        birth_date = f"{birth_data.get('birth_year')}年{birth_data.get('birth_month')}月{birth_data.get('birth_day')}日"
        birth_time = f"{birth_data.get('birth_hour', 12):02d}:{birth_data.get('birth_minute', 0):02d}"
        birth_place = birth_data.get('birth_place', '東京都')
        generation_date = datetime.now().strftime("%Y年%m月%d日")
        
        # スペーサー（上部余白）
        self.story.append(Spacer(1, 60 * mm))
        
        # タイトル
        title = Paragraph(
            "人生経営戦略書",
            self.styles['CoverTitle']
        )
        self.story.append(title)
        self.story.append(Spacer(1, 10 * mm))
        
        # サブタイトル
        subtitle = Paragraph(
            "Strategic Life Navigation System",
            self.styles['CoverSubtitle']
        )
        self.story.append(subtitle)
        self.story.append(Spacer(1, 5 * mm))
        
        code_name = Paragraph(
            "Anti-Gravity",
            self.styles['CoverSubtitle']
        )
        self.story.append(code_name)
        self.story.append(Spacer(1, 30 * mm))
        
        # 出生データ
        info_lines = [
            f"氏名：{name} 様",
            f"出生日時：{birth_date} {birth_time}",
            f"出生地：{birth_place}",
            "",
            f"作成日：{generation_date}",
        ]
        
        for line in info_lines:
            info = Paragraph(line, self.styles['CoverInfo'])
            self.story.append(info)
        
        # ページ区切り
        self.story.append(PageBreak())
    
    # =========================================================================
    # 目次
    # =========================================================================
    
    def _build_table_of_contents(self):
        """目次を構築"""
        toc_title = Paragraph("目次", self.styles['TOCTitle'])
        self.story.append(toc_title)
        self.story.append(Spacer(1, 10 * mm))
        
        # セッション構造を取得
        sessions = self.master_content.get('sessions', [])
        completed_steps = self.session_data.get('completed_steps', [])
        
        for session in sessions:
            session_title = session.get('title', '')
            session_para = Paragraph(
                f"Session {session.get('session_id')}: {session_title}",
                self.styles['TOCSession']
            )
            self.story.append(session_para)
            
            for step in session.get('steps', []):
                step_id = step.get('step_id')
                if step_id in completed_steps:
                    chapter_title = step.get('chapter_title', '')
                    step_para = Paragraph(
                        f"　{step_id}: {chapter_title}",
                        self.styles['TOCStep']
                    )
                    self.story.append(step_para)
        
        self.story.append(PageBreak())
    
    # =========================================================================
    # メインコンテンツ
    # =========================================================================
    
    def _build_content(self):
        """メインコンテンツを構築"""
        sessions = self.master_content.get('sessions', [])
        completed_steps = self.session_data.get('completed_steps', [])
        generated_content = self.session_data.get('generated_content', {})
        
        for session in sessions:
            # セッションタイトル
            session_title = Paragraph(
                f"Session {session.get('session_id')}: {session.get('title', '')}",
                self.styles['SessionTitle']
            )
            self.story.append(session_title)
            
            # セッション説明
            if session.get('description'):
                desc = Paragraph(
                    session.get('description'),
                    self.styles['BodyIndent']
                )
                self.story.append(desc)
                self.story.append(Spacer(1, 8 * mm))
            
            # 各ステップ
            for step in session.get('steps', []):
                step_id = step.get('step_id')
                
                if step_id not in completed_steps:
                    continue
                
                # チャプタータイトル
                chapter_title = Paragraph(
                    f"{step.get('chapter_number', '')}: {step.get('chapter_title', '')}",
                    self.styles['ChapterTitle']
                )
                self.story.append(chapter_title)
                self.story.append(Spacer(1, 4 * mm))
                
                # コンテンツ取得
                step_content = generated_content.get(step_id, {})
                static_content = step_content.get('static_content', {})
                dynamic_content = step_content.get('dynamic_content', {})
                
                # プロローグ（はじめに）- Step 1-Aのみ
                if step_id == "1-A" and "prologue" in static_content:
                    self._add_section(
                        static_content['prologue'].get('title', 'はじめに'),
                        static_content['prologue'].get('text', '')
                    )
                
                # 理論背景（Theory）
                for key in ['theory', 'theory_modality', 'theory_angles']:
                    if key in static_content:
                        self._add_section(
                            static_content[key].get('title', ''),
                            static_content[key].get('text', '')
                        )
                
                # 基礎講義（Lecture）
                if 'lecture' in static_content:
                    self._add_section(
                        static_content['lecture'].get('title', ''),
                        static_content['lecture'].get('text', '')
                    )
                
                # 動的コンテンツ（AI生成）
                # 配置分析（Analysis）
                if 'analysis' in dynamic_content:
                    self._add_section(
                        "【配置分析】",
                        dynamic_content['analysis']
                    )
                
                # 深層読解（Symbol）
                if 'symbol' in dynamic_content:
                    self._add_section(
                        "【深層読解】",
                        dynamic_content['symbol']
                    )
                
                # シナリオ（Scenario）
                if 'scenario' in dynamic_content:
                    self._add_section(
                        "【シナリオ】",
                        dynamic_content['scenario']
                    )
                
                # 提言とワーク（Action）
                if 'action' in dynamic_content:
                    self._add_section(
                        "【提言とワーク】",
                        dynamic_content['action']
                    )
                
                # 手紙（Letter） - エピローグのみ
                if 'letter' in dynamic_content:
                    self._add_section(
                        "【CEOへの手紙】",
                        dynamic_content['letter']
                    )
                
                # ステップ間のスペース
                self.story.append(Spacer(1, 8 * mm))
            
            # セッション終了後に改ページ
            self.story.append(PageBreak())
    
    def _add_section(self, title: str, content: str):
        """セクションを追加"""
        if not content:
            return
        
        # セクションタイトル
        if title:
            title_para = Paragraph(title, self.styles['SectionTitle'])
            self.story.append(title_para)
        
        # コンテンツを段落に分割
        paragraphs = content.split('\n\n')
        for para_text in paragraphs:
            if para_text.strip():
                # 改行を<br/>タグに変換
                para_text_formatted = para_text.strip().replace('\n', '<br/>')
                
                para = Paragraph(para_text_formatted, self.styles['Body'])
                self.story.append(para)
                self.story.append(Spacer(1, 3 * mm))
        
        # セクション後のスペース
        self.story.append(Spacer(1, 4 * mm))


# =============================================================================
# ヘルパー関数
# =============================================================================

def generate_pdf_from_session(
    session_data: Dict[str, Any],
    master_content: Dict[str, Any],
    output_path: Optional[str] = None
) -> str:
    """
    セッションデータからPDFを生成
    
    Args:
        session_data: セッションデータ
        master_content: マスターコンテンツJSON
        output_path: 出力パス（Noneの場合は自動生成）
    
    Returns:
        生成されたPDFのパス
    """
    if output_path is None:
        session_id = session_data.get('session_id', 'unknown')
        name = session_data.get('birth_data', {}).get('name', 'user')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"anti_gravity_{name}_{timestamp}.pdf"
    
    generator = AntiGravityPDFGenerator(session_data, master_content)
    return generator.generate(output_path)


def generate_pdf_to_buffer(
    session_data: Dict[str, Any],
    master_content: Dict[str, Any]
) -> BytesIO:
    """
    セッションデータからPDFをメモリバッファに生成
    
    Args:
        session_data: セッションデータ
        master_content: マスターコンテンツJSON
    
    Returns:
        BytesIO: PDFバイナリデータ
    """
    generator = AntiGravityPDFGenerator(session_data, master_content)
    return generator.generate_to_buffer()


# =============================================================================
# CLI テスト用
# =============================================================================

def main():
    """テスト実行"""
    import json
    
    # マスターコンテンツ読み込み
    with open('anti_gravity_master_content.json', 'r', encoding='utf-8') as f:
        master_content = json.load(f)
    
    # テスト用セッションデータ
    test_session = {
        "session_id": "test-session-001",
        "birth_data": {
            "name": "テスト太郎",
            "birth_year": 1990,
            "birth_month": 1,
            "birth_day": 15,
            "birth_hour": 10,
            "birth_minute": 30,
            "birth_place": "東京都"
        },
        "completed_steps": ["1-A", "1-B"],
        "generated_content": {
            "1-A": {
                "static_content": {
                    "prologue": {
                        "title": "はじめに",
                        "text": "本書は、あなたの出生図（ネイタルチャート）を「人生経営の設計図」として読み解く試みです。\n\n占星術は、しばしば神秘主義や予言と混同されますが、本書ではそれを「経営資源の分析ツール」として活用します。"
                    },
                    "theory": {
                        "title": "【理論背景】4元素とは何か",
                        "text": "西洋占星術における4元素（火・地・風・水）は、古代ギリシャの哲学者エンペドクレスに遡る概念です。経営学の観点からは、これは「組織の行動特性」を4つのカテゴリーに分類するフレームワークと捉えることができます。"
                    },
                    "lecture": {
                        "title": "【基礎講義】4元素のバランスを読む",
                        "text": "出生図における4元素の分布は、10の主要天体（太陽、月、水星、金星、火星、木星、土星、天王星、海王星、冥王星）がどのサインに位置しているかによって決まります。"
                    }
                },
                "dynamic_content": {
                    "analysis": "あなたの4元素バランスは、火1、地6、風1、水2という配置です。圧倒的に地のエネルギーが強く、これは「実務能力」「安定志向」「資源管理能力」に優れた経営スタイルを示しています。一方、火のエネルギーが不足しているため、新規事業への推進力や変革への動機が弱い傾向があります。",
                    "scenario": "💀失敗シナリオ：保守的すぎて市場の変化に取り残される...\n\n✨成功シナリオ：安定した基盤を活かしながら、少しずつ変革を導入し、持続可能な成長を実現する...",
                    "action": "1. 火のエネルギーを補うため、週に1度は「新しい挑戦」を意識的に取り入れましょう。\n2. 地の強みを活かし、財務管理や品質管理の専門性を高めましょう。\n3. 風のエネルギーを意識し、異業種交流やネットワーキングに参加しましょう。"
                },
                "character_count": 2800
            }
        },
        "total_characters": 2800
    }
    
    # PDF生成
    output_path = "test_output.pdf"
    result = generate_pdf_from_session(test_session, master_content, output_path)
    print(f"PDF生成完了: {result}")


if __name__ == "__main__":
    main()

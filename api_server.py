"""
Anti-Gravity API Server
FastAPIを使用したバックエンドAPI
AI生成機能統合版
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import asyncio
import uuid
import os
import logging

from astro_calculator import AstroCalculator, ProgressedCalculator, TransitCalculator, create_chart

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# FastAPIアプリケーション設定
# =============================================================================

app = FastAPI(
    title="Anti-Gravity API",
    description="占星術人生経営戦略書 自動生成システム",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# AI生成モジュールの遅延読み込み
# =============================================================================

_ai_generator = None
_prompt_generator = None
_session_manager = None


def get_prompt_generator():
    """プロンプトジェネレーターを取得"""
    global _prompt_generator
    if _prompt_generator is None:
        try:
            from prompt_generator import create_prompt_generator
            _prompt_generator = create_prompt_generator()
            logger.info("PromptGenerator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PromptGenerator: {e}")
    return _prompt_generator


def get_ai_generator(provider: str = "openai"):
    """AIジェネレーターを取得"""
    global _ai_generator
    if _ai_generator is None:
        try:
            from ai_generator import create_generator
            _ai_generator = create_generator(
                provider=provider,
                prompt_generator=get_prompt_generator()
            )
            logger.info(f"AIGenerator initialized with provider: {provider}")
        except Exception as e:
            logger.error(f"Failed to initialize AIGenerator: {e}")
    return _ai_generator


def get_session_manager():
    """セッションマネージャーを取得"""
    global _session_manager
    if _session_manager is None:
        try:
            from ai_generator import SessionManager
            generator = get_ai_generator()
            if generator:
                _session_manager = SessionManager(generator)
                logger.info("SessionManager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SessionManager: {e}")
    return _session_manager


# =============================================================================
# データモデル
# =============================================================================

class BirthDataInput(BaseModel):
    """出生データ入力"""
    name: str = Field(..., description="名前")
    birth_year: int = Field(..., ge=1900, le=2100, description="出生年")
    birth_month: int = Field(..., ge=1, le=12, description="出生月")
    birth_day: int = Field(..., ge=1, le=31, description="出生日")
    birth_hour: int = Field(12, ge=0, le=23, description="出生時（不明の場合は12）")
    birth_minute: int = Field(0, ge=0, le=59, description="出生分")
    birth_place: str = Field("東京都", description="出生地")
    birth_time_unknown: bool = Field(False, description="出生時間不明フラグ")


class SessionCreateResponse(BaseModel):
    """セッション作成レスポンス"""
    session_id: str
    chart_data: Dict[str, Any]
    variables: Dict[str, Any]


class StepGenerateRequest(BaseModel):
    """ステップ生成リクエスト"""
    session_id: str
    step_id: str
    provider: str = Field("openai", description="AI provider: openai or gemini")
    stream: bool = Field(False, description="ストリーミングモード")


class GenerationStatus(BaseModel):
    """生成ステータス"""
    session_id: str
    current_step: str
    total_steps: int
    completed_steps: int
    status: str  # "pending", "generating", "completed", "error"
    generated_content: Optional[Dict[str, str]] = None
    total_characters: int = 0


class AIConfigInput(BaseModel):
    """AI設定入力"""
    provider: str = Field("openai", description="openai or gemini")
    model: Optional[str] = Field(None, description="モデル名")
    temperature: float = Field(0.7, ge=0, le=2, description="温度パラメータ")
    api_key: Optional[str] = Field(None, description="APIキー（環境変数より優先）")


# =============================================================================
# インメモリセッション管理（本番ではDBを使用）
# =============================================================================

sessions: Dict[str, Dict[str, Any]] = {}


# =============================================================================
# マスターコンテンツの読み込み
# =============================================================================

def load_master_content() -> Dict[str, Any]:
    """マスターコンテンツJSONを読み込む"""
    try:
        with open('anti_gravity_master_content.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


MASTER_CONTENT = load_master_content()


# =============================================================================
# API エンドポイント - 基本
# =============================================================================

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Anti-Gravity API",
        "version": "1.0.0",
        "status": "running",
        "ai_enabled": get_ai_generator() is not None
    }


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "service": "Anti-Gravity API",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "astro_calculator": True,
            "prompt_generator": get_prompt_generator() is not None,
            "ai_generator": get_ai_generator() is not None,
        }
    }


# =============================================================================
# API エンドポイント - セッション管理
# =============================================================================

@app.post("/api/session/create", response_model=SessionCreateResponse)
async def create_session(birth_data: BirthDataInput):
    """
    新しいセッションを作成し、ホロスコープを計算する
    """
    try:
        # ホロスコープ計算
        birth_datetime = datetime(
            birth_data.birth_year,
            birth_data.birth_month,
            birth_data.birth_day,
            birth_data.birth_hour,
            birth_data.birth_minute
        )
        
        calculator = AstroCalculator(
            birth_datetime,
            birth_data.birth_place,
            birth_data.name
        )
        chart_data = calculator.calculate_all()
        
        # セッションID生成
        session_id = str(uuid.uuid4())
        
        # 全ステップ用の変数を準備
        all_variables = {
            "1-A": calculator.get_variables_for_step("1-A"),
            "1-B": calculator.get_variables_for_step("1-B"),
            "2-A": calculator.get_variables_for_step("2-A"),
            "2-B": calculator.get_variables_for_step("2-B"),
        }
        
        # セッション情報を保存
        sessions[session_id] = {
            "session_id": session_id,
            "birth_data": birth_data.dict(),
            "chart_data": chart_data,
            "calculator": calculator,
            "variables": all_variables,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "completed_steps": [],
            "generated_content": {},
            "total_characters": 0,
            "user_profile": None,
        }
        
        logger.info(f"Session created: {session_id}")
        
        return SessionCreateResponse(
            session_id=session_id,
            chart_data=chart_data,
            variables=all_variables
        )
        
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """セッション情報を取得"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "birth_data": session["birth_data"],
        "status": session["status"],
        "completed_steps": session["completed_steps"],
        "total_characters": session["total_characters"],
        "user_profile": session.get("user_profile"),
    }


@app.get("/api/session/{session_id}/chart")
async def get_chart(session_id: str):
    """ホロスコープデータを取得"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]["chart_data"]


@app.get("/api/session/{session_id}/variables/{step_id}")
async def get_step_variables(session_id: str, step_id: str):
    """特定ステップの変数を取得"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if step_id not in session["variables"]:
        calculator = session["calculator"]
        variables = calculator.get_variables_for_step(step_id)
        session["variables"][step_id] = variables
    
    return session["variables"][step_id]


# =============================================================================
# API エンドポイント - AI生成
# =============================================================================

@app.post("/api/generate/step")
async def generate_step_content(request: StepGenerateRequest):
    """
    特定ステップのコンテンツをAIで生成
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    
    # ステップの静的コンテンツを取得
    step_content = None
    for sess in MASTER_CONTENT.get("sessions", []):
        for step in sess.get("steps", []):
            if step.get("step_id") == request.step_id:
                step_content = step
                break
    
    if not step_content:
        raise HTTPException(status_code=404, detail="Step not found")
    
    # 変数を取得
    if request.step_id not in session["variables"]:
        calculator = session["calculator"]
        session["variables"][request.step_id] = calculator.get_variables_for_step(request.step_id)
    
    variables = session["variables"][request.step_id]
    
    # AIジェネレーターを取得
    generator = get_ai_generator(request.provider)
    
    if not generator:
        # AI未設定時はプレースホルダーを返す
        logger.warning("AI Generator not available, returning placeholder")
        generated = {
            "step_id": request.step_id,
            "static_content": step_content.get("static_content", {}),
            "dynamic_content": {
                "analysis": f"[AI未設定] 配置分析コンテンツ\n変数: {json.dumps(variables, ensure_ascii=False, indent=2)}",
                "scenario": "[AI未設定] シナリオコンテンツ",
                "action": "[AI未設定] 提言コンテンツ",
            },
            "character_count": 0,
            "status": "placeholder",
            "message": "AI APIキーが設定されていません。環境変数 OPENAI_API_KEY または GOOGLE_API_KEY を設定してください。"
        }
    else:
        # AI生成を実行
        try:
            session["status"] = "generating"
            
            # 前章の要約を取得
            previous_summary = None
            if session["completed_steps"]:
                last_step = session["completed_steps"][-1]
                last_content = session["generated_content"].get(last_step, {})
                # 簡易的な要約（実際は別途生成）
                previous_summary = last_content.get("summary", "")
            
            # 生成実行
            result = await generator.generate_step(
                step_id=request.step_id,
                variables=variables,
                user_profile=session.get("user_profile"),
                previous_summary=previous_summary,
            )
            
            # 結果を整形
            dynamic_content = {}
            for block_id, block_data in result.get("blocks", {}).items():
                dynamic_content[block_id] = block_data.get("content", "")
            
            generated = {
                "step_id": request.step_id,
                "static_content": step_content.get("static_content", {}),
                "dynamic_content": dynamic_content,
                "character_count": result.get("total_character_count", 0),
                "status": result.get("status", "success"),
                "blocks_detail": result.get("blocks", {}),
            }
            
            # ユーザープロファイル生成（Step 2-A完了時）
            if request.step_id == "2-A" and not session.get("user_profile"):
                try:
                    combined_vars = {}
                    for s in ["1-A", "1-B", "2-A"]:
                        combined_vars.update(session["variables"].get(s, {}))
                    session["user_profile"] = await generator.generate_user_profile(combined_vars)
                    logger.info(f"User profile generated for session {request.session_id}")
                except Exception as e:
                    logger.error(f"User profile generation failed: {e}")
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            generated = {
                "step_id": request.step_id,
                "static_content": step_content.get("static_content", {}),
                "dynamic_content": {},
                "character_count": 0,
                "status": "error",
                "error": str(e)
            }
    
    # セッションを更新
    if request.step_id not in session["completed_steps"]:
        session["completed_steps"].append(request.step_id)
    session["generated_content"][request.step_id] = generated
    session["total_characters"] += generated.get("character_count", 0)
    session["status"] = "created" if generated["status"] == "error" else "generated"
    
    return generated


@app.post("/api/generate/step/stream")
async def generate_step_content_stream(request: StepGenerateRequest):
    """
    ステップコンテンツをストリーミング生成
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    generator = get_ai_generator(request.provider)
    
    if not generator:
        raise HTTPException(status_code=503, detail="AI Generator not available")
    
    # 変数を取得
    if request.step_id not in session["variables"]:
        calculator = session["calculator"]
        session["variables"][request.step_id] = calculator.get_variables_for_step(request.step_id)
    
    variables = session["variables"][request.step_id]
    
    async def generate():
        """ストリーミングジェネレーター"""
        try:
            async for chunk in generator.generate_step_stream(
                step_id=request.step_id,
                variables=variables,
                user_profile=session.get("user_profile"),
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/api/generate/status/{session_id}")
async def get_generation_status(session_id: str):
    """生成ステータスを取得"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    total_steps = sum(len(s.get("steps", [])) for s in MASTER_CONTENT.get("sessions", []))
    
    return GenerationStatus(
        session_id=session_id,
        current_step=session["completed_steps"][-1] if session["completed_steps"] else "",
        total_steps=total_steps,
        completed_steps=len(session["completed_steps"]),
        status=session["status"],
        total_characters=session["total_characters"]
    )


@app.get("/api/session/{session_id}/content")
async def get_session_content(session_id: str):
    """セッションの生成済みコンテンツを取得"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "completed_steps": session["completed_steps"],
        "generated_content": session["generated_content"],
        "total_characters": session["total_characters"],
        "user_profile": session.get("user_profile"),
    }


@app.get("/api/session/{session_id}/full-text")
async def get_full_text(session_id: str):
    """全コンテンツを結合したテキストを取得"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    full_text_parts = []
    
    for step_id in session["completed_steps"]:
        step_data = session["generated_content"].get(step_id, {})
        
        # 静的コンテンツ
        static = step_data.get("static_content", {})
        for key, content in static.items():
            if isinstance(content, dict) and "text" in content:
                full_text_parts.append(f"## {content.get('title', key)}\n\n{content['text']}")
            elif isinstance(content, str):
                full_text_parts.append(content)
        
        # 動的コンテンツ
        dynamic = step_data.get("dynamic_content", {})
        for key, content in dynamic.items():
            if content:
                full_text_parts.append(content)
    
    full_text = "\n\n---\n\n".join(full_text_parts)
    
    return {
        "session_id": session_id,
        "full_text": full_text,
        "character_count": len(full_text),
        "completed_steps": len(session["completed_steps"]),
    }


# =============================================================================
# API エンドポイント - プログレス・トランジット
# =============================================================================

@app.get("/api/session/{session_id}/progressed")
async def get_progressed_chart(session_id: str, target_date: Optional[str] = None):
    """プログレスチャートを取得"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    calculator = session["calculator"]
    
    if target_date:
        target_dt = datetime.fromisoformat(target_date)
    else:
        target_dt = datetime.now()
    
    progressed = ProgressedCalculator(calculator, target_dt)
    return progressed.calculate()


@app.get("/api/session/{session_id}/transit")
async def get_transit_chart(session_id: str, target_date: Optional[str] = None):
    """トランジットチャートを取得"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    calculator = session["calculator"]
    
    if target_date:
        target_dt = datetime.fromisoformat(target_date)
    else:
        target_dt = datetime.now()
    
    transit = TransitCalculator(calculator)
    transit_data = transit.calculate_for_date(target_dt)
    aspects = transit.find_aspects_to_natal(target_dt)
    
    return {
        "transit": transit_data,
        "aspects_to_natal": aspects
    }


@app.get("/api/session/{session_id}/forecast")
async def get_forecast(session_id: str, years: int = 3):
    """未来予測を取得"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    calculator = session["calculator"]
    transit = TransitCalculator(calculator)
    
    current_year = datetime.now().year
    forecast = {}
    
    for i in range(years):
        year = current_year + i
        forecast[f"year_{i+1}"] = transit.forecast_year(year)
    
    return forecast


# =============================================================================
# API エンドポイント - 直接計算
# =============================================================================

@app.post("/api/calculate")
async def calculate_chart(birth_data: BirthDataInput):
    """
    セッションを作成せずにホロスコープを計算
    """
    try:
        chart = create_chart(
            name=birth_data.name,
            birth_year=birth_data.birth_year,
            birth_month=birth_data.birth_month,
            birth_day=birth_data.birth_day,
            birth_hour=birth_data.birth_hour,
            birth_minute=birth_data.birth_minute,
            birth_place=birth_data.birth_place
        )
        
        if birth_data.birth_time_unknown:
            chart["warnings"] = [
                "出生時間が不明なため、正午（12:00）を仮定して計算しています。",
                "ハウスとアングルの解釈は参考程度にお考えください。"
            ]
        
        return chart
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# API エンドポイント - コンテンツ
# =============================================================================

@app.get("/api/content/master")
async def get_master_content():
    """マスターコンテンツ全体を取得"""
    return MASTER_CONTENT


@app.get("/api/content/step/{step_id}")
async def get_step_content(step_id: str):
    """ステップの静的コンテンツを取得"""
    for session in MASTER_CONTENT.get("sessions", []):
        for step in session.get("steps", []):
            if step.get("step_id") == step_id:
                return {
                    "step_id": step_id,
                    "chapter_title": step.get("chapter_title"),
                    "static_content": step.get("static_content"),
                    "dynamic_prompt": step.get("dynamic_prompt"),
                    "target_characters": step.get("target_characters"),
                }
    
    raise HTTPException(status_code=404, detail="Step not found")


@app.get("/api/content/sessions")
async def get_sessions_structure():
    """セッション構造を取得"""
    sessions_info = []
    for session in MASTER_CONTENT.get("sessions", []):
        steps_info = []
        for step in session.get("steps", []):
            steps_info.append({
                "step_id": step.get("step_id"),
                "chapter_title": step.get("chapter_title"),
                "target_characters": step.get("target_characters"),
            })
        sessions_info.append({
            "session_id": session.get("session_id"),
            "title": session.get("title"),
            "description": session.get("description"),
            "steps": steps_info
        })
    return sessions_info


@app.get("/api/content/system-settings")
async def get_system_settings():
    """システム設定を取得"""
    return MASTER_CONTENT.get("system_settings", {})


# =============================================================================
# API エンドポイント - PDF生成
# =============================================================================

@app.get("/api/session/{session_id}/pdf")
async def generate_session_pdf(session_id: str):
    """
    セッションのPDFを生成してダウンロード
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # 完了したステップがあるか確認
    if not session.get("completed_steps"):
        raise HTTPException(
            status_code=400,
            detail="No content available. Please generate content first."
        )
    
    try:
        from pdf_generator import generate_pdf_to_buffer
        
        # PDFをメモリバッファに生成
        pdf_buffer = generate_pdf_to_buffer(session, MASTER_CONTENT)
        
        # ファイル名を生成
        name = session.get('birth_data', {}).get('name', 'user')
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"anti_gravity_{name}_{timestamp}.pdf"
        
        logger.info(f"PDF generated for session {session_id}")
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except ImportError as e:
        logger.error(f"PDF generator not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="PDF generation is not available. Please install reportlab: pip install reportlab"
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/api/session/{session_id}/pdf/save")
async def save_session_pdf(session_id: str, output_dir: str = "./output"):
    """
    セッションのPDFをファイルシステムに保存
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if not session.get("completed_steps"):
        raise HTTPException(
            status_code=400,
            detail="No content available. Please generate content first."
        )
    
    try:
        from pdf_generator import generate_pdf_from_session
        
        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイル名を生成
        name = session.get('birth_data', {}).get('name', 'user')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"anti_gravity_{name}_{timestamp}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        # PDF生成
        result_path = generate_pdf_from_session(session, MASTER_CONTENT, output_path)
        
        logger.info(f"PDF saved: {result_path}")
        
        return {
            "success": True,
            "file_path": result_path,
            "file_name": filename,
            "session_id": session_id,
            "total_characters": session.get("total_characters", 0),
            "completed_steps": len(session.get("completed_steps", []))
        }
        
    except ImportError as e:
        logger.error(f"PDF generator not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="PDF generation is not available. Please install reportlab: pip install reportlab"
        )
    except Exception as e:
        logger.error(f"PDF save failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF save failed: {str(e)}")


@app.get("/api/session/{session_id}/pdf/preview")
async def preview_pdf_structure(session_id: str):
    """
    PDF生成前に構造をプレビュー
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    preview = {
        "session_id": session_id,
        "document_title": f"{session.get('birth_data', {}).get('name', 'ユーザー')}様 人生経営戦略書",
        "total_characters": session.get("total_characters", 0),
        "completed_steps": len(session.get("completed_steps", [])),
        "sections": []
    }
    
    # セッション構造を取得
    for sess in MASTER_CONTENT.get("sessions", []):
        session_info = {
            "session_id": sess.get("session_id"),
            "title": sess.get("title"),
            "steps": []
        }
        
        for step in sess.get("steps", []):
            step_id = step.get("step_id")
            if step_id in session.get("completed_steps", []):
                step_content = session.get("generated_content", {}).get(step_id, {})
                step_info = {
                    "step_id": step_id,
                    "chapter_title": step.get("chapter_title"),
                    "character_count": step_content.get("character_count", 0),
                    "has_content": bool(step_content)
                }
                session_info["steps"].append(step_info)
        
        if session_info["steps"]:
            preview["sections"].append(session_info)
    
    return preview


# =============================================================================
# API エンドポイント - ユーティリティ
# =============================================================================

@app.get("/api/prefectures")
async def get_prefectures():
    """都道府県リストを取得"""
    from astro_calculator import PREFECTURES
    return [
        {"name": name, "latitude": coords[0], "longitude": coords[1]}
        for name, coords in PREFECTURES.items()
    ]


@app.get("/api/ai/status")
async def get_ai_status():
    """AI設定状態を取得"""
    openai_key = bool(os.getenv("OPENAI_API_KEY"))
    google_key = bool(os.getenv("GOOGLE_API_KEY"))
    
    return {
        "openai_configured": openai_key,
        "gemini_configured": google_key,
        "generator_initialized": get_ai_generator() is not None,
        "prompt_generator_initialized": get_prompt_generator() is not None,
        "available_providers": [
            p for p, v in [("openai", openai_key), ("gemini", google_key)] if v
        ]
    }


@app.post("/api/ai/test")
async def test_ai_generation(
    provider: str = Query("openai", description="AI provider"),
    prompt: str = Query("こんにちは。簡単な自己紹介をしてください。", description="テストプロンプト")
):
    """AI生成をテスト"""
    generator = get_ai_generator(provider)
    
    if not generator:
        return {
            "success": False,
            "error": f"AI Generator not available for provider: {provider}",
            "hint": f"環境変数 {'OPENAI_API_KEY' if provider == 'openai' else 'GOOGLE_API_KEY'} を設定してください"
        }
    
    try:
        result = await generator.client.generate(prompt)
        return {
            "success": True,
            "provider": provider,
            "response": result[:500] + "..." if len(result) > 500 else result,
            "character_count": len(result)
        }
    except Exception as e:
        return {
            "success": False,
            "provider": provider,
            "error": str(e)
        }


# =============================================================================
# メイン実行
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
Anti-Gravity AI生成モジュール
OpenAI / Gemini API統合
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# 設定・定数
# =============================================================================

class AIProvider(Enum):
    """AIプロバイダー"""
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


@dataclass
class AIConfig:
    """AI設定"""
    provider: AIProvider = AIProvider.OPENAI
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    api_key: Optional[str] = None
    
    # 文字数管理
    min_characters: int = 2500
    max_characters: int = 4000
    target_characters: int = 3000
    max_retry: int = 3
    
    # レート制限
    requests_per_minute: int = 10
    tokens_per_minute: int = 100000


# デフォルト設定
DEFAULT_OPENAI_CONFIG = AIConfig(
    provider=AIProvider.OPENAI,
    model="gpt-4o",
    temperature=0.7,
    max_tokens=4096,
)

DEFAULT_GEMINI_CONFIG = AIConfig(
    provider=AIProvider.GEMINI,
    model="gemini-1.5-pro",
    temperature=0.7,
    max_tokens=8192,
)


# =============================================================================
# AI クライアント基底クラス
# =============================================================================

class BaseAIClient:
    """AI クライアント基底クラス"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self._last_request_time = 0
        self._request_count = 0
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> str:
        """テキスト生成（同期）"""
        raise NotImplementedError
    
    async def generate_stream(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """テキスト生成（ストリーミング）"""
        raise NotImplementedError
    
    def _rate_limit(self):
        """レート制限"""
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        
        if elapsed < 60 / self.config.requests_per_minute:
            sleep_time = (60 / self.config.requests_per_minute) - elapsed
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()


# =============================================================================
# OpenAI クライアント
# =============================================================================

class OpenAIClient(BaseAIClient):
    """OpenAI API クライアント"""
    
    def __init__(self, config: AIConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")
            self.client = None
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> str:
        """テキスト生成"""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        self._rate_limit()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_stream(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """ストリーミング生成"""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        self._rate_limit()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True,
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise


# =============================================================================
# Gemini クライアント
# =============================================================================

class GeminiClient(BaseAIClient):
    """Google Gemini API クライアント"""
    
    def __init__(self, config: AIConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            logger.warning("Google API key not found. Set GOOGLE_API_KEY environment variable.")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(config.model)
            self.genai = genai
        except ImportError:
            logger.error("google-generativeai package not installed. Run: pip install google-generativeai")
            self.model = None
            self.genai = None
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> str:
        """テキスト生成"""
        if not self.model:
            raise RuntimeError("Gemini client not initialized")
        
        self._rate_limit()
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=self.genai.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    async def generate_stream(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """ストリーミング生成"""
        if not self.model:
            raise RuntimeError("Gemini client not initialized")
        
        self._rate_limit()
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=self.genai.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                ),
                stream=True,
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise


# =============================================================================
# AI クライアントファクトリー
# =============================================================================

def create_ai_client(config: AIConfig) -> BaseAIClient:
    """AIクライアントを作成"""
    if config.provider == AIProvider.OPENAI:
        return OpenAIClient(config)
    elif config.provider == AIProvider.GEMINI:
        return GeminiClient(config)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")


# =============================================================================
# 文字数管理・リカバリーシステム
# =============================================================================

@dataclass
class GenerationResult:
    """生成結果"""
    content: str
    character_count: int
    token_count: int = 0
    retry_count: int = 0
    status: str = "success"  # success, recovered, failed
    recovery_history: List[Dict] = field(default_factory=list)


class CharacterCountManager:
    """文字数管理・リカバリーマネージャー"""
    
    def __init__(self, config: AIConfig, client: BaseAIClient):
        self.config = config
        self.client = client
    
    async def generate_with_recovery(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        min_chars: Optional[int] = None,
        max_chars: Optional[int] = None,
        on_progress: Optional[Callable[[str, int], None]] = None
    ) -> GenerationResult:
        """
        文字数リカバリー付き生成
        
        Args:
            prompt: プロンプト
            system_prompt: システムプロンプト
            min_chars: 最小文字数（デフォルトは設定値）
            max_chars: 最大文字数（デフォルトは設定値）
            on_progress: 進捗コールバック
        
        Returns:
            GenerationResult
        """
        min_chars = min_chars or self.config.min_characters
        max_chars = max_chars or self.config.max_characters
        
        result = GenerationResult(
            content="",
            character_count=0,
        )
        
        # 初回生成
        try:
            content = await self.client.generate(prompt, system_prompt)
            result.content = content
            result.character_count = len(content)
            
            if on_progress:
                on_progress("initial", result.character_count)
                
        except Exception as e:
            logger.error(f"Initial generation failed: {e}")
            result.status = "failed"
            return result
        
        # 文字数チェック＆リカバリー
        retry = 0
        while retry < self.config.max_retry:
            char_count = len(result.content)
            
            if min_chars <= char_count <= max_chars:
                # 範囲内なら成功
                result.status = "success" if retry == 0 else "recovered"
                break
            
            retry += 1
            result.retry_count = retry
            
            if char_count < min_chars:
                # 文字数不足 → 追加生成
                shortage = min_chars - char_count
                recovery_prompt = self._create_expansion_prompt(result.content, shortage)
                
                try:
                    additional = await self.client.generate(recovery_prompt, system_prompt)
                    result.content += "\n\n" + additional
                    result.recovery_history.append({
                        "type": "expansion",
                        "before": char_count,
                        "after": len(result.content),
                        "retry": retry,
                    })
                    
                    if on_progress:
                        on_progress("expansion", len(result.content))
                        
                except Exception as e:
                    logger.error(f"Expansion failed: {e}")
                    result.status = "failed"
                    break
                    
            elif char_count > max_chars:
                # 文字数過剰 → 要約
                excess = char_count - max_chars
                recovery_prompt = self._create_summary_prompt(result.content, max_chars)
                
                try:
                    summarized = await self.client.generate(recovery_prompt, system_prompt)
                    result.content = summarized
                    result.recovery_history.append({
                        "type": "summary",
                        "before": char_count,
                        "after": len(result.content),
                        "retry": retry,
                    })
                    
                    if on_progress:
                        on_progress("summary", len(result.content))
                        
                except Exception as e:
                    logger.error(f"Summary failed: {e}")
                    result.status = "failed"
                    break
        
        result.character_count = len(result.content)
        
        if result.retry_count >= self.config.max_retry and not (min_chars <= result.character_count <= max_chars):
            result.status = "failed"
        
        return result
    
    def _create_expansion_prompt(self, content: str, shortage: int) -> str:
        """追加生成用プロンプト"""
        return f"""以下のテキストに、約{shortage + 200}文字の追加コンテンツを自然に付け加えてください。

【現在のテキスト】
{content}

【追加の指示】
- 同じ内容を繰り返さず、新しい視点や具体例を追加してください
- 文脈の流れを維持し、自然に接続してください
- 追加部分のみを出力してください（元のテキストは含めない）
- ビジネスや経営の観点からの洞察を含めてください"""
    
    def _create_summary_prompt(self, content: str, target: int) -> str:
        """要約用プロンプト"""
        return f"""以下のテキストを約{target}文字に要約してください。

【元のテキスト】
{content}

【要約の指示】
- 重要なポイントを維持しながら簡潔にまとめてください
- 具体例は最も重要なものだけを残してください
- 文の流れと読みやすさを保ってください
- 約{target}文字に収めてください"""


# =============================================================================
# コンテンツ生成エンジン
# =============================================================================

class ContentGenerator:
    """コンテンツ生成エンジン"""
    
    def __init__(
        self, 
        config: AIConfig,
        prompt_generator: Optional[Any] = None
    ):
        self.config = config
        self.client = create_ai_client(config)
        self.char_manager = CharacterCountManager(config, self.client)
        self.prompt_generator = prompt_generator
        
        # システムプロンプトを読み込み
        if prompt_generator:
            self.system_prompt = prompt_generator.get_system_prompt()
        else:
            self.system_prompt = self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """デフォルトシステムプロンプト"""
        return """あなたは、MBAを持つ人生経営戦略コンサルタントです。占星術を「経営資源の分析ツール」として活用し、クライアントに対して論理的かつ洞察に満ちたアドバイスを提供します。

【文体のガイドライン】
- 論理的かつ文学的な日本語を使用
- 翻訳調を避け、自然で美しい日本語表現
- 不必要な英語やカタカナ語を避ける
- 具体的なビジネスシーンの例示を交える"""
    
    async def generate_block(
        self,
        block_id: str,
        prompt: str,
        min_chars: int = 500,
        max_chars: int = 1500,
        on_progress: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Any]:
        """
        単一ブロックを生成
        
        Args:
            block_id: ブロックID（analysis, scenario等）
            prompt: プロンプト
            min_chars: 最小文字数
            max_chars: 最大文字数
            on_progress: 進捗コールバック
        
        Returns:
            生成結果
        """
        result = await self.char_manager.generate_with_recovery(
            prompt=prompt,
            system_prompt=self.system_prompt,
            min_chars=min_chars,
            max_chars=max_chars,
            on_progress=on_progress
        )
        
        return {
            "block_id": block_id,
            "content": result.content,
            "character_count": result.character_count,
            "status": result.status,
            "retry_count": result.retry_count,
            "recovery_history": result.recovery_history,
        }
    
    async def generate_step(
        self,
        step_id: str,
        variables: Dict[str, Any],
        user_profile: Optional[str] = None,
        previous_summary: Optional[str] = None,
        on_block_complete: Optional[Callable[[str, Dict], None]] = None
    ) -> Dict[str, Any]:
        """
        1ステップ全体を生成
        
        Args:
            step_id: ステップID
            variables: 変数
            user_profile: ユーザープロファイル
            previous_summary: 前章要約
            on_block_complete: ブロック完了コールバック
        
        Returns:
            ステップ全体の生成結果
        """
        if not self.prompt_generator:
            raise RuntimeError("PromptGenerator is required for step generation")
        
        # プロンプトを取得
        prompts = self.prompt_generator.get_step_prompts(
            step_id=step_id,
            variables=variables,
            user_profile=user_profile,
            previous_summary=previous_summary
        )
        
        results = {}
        total_chars = 0
        
        for block_id, prompt_data in prompts.items():
            logger.info(f"Generating block: {step_id}/{block_id}")
            
            block_result = await self.generate_block(
                block_id=block_id,
                prompt=prompt_data["prompt"],
                min_chars=prompt_data.get("min_characters", 500),
                max_chars=prompt_data.get("min_characters", 500) * 2,
            )
            
            # プレフィックスを追加
            block_result["content"] = f"{prompt_data['prefix']}\n{block_result['content']}"
            
            results[block_id] = block_result
            total_chars += block_result["character_count"]
            
            if on_block_complete:
                on_block_complete(block_id, block_result)
        
        return {
            "step_id": step_id,
            "blocks": results,
            "total_character_count": total_chars,
            "status": "success" if all(b["status"] != "failed" for b in results.values()) else "partial",
        }
    
    async def generate_step_stream(
        self,
        step_id: str,
        variables: Dict[str, Any],
        user_profile: Optional[str] = None,
        previous_summary: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        1ステップをストリーミング生成
        
        Yields:
            各チャンクの情報
        """
        if not self.prompt_generator:
            raise RuntimeError("PromptGenerator is required for step generation")
        
        prompts = self.prompt_generator.get_step_prompts(
            step_id=step_id,
            variables=variables,
            user_profile=user_profile,
            previous_summary=previous_summary
        )
        
        for block_id, prompt_data in prompts.items():
            # ブロック開始を通知
            yield {
                "type": "block_start",
                "block_id": block_id,
                "prefix": prompt_data["prefix"],
            }
            
            # ストリーミング生成
            full_content = ""
            async for chunk in self.client.generate_stream(
                prompt=prompt_data["prompt"],
                system_prompt=self.system_prompt
            ):
                full_content += chunk
                yield {
                    "type": "chunk",
                    "block_id": block_id,
                    "content": chunk,
                }
            
            # ブロック完了を通知
            yield {
                "type": "block_end",
                "block_id": block_id,
                "character_count": len(full_content),
            }
    
    async def generate_user_profile(
        self,
        variables: Dict[str, Any]
    ) -> str:
        """
        ユーザープロファイルを生成
        
        Args:
            variables: Step 1-A, 1-B, 2-Aの統合変数
        
        Returns:
            ユーザープロファイル（500文字以内）
        """
        if not self.prompt_generator:
            prompt = self._get_default_profile_prompt(variables)
        else:
            prompt = self.prompt_generator.generate_user_profile_prompt(variables)
        
        result = await self.char_manager.generate_with_recovery(
            prompt=prompt,
            system_prompt=self.system_prompt,
            min_chars=400,
            max_chars=600,
        )
        
        return result.content
    
    def _get_default_profile_prompt(self, variables: Dict[str, Any]) -> str:
        """デフォルトプロファイル生成プロンプト"""
        return f"""以下の占星術データに基づいて、この人の「ユーザープロファイル」を500文字以内で作成してください。

【データ】
{json.dumps(variables, ensure_ascii=False, indent=2)}

【出力形式】
- 箇条書きではなく、流れるような文章で
- 500文字以内に収める
- ビジネスパーソンとしての特性を強調"""


# =============================================================================
# セッションマネージャー
# =============================================================================

@dataclass
class GenerationSession:
    """生成セッション"""
    session_id: str
    chart_data: Dict[str, Any]
    variables: Dict[str, Dict[str, Any]]
    user_profile: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    generated_content: Dict[str, Dict] = field(default_factory=dict)
    step_summaries: Dict[str, str] = field(default_factory=dict)
    total_characters: int = 0
    status: str = "created"


class SessionManager:
    """セッションマネージャー"""
    
    def __init__(self, generator: ContentGenerator):
        self.generator = generator
        self.sessions: Dict[str, GenerationSession] = {}
    
    def create_session(
        self,
        session_id: str,
        chart_data: Dict[str, Any],
        variables: Dict[str, Dict[str, Any]]
    ) -> GenerationSession:
        """セッション作成"""
        session = GenerationSession(
            session_id=session_id,
            chart_data=chart_data,
            variables=variables,
        )
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[GenerationSession]:
        """セッション取得"""
        return self.sessions.get(session_id)
    
    async def generate_step(
        self,
        session_id: str,
        step_id: str,
        on_progress: Optional[Callable[[str, Dict], None]] = None
    ) -> Dict[str, Any]:
        """セッション内でステップを生成"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # 変数を取得
        variables = session.variables.get(step_id, {})
        
        # 前章の要約を取得
        previous_summary = None
        if session.completed_steps:
            last_step = session.completed_steps[-1]
            previous_summary = session.step_summaries.get(last_step)
        
        # 生成実行
        result = await self.generator.generate_step(
            step_id=step_id,
            variables=variables,
            user_profile=session.user_profile,
            previous_summary=previous_summary,
            on_block_complete=on_progress
        )
        
        # セッションを更新
        session.completed_steps.append(step_id)
        session.generated_content[step_id] = result
        session.total_characters += result["total_character_count"]
        
        # ユーザープロファイル生成（Step 2-A完了時）
        if step_id == "2-A" and not session.user_profile:
            combined_vars = {}
            for s in ["1-A", "1-B", "2-A"]:
                combined_vars.update(session.variables.get(s, {}))
            session.user_profile = await self.generator.generate_user_profile(combined_vars)
        
        return result
    
    def get_full_content(self, session_id: str) -> str:
        """全コンテンツを結合して取得"""
        session = self.sessions.get(session_id)
        if not session:
            return ""
        
        full_content = []
        for step_id in session.completed_steps:
            step_content = session.generated_content.get(step_id, {})
            for block_id, block_data in step_content.get("blocks", {}).items():
                full_content.append(block_data.get("content", ""))
        
        return "\n\n".join(full_content)


# =============================================================================
# 便利関数
# =============================================================================

def create_generator(
    provider: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    prompt_generator: Optional[Any] = None
) -> ContentGenerator:
    """
    コンテンツジェネレーターを作成
    
    Args:
        provider: "openai" or "gemini"
        model: モデル名（省略時はデフォルト）
        api_key: APIキー（省略時は環境変数）
        prompt_generator: PromptGeneratorインスタンス
    
    Returns:
        ContentGenerator
    """
    if provider == "openai":
        config = AIConfig(
            provider=AIProvider.OPENAI,
            model=model or "gpt-4o",
            api_key=api_key,
        )
    elif provider == "gemini":
        config = AIConfig(
            provider=AIProvider.GEMINI,
            model=model or "gemini-1.5-pro",
            api_key=api_key,
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    return ContentGenerator(config, prompt_generator)


# =============================================================================
# テスト用
# =============================================================================

async def test_generation():
    """テスト実行"""
    # プロンプトジェネレーターを読み込み
    try:
        from prompt_generator import create_prompt_generator
        prompt_gen = create_prompt_generator()
    except:
        prompt_gen = None
    
    # ジェネレーターを作成
    generator = create_generator(
        provider="openai",
        prompt_generator=prompt_gen
    )
    
    # テストプロンプト
    test_prompt = """以下の4元素バランスを持つ経営者の特性を分析してください。

火: 3, 地: 2, 風: 4, 水: 1
優位: 風, 不足: 水

800文字程度で分析してください。"""
    
    print("=== テスト生成開始 ===")
    result = await generator.generate_block(
        block_id="test",
        prompt=test_prompt,
        min_chars=600,
        max_chars=1000,
    )
    
    print(f"\n=== 生成結果 ===")
    print(f"文字数: {result['character_count']}")
    print(f"ステータス: {result['status']}")
    print(f"リトライ回数: {result['retry_count']}")
    print(f"\n{result['content'][:500]}...")


if __name__ == "__main__":
    asyncio.run(test_generation())

"""
Claude API 클라이언트

Anthropic Claude API를 활용한 콘텐츠 생성
"""

import os
from typing import Optional

from anthropic import Anthropic
from pydantic import BaseModel


class GenerationConfig(BaseModel):
    """생성 설정"""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4000
    temperature: float = 0.7
    system_prompt: Optional[str] = None


class ClaudeClient:
    """Claude API 클라이언트"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Anthropic API 키 (없으면 환경변수에서 로드)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY 환경변수를 설정하거나 api_key를 전달해주세요."
            )
        self.client = Anthropic(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """
        콘텐츠 생성

        Args:
            prompt: 사용자 프롬프트
            config: 생성 설정

        Returns:
            생성된 텍스트
        """
        config = config or GenerationConfig()

        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": config.model,
            "max_tokens": config.max_tokens,
            "messages": messages,
        }

        if config.system_prompt:
            kwargs["system"] = config.system_prompt

        if config.temperature is not None:
            kwargs["temperature"] = config.temperature

        response = self.client.messages.create(**kwargs)

        # 텍스트 블록 추출
        text_blocks = [
            block.text
            for block in response.content
            if hasattr(block, "text")
        ]

        return "\n".join(text_blocks)

    def generate_with_thinking(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> tuple[str, str]:
        """
        Extended Thinking을 활용한 콘텐츠 생성

        Args:
            prompt: 사용자 프롬프트
            config: 생성 설정

        Returns:
            (생성된 텍스트, 사고 과정)
        """
        config = config or GenerationConfig()

        # Extended Thinking 지원 모델 사용
        thinking_model = "claude-sonnet-4-20250514"

        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": thinking_model,
            "max_tokens": 16000,  # Extended thinking은 더 많은 토큰 필요
            "thinking": {
                "type": "enabled",
                "budget_tokens": 10000,
            },
            "messages": messages,
        }

        if config.system_prompt:
            kwargs["system"] = config.system_prompt

        response = self.client.messages.create(**kwargs)

        # 사고 과정과 텍스트 분리
        thinking = ""
        text = ""

        for block in response.content:
            if hasattr(block, "thinking"):
                thinking = block.thinking
            elif hasattr(block, "text"):
                text += block.text + "\n"

        return text.strip(), thinking


class ClaudeClientAsync:
    """비동기 Claude API 클라이언트"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Anthropic API 키 (없으면 환경변수에서 로드)
        """
        from anthropic import AsyncAnthropic

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY 환경변수를 설정하거나 api_key를 전달해주세요."
            )
        self.client = AsyncAnthropic(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """
        비동기 콘텐츠 생성

        Args:
            prompt: 사용자 프롬프트
            config: 생성 설정

        Returns:
            생성된 텍스트
        """
        config = config or GenerationConfig()

        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": config.model,
            "max_tokens": config.max_tokens,
            "messages": messages,
        }

        if config.system_prompt:
            kwargs["system"] = config.system_prompt

        if config.temperature is not None:
            kwargs["temperature"] = config.temperature

        response = await self.client.messages.create(**kwargs)

        text_blocks = [
            block.text
            for block in response.content
            if hasattr(block, "text")
        ]

        return "\n".join(text_blocks)

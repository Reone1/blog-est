"""
Claude 클라이언트

두 가지 모드 지원:
1. CLI 모드: `claude -p` 명령어 사용 (setup 토큰 / API Key 모두 지원)
2. SDK 모드: anthropic Python SDK 사용 (API Key 필요)

우선순위: CLI → SDK → 에러
"""

import os
import shutil
import subprocess
import json
from typing import Optional

from pydantic import BaseModel


class GenerationConfig(BaseModel):
    """생성 설정"""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4000
    temperature: float = 0.7
    system_prompt: Optional[str] = None


def _find_claude_cli() -> Optional[str]:
    """claude CLI 경로 찾기"""
    return shutil.which("claude")


class ClaudeCliClient:
    """Claude CLI 기반 클라이언트 (setup 토큰 사용)"""

    def __init__(self):
        self.cli_path = _find_claude_cli()
        if not self.cli_path:
            raise FileNotFoundError("claude CLI를 찾을 수 없습니다.")

    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """
        claude CLI로 콘텐츠 생성

        Args:
            prompt: 사용자 프롬프트
            config: 생성 설정 (system_prompt만 적용)

        Returns:
            생성된 텍스트
        """
        config = config or GenerationConfig()

        # 시스템 프롬프트가 있으면 프롬프트 앞에 추가
        full_prompt = prompt
        if config.system_prompt:
            full_prompt = (
                f"<system>\n{config.system_prompt}\n</system>\n\n{prompt}"
            )

        cmd = [
            self.cli_path,
            "-p", full_prompt,
            "--output-format", "text",
            "--model", config.model,
            "--max-turns", "1",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5분 타임아웃
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"claude CLI 오류 (exit={result.returncode}): {result.stderr}"
            )

        return result.stdout.strip()


class ClaudeSdkClient:
    """Anthropic SDK 기반 클라이언트 (API Key 필요)"""

    def __init__(self, api_key: Optional[str] = None):
        from anthropic import Anthropic

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

        text_blocks = [
            block.text
            for block in response.content
            if hasattr(block, "text")
        ]
        return "\n".join(text_blocks)


class ClaudeClient:
    """
    자동 감지 Claude 클라이언트

    우선순위:
    1. ANTHROPIC_API_KEY가 있으면 → SDK 모드
    2. claude CLI가 있으면 → CLI 모드
    3. 둘 다 없으면 → 에러
    """

    def __init__(self, api_key: Optional[str] = None):
        self._client = None
        self._mode = None

        # 1. API Key가 있으면 SDK 모드 우선
        effective_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if effective_key:
            try:
                self._client = ClaudeSdkClient(api_key=effective_key)
                self._mode = "sdk"
                return
            except Exception:
                pass

        # 2. CLI 모드 시도
        if _find_claude_cli():
            try:
                self._client = ClaudeCliClient()
                self._mode = "cli"
                return
            except Exception:
                pass

        raise ValueError(
            "Claude 인증 수단을 찾을 수 없습니다.\n"
            "다음 중 하나를 설정해주세요:\n"
            "  1. claude CLI 설치 + setup (claude login)\n"
            "  2. ANTHROPIC_API_KEY 환경변수 설정"
        )

    @property
    def mode(self) -> str:
        """현재 인증 모드 ('cli' 또는 'sdk')"""
        return self._mode

    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """콘텐츠 생성 (자동 감지된 모드 사용)"""
        return self._client.generate(prompt, config)

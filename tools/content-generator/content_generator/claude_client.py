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

        stream-json --verbose 모드로 실행하여 assistant 텍스트 블록을 직접 파싱합니다.
        (--output-format text의 result 필드가 빈 문자열로 반환되는 CLI 동작 우회)

        Args:
            prompt: 사용자 프롬프트
            config: 생성 설정 (system_prompt만 적용)

        Returns:
            생성된 텍스트
        """
        config = config or GenerationConfig()

        # CLI 모드: 텍스트 직접 출력 지시를 프롬프트 앞에 추가
        output_instruction = (
            "[지시사항] 아래 요청에 대한 응답을 파일 저장 없이 텍스트로 직접 출력하세요. "
            "Write/Edit/Bash 등 어떤 도구도 사용하지 마세요. "
            "# 제목부터 시작하여 완성된 마크다운 글을 바로 출력하세요.\n\n"
        )
        cli_prompt = output_instruction + prompt

        system_parts = []
        if config.system_prompt:
            system_parts.append(config.system_prompt)
        system_parts.append(
            "Output the complete article as plain text. "
            "Do NOT write to files. Do NOT use any tools."
        )
        combined_system = "\n\n".join(system_parts)

        cmd = [
            self.cli_path,
            "-p", cli_prompt,
            "--output-format", "stream-json",
            "--verbose",
            "--model", config.model,
            "--append-system-prompt", combined_system,
            "--dangerously-skip-permissions",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5분 타임아웃
            cwd="/tmp",  # CLAUDE.md 간섭 방지
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"claude CLI 오류 (exit={result.returncode}): {result.stderr}"
            )

        # stream-json에서 assistant 텍스트 블록 추출
        output = self._extract_text_from_stream(result.stdout)

        if not output:
            raise RuntimeError(
                f"claude CLI 빈 응답: stream에서 텍스트를 찾을 수 없습니다.\nstderr: {result.stderr}"
            )

        return output

    def _extract_text_from_stream(self, stream_output: str) -> str:
        """
        stream-json 출력에서 마지막 assistant 메시지의 텍스트 블록 추출

        Args:
            stream_output: claude CLI의 stream-json 출력 문자열

        Returns:
            추출된 텍스트 (없으면 빈 문자열)
        """
        last_text = ""

        for line in stream_output.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except json.JSONDecodeError:
                continue

            # assistant 메시지 이벤트에서 텍스트 블록 수집
            if evt.get("type") == "assistant":
                msg = evt.get("message", {})
                text_parts = []
                for block in msg.get("content", []):
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                if text_parts:
                    last_text = "\n".join(text_parts)

        return last_text.strip()


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

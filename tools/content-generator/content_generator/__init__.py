"""
Content Generator - AI 기반 투자정보 블로그 콘텐츠 생성기

기능:
- Claude API를 활용한 콘텐츠 생성
- 다양한 콘텐츠 유형 지원 (데일리 브리핑, 섹터 분석, 표준편차 분석 등)
- 마크다운 형식 블로그 포스트 생성
"""

__version__ = "0.1.0"

from .generator import ContentGenerator, ContentType
from .claude_client import ClaudeClient

__all__ = [
    "ContentGenerator",
    "ContentType",
    "ClaudeClient",
]

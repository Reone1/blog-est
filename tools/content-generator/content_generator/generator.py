"""
콘텐츠 생성기

stock-researcher 데이터를 기반으로 블로그 콘텐츠 생성
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

# stock-researcher 경로 추가 (로컬 개발용, CI에서는 pip install -e로 설치됨)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "stock-researcher"))

from .claude_client import ClaudeClient, GenerationConfig


class ContentType(Enum):
    """콘텐츠 유형"""
    DAILY_BRIEFING = "daily_briefing"       # 시장 데일리 브리핑
    SECTOR_ANALYSIS = "sector_analysis"     # 섹터/테마 분석
    STOCK_REPORT = "stock_report"           # 개별 종목 리포트
    WEEKLY_REVIEW = "weekly_review"         # 주간 리뷰
    MONTHLY_REVIEW = "monthly_review"       # 월간 리뷰
    STD_ANALYSIS = "std_analysis"           # 표준편차 매매 분석


@dataclass
class BlogPost:
    """블로그 포스트"""
    title: str
    content: str
    content_type: ContentType
    date: datetime
    filename: str
    tags: list[str]
    summary: str


class ContentGenerator:
    """AI 기반 콘텐츠 생성기"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        prompts_dir: Optional[Path] = None,
    ):
        """
        Args:
            api_key: Anthropic API 키
            prompts_dir: 프롬프트 템플릿 디렉토리
        """
        self.claude = ClaudeClient(api_key=api_key)

        base_dir = Path(__file__).parent
        self.prompts_dir = prompts_dir or base_dir / "prompts"

    def _load_prompt(self, content_type: ContentType) -> str:
        """프롬프트 템플릿 로드"""
        prompt_file = self.prompts_dir / f"{content_type.value}.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {prompt_file}")

    def _collect_market_data(self, content_type: ContentType) -> dict:
        """콘텐츠 유형에 맞는 시장 데이터 수집"""
        try:
            from stock_researcher import (
                get_market_summary,
                get_top_movers,
                get_top_by_market_cap,
                get_std_signals,
                get_market_breadth,
                get_volatility_ranking,
            )
        except ImportError:
            raise RuntimeError(
                "stock-researcher 모듈이 설치되지 않았습니다. "
                "실제 시장 데이터 없이는 콘텐츠를 생성할 수 없습니다."
            )

        data = {
            "date": datetime.now().strftime("%Y년 %m월 %d일"),
            "timestamp": datetime.now().isoformat(),
        }

        try:
            if content_type == ContentType.DAILY_BRIEFING:
                data["kospi_summary"] = get_market_summary("KOSPI")
                data["kosdaq_summary"] = get_market_summary("KOSDAQ")
                data["kospi_movers"] = get_top_movers("KOSPI", limit=5)
                data["kosdaq_movers"] = get_top_movers("KOSDAQ", limit=5)
                data["market_breadth"] = get_market_breadth("KOSPI")

            elif content_type == ContentType.STD_ANALYSIS:
                data["kospi_signals"] = get_std_signals("KOSPI", limit=10)
                data["kosdaq_signals"] = get_std_signals("KOSDAQ", limit=10)
                data["volatility_ranking"] = get_volatility_ranking(
                    "KOSPI", sort_by="zscore", ascending=True, limit=10
                )
                data["market_breadth"] = get_market_breadth("KOSPI")

            elif content_type == ContentType.SECTOR_ANALYSIS:
                data["kospi_top"] = get_top_by_market_cap("KOSPI", limit=20)
                data["kospi_movers"] = get_top_movers("KOSPI", limit=10)

            elif content_type in (ContentType.WEEKLY_REVIEW, ContentType.MONTHLY_REVIEW):
                data["kospi_summary"] = get_market_summary("KOSPI")
                data["kosdaq_summary"] = get_market_summary("KOSDAQ")
                data["kospi_movers"] = get_top_movers("KOSPI", limit=10)
                data["market_breadth"] = get_market_breadth("KOSPI")

        except Exception as e:
            raise RuntimeError(
                f"시장 데이터 수집 실패: {e}. "
                "실제 데이터 없이는 콘텐츠를 생성할 수 없습니다."
            )

        return data

    def _format_market_data(self, data: dict) -> str:
        """시장 데이터를 프롬프트용 텍스트로 변환"""
        lines = []

        if "kospi_summary" in data:
            summary = data["kospi_summary"]
            if hasattr(summary, "index_value"):
                lines.append(f"## KOSPI")
                lines.append(f"- 지수: {summary.index_value:,.2f}")
                lines.append(f"- 등락률: {summary.index_change_percent:+.2f}%")
                lines.append(f"- 상승: {summary.advancing}개, 하락: {summary.declining}개")
            elif isinstance(summary, dict):
                lines.append(f"## KOSPI")
                lines.append(f"- 지수: {summary.get('index_value', 'N/A')}")
                lines.append(f"- 등락률: {summary.get('index_change_percent', 'N/A')}%")

        if "kosdaq_summary" in data:
            summary = data["kosdaq_summary"]
            if hasattr(summary, "index_value"):
                lines.append(f"\n## KOSDAQ")
                lines.append(f"- 지수: {summary.index_value:,.2f}")
                lines.append(f"- 등락률: {summary.index_change_percent:+.2f}%")
            elif isinstance(summary, dict):
                lines.append(f"\n## KOSDAQ")
                lines.append(f"- 지수: {summary.get('index_value', 'N/A')}")

        if "kospi_movers" in data:
            movers = data["kospi_movers"]
            if hasattr(movers, "gainers") and movers.gainers:
                lines.append(f"\n## 급등주 (KOSPI)")
                for stock in movers.gainers[:5]:
                    lines.append(f"- {stock.name}({stock.symbol}): {stock.change_percent:+.2f}%")

            if hasattr(movers, "losers") and movers.losers:
                lines.append(f"\n## 급락주 (KOSPI)")
                for stock in movers.losers[:5]:
                    lines.append(f"- {stock.name}({stock.symbol}): {stock.change_percent:+.2f}%")

        if "kospi_signals" in data:
            signals = data["kospi_signals"]
            if signals:
                lines.append(f"\n## 표준편차 매매 시그널")
                for signal in signals[:10]:
                    stock = signal.stock
                    lines.append(
                        f"- {stock.name}({stock.symbol}): "
                        f"Z-score {stock.zscore:.2f}, "
                        f"{signal.signal_type} ({signal.description})"
                    )

        if "market_breadth" in data:
            breadth = data["market_breadth"]
            if hasattr(breadth, "advance_decline_ratio"):
                lines.append(f"\n## 시장 심리")
                lines.append(f"- 상승/하락 비율: {breadth.advance_decline_ratio:.2f}")
                lines.append(f"- 과매도 종목: {breadth.oversold_count}개")
                lines.append(f"- 과매수 종목: {breadth.overbought_count}개")

        if "error" in data:
            lines.append(f"\n⚠️ 데이터 수집 중 오류: {data['error']}")

        if "note" in data:
            lines.append(f"\n📝 {data['note']}")

        return "\n".join(lines)

    def generate(
        self,
        content_type: ContentType,
        additional_context: Optional[str] = None,
    ) -> BlogPost:
        """
        콘텐츠 생성

        Args:
            content_type: 콘텐츠 유형
            additional_context: 추가 컨텍스트 (선택)

        Returns:
            BlogPost 객체
        """
        # 1. 시장 데이터 수집
        market_data = self._collect_market_data(content_type)

        # 2. 프롬프트 구성
        prompt_template = self._load_prompt(content_type)
        formatted_data = self._format_market_data(market_data)

        prompt = prompt_template.replace("{market_data}", formatted_data)
        prompt = prompt.replace("{date}", market_data.get("date", ""))

        if additional_context:
            prompt += f"\n\n## 추가 컨텍스트\n{additional_context}"

        # 3. Claude API 호출 (10분 분량 = ~5000자 = ~8000 토큰)
        config = GenerationConfig(
            max_tokens=8000,
            temperature=0.7,
            system_prompt=self._get_system_prompt(),
        )

        content = self.claude.generate(prompt, config)

        # 4. 포스트 구성
        now = datetime.now()
        title = self._extract_title(content, content_type, now)
        filename = self._generate_filename(content_type, now)
        tags = self._generate_tags(content_type)
        summary = self._extract_summary(content)

        return BlogPost(
            title=title,
            content=content,
            content_type=content_type,
            date=now,
            filename=filename,
            tags=tags,
            summary=summary,
        )

    def _get_system_prompt(self) -> str:
        """시스템 프롬프트"""
        return """당신은 한국 주식시장 전문 애널리스트입니다.
객관적이고 정확한 시장 분석을 제공하며, 투자자들이 이해하기 쉬운 언어로 설명합니다.

중요한 원칙:
1. 항상 객관적 사실에 기반하여 작성합니다.
2. 특정 종목의 매수/매도를 직접 권유하지 않습니다.
3. 글 말미에 투자 면책조항을 포함합니다.
4. 마크다운 형식으로 깔끔하게 작성합니다.
5. 한국어로 작성합니다.
6. 이모지를 절대 사용하지 않습니다. 텍스트만으로 작성합니다.
7. 충분한 분량(4,000-6,000자)으로 심층 분석합니다.
8. 각 섹션에 구체적인 데이터와 분석적 서술을 포함합니다.
9. 제목은 독자의 이목을 끌 수 있도록 구체적 종목명/수치를 포함하고, 질문형이나 대시(—) 활용, 대비 구조 등을 사용합니다."""

    def _extract_title(
        self,
        content: str,
        content_type: ContentType,
        date: datetime,
    ) -> str:
        """콘텐츠에서 제목 추출 또는 생성"""
        # 첫 번째 # 헤더 찾기
        for line in content.split("\n"):
            if line.startswith("# "):
                return line[2:].strip()

        # 기본 제목 생성 (이모지 없음)
        date_str = date.strftime("%Y년 %m월 %d일")
        titles = {
            ContentType.DAILY_BRIEFING: f"{date_str} 시장 브리핑",
            ContentType.STD_ANALYSIS: f"{date_str} 표준편차 매매 분석",
            ContentType.SECTOR_ANALYSIS: f"섹터 분석 — {date_str}",
            ContentType.WEEKLY_REVIEW: f"주간 시장 리뷰 ({date_str})",
            ContentType.MONTHLY_REVIEW: f"월간 시장 리뷰 ({date.strftime('%Y년 %m월')})",
            ContentType.STOCK_REPORT: f"종목 리포트 — {date_str}",
        }
        return titles.get(content_type, f"시장 분석 - {date_str}")

    def _generate_filename(self, content_type: ContentType, date: datetime) -> str:
        """파일명 생성"""
        date_str = date.strftime("%Y-%m-%d")
        type_slug = content_type.value.replace("_", "-")
        return f"{date_str}-{type_slug}.md"

    def _generate_tags(self, content_type: ContentType) -> list[str]:
        """태그 생성"""
        base_tags = ["한국주식", "시장분석"]

        type_tags = {
            ContentType.DAILY_BRIEFING: ["데일리", "시황"],
            ContentType.STD_ANALYSIS: ["표준편차", "기술적분석", "변동성"],
            ContentType.SECTOR_ANALYSIS: ["섹터", "테마"],
            ContentType.WEEKLY_REVIEW: ["주간리뷰"],
            ContentType.MONTHLY_REVIEW: ["월간리뷰"],
            ContentType.STOCK_REPORT: ["종목분석"],
        }

        return base_tags + type_tags.get(content_type, [])

    def _extract_summary(self, content: str, max_length: int = 200) -> str:
        """콘텐츠 요약 추출"""
        # 첫 번째 단락 추출 (헤더 제외)
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                if len(line) > max_length:
                    return line[:max_length] + "..."
                return line
        return ""

    def save_post(self, post: BlogPost, output_dir: Path) -> Path:
        """
        포스트를 파일로 저장

        Args:
            post: BlogPost 객체
            output_dir: 저장 디렉토리

        Returns:
            저장된 파일 경로
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / post.filename

        # 파일명에서 slug 추출 (.md 제거)
        slug = post.filename.replace(".md", "")
        post_url = f"https://totalr.vercel.app/posts/{slug}"
        date_str = post.date.strftime("%Y-%m-%d")

        # 프론트매터 + JSON-LD Schema 추가
        frontmatter = f"""---
title: "{post.title}"
date: {post.date.isoformat()}
tags: {post.tags}
summary: "{post.summary}"
type: {post.content_type.value}
---

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{post.title}",
  "description": "{post.summary}",
  "datePublished": "{date_str}",
  "dateModified": "{date_str}",
  "author": {{
    "@type": "Organization",
    "name": "한국 주식시장 분석 블로그"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "한국 주식시장 분석 블로그",
    "logo": {{
      "@type": "ImageObject",
      "url": "https://totalr.vercel.app/assets/logo.svg"
    }}
  }},
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "{post_url}"
  }},
  "image": "https://totalr.vercel.app/assets/og-image.svg"
}}
</script>

"""
        full_content = frontmatter + post.content

        output_path.write_text(full_content, encoding="utf-8")
        return output_path

#!/usr/bin/env python3
"""
Home 페이지 자동 업데이트 스크립트

home.md의 마커 구간을 최신 포스트로 자동 갱신한다.
- LATEST_BRIEFING: 최신 daily_briefing 1건
- RECENT_POSTS: 최신 4건 (브리핑 제외 타입 혼합)
- PINNED: 수동 관리 (건드리지 않음)
"""

import re
from datetime import datetime
from pathlib import Path


# 카테고리 표시명
TYPE_LABELS = {
    "daily_briefing": "데일리 브리핑",
    "std_analysis": "표준편차 분석",
    "sector_analysis": "섹터 분석",
    "weekly_review": "주간 리뷰",
    "monthly_review": "월간 리뷰",
    "stock_report": "종목 리포트",
    "investment_strategy": "투자 전략",
}


def extract_frontmatter(content: str) -> dict:
    """마크다운 파일에서 frontmatter 추출"""
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_content = parts[1].strip()
            for line in fm_content.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip().strip("\"'")
    return frontmatter


def get_posts(posts_dir: Path) -> list[dict]:
    """포스트 목록을 날짜 역순으로 반환"""
    posts = []
    for md_file in posts_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        fm = extract_frontmatter(content)

        title = fm.get("title", "")
        if not title:
            for line in content.split("\n"):
                if line.strip().startswith("# "):
                    title = line.strip()[2:]
                    break

        date_str = fm.get("date", "")
        if not date_str:
            match = re.match(r"(\d{4}-\d{2}-\d{2})", md_file.name)
            if match:
                date_str = match.group(1)

        try:
            date = datetime.fromisoformat(date_str.split("T")[0]) if date_str else datetime.min
        except ValueError:
            date = datetime.min

        summary = fm.get("summary", "")
        # summary가 길면 150자로 자름
        if len(summary) > 150:
            summary = summary[:147] + "..."

        posts.append({
            "filename": md_file.stem,
            "title": title,
            "date": date,
            "type": fm.get("type", ""),
            "summary": summary,
        })

    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts


def build_card(post: dict, include_summary: bool = False) -> str:
    """단일 포스트 카드 HTML 생성"""
    date_display = post["date"].strftime("%Y.%m.%d") if post["date"] != datetime.min else ""
    type_label = TYPE_LABELS.get(post["type"], post["type"])

    lines = []
    lines.append(f'  <a class="doc-card" href="#/posts/{post["filename"]}">')
    lines.append(f'    <h3>{post["title"]}</h3>')
    if include_summary and post["summary"]:
        lines.append(f'    <p class="meta">{post["summary"]}</p>')
    lines.append(f'    <div class="card-footer">')
    lines.append(f'      <span>{date_display}</span>')
    lines.append(f'      <span class="meta-separator">·</span>')
    if include_summary:
        lines.append(f'      <span>{type_label}</span>')
    else:
        lines.append(f'      <span class="card-tag">{type_label}</span>')
    lines.append(f'    </div>')
    lines.append(f'  </a>')
    return "\n".join(lines)


def generate_briefing_section(posts: list[dict]) -> str:
    """오늘의 브리핑 섹션 (최신 daily_briefing 1건)"""
    briefing = next((p for p in posts if p["type"] == "daily_briefing"), None)
    if not briefing:
        return "<!-- LATEST_BRIEFING_START -->\n<!-- LATEST_BRIEFING_END -->"

    lines = [
        "<!-- LATEST_BRIEFING_START -->",
        "## 오늘의 브리핑",
        "",
        '<div class="doc-cards">',
        build_card(briefing, include_summary=True),
        "</div>",
        "<!-- LATEST_BRIEFING_END -->",
    ]
    return "\n".join(lines)


def generate_recent_section(posts: list[dict]) -> str:
    """최근 분석 섹션 (최신 4건, 브리핑 첫 건 제외)"""
    # 최신 브리핑은 위에서 이미 표시하므로 건너뜀
    first_briefing_skipped = False
    recent = []
    for p in posts:
        if p["type"] == "daily_briefing" and not first_briefing_skipped:
            first_briefing_skipped = True
            continue
        recent.append(p)
        if len(recent) >= 4:
            break

    if not recent:
        return "<!-- RECENT_POSTS_START -->\n<!-- RECENT_POSTS_END -->"

    lines = [
        "<!-- RECENT_POSTS_START -->",
        "## 최근 분석",
        "",
        '<div class="doc-cards">',
    ]
    for post in recent:
        lines.append(build_card(post, include_summary=False))
    lines.append("</div>")
    lines.append("<!-- RECENT_POSTS_END -->")
    return "\n".join(lines)


def update_home(home_path: Path, posts: list[dict]):
    """home.md의 마커 구간을 최신 데이터로 교체"""
    content = home_path.read_text(encoding="utf-8")

    # LATEST_BRIEFING 구간 교체
    briefing_section = generate_briefing_section(posts)
    content = re.sub(
        r"<!-- LATEST_BRIEFING_START -->.*?<!-- LATEST_BRIEFING_END -->",
        briefing_section,
        content,
        flags=re.DOTALL,
    )

    # RECENT_POSTS 구간 교체
    recent_section = generate_recent_section(posts)
    content = re.sub(
        r"<!-- RECENT_POSTS_START -->.*?<!-- RECENT_POSTS_END -->",
        recent_section,
        content,
        flags=re.DOTALL,
    )

    # PINNED 구간은 건드리지 않음

    home_path.write_text(content, encoding="utf-8")


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    posts_dir = project_root / "posts"
    home_path = project_root / "home.md"

    if not posts_dir.exists():
        print(f"posts 디렉토리가 없습니다: {posts_dir}")
        return

    if not home_path.exists():
        print(f"home.md가 없습니다: {home_path}")
        return

    posts = get_posts(posts_dir)
    print(f"{len(posts)}개의 포스트를 찾았습니다.")

    update_home(home_path, posts)
    print(f"Home 업데이트 완료: {home_path}")


if __name__ == "__main__":
    main()

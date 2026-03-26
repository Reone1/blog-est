#!/usr/bin/env python3
"""
Sidebar 자동 업데이트 스크립트

posts/ 폴더의 포스트들을 카테고리별로 _sidebar.md에 반영
"""

import re
from datetime import datetime
from pathlib import Path

# 카테고리 매핑: type → (카테고리명, 정렬순서)
CATEGORIES = {
    "daily_briefing": ("일간 분석", 1),
    "std_analysis": ("일간 분석", 1),
    "weekly_review": ("주간 분석", 2),
    "monthly_review": ("월간 분석", 3),
    "sector_analysis": ("섹터 분석", 4),
    "stock_report": ("종목 리포트", 5),
}

DEFAULT_CATEGORY = ("투자 전략", 6)


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
                    frontmatter[key.strip()] = value.strip().strip('"\'')

    return frontmatter


def get_title_from_content(content: str) -> str:
    """콘텐츠에서 제목 추출 (# 헤더 또는 첫 줄)"""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line and not line.startswith("---"):
            return line[:50]
    return "제목 없음"


def get_posts(posts_dir: Path) -> list[dict]:
    """포스트 목록 조회"""
    posts = []

    for md_file in posts_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        frontmatter = extract_frontmatter(content)

        title = frontmatter.get("title") or get_title_from_content(content)

        date_str = frontmatter.get("date", "")
        if not date_str:
            match = re.match(r"(\d{4}-\d{2}-\d{2})", md_file.name)
            if match:
                date_str = match.group(1)

        try:
            date = datetime.fromisoformat(date_str.split("T")[0]) if date_str else datetime.min
        except ValueError:
            date = datetime.min

        content_type = frontmatter.get("type", "")
        category_name, category_order = CATEGORIES.get(content_type, DEFAULT_CATEGORY)

        # category frontmatter가 있으면 우선 사용
        if frontmatter.get("category"):
            category_name = frontmatter["category"]

        posts.append({
            "filename": md_file.name,
            "title": title,
            "date": date,
            "type": content_type,
            "category": category_name,
            "category_order": category_order,
        })

    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts


def generate_sidebar(posts: list[dict]) -> str:
    """카테고리별로 그룹화한 _sidebar.md 생성"""

    sidebar = "* [홈](home.md)\n* [소개](about.md)\n"

    # 카테고리별 그룹화
    categories: dict[str, list[dict]] = {}
    for post in posts:
        cat = post["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(post)

    # 카테고리 정렬 (category_order 기준)
    sorted_cats = sorted(
        categories.items(),
        key=lambda x: min(p["category_order"] for p in x[1]),
    )

    for cat_name, cat_posts in sorted_cats:
        sidebar += f"\n## {cat_name}\n\n"

        # 각 카테고리 내에서 최신순, 최대 10개
        for post in cat_posts[:10]:
            date_str = post["date"].strftime("%m/%d") if post["date"] != datetime.min else ""
            sidebar += f"* [{post['title']}](posts/{post['filename']})"
            if date_str:
                sidebar += f" <small>{date_str}</small>"
            sidebar += "\n"

    return sidebar


def main():
    """메인 실행"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    posts_dir = project_root / "posts"
    sidebar_path = project_root / "_sidebar.md"

    if not posts_dir.exists():
        print(f"posts 디렉토리가 없습니다: {posts_dir}")
        return

    posts = get_posts(posts_dir)
    print(f"{len(posts)}개의 포스트를 찾았습니다.")

    sidebar_content = generate_sidebar(posts)

    sidebar_path.write_text(sidebar_content, encoding="utf-8")
    print(f"Sidebar 업데이트 완료: {sidebar_path}")


if __name__ == "__main__":
    main()

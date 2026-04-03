#!/usr/bin/env python3
"""
Health blog sidebar 자동 업데이트 스크립트

sites/health/docs/posts/ 포스트들을 카테고리별로 _sidebar.md에 반영
"""

import re
from datetime import datetime
from pathlib import Path

CATEGORIES = {
    "how-to": ("How-To Guides", 1),
    "routine": ("Routines", 2),
    "explainer": ("Explainers", 3),
    "listicle": ("Lists", 4),
    "myth-busting": ("Myth Busting", 5),
    "comparison": ("Comparisons", 6),
}

DEFAULT_CATEGORY = ("Other", 7)


def extract_frontmatter(content: str) -> dict:
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip().strip('"\'')
    return frontmatter


def get_posts(posts_dir: Path) -> list[dict]:
    posts = []
    for md_file in posts_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        fm = extract_frontmatter(content)
        title = fm.get("title", md_file.stem.replace("-", " ").title())
        date_str = fm.get("date", "")
        try:
            date = datetime.fromisoformat(date_str.split("T")[0]) if date_str else datetime.min
        except ValueError:
            date = datetime.min
        content_type = fm.get("type", "")
        cat_name, cat_order = CATEGORIES.get(content_type, DEFAULT_CATEGORY)
        posts.append({
            "filename": md_file.name,
            "title": title,
            "date": date,
            "category": cat_name,
            "category_order": cat_order,
        })
    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts


def generate_sidebar(posts: list[dict]) -> str:
    sidebar = "* [Home](home.md)\n"
    categories: dict[str, list[dict]] = {}
    for post in posts:
        cat = post["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(post)

    sorted_cats = sorted(
        categories.items(),
        key=lambda x: min(p["category_order"] for p in x[1]),
    )

    for cat_name, cat_posts in sorted_cats:
        sidebar += f"\n* **{cat_name}**\n"
        for post in cat_posts:
            date_str = post["date"].strftime("%m/%d") if post["date"] != datetime.min else ""
            sidebar += f"  * [{post['title']}](posts/{post['filename']})"
            if date_str:
                sidebar += f" <small>{date_str}</small>"
            sidebar += "\n"

    return sidebar


def main():
    script_dir = Path(__file__).parent
    health_docs = script_dir.parent / "sites" / "health" / "docs"
    posts_dir = health_docs / "posts"
    sidebar_path = health_docs / "_sidebar.md"

    if not posts_dir.exists():
        print(f"posts 디렉토리가 없습니다: {posts_dir}")
        return

    posts = get_posts(posts_dir)
    print(f"{len(posts)}개의 포스트를 찾았습니다.")
    sidebar_path.write_text(generate_sidebar(posts), encoding="utf-8")
    print(f"Health sidebar 업데이트 완료: {sidebar_path}")


if __name__ == "__main__":
    main()

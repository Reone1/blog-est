#!/usr/bin/env python3
"""
Sidebar 자동 업데이트 스크립트

posts/ 폴더의 최신 포스트들을 _sidebar.md에 반영
"""

import os
import re
from datetime import datetime
from pathlib import Path


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


def get_posts(posts_dir: Path, limit: int = 15) -> list[dict]:
    """최신 포스트 목록 조회"""
    posts = []
    
    for md_file in posts_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        frontmatter = extract_frontmatter(content)
        
        # 제목 결정
        title = frontmatter.get("title") or get_title_from_content(content)
        
        # 날짜 결정 (파일명에서 추출 또는 frontmatter)
        date_str = frontmatter.get("date", "")
        if not date_str:
            # 파일명에서 날짜 추출 (YYYY-MM-DD-*.md)
            match = re.match(r"(\d{4}-\d{2}-\d{2})", md_file.name)
            if match:
                date_str = match.group(1)
        
        try:
            date = datetime.fromisoformat(date_str.split("T")[0]) if date_str else datetime.min
        except ValueError:
            date = datetime.min
        
        # 콘텐츠 유형
        content_type = frontmatter.get("type", "")
        
        posts.append({
            "filename": md_file.name,
            "title": title,
            "date": date,
            "type": content_type,
        })
    
    # 날짜순 정렬 (최신순)
    posts.sort(key=lambda x: x["date"], reverse=True)
    
    return posts[:limit]


def generate_sidebar(posts: list[dict], base_path: Path) -> str:
    """_sidebar.md 콘텐츠 생성"""

    # 유형별 이모지
    type_emoji = {
        "daily_briefing": "📈",
        "std_analysis": "📊",
        "sector_analysis": "🔍",
        "weekly_review": "📅",
        "monthly_review": "📆",
        "stock_report": "📋",
    }

    # 유형별 한글 이름
    type_name = {
        "daily_briefing": "데일리 브리핑",
        "std_analysis": "표준편차 분석",
        "sector_analysis": "섹터 분석",
        "weekly_review": "주간 리뷰",
        "monthly_review": "월간 리뷰",
        "stock_report": "종목 리포트",
    }

    sidebar = """# 한국 주식시장 분석

* [🏠 홈](home.md)
* [ℹ️ 소개](about.md)

## 📰 최근 글

"""

    for post in posts:
        emoji = type_emoji.get(post["type"], "📝")
        date_str = post["date"].strftime("%m/%d") if post["date"] != datetime.min else ""
        title = post["title"]

        # 제목이 너무 길면 자르기
        if len(title) > 40:
            title = title[:37] + "..."

        sidebar += f"* [{emoji} {title}](posts/{post['filename']})"
        if date_str:
            sidebar += f" <small>({date_str})</small>"
        sidebar += "\n"

    # 유형별 카테고리 (실제 포스트가 있는 유형만 표시)
    existing_types = {p["type"] for p in posts if p["type"]}
    if existing_types:
        sidebar += "\n## 📚 카테고리\n\n"
        for type_key, name in type_name.items():
            type_posts = [p for p in posts if p["type"] == type_key]
            if type_posts:
                emoji = type_emoji.get(type_key, "📝")
                count = len(type_posts)
                # 해당 유형의 최신 포스트로 링크
                latest = type_posts[0]
                sidebar += f"* {emoji} **{name}** ({count}건)"
                sidebar += f" — [{latest['title'][:25]}...](posts/{latest['filename']})\n" if len(latest['title']) > 25 else f" — [{latest['title']}](posts/{latest['filename']})\n"

    sidebar += """
## 🔗 링크

* [GitHub](https://github.com/Reone1/blog-est)
"""

    return sidebar


def main():
    """메인 실행"""
    # 프로젝트 루트 찾기
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    posts_dir = project_root / "posts"
    sidebar_path = project_root / "_sidebar.md"
    
    if not posts_dir.exists():
        print(f"⚠️ posts 디렉토리가 없습니다: {posts_dir}")
        return
    
    # 포스트 조회
    posts = get_posts(posts_dir)
    print(f"📚 {len(posts)}개의 포스트를 찾았습니다.")
    
    # Sidebar 생성
    sidebar_content = generate_sidebar(posts, project_root)
    
    # 파일 저장
    sidebar_path.write_text(sidebar_content, encoding="utf-8")
    print(f"✅ Sidebar 업데이트 완료: {sidebar_path}")


if __name__ == "__main__":
    main()

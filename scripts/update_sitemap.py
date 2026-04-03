#!/usr/bin/env python3
"""
Sitemap 자동 업데이트 스크립트

posts/ 폴더의 포스트들을 sitemap.xml에 반영
"""

import re
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent


# 블로그 기본 URL
BASE_URL = "https://totalr.vercel.app"


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


def get_post_date(md_file: Path, frontmatter: dict) -> str:
    """포스트의 날짜를 YYYY-MM-DD 형식으로 반환"""
    date_str = frontmatter.get("date", "")

    # frontmatter에서 날짜 추출
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.split("T")[0])
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # 파일명에서 날짜 추출 (YYYY-MM-DD-*.md)
    match = re.match(r"(\d{4}-\d{2}-\d{2})", md_file.name)
    if match:
        return match.group(1)

    return datetime.now().strftime("%Y-%m-%d")


def get_content_type_freq(content_type: str) -> str:
    """콘텐츠 유형별 변경 빈도"""
    freq_map = {
        "daily_briefing": "daily",
        "std_analysis": "daily",
        "sector_analysis": "weekly",
        "weekly_review": "weekly",
        "monthly_review": "monthly",
        "stock_report": "monthly",
    }
    return freq_map.get(content_type, "weekly")


def generate_sitemap(project_root: Path) -> str:
    """sitemap.xml 생성"""
    posts_dir = project_root / "posts"
    today = datetime.now().strftime("%Y-%m-%d")

    # XML namespace
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    urlset = Element("urlset", xmlns=ns)

    # 고정 페이지
    static_pages = [
        {"loc": f"{BASE_URL}/", "priority": "1.0", "changefreq": "daily", "lastmod": today},
        {"loc": f"{BASE_URL}/home", "priority": "0.9", "changefreq": "daily", "lastmod": today},
        {"loc": f"{BASE_URL}/about", "priority": "0.7", "changefreq": "monthly"},
    ]

    for page in static_pages:
        url = SubElement(urlset, "url")
        SubElement(url, "loc").text = page["loc"]
        SubElement(url, "lastmod").text = page.get("lastmod", today)
        SubElement(url, "changefreq").text = page["changefreq"]
        SubElement(url, "priority").text = page["priority"]

    # 포스트 페이지
    if posts_dir.exists():
        post_files = sorted(posts_dir.glob("*.md"), reverse=True)

        for md_file in post_files:
            content = md_file.read_text(encoding="utf-8")
            frontmatter = extract_frontmatter(content)
            post_date = get_post_date(md_file, frontmatter)
            content_type = frontmatter.get("type", "")
            changefreq = get_content_type_freq(content_type)

            # 파일명에서 .md 제거
            slug = md_file.stem

            url = SubElement(urlset, "url")
            SubElement(url, "loc").text = f"{BASE_URL}/posts/{slug}"
            SubElement(url, "lastmod").text = post_date
            SubElement(url, "changefreq").text = changefreq
            SubElement(url, "priority").text = "0.8"

    # XML 문자열 생성
    indent(urlset, space="  ")
    tree = ElementTree(urlset)

    import io
    output = io.BytesIO()
    tree.write(output, encoding="UTF-8", xml_declaration=True)

    return output.getvalue().decode("utf-8")


def main():
    """메인 실행"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    sitemap_path = project_root / "sitemap.xml"

    # Sitemap 생성
    sitemap_content = generate_sitemap(project_root)

    # 파일 저장
    sitemap_path.write_text(sitemap_content, encoding="utf-8")

    # 포스트 수 출력
    posts_dir = project_root / "posts"
    post_count = len(list(posts_dir.glob("*.md"))) if posts_dir.exists() else 0
    print(f"✅ Sitemap 업데이트 완료: {sitemap_path} ({post_count}개 포스트 포함)")


if __name__ == "__main__":
    main()

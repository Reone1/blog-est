#!/usr/bin/env python3
"""
Health blog sitemap 자동 업데이트 스크립트

sites/health/docs/posts/ 포스트들을 sitemap.xml에 반영
"""

import io
import re
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent

BASE_URL = "https://healthem.vercel.app"


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


def get_post_date(md_file: Path, frontmatter: dict) -> str:
    date_str = frontmatter.get("date", "")
    if date_str:
        try:
            return datetime.fromisoformat(date_str.split("T")[0]).strftime("%Y-%m-%d")
        except ValueError:
            pass
    match = re.match(r"(\d{4}-\d{2}-\d{2})", md_file.name)
    if match:
        return match.group(1)
    return datetime.now().strftime("%Y-%m-%d")


def generate_sitemap(docs_dir: Path) -> str:
    posts_dir = docs_dir / "posts"
    today = datetime.now().strftime("%Y-%m-%d")
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    urlset = Element("urlset", xmlns=ns)

    # Homepage
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = f"{BASE_URL}/"
    SubElement(url, "lastmod").text = today
    SubElement(url, "changefreq").text = "daily"
    SubElement(url, "priority").text = "1.0"

    # Posts
    if posts_dir.exists():
        for md_file in sorted(posts_dir.glob("*.md"), reverse=True):
            content = md_file.read_text(encoding="utf-8")
            fm = extract_frontmatter(content)
            post_date = get_post_date(md_file, fm)
            slug = md_file.stem

            entry = SubElement(urlset, "url")
            SubElement(entry, "loc").text = f"{BASE_URL}/#/posts/{slug}"
            SubElement(entry, "lastmod").text = post_date
            SubElement(entry, "changefreq").text = "monthly"
            SubElement(entry, "priority").text = "0.8"

    indent(urlset, space="  ")
    tree = ElementTree(urlset)
    output = io.BytesIO()
    tree.write(output, encoding="UTF-8", xml_declaration=True)
    return output.getvalue().decode("utf-8")


def main():
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent / "sites" / "health" / "docs"
    sitemap_path = docs_dir / "sitemap.xml"

    content = generate_sitemap(docs_dir)
    sitemap_path.write_text(content, encoding="utf-8")

    posts_dir = docs_dir / "posts"
    count = len(list(posts_dir.glob("*.md"))) if posts_dir.exists() else 0
    print(f"Health sitemap 업데이트 완료: {sitemap_path} ({count}개 포스트)")


if __name__ == "__main__":
    main()

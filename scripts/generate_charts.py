#!/usr/bin/env python3
"""
포스트 본문 데이터를 파싱하여 차트 이미지를 자동 생성하는 스크립트.

사용법:
  python scripts/generate_charts.py                    # 모든 포스트
  python scripts/generate_charts.py posts/2026-03-31-daily-briefing.md  # 특정 포스트
"""

import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ── 한글 폰트 설정 ──
def setup_korean_font():
    """시스템에서 사용 가능한 한글 폰트 탐색"""
    korean_fonts = [
        "NanumGothic", "NanumBarunGothic", "Malgun Gothic",
        "AppleGothic", "Noto Sans CJK KR", "Noto Sans KR",
        "UnDotum", "DejaVu Sans",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for font in korean_fonts:
        if font in available:
            return font
    return "DejaVu Sans"  # fallback

FONT_NAME = setup_korean_font()
plt.rcParams.update({
    "font.family": FONT_NAME,
    "axes.unicode_minus": False,
    "figure.facecolor": "#ffffff",
    "axes.facecolor": "#fafafa",
    "axes.edgecolor": "#e0e0e0",
    "axes.grid": True,
    "grid.color": "#e8e8e8",
    "grid.linewidth": 0.5,
})

# 스토쿼트 브랜드 컬러
COLORS = {
    "accent": "#b4a078",
    "red": "#e74c3c",
    "green": "#27ae60",
    "blue": "#3498db",
    "gray": "#95a5a6",
    "dark": "#2c3e50",
}


def extract_frontmatter(content: str) -> dict:
    fm = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip("\"'")
    return fm


def parse_table(content: str, header_pattern: str) -> list[dict]:
    """마크다운 테이블을 파싱. header_pattern으로 시작하는 테이블을 찾음."""
    lines = content.split("\n")
    tables = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "|" in line and header_pattern.lower() in line.lower():
            # 헤더 행 발견
            headers = [h.strip() for h in line.split("|") if h.strip()]
            # 구분선 건너뛰기
            i += 1
            if i < len(lines) and "---" in lines[i]:
                i += 1
            # 데이터 행 수집
            rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                cells = [c.strip() for c in lines[i].split("|") if c.strip()]
                if len(cells) >= len(headers):
                    rows.append(dict(zip(headers, cells)))
                i += 1
            tables.extend(rows)
        i += 1
    return tables


def parse_percentage(text: str) -> float | None:
    """텍스트에서 퍼센트 숫자 추출"""
    match = re.search(r"([+-]?\d+\.?\d*)%", text)
    if match:
        return float(match.group(1))
    return None


def generate_daily_chart(content: str, fm: dict, output_path: Path):
    """데일리 브리핑: 급등/급락주 비교 차트"""
    # 급등주 테이블 파싱
    gainers = parse_table(content, "종목명")

    if len(gainers) < 4:
        return None

    # 급등/급락 분리 (등락률 기준)
    up_stocks = []
    down_stocks = []
    for row in gainers:
        pct = parse_percentage(row.get("등락률", ""))
        name = re.sub(r"\(.*?\)", "", row.get("종목명", "")).strip()
        if pct is not None and name:
            if pct > 0:
                up_stocks.append((name, pct))
            else:
                down_stocks.append((name, pct))

    if not up_stocks and not down_stocks:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1, 1]})
    fig.suptitle(fm.get("date", "").split("T")[0] + " 특징주 등락률",
                 fontsize=14, fontweight="bold", color=COLORS["dark"], y=0.98)

    # 급등주
    ax1 = axes[0]
    if up_stocks:
        up_stocks = sorted(up_stocks, key=lambda x: x[1])[-7:]
        names = [s[0] for s in up_stocks]
        vals = [s[1] for s in up_stocks]
        bars = ax1.barh(names, vals, color=COLORS["red"], height=0.6, edgecolor="none")
        for bar, v in zip(bars, vals):
            ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                     f"+{v:.1f}%", va="center", fontsize=10, color=COLORS["red"], fontweight="bold")
    ax1.set_title("급등주 TOP", fontsize=12, fontweight="bold", color=COLORS["red"])
    ax1.set_xlim(0, max([s[1] for s in up_stocks], default=0) * 1.3)
    ax1.tick_params(axis="y", labelsize=10)
    ax1.tick_params(axis="x", labelbottom=False)

    # 급락주
    ax2 = axes[1]
    if down_stocks:
        down_stocks = sorted(down_stocks, key=lambda x: x[1])[:7]
        names = [s[0] for s in down_stocks]
        vals = [s[1] for s in down_stocks]
        bars = ax2.barh(names, vals, color=COLORS["blue"], height=0.6, edgecolor="none")
        for bar, v in zip(bars, vals):
            ax2.text(bar.get_width() - 0.3, bar.get_y() + bar.get_height() / 2,
                     f"{v:.1f}%", va="center", ha="right", fontsize=10, color=COLORS["blue"], fontweight="bold")
    ax2.set_title("급락주 TOP", fontsize=12, fontweight="bold", color=COLORS["blue"])
    ax2.set_xlim(min([s[1] for s in down_stocks], default=0) * 1.3, 0)
    ax2.tick_params(axis="y", labelsize=10)
    ax2.tick_params(axis="x", labelbottom=False)

    # 브랜드 워터마크
    fig.text(0.99, 0.01, "stoquote.vercel.app", fontsize=8, color=COLORS["gray"],
             ha="right", va="bottom", style="italic")

    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    return output_path


def generate_sector_chart(content: str, fm: dict, output_path: Path):
    """섹터 분석: 관련주 등락률 차트"""
    rows = parse_table(content, "종목명")
    if len(rows) < 3:
        return None

    stocks = []
    for row in rows:
        pct = parse_percentage(row.get("등락률", ""))
        name = re.sub(r"\(.*?\)", "", row.get("종목명", "")).strip()
        if pct is not None and name:
            stocks.append((name, pct))

    if not stocks:
        return None

    stocks = sorted(stocks, key=lambda x: x[1], reverse=True)[:10]
    names = [s[0] for s in stocks]
    vals = [s[1] for s in stocks]
    bar_colors = [COLORS["red"] if v > 0 else COLORS["blue"] for v in vals]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(names[::-1], vals[::-1], color=bar_colors[::-1], height=0.6, edgecolor="none")

    for bar, v in zip(bars, vals[::-1]):
        offset = 0.3 if v > 0 else -0.3
        ha = "left" if v > 0 else "right"
        label = f"+{v:.1f}%" if v > 0 else f"{v:.1f}%"
        ax.text(bar.get_width() + offset, bar.get_y() + bar.get_height() / 2,
                label, va="center", ha=ha, fontsize=10, fontweight="bold",
                color=COLORS["red"] if v > 0 else COLORS["blue"])

    title = fm.get("title", "섹터 분석")
    if len(title) > 30:
        title = title[:30] + "..."
    ax.set_title(title, fontsize=13, fontweight="bold", color=COLORS["dark"], pad=12)
    ax.axvline(x=0, color=COLORS["gray"], linewidth=0.8)
    ax.tick_params(axis="x", labelbottom=False)

    fig.text(0.99, 0.01, "stoquote.vercel.app", fontsize=8, color=COLORS["gray"],
             ha="right", va="bottom", style="italic")
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    return output_path


def generate_std_chart(content: str, fm: dict, output_path: Path):
    """표준편차 분석: 과매수/과매도 종목 시각화"""
    rows = parse_table(content, "종목")
    if len(rows) < 3:
        return None

    stocks = []
    for row in rows:
        name = ""
        zscore = None
        for k, v in row.items():
            if "종목" in k:
                name = re.sub(r"\(.*?\)", "", v).strip()
            if "z" in k.lower() or "score" in k.lower() or "편차" in k.lower():
                match = re.search(r"([+-]?\d+\.?\d*)", v)
                if match:
                    zscore = float(match.group(1))
        if name and zscore is not None:
            stocks.append((name, zscore))

    if not stocks:
        return None

    stocks = sorted(stocks, key=lambda x: x[1])
    names = [s[0] for s in stocks]
    vals = [s[1] for s in stocks]
    bar_colors = [COLORS["red"] if v > 0 else COLORS["green"] for v in vals]

    fig, ax = plt.subplots(figsize=(10, max(4, len(stocks) * 0.5)))
    bars = ax.barh(names, vals, color=bar_colors, height=0.6, edgecolor="none")

    for bar, v in zip(bars, vals):
        offset = 0.05 if v > 0 else -0.05
        ha = "left" if v > 0 else "right"
        ax.text(bar.get_width() + offset, bar.get_y() + bar.get_height() / 2,
                f"{v:+.2f}", va="center", ha=ha, fontsize=10, fontweight="bold",
                color=COLORS["red"] if v > 0 else COLORS["green"])

    ax.set_title("Z-Score 기반 매매 시그널", fontsize=13, fontweight="bold", color=COLORS["dark"], pad=12)
    ax.axvline(x=0, color=COLORS["dark"], linewidth=0.8)
    ax.axvline(x=2, color=COLORS["red"], linewidth=0.5, linestyle="--", alpha=0.5)
    ax.axvline(x=-2, color=COLORS["green"], linewidth=0.5, linestyle="--", alpha=0.5)
    ax.text(2.05, len(stocks) - 0.5, "과매수", fontsize=8, color=COLORS["red"], alpha=0.7)
    ax.text(-2.4, len(stocks) - 0.5, "과매도", fontsize=8, color=COLORS["green"], alpha=0.7)

    fig.text(0.99, 0.01, "stoquote.vercel.app", fontsize=8, color=COLORS["gray"],
             ha="right", va="bottom", style="italic")
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    return output_path


def process_post(post_path: Path, charts_dir: Path) -> str | None:
    """포스트를 처리하여 차트 생성 & 본문에 삽입"""
    content = post_path.read_text(encoding="utf-8")
    fm = extract_frontmatter(content)
    post_type = fm.get("type", "")
    stem = post_path.stem

    chart_path = charts_dir / f"{stem}.png"
    result = None

    if post_type == "daily_briefing":
        result = generate_daily_chart(content, fm, chart_path)
    elif post_type == "sector_analysis":
        result = generate_sector_chart(content, fm, chart_path)
    elif post_type == "std_analysis":
        result = generate_std_chart(content, fm, chart_path)

    if result is None:
        return None

    # 본문에 이미지 태그가 이미 있으면 건너뛰기
    chart_ref = f"/assets/charts/{stem}.png"
    if chart_ref in content:
        print(f"  이미 이미지 삽입됨: {stem}")
        return chart_ref

    # H1 제목 + article-meta 블록 다음에 이미지 삽입
    img_md = f"\n![{fm.get('title', '차트')}]({chart_ref})\n"

    # H1 뒤 첫 번째 빈 줄 앞에 삽입
    lines = content.split("\n")
    h1_found = False
    insert_idx = None
    for i, line in enumerate(lines):
        if line.startswith("# ") and not h1_found:
            h1_found = True
            continue
        if h1_found and line.strip() and not line.startswith("#"):
            insert_idx = i
            break

    if insert_idx:
        lines.insert(insert_idx, img_md)
        post_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  이미지 삽입 완료: {stem}")
    else:
        print(f"  삽입 위치를 찾을 수 없음: {stem}")

    return chart_ref


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    posts_dir = project_root / "posts"
    charts_dir = project_root / "assets" / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        # 특정 포스트만
        targets = [Path(p) for p in sys.argv[1:]]
    else:
        # 모든 포스트
        targets = sorted(posts_dir.glob("*.md"))

    generated = 0
    for post_path in targets:
        print(f"처리 중: {post_path.name}")
        result = process_post(post_path, charts_dir)
        if result:
            generated += 1

    print(f"\n완료: {generated}개 차트 생성")


if __name__ == "__main__":
    main()

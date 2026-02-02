"""
CLI 인터페이스 (Typer + Rich)

사용법:
    stock top --market us --limit 10
    stock movers --market kr
    stock sector semiconductor --market us
    stock search "삼성전자"
"""

from enum import Enum
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from . import kr_market, us_market
from .models import Market, StockInfo

app = typer.Typer(
    name="stock",
    help="한국/미국 증시 리서치 도구",
    add_completion=False,
)
console = Console()


class MarketChoice(str, Enum):
    us = "us"
    kr = "kr"
    all = "all"


def format_number(value: Optional[float], suffix: str = "") -> str:
    """숫자 포맷팅 (조/억/만 단위)"""
    if value is None:
        return "-"

    if value >= 1_000_000_000_000:  # 조 단위
        return f"{value / 1_000_000_000_000:.1f}조{suffix}"
    elif value >= 100_000_000:  # 억 단위
        return f"{value / 100_000_000:.0f}억{suffix}"
    elif value >= 10_000:  # 만 단위
        return f"{value / 10_000:.0f}만{suffix}"
    else:
        return f"{value:,.0f}{suffix}"


def format_percent(value: Optional[float]) -> str:
    """등락률 포맷팅 (색상 포함)"""
    if value is None:
        return "-"

    if value > 0:
        return f"[green]+{value:.2f}%[/green]"
    elif value < 0:
        return f"[red]{value:.2f}%[/red]"
    else:
        return f"{value:.2f}%"


def format_price(value: Optional[float], market: Market) -> str:
    """가격 포맷팅"""
    if value is None:
        return "-"

    if market == Market.US:
        return f"${value:,.2f}"
    else:
        return f"₩{value:,.0f}"


def create_stock_table(stocks: list[StockInfo], title: str) -> Table:
    """종목 테이블 생성"""
    table = Table(title=title, show_header=True, header_style="bold cyan")

    table.add_column("심볼", style="bold")
    table.add_column("종목명", max_width=20)
    table.add_column("현재가", justify="right")
    table.add_column("등락률", justify="right")
    table.add_column("시가총액", justify="right")
    table.add_column("거래량", justify="right")

    for stock in stocks:
        table.add_row(
            stock.symbol,
            stock.name[:20] if stock.name else "-",
            format_price(stock.price, stock.market),
            format_percent(stock.change_percent),
            format_number(stock.market_cap),
            format_number(stock.volume),
        )

    return table


@app.command("top")
def cmd_top(
    market: MarketChoice = typer.Option(MarketChoice.us, "--market", "-m", help="시장 선택"),
    limit: int = typer.Option(10, "--limit", "-n", help="조회 개수"),
):
    """
    시가총액 TOP 종목 조회
    """
    console.print(Panel(f"[bold]시가총액 TOP {limit}[/bold] - {market.value.upper()}", style="blue"))

    if market == MarketChoice.kr or market == MarketChoice.all:
        with console.status("한국 시장 조회 중..."):
            kr_stocks = kr_market.get_top_by_market_cap(
                market_type="ALL" if market == MarketChoice.all else "KOSPI",
                limit=limit
            )
        if kr_stocks:
            console.print(create_stock_table(kr_stocks, "🇰🇷 한국 시가총액 TOP"))
            console.print()

    if market == MarketChoice.us or market == MarketChoice.all:
        with console.status("미국 시장 조회 중..."):
            us_stocks = us_market.get_top_by_market_cap(limit=limit)
        if us_stocks:
            console.print(create_stock_table(us_stocks, "🇺🇸 미국 시가총액 TOP"))


@app.command("movers")
def cmd_movers(
    market: MarketChoice = typer.Option(MarketChoice.us, "--market", "-m", help="시장 선택"),
    limit: int = typer.Option(10, "--limit", "-n", help="조회 개수"),
):
    """
    급등/급락/거래량 상위 종목 조회
    """
    console.print(Panel("[bold]급등/급락/거래량 TOP[/bold]", style="blue"))

    if market == MarketChoice.kr or market == MarketChoice.all:
        with console.status("한국 시장 조회 중..."):
            kr_movers = kr_market.get_top_movers(market_type="KOSPI", limit=limit)

        console.print(f"\n[bold cyan]🇰🇷 한국 시장[/bold cyan]")

        # 상승 TOP
        table = Table(title="📈 상승 TOP", show_header=True)
        table.add_column("심볼")
        table.add_column("종목명")
        table.add_column("등락률", justify="right")
        table.add_column("현재가", justify="right")
        for stock in kr_movers.gainers:
            table.add_row(
                stock.symbol,
                stock.name[:15] if stock.name else "-",
                format_percent(stock.change_percent),
                format_price(stock.price, stock.market),
            )
        console.print(table)

        # 하락 TOP
        table = Table(title="📉 하락 TOP", show_header=True)
        table.add_column("심볼")
        table.add_column("종목명")
        table.add_column("등락률", justify="right")
        table.add_column("현재가", justify="right")
        for stock in kr_movers.losers:
            table.add_row(
                stock.symbol,
                stock.name[:15] if stock.name else "-",
                format_percent(stock.change_percent),
                format_price(stock.price, stock.market),
            )
        console.print(table)

        # 거래량 TOP
        table = Table(title="🔥 거래량 TOP", show_header=True)
        table.add_column("심볼")
        table.add_column("종목명")
        table.add_column("거래량", justify="right")
        table.add_column("등락률", justify="right")
        for stock in kr_movers.most_active:
            table.add_row(
                stock.symbol,
                stock.name[:15] if stock.name else "-",
                format_number(stock.volume),
                format_percent(stock.change_percent),
            )
        console.print(table)
        console.print()

    if market == MarketChoice.us or market == MarketChoice.all:
        with console.status("미국 시장 조회 중..."):
            us_movers = us_market.get_top_movers(limit=limit)

        console.print(f"\n[bold cyan]🇺🇸 미국 시장[/bold cyan]")

        # 상승 TOP
        table = Table(title="📈 상승 TOP", show_header=True)
        table.add_column("심볼")
        table.add_column("종목명")
        table.add_column("등락률", justify="right")
        table.add_column("현재가", justify="right")
        for stock in us_movers.gainers:
            table.add_row(
                stock.symbol,
                stock.name[:15] if stock.name else "-",
                format_percent(stock.change_percent),
                format_price(stock.price, stock.market),
            )
        console.print(table)

        # 하락 TOP
        table = Table(title="📉 하락 TOP", show_header=True)
        table.add_column("심볼")
        table.add_column("종목명")
        table.add_column("등락률", justify="right")
        table.add_column("현재가", justify="right")
        for stock in us_movers.losers:
            table.add_row(
                stock.symbol,
                stock.name[:15] if stock.name else "-",
                format_percent(stock.change_percent),
                format_price(stock.price, stock.market),
            )
        console.print(table)

        # 거래량 TOP
        table = Table(title="🔥 거래량 TOP", show_header=True)
        table.add_column("심볼")
        table.add_column("종목명")
        table.add_column("거래량", justify="right")
        table.add_column("등락률", justify="right")
        for stock in us_movers.most_active:
            table.add_row(
                stock.symbol,
                stock.name[:15] if stock.name else "-",
                format_number(stock.volume),
                format_percent(stock.change_percent),
            )
        console.print(table)


@app.command("sector")
def cmd_sector(
    sector: str = typer.Argument(..., help="섹터 (technology, semiconductor, ai, bio, ev, battery 등)"),
    market: MarketChoice = typer.Option(MarketChoice.us, "--market", "-m", help="시장 선택"),
    limit: int = typer.Option(10, "--limit", "-n", help="조회 개수"),
):
    """
    섹터별 상위 종목 조회
    """
    console.print(Panel(f"[bold]{sector.upper()} 섹터 TOP {limit}[/bold]", style="blue"))

    if market == MarketChoice.kr or market == MarketChoice.all:
        with console.status("한국 시장 조회 중..."):
            kr_stocks = kr_market.get_sector_top(sector, limit=limit)
        if kr_stocks:
            console.print(create_stock_table(kr_stocks, f"🇰🇷 한국 {sector.upper()}"))
        else:
            console.print(f"[yellow]한국 시장에서 '{sector}' 섹터 데이터를 찾을 수 없습니다.[/yellow]")
        console.print()

    if market == MarketChoice.us or market == MarketChoice.all:
        with console.status("미국 시장 조회 중..."):
            us_stocks = us_market.get_sector_top(sector, limit=limit)
        if us_stocks:
            console.print(create_stock_table(us_stocks, f"🇺🇸 미국 {sector.upper()}"))
        else:
            console.print(f"[yellow]미국 시장에서 '{sector}' 섹터 데이터를 찾을 수 없습니다.[/yellow]")


@app.command("search")
def cmd_search(
    query: str = typer.Argument(..., help="검색어 (종목명 또는 티커)"),
    market: MarketChoice = typer.Option(MarketChoice.all, "--market", "-m", help="시장 선택"),
    limit: int = typer.Option(10, "--limit", "-n", help="조회 개수"),
):
    """
    종목 검색
    """
    console.print(Panel(f"[bold]'{query}' 검색 결과[/bold]", style="blue"))

    if market == MarketChoice.kr or market == MarketChoice.all:
        with console.status("한국 시장 검색 중..."):
            kr_stocks = kr_market.search_stocks(query, limit=limit)
        if kr_stocks:
            console.print(create_stock_table(kr_stocks, "🇰🇷 한국"))
        console.print()

    if market == MarketChoice.us or market == MarketChoice.all:
        with console.status("미국 시장 검색 중..."):
            us_stocks = us_market.search_stocks(query, limit=limit)
        if us_stocks:
            console.print(create_stock_table(us_stocks, "🇺🇸 미국"))


@app.command("summary")
def cmd_summary(
    market: MarketChoice = typer.Option(MarketChoice.all, "--market", "-m", help="시장 선택"),
):
    """
    시장 요약 정보 조회
    """
    console.print(Panel("[bold]시장 요약[/bold]", style="blue"))

    if market == MarketChoice.kr or market == MarketChoice.all:
        with console.status("한국 시장 조회 중..."):
            kospi = kr_market.get_market_summary("KOSPI")
            kosdaq = kr_market.get_market_summary("KOSDAQ")

        table = Table(title="🇰🇷 한국 시장", show_header=True)
        table.add_column("지수")
        table.add_column("상승", justify="right", style="green")
        table.add_column("하락", justify="right", style="red")
        table.add_column("보합", justify="right")
        table.add_column("거래대금", justify="right")

        table.add_row(
            "KOSPI",
            str(kospi.advancing),
            str(kospi.declining),
            str(kospi.unchanged),
            format_number(kospi.total_value, "원"),
        )
        table.add_row(
            "KOSDAQ",
            str(kosdaq.advancing),
            str(kosdaq.declining),
            str(kosdaq.unchanged),
            format_number(kosdaq.total_value, "원"),
        )
        console.print(table)
        console.print()

    if market == MarketChoice.us or market == MarketChoice.all:
        with console.status("미국 시장 조회 중..."):
            sp500 = us_market.get_market_summary("SP500")
            nasdaq = us_market.get_market_summary("NASDAQ")

        table = Table(title="🇺🇸 미국 시장", show_header=True)
        table.add_column("지수")
        table.add_column("현재", justify="right")
        table.add_column("변동", justify="right")
        table.add_column("등락률", justify="right")

        table.add_row(
            "S&P 500",
            f"{sp500.index_value:,.2f}",
            f"{sp500.index_change:+,.2f}",
            format_percent(sp500.index_change_percent),
        )
        table.add_row(
            "NASDAQ",
            f"{nasdaq.index_value:,.2f}",
            f"{nasdaq.index_change:+,.2f}",
            format_percent(nasdaq.index_change_percent),
        )
        console.print(table)


@app.command("sectors")
def cmd_sectors():
    """
    사용 가능한 섹터 목록 출력
    """
    console.print(Panel("[bold]사용 가능한 섹터[/bold]", style="blue"))

    table = Table(show_header=True)
    table.add_column("섹터 키", style="bold")
    table.add_column("설명")
    table.add_column("미국", justify="center")
    table.add_column("한국", justify="center")

    sectors = [
        ("technology", "기술/IT", "✅", "⚠️"),
        ("semiconductor", "반도체", "✅", "✅"),
        ("ai", "인공지능", "✅", "⚠️"),
        ("healthcare", "헬스케어", "✅", "⚠️"),
        ("bio", "바이오", "✅", "✅"),
        ("financials", "금융", "✅", "⚠️"),
        ("consumer_cyclical", "경기소비재", "✅", "⚠️"),
        ("consumer_defensive", "필수소비재", "✅", "⚠️"),
        ("energy", "에너지", "✅", "⚠️"),
        ("industrials", "산업재", "✅", "⚠️"),
        ("communication", "커뮤니케이션", "✅", "⚠️"),
        ("utilities", "유틸리티", "✅", "⚠️"),
        ("real_estate", "부동산", "✅", "⚠️"),
        ("materials", "소재", "✅", "⚠️"),
        ("ev", "전기차", "✅", "⚠️"),
        ("battery", "배터리/2차전지", "✅", "✅"),
    ]

    for key, desc, us, kr in sectors:
        table.add_row(key, desc, us, kr)

    console.print(table)
    console.print("\n[dim]✅ 지원 | ⚠️ 제한적 지원 (ETF 기반)[/dim]")


if __name__ == "__main__":
    app()

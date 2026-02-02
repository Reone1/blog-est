"""
미국 증시 조회 모듈 (yfinance 기반)

기능:
- S&P500, NASDAQ 시가총액 TOP 10
- 섹터별 상위 종목
- 급등주/거래량 급증 종목
"""

from datetime import date, datetime
from typing import Optional

import yfinance as yf

from .models import Market, MarketSummary, StockInfo, TopMovers


# S&P500 대표 종목 (시가총액 상위)
SP500_TOP = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "UNH", "JNJ",
    "JPM", "V", "PG", "XOM", "HD", "CVX", "MA", "ABBV", "MRK", "LLY",
    "PEP", "KO", "COST", "AVGO", "TMO", "MCD", "WMT", "CSCO", "ACN", "ABT",
    "DHR", "VZ", "ADBE", "CRM", "NKE", "CMCSA", "TXN", "PM", "NEE", "BMY",
    "INTC", "AMD", "QCOM", "ORCL", "IBM", "NOW", "INTU", "AMGN", "HON", "UPS"
]

# 섹터별 대표 종목
SECTOR_TICKERS = {
    "technology": ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "ADBE", "CSCO", "ACN", "IBM"],
    "semiconductor": ["NVDA", "AMD", "INTC", "AVGO", "QCOM", "TXN", "MU", "AMAT", "LRCX", "KLAC"],
    "ai": ["NVDA", "MSFT", "GOOGL", "META", "AMD", "PLTR", "CRM", "NOW", "SNOW", "AI"],
    "healthcare": ["UNH", "JNJ", "LLY", "ABBV", "MRK", "PFE", "TMO", "ABT", "DHR", "BMY"],
    "bio": ["LLY", "ABBV", "MRK", "AMGN", "GILD", "VRTX", "REGN", "BIIB", "MRNA", "ILMN"],
    "financials": ["JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "BLK", "AXP", "C"],
    "consumer_cyclical": ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "TGT", "LOW", "BKNG", "GM"],
    "consumer_defensive": ["PG", "KO", "PEP", "COST", "WMT", "PM", "MO", "CL", "KMB", "GIS"],
    "energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL"],
    "industrials": ["HON", "UPS", "CAT", "BA", "RTX", "GE", "DE", "LMT", "MMM", "FDX"],
    "communication": ["GOOGL", "META", "NFLX", "DIS", "CMCSA", "VZ", "T", "TMUS", "CHTR", "EA"],
    "utilities": ["NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL", "PEG", "ED"],
    "real_estate": ["PLD", "AMT", "EQIX", "CCI", "PSA", "O", "WELL", "SPG", "DLR", "AVB"],
    "materials": ["LIN", "APD", "SHW", "ECL", "DD", "NEM", "FCX", "NUE", "VMC", "MLM"],
    "ev": ["TSLA", "RIVN", "LCID", "NIO", "XPEV", "LI", "GM", "F", "STLA", "CHPT"],
    "battery": ["ALB", "SQM", "LTHM", "LAC", "PLL", "MP", "FREYR", "QS", "MVST", "DCRC"],
}

# 지수 티커
INDEX_TICKERS = {
    "SP500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
}


def get_market_summary(index_type: str = "SP500") -> MarketSummary:
    """
    시장 요약 정보 조회

    Args:
        index_type: "SP500", "NASDAQ", "DOW"
    """
    ticker = INDEX_TICKERS.get(index_type, "^GSPC")
    index = yf.Ticker(ticker)

    try:
        hist = index.history(period="2d")
        if len(hist) >= 2:
            current = hist.iloc[-1]["Close"]
            previous = hist.iloc[-2]["Close"]
            change = current - previous
            change_pct = (change / previous) * 100
        else:
            current = hist.iloc[-1]["Close"] if len(hist) > 0 else 0
            change = 0
            change_pct = 0
    except Exception:
        current = change = change_pct = 0

    return MarketSummary(
        market=Market.US,
        date=date.today(),
        index_name=index_type,
        index_value=float(current),
        index_change=float(change),
        index_change_percent=float(change_pct),
    )


def get_stock_info(symbol: str) -> Optional[StockInfo]:
    """
    개별 종목 정보 조회

    Args:
        symbol: 티커 심볼
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # 현재가와 등락률
        hist = ticker.history(period="2d")
        if len(hist) >= 2:
            price = hist.iloc[-1]["Close"]
            prev_price = hist.iloc[-2]["Close"]
            change_pct = ((price - prev_price) / prev_price) * 100
            volume = int(hist.iloc[-1]["Volume"])
        elif len(hist) == 1:
            price = hist.iloc[-1]["Close"]
            change_pct = 0
            volume = int(hist.iloc[-1]["Volume"])
        else:
            price = info.get("regularMarketPrice", 0)
            change_pct = info.get("regularMarketChangePercent", 0)
            volume = info.get("regularMarketVolume", 0)

        return StockInfo(
            symbol=symbol,
            name=info.get("shortName", info.get("longName", symbol)),
            market=Market.US,
            sector=info.get("sector"),
            industry=info.get("industry"),
            price=float(price) if price else None,
            change_percent=float(change_pct) if change_pct else None,
            volume=int(volume) if volume else None,
            market_cap=float(info.get("marketCap", 0)) if info.get("marketCap") else None,
            pe_ratio=info.get("trailingPE"),
            pb_ratio=info.get("priceToBook"),
            dividend_yield=info.get("dividendYield"),
            fetched_at=date.today(),
        )
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def get_top_by_market_cap(limit: int = 10) -> list[StockInfo]:
    """
    시가총액 상위 종목 조회

    Args:
        limit: 조회 개수
    """
    results = []

    for symbol in SP500_TOP[:limit * 2]:  # 여유있게 조회
        stock = get_stock_info(symbol)
        if stock and stock.market_cap:
            results.append(stock)

        if len(results) >= limit:
            break

    # 시가총액 기준 정렬
    results.sort(key=lambda x: x.market_cap or 0, reverse=True)
    return results[:limit]


def get_top_movers(limit: int = 10) -> TopMovers:
    """
    급등/급락/거래량 상위 종목 조회

    Args:
        limit: 각 카테고리별 조회 개수
    """
    # 더 많은 종목에서 조회
    all_stocks = []
    for symbol in SP500_TOP:
        stock = get_stock_info(symbol)
        if stock:
            all_stocks.append(stock)

    # 상승률 TOP
    gainers = sorted(
        [s for s in all_stocks if s.change_percent is not None],
        key=lambda x: x.change_percent or 0,
        reverse=True
    )[:limit]

    # 하락률 TOP
    losers = sorted(
        [s for s in all_stocks if s.change_percent is not None],
        key=lambda x: x.change_percent or 0
    )[:limit]

    # 거래량 TOP
    most_active = sorted(
        [s for s in all_stocks if s.volume is not None],
        key=lambda x: x.volume or 0,
        reverse=True
    )[:limit]

    return TopMovers(
        gainers=gainers,
        losers=losers,
        most_active=most_active,
        market=Market.US,
        date=date.today(),
    )


def get_sector_top(sector: str, limit: int = 10) -> list[StockInfo]:
    """
    섹터별 상위 종목 조회

    Args:
        sector: 섹터 키 (technology, semiconductor, ai 등)
        limit: 조회 개수
    """
    tickers = SECTOR_TICKERS.get(sector.lower(), [])

    if not tickers:
        return []

    results = []
    for symbol in tickers:
        stock = get_stock_info(symbol)
        if stock:
            stock.sector = sector
            results.append(stock)

        if len(results) >= limit:
            break

    # 시가총액 기준 정렬
    results.sort(key=lambda x: x.market_cap or 0, reverse=True)
    return results[:limit]


def search_stocks(query: str, limit: int = 10) -> list[StockInfo]:
    """
    종목 검색

    Args:
        query: 검색어 (종목명 또는 티커)
        limit: 조회 개수
    """
    results = []

    # 직접 티커로 검색
    stock = get_stock_info(query.upper())
    if stock:
        results.append(stock)

    # 대표 종목에서 검색
    for symbol in SP500_TOP:
        if query.lower() in symbol.lower():
            stock = get_stock_info(symbol)
            if stock and stock not in results:
                results.append(stock)

        if len(results) >= limit:
            break

    return results[:limit]


def get_multiple_stocks(symbols: list[str]) -> list[StockInfo]:
    """
    여러 종목 일괄 조회

    Args:
        symbols: 티커 리스트
    """
    results = []
    for symbol in symbols:
        stock = get_stock_info(symbol)
        if stock:
            results.append(stock)
    return results

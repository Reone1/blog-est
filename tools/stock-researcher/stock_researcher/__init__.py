"""
Stock Researcher - 한국/미국 증시 리서치 도구

기능:
- 섹터별 상위 종목 조회
- 시가총액 TOP 10
- 급등주/거래량 급증 종목
- 변동성 분석 및 표준편차 매매 시그널
- MCP 서버로 확장 가능
"""

__version__ = "0.2.0"

# 데이터 모델
from .models import (
    Market,
    MarketBreadth,
    MarketSummary,
    Sector,
    StdSignal,
    StockInfo,
    TopMovers,
    VolatilityData,
    VolatilitySignal,
)

# 한국 시장
from .kr_market import (
    enrich_stock_detail,
    enrich_stocks_detail,
    get_market_summary,
    get_sector_top,
    get_top_by_market_cap,
    get_top_movers,
    get_trading_date,
    search_stocks,
)

# 변동성 분석
from .analytics import (
    calculate_volatility,
    get_market_breadth,
    get_std_signals,
    get_volatility_ranking,
)

__all__ = [
    # 모델
    "Market",
    "Sector",
    "StockInfo",
    "MarketSummary",
    "TopMovers",
    "VolatilityData",
    "VolatilitySignal",
    "StdSignal",
    "MarketBreadth",
    # 한국 시장
    "get_trading_date",
    "get_market_summary",
    "get_top_by_market_cap",
    "get_top_movers",
    "get_sector_top",
    "search_stocks",
    "enrich_stock_detail",
    "enrich_stocks_detail",
    # 변동성 분석
    "calculate_volatility",
    "get_std_signals",
    "get_market_breadth",
    "get_volatility_ranking",
]

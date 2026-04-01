"""
한국 증시 조회 모듈 (Naver Finance API + FinanceDataReader 기반)

기능:
- KOSPI/KOSDAQ 시장 요약 (지수, 등락률, 상승/하락 종목 수)
- 시가총액 상위 종목
- 급등주/급락주/거래량 상위 종목
- 섹터별 상위 종목
- 종목 검색
"""

import re
from datetime import date, datetime, timedelta
from typing import Optional

import requests

from .models import Market, MarketSummary, StockInfo, TopMovers


# Naver Finance API 기본 URL
NAVER_API_BASE = "https://m.stock.naver.com/api"

# 시장 코드 매핑
MARKET_CODE_MAP = {
    "KOSPI": "KOSPI",
    "KOSDAQ": "KOSDAQ",
}

# 지수 코드 매핑 (FinanceDataReader용)
INDEX_CODE_MAP = {
    "KOSPI": "KS11",
    "KOSDAQ": "KQ11",
}

# 테마 ETF 티커 (섹터 대용)
THEME_ETFS = {
    "semiconductor": ["091160", "091170", "395170"],
    "battery": ["305720", "373540"],
    "bio": ["244580", "261110"],
    "ai": ["463050", "466920"],
}


def _naver_session() -> requests.Session:
    """Naver Finance API용 세션 생성"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://m.stock.naver.com/",
    })
    return session


def _parse_naver_number(value: str) -> float:
    """Naver API의 숫자 문자열을 float으로 변환 (쉼표 제거)"""
    if not value or value == "N/A":
        return 0.0
    return float(str(value).replace(",", ""))


def _parse_naver_int(value: str) -> int:
    """Naver API의 숫자 문자열을 int으로 변환"""
    if not value or value == "N/A":
        return 0
    return int(str(value).replace(",", ""))


def _naver_stock_to_stock_info(item: dict, market: Market = Market.KR) -> StockInfo:
    """Naver API 종목 데이터를 StockInfo로 변환"""
    # PER/PBR은 개별 종목 상세 API에서만 제공되므로 있을 때만 파싱
    pe_ratio = None
    pb_ratio = None
    dividend_yield = None
    if "per" in item:
        try:
            pe_ratio = float(item["per"])
        except (ValueError, TypeError):
            pass
    if "pbr" in item:
        try:
            pb_ratio = float(item["pbr"])
        except (ValueError, TypeError):
            pass
    if "dividendYield" in item:
        try:
            dividend_yield = float(item["dividendYield"])
        except (ValueError, TypeError):
            pass

    return StockInfo(
        symbol=item.get("itemCode", ""),
        name=item.get("stockName", ""),
        market=market,
        price=_parse_naver_number(item.get("closePrice", "0")),
        change_percent=float(item.get("fluctuationsRatio", 0)),
        volume=_parse_naver_int(item.get("accumulatedTradingVolume", "0")),
        market_cap=_parse_naver_number(item.get("marketValue", "0")) * 1_0000_0000,
        pe_ratio=pe_ratio,
        pb_ratio=pb_ratio,
        dividend_yield=dividend_yield,
        fetched_at=date.today(),
    )


def get_trading_date(offset: int = 0) -> str:
    """
    최근 거래일 반환 (YYYYMMDD 형식)

    Args:
        offset: 0=오늘/가장 최근, -1=전일, ...
    """
    today = datetime.now()

    # 주말 건너뛰기
    skip_count = 0
    for i in range(30):
        check_date = today - timedelta(days=i)
        # 주말 제외
        if check_date.weekday() >= 5:
            continue

        if skip_count == abs(offset):
            return check_date.strftime("%Y%m%d")
        skip_count += 1

    return today.strftime("%Y%m%d")


def get_market_summary(market_type: str = "KOSPI") -> MarketSummary:
    """
    시장 요약 정보 조회

    Args:
        market_type: "KOSPI" 또는 "KOSDAQ"
    """
    session = _naver_session()
    market_code = MARKET_CODE_MAP.get(market_type, market_type)

    # 1. 지수 데이터 조회
    index_data = {}
    try:
        r = session.get(
            f"{NAVER_API_BASE}/index/{market_code}/basic",
            timeout=10,
        )
        if r.status_code == 200:
            index_data = r.json()
    except Exception:
        pass

    # 2. 상승/하락 종목 수 조회
    advancing = 0
    declining = 0
    for direction, attr in [("up", "advancing"), ("down", "declining")]:
        try:
            r = session.get(
                f"{NAVER_API_BASE}/stocks/{direction}/{market_code}",
                params={"page": 1, "pageSize": 1},
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                count = data.get("totalCount", 0)
                if attr == "advancing":
                    advancing = count
                else:
                    declining = count
        except Exception:
            pass

    # 지수 값 파싱
    index_value = _parse_naver_number(index_data.get("closePrice", "0"))
    index_change = _parse_naver_number(
        index_data.get("compareToPreviousClosePrice", "0")
    )
    fluctuations_ratio = float(index_data.get("fluctuationsRatio", 0))

    # 거래량/거래대금 파싱
    total_volume = None
    total_value = None
    raw_volume = index_data.get("accumulatedTradingVolume")
    raw_value = index_data.get("accumulatedTradingValue")
    if raw_volume:
        total_volume = _parse_naver_int(str(raw_volume))
    if raw_value:
        total_value = _parse_naver_number(str(raw_value))

    return MarketSummary(
        market=Market.KR,
        date=date.today(),
        index_name=market_type,
        index_value=index_value,
        index_change=index_change,
        index_change_percent=fluctuations_ratio,
        advancing=advancing,
        declining=declining,
        unchanged=0,
        total_volume=total_volume,
        total_value=total_value,
    )


def get_top_by_market_cap(
    market_type: str = "KOSPI",
    limit: int = 10,
) -> list[StockInfo]:
    """
    시가총액 상위 종목 조회

    Args:
        market_type: "KOSPI" 또는 "KOSDAQ" 또는 "ALL"
        limit: 조회 개수
    """
    session = _naver_session()
    results = []
    markets = ["KOSPI", "KOSDAQ"] if market_type == "ALL" else [market_type]

    for mkt in markets:
        market_code = MARKET_CODE_MAP.get(mkt, mkt)
        page_size = limit if market_type != "ALL" else limit * 2

        try:
            r = session.get(
                f"{NAVER_API_BASE}/stocks/marketValue/{market_code}",
                params={"page": 1, "pageSize": page_size},
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                items = data.get("stocks", [])
                for item in items:
                    results.append(_naver_stock_to_stock_info(item))
        except Exception:
            continue

    # 시가총액 기준 정렬
    results.sort(key=lambda x: x.market_cap or 0, reverse=True)
    return results[:limit]


def get_top_movers(
    market_type: str = "KOSPI",
    limit: int = 10,
) -> TopMovers:
    """
    급등/급락/거래량 상위 종목 조회

    Args:
        market_type: "KOSPI" 또는 "KOSDAQ"
        limit: 각 카테고리별 조회 개수
    """
    session = _naver_session()
    market_code = MARKET_CODE_MAP.get(market_type, market_type)

    gainers = []
    losers = []
    most_active = []

    # 상승률 상위
    try:
        r = session.get(
            f"{NAVER_API_BASE}/stocks/up/{market_code}",
            params={"page": 1, "pageSize": limit},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            items = data.get("stocks", [])
            gainers = [_naver_stock_to_stock_info(item) for item in items]
    except Exception:
        pass

    # 하락률 상위
    try:
        r = session.get(
            f"{NAVER_API_BASE}/stocks/down/{market_code}",
            params={"page": 1, "pageSize": limit},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            items = data.get("stocks", [])
            losers = [_naver_stock_to_stock_info(item) for item in items]
    except Exception:
        pass

    # 거래량 상위 = 시총 상위 목록에서 거래량 기준 재정렬
    try:
        r = session.get(
            f"{NAVER_API_BASE}/stocks/marketValue/{market_code}",
            params={"page": 1, "pageSize": 50},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            items = data.get("stocks", [])
            all_stocks = [_naver_stock_to_stock_info(item) for item in items]
            # 거래량 기준 정렬
            all_stocks.sort(key=lambda x: x.volume or 0, reverse=True)
            most_active = all_stocks[:limit]
    except Exception:
        pass

    return TopMovers(
        gainers=gainers,
        losers=losers,
        most_active=most_active,
        market=Market.KR,
        date=date.today(),
    )


def get_sector_top(
    sector: str,
    limit: int = 10,
) -> list[StockInfo]:
    """
    섹터별 상위 종목 조회

    Args:
        sector: 섹터 키 (semiconductor, bio, battery, ai 등)
        limit: 조회 개수

    Note:
        테마 ETF 구성종목 또는 시총 상위에서 섹터 필터링
    """
    # 시총 상위에서 관련 종목 추출
    try:
        all_stocks = get_top_by_market_cap("ALL", limit=50)
        # 섹터 키워드 매핑
        sector_keywords = {
            "semiconductor": ["반도체", "하이닉스", "삼성전자"],
            "battery": ["배터리", "2차전지", "에너지솔루션", "에코프로"],
            "bio": ["바이오", "제약", "셀트리온", "삼성바이오"],
            "ai": ["AI", "인공지능", "네이버", "카카오"],
            "financials": ["금융", "은행", "증권", "보험", "KB", "신한"],
            "technology": ["전자", "IT", "소프트웨어", "LG이노텍"],
        }

        keywords = sector_keywords.get(sector, [sector])
        results = [
            stock for stock in all_stocks
            if any(kw in stock.name for kw in keywords)
        ]
        return results[:limit]
    except Exception:
        return []


def enrich_stock_detail(stock: StockInfo) -> StockInfo:
    """
    개별 종목 상세 API 호출로 PER, PBR, 배당수익률 등 보강

    Args:
        stock: 기본 정보가 담긴 StockInfo

    Returns:
        보강된 StockInfo (원본 변경)
    """
    if not stock.symbol:
        return stock

    session = _naver_session()
    try:
        r = session.get(
            f"{NAVER_API_BASE}/stock/{stock.symbol}/basic",
            timeout=10,
        )
        if r.status_code == 200:
            detail = r.json()

            # PER
            if detail.get("per"):
                try:
                    stock.pe_ratio = float(detail["per"])
                except (ValueError, TypeError):
                    pass

            # PBR
            if detail.get("pbr"):
                try:
                    stock.pb_ratio = float(detail["pbr"])
                except (ValueError, TypeError):
                    pass

            # 배당수익률
            if detail.get("dividendYield"):
                try:
                    stock.dividend_yield = float(detail["dividendYield"])
                except (ValueError, TypeError):
                    pass

            # 가격 정보 보강 (리스트 API에서 누락됐을 경우)
            if not stock.price or stock.price == 0:
                stock.price = _parse_naver_number(
                    detail.get("closePrice", "0")
                )
            if not stock.volume or stock.volume == 0:
                stock.volume = _parse_naver_int(
                    detail.get("accumulatedTradingVolume", "0")
                )
    except Exception:
        pass

    return stock


def enrich_stocks_detail(
    stocks: list[StockInfo],
    limit: int = 10,
) -> list[StockInfo]:
    """
    종목 리스트에 대해 상세 정보 보강 (상위 limit개만)

    Args:
        stocks: StockInfo 리스트
        limit: 상세 조회할 최대 종목 수
    """
    for stock in stocks[:limit]:
        enrich_stock_detail(stock)
    return stocks


def search_stocks(query: str, limit: int = 10) -> list[StockInfo]:
    """
    종목 검색

    Args:
        query: 검색어 (종목명 또는 티커)
        limit: 조회 개수
    """
    session = _naver_session()
    results = []

    # Naver 검색 API 활용
    try:
        r = session.get(
            "https://ac.stock.naver.com/ac",
            params={
                "q": query,
                "target": "stock",
                "st": "t",
            },
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            items = data.get("items", [[]])[0] if data.get("items") else []

            for item in items[:limit]:
                code = item.get("code", "")
                name = item.get("name", "")

                # 개별 종목 상세 조회
                try:
                    detail_r = session.get(
                        f"{NAVER_API_BASE}/stock/{code}/basic",
                        timeout=10,
                    )
                    if detail_r.status_code == 200:
                        detail = detail_r.json()
                        results.append(StockInfo(
                            symbol=code,
                            name=name,
                            market=Market.KR,
                            price=_parse_naver_number(
                                detail.get("closePrice", "0")
                            ),
                            change_percent=float(
                                detail.get("fluctuationsRatio", 0)
                            ),
                            volume=_parse_naver_int(
                                detail.get("accumulatedTradingVolume", "0")
                            ),
                            market_cap=_parse_naver_number(
                                detail.get("marketValue", "0")
                            ) * 1_0000_0000,
                            fetched_at=date.today(),
                        ))
                except Exception:
                    results.append(StockInfo(
                        symbol=code,
                        name=name,
                        market=Market.KR,
                        fetched_at=date.today(),
                    ))
    except Exception:
        pass

    return results

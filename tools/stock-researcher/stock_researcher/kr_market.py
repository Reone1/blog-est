"""
한국 증시 조회 모듈 (pykrx 기반)

기능:
- KOSPI/KOSDAQ 시가총액 TOP 10
- 섹터별 상위 종목
- 급등주/거래량 급증 종목
"""

from datetime import date, datetime, timedelta
from typing import Optional

import pandas as pd
from pykrx import stock as krx

from .models import Market, MarketSummary, StockInfo, TopMovers


# 한국 섹터 매핑 (업종명 → 표준 섹터)
KR_SECTOR_MAP = {
    "반도체": "semiconductor",
    "IT부품": "technology",
    "소프트웨어": "technology",
    "통신장비": "communication",
    "디스플레이": "technology",
    "제약": "bio",
    "바이오": "bio",
    "의료정밀": "healthcare",
    "화학": "materials",
    "철강": "materials",
    "비철금속": "materials",
    "기계": "industrials",
    "조선": "industrials",
    "자동차": "consumer_cyclical",
    "운수장비": "industrials",
    "전기전자": "technology",
    "유통업": "consumer_cyclical",
    "건설업": "industrials",
    "금융업": "financials",
    "은행": "financials",
    "증권": "financials",
    "보험": "financials",
    "음식료품": "consumer_defensive",
    "섬유의복": "consumer_cyclical",
    "종이목재": "materials",
    "전기가스업": "utilities",
    "서비스업": "communication",
}

# 테마 ETF 티커 (섹터 대용)
THEME_ETFS = {
    "semiconductor": ["091160", "091170", "395170"],  # KODEX 반도체
    "battery": ["305720", "373540"],                   # KODEX 2차전지
    "bio": ["244580", "261110"],                       # KODEX 바이오
    "ai": ["463050", "466920"],                        # AI 관련 ETF
}


def get_trading_date(offset: int = 0) -> str:
    """
    최근 거래일 반환 (YYYYMMDD 형식)

    Args:
        offset: 0=오늘/가장 최근, -1=전일, ...
    """
    today = datetime.now()

    # 최근 10일 내에서 거래일 찾기
    for i in range(10):
        check_date = today - timedelta(days=i)
        date_str = check_date.strftime("%Y%m%d")

        try:
            # KOSPI 데이터가 있으면 거래일
            df = krx.get_market_ohlcv(date_str, market="KOSPI")
            if not df.empty:
                if offset == 0:
                    return date_str
                offset += 1
        except Exception:
            continue

    # 못 찾으면 오늘 날짜 반환
    return today.strftime("%Y%m%d")


def get_market_summary(market_type: str = "KOSPI") -> MarketSummary:
    """
    시장 요약 정보 조회

    Args:
        market_type: "KOSPI" 또는 "KOSDAQ"
    """
    date_str = get_trading_date()

    # OHLCV 데이터 조회
    df = krx.get_market_ohlcv(date_str, market=market_type)

    # 등락 통계
    advancing = len(df[df["등락률"] > 0])
    declining = len(df[df["등락률"] < 0])
    unchanged = len(df[df["등락률"] == 0])

    # 지수 정보 (간접 계산 또는 별도 API)
    # pykrx는 지수 직접 조회가 제한적이므로 대표 종목으로 대체
    index_name = market_type

    return MarketSummary(
        market=Market.KR,
        date=datetime.strptime(date_str, "%Y%m%d").date(),
        index_name=index_name,
        index_value=0,  # TODO: 지수 API 연동
        index_change=0,
        index_change_percent=0,
        advancing=advancing,
        declining=declining,
        unchanged=unchanged,
        total_volume=int(df["거래량"].sum()) if "거래량" in df.columns else None,
        total_value=float(df["거래대금"].sum()) if "거래대금" in df.columns else None,
    )


def get_top_by_market_cap(
    market_type: str = "KOSPI",
    limit: int = 10
) -> list[StockInfo]:
    """
    시가총액 상위 종목 조회

    Args:
        market_type: "KOSPI" 또는 "KOSDAQ" 또는 "ALL"
        limit: 조회 개수
    """
    date_str = get_trading_date()

    results = []
    markets = ["KOSPI", "KOSDAQ"] if market_type == "ALL" else [market_type]

    for mkt in markets:
        # 시가총액 데이터 조회
        df_cap = krx.get_market_cap(date_str, market=mkt)
        # OHLCV 데이터 조회 (가격, 등락률)
        df_ohlcv = krx.get_market_ohlcv(date_str, market=mkt)

        # 병합 (중복 컬럼 제거: df_cap에 이미 종가, 거래량 있을 수 있음)
        ohlcv_cols = [c for c in ["등락률"] if c in df_ohlcv.columns and c not in df_cap.columns]
        if ohlcv_cols:
            df = df_cap.join(df_ohlcv[ohlcv_cols], how="left")
        else:
            df = df_cap.copy()
        df = df.sort_values("시가총액", ascending=False)

        for ticker in df.head(limit if market_type != "ALL" else limit * 2).index:
            try:
                name = krx.get_market_ticker_name(ticker)
                row = df.loc[ticker]

                results.append(StockInfo(
                    symbol=ticker,
                    name=name,
                    market=Market.KR,
                    price=float(row.get("종가", 0)),
                    change_percent=float(row.get("등락률", 0)),
                    volume=int(row.get("거래량", 0)),
                    market_cap=float(row.get("시가총액", 0)),
                    fetched_at=datetime.strptime(date_str, "%Y%m%d").date(),
                ))
            except Exception:
                continue

    # 시가총액 기준 정렬 후 상위 N개
    results.sort(key=lambda x: x.market_cap or 0, reverse=True)
    return results[:limit]


def get_top_movers(
    market_type: str = "KOSPI",
    limit: int = 10
) -> TopMovers:
    """
    급등/급락/거래량 상위 종목 조회

    Args:
        market_type: "KOSPI" 또는 "KOSDAQ"
        limit: 각 카테고리별 조회 개수
    """
    date_str = get_trading_date()

    # OHLCV 데이터 조회 (이미 시가총액 포함됨)
    df = krx.get_market_ohlcv(date_str, market=market_type)

    def to_stock_info(ticker: str, row: pd.Series) -> StockInfo:
        try:
            name = krx.get_market_ticker_name(ticker)
        except Exception:
            name = ticker

        return StockInfo(
            symbol=ticker,
            name=name,
            market=Market.KR,
            price=float(row.get("종가", 0)),
            change_percent=float(row.get("등락률", 0)),
            volume=int(row.get("거래량", 0)),
            market_cap=float(row.get("시가총액", 0)) if "시가총액" in row else None,
            fetched_at=datetime.strptime(date_str, "%Y%m%d").date(),
        )

    # 상승률 TOP
    gainers_df = df.sort_values("등락률", ascending=False).head(limit)
    gainers = [to_stock_info(t, gainers_df.loc[t]) for t in gainers_df.index]

    # 하락률 TOP
    losers_df = df.sort_values("등락률", ascending=True).head(limit)
    losers = [to_stock_info(t, losers_df.loc[t]) for t in losers_df.index]

    # 거래량 TOP
    active_df = df.sort_values("거래량", ascending=False).head(limit)
    most_active = [to_stock_info(t, active_df.loc[t]) for t in active_df.index]

    return TopMovers(
        gainers=gainers,
        losers=losers,
        most_active=most_active,
        market=Market.KR,
        date=datetime.strptime(date_str, "%Y%m%d").date(),
    )


def get_sector_top(
    sector: str,
    limit: int = 10
) -> list[StockInfo]:
    """
    섹터별 상위 종목 조회

    Args:
        sector: 섹터 키 (semiconductor, bio, battery 등)
        limit: 조회 개수

    Note:
        pykrx는 섹터 직접 조회가 제한적이므로,
        업종별 시가총액 조회 또는 테마 ETF 구성종목 활용
    """
    date_str = get_trading_date()
    results = []

    # 테마 ETF가 있으면 구성종목 활용
    if sector in THEME_ETFS:
        for etf_ticker in THEME_ETFS[sector]:
            try:
                # ETF 구성종목 조회
                df = krx.get_etf_portfolio_deposit_file(etf_ticker, date_str)
                if df is not None and not df.empty:
                    # 상위 종목 추출
                    for ticker in df.head(limit).index:
                        try:
                            name = krx.get_market_ticker_name(ticker)
                            # 시가총액 조회
                            cap_df = krx.get_market_cap(date_str, market="ALL")
                            ohlcv_df = krx.get_market_ohlcv(date_str, market="ALL")

                            if ticker in cap_df.index:
                                results.append(StockInfo(
                                    symbol=ticker,
                                    name=name,
                                    market=Market.KR,
                                    sector=sector,
                                    price=float(ohlcv_df.loc[ticker, "종가"]) if ticker in ohlcv_df.index else None,
                                    change_percent=float(ohlcv_df.loc[ticker, "등락률"]) if ticker in ohlcv_df.index else None,
                                    market_cap=float(cap_df.loc[ticker, "시가총액"]),
                                    fetched_at=datetime.strptime(date_str, "%Y%m%d").date(),
                                ))
                        except Exception:
                            continue
            except Exception:
                continue

    # 업종별 조회 시도
    if not results:
        try:
            # KOSPI 업종별 시가총액
            sectors_list = krx.get_index_ticker_list(date_str, market="KOSPI")
            # 섹터 매칭되는 업종 찾기
            for kr_sector, std_sector in KR_SECTOR_MAP.items():
                if std_sector == sector:
                    # 해당 업종 종목 조회 시도
                    pass  # pykrx 업종별 조회 제한
        except Exception:
            pass

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
    date_str = get_trading_date()
    results = []

    # 전체 티커 목록
    for market in ["KOSPI", "KOSDAQ"]:
        tickers = krx.get_market_ticker_list(date_str, market=market)

        for ticker in tickers:
            try:
                name = krx.get_market_ticker_name(ticker)
                if query.lower() in name.lower() or query in ticker:
                    # 시가총액, 가격 조회
                    cap_df = krx.get_market_cap(date_str, market=market)
                    ohlcv_df = krx.get_market_ohlcv(date_str, market=market)

                    if ticker in cap_df.index:
                        results.append(StockInfo(
                            symbol=ticker,
                            name=name,
                            market=Market.KR,
                            price=float(ohlcv_df.loc[ticker, "종가"]) if ticker in ohlcv_df.index else None,
                            change_percent=float(ohlcv_df.loc[ticker, "등락률"]) if ticker in ohlcv_df.index else None,
                            volume=int(ohlcv_df.loc[ticker, "거래량"]) if ticker in ohlcv_df.index else None,
                            market_cap=float(cap_df.loc[ticker, "시가총액"]),
                            fetched_at=datetime.strptime(date_str, "%Y%m%d").date(),
                        ))

                        if len(results) >= limit:
                            return results
            except Exception:
                continue

    return results

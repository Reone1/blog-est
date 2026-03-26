"""
변동성 분석 모듈 (FinanceDataReader + Naver Finance API 기반)

기능:
- 표준편차 기반 변동성 분석
- 볼린저 밴드 계산
- 표준편차 매매 시그널 생성
- 시장 심리 지표 (Market Breadth)
"""

from datetime import date, datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd

from .models import (
    Market,
    MarketBreadth,
    StdSignal,
    VolatilityData,
    VolatilitySignal,
)


def get_stock_history(ticker: str, days: int = 60) -> pd.DataFrame:
    """
    종목의 과거 가격 데이터 조회 (FinanceDataReader 사용)

    Args:
        ticker: 종목코드
        days: 조회 기간 (거래일 기준)

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume
    """
    import FinanceDataReader as fdr

    today = datetime.now()
    # 여유 있게 조회 (주말/공휴일 고려)
    start_date = (today - timedelta(days=days * 2)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    try:
        df = fdr.DataReader(ticker, start_date, end_date)
        return df.tail(days) if len(df) > days else df
    except Exception:
        return pd.DataFrame()


def _get_stock_name(ticker: str) -> str:
    """Naver API로 종목명 조회"""
    import requests

    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})
        r = session.get(
            f"https://m.stock.naver.com/api/stock/{ticker}/basic",
            timeout=5,
        )
        if r.status_code == 200:
            return r.json().get("stockName", ticker)
    except Exception:
        pass
    return ticker


def calculate_volatility(ticker: str, name: str = "") -> Optional[VolatilityData]:
    """
    단일 종목 변동성 분석

    Args:
        ticker: 종목코드
        name: 종목명 (없으면 조회)

    Returns:
        VolatilityData 또는 None (데이터 부족 시)
    """
    # 70일 데이터 조회 (20/60일 MA 계산용)
    df = get_stock_history(ticker, days=70)

    if len(df) < 20:
        return None

    # 종목명 조회
    if not name:
        name = _get_stock_name(ticker)

    # 종가 시리즈
    close = df["Close"]
    current_price = float(close.iloc[-1])

    # 이동평균 계산
    ma_20 = float(close.rolling(window=20).mean().iloc[-1])
    ma_60 = (
        float(close.rolling(window=60).mean().iloc[-1])
        if len(close) >= 60
        else ma_20
    )

    # 표준편차 계산
    std_20d = float(close.rolling(window=20).std().iloc[-1])
    std_60d = (
        float(close.rolling(window=60).std().iloc[-1])
        if len(close) >= 60
        else std_20d
    )

    # 볼린저 밴드
    bb_upper = ma_20 + (2 * std_20d)
    bb_lower = ma_20 - (2 * std_20d)

    # 밴드 내 위치 (0=하단, 0.5=중간, 1=상단)
    if bb_upper != bb_lower:
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
    else:
        bb_position = 0.5

    # Z-score
    zscore = (current_price - ma_20) / std_20d if std_20d > 0 else 0.0

    # 시그널 판단
    if zscore <= -2:
        signal = VolatilitySignal.OVERSOLD
    elif zscore >= 2:
        signal = VolatilitySignal.OVERBOUGHT
    else:
        signal = VolatilitySignal.NEUTRAL

    # 당일 등락률
    if len(close) >= 2:
        prev_close = float(close.iloc[-2])
        change_percent = ((current_price - prev_close) / prev_close) * 100
    else:
        change_percent = 0.0

    return VolatilityData(
        symbol=ticker,
        name=name,
        market=Market.KR,
        price=current_price,
        change_percent=change_percent,
        ma_20=ma_20,
        ma_60=ma_60,
        std_20d=std_20d,
        std_60d=std_60d,
        bb_upper=bb_upper,
        bb_lower=bb_lower,
        bb_position=bb_position,
        zscore=zscore,
        signal=signal,
        fetched_at=datetime.now().date(),
    )


def get_std_signals(
    market_type: str = "KOSPI",
    min_market_cap: float = 1_000_000_000_000,  # 1조원 이상
    limit: int = 20,
) -> list[StdSignal]:
    """
    표준편차 매매 시그널 스캔

    시가총액 상위 종목 중 과매도/과매수 시그널 탐지

    Args:
        market_type: "KOSPI" 또는 "KOSDAQ"
        min_market_cap: 최소 시가총액 (원)
        limit: 각 시그널 유형별 최대 개수

    Returns:
        StdSignal 리스트 (과매도 → 과매수 순)
    """
    from .kr_market import get_top_by_market_cap

    # 시총 상위 종목 조회 (Naver API)
    top_stocks = get_top_by_market_cap(market_type, limit=50)

    # 시가총액 필터링
    filtered = [
        s for s in top_stocks
        if (s.market_cap or 0) >= min_market_cap
    ]

    oversold = []
    overbought = []

    for stock in filtered:
        vol_data = calculate_volatility(stock.symbol, stock.name)
        if vol_data is None:
            continue

        if vol_data.signal == VolatilitySignal.OVERSOLD:
            strength = min(abs(vol_data.zscore) / 3, 1.0)
            oversold.append(StdSignal(
                stock=vol_data,
                signal_type="buy",
                signal_strength=strength,
                description=f"Z-score {vol_data.zscore:.2f}, 볼린저 하단 이탈",
            ))
        elif vol_data.signal == VolatilitySignal.OVERBOUGHT:
            strength = min(abs(vol_data.zscore) / 3, 1.0)
            overbought.append(StdSignal(
                stock=vol_data,
                signal_type="sell",
                signal_strength=strength,
                description=f"Z-score {vol_data.zscore:.2f}, 볼린저 상단 이탈",
            ))

    # 강도순 정렬
    oversold.sort(key=lambda x: x.signal_strength, reverse=True)
    overbought.sort(key=lambda x: x.signal_strength, reverse=True)

    # 과매도(매수) 시그널 먼저, 그 다음 과매수(매도) 시그널
    signals = []
    signals.extend(oversold[:limit])
    signals.extend(overbought[:limit])

    return signals


def get_market_breadth(market_type: str = "KOSPI") -> Optional[MarketBreadth]:
    """
    시장 심리 지표 계산

    Args:
        market_type: "KOSPI" 또는 "KOSDAQ"

    Returns:
        MarketBreadth 또는 None
    """
    from .kr_market import get_market_summary, get_top_by_market_cap

    # 시장 요약에서 상승/하락 종목 수 가져오기
    try:
        summary = get_market_summary(market_type)
    except Exception:
        return None

    advance_count = summary.advancing
    decline_count = summary.declining

    # 등락 비율
    if decline_count > 0:
        advance_decline_ratio = advance_count / decline_count
    else:
        advance_decline_ratio = float("inf") if advance_count > 0 else 1.0

    # 변동성 분포 (시가총액 상위 30개로 축소 - 성능)
    oversold_count = 0
    overbought_count = 0

    try:
        top_stocks = get_top_by_market_cap(market_type, limit=30)
        for stock in top_stocks:
            vol_data = calculate_volatility(stock.symbol, stock.name)
            if vol_data:
                if vol_data.signal == VolatilitySignal.OVERSOLD:
                    oversold_count += 1
                elif vol_data.signal == VolatilitySignal.OVERBOUGHT:
                    overbought_count += 1
    except Exception:
        pass

    return MarketBreadth(
        market=Market.KR,
        date=date.today(),
        advance_count=advance_count,
        decline_count=decline_count,
        advance_decline_ratio=advance_decline_ratio,
        new_highs_52w=0,
        new_lows_52w=0,
        volume_breadth=0.5,
        oversold_count=oversold_count,
        overbought_count=overbought_count,
    )


def get_volatility_ranking(
    market_type: str = "KOSPI",
    sort_by: str = "zscore",
    ascending: bool = True,
    limit: int = 20,
) -> list[VolatilityData]:
    """
    변동성 기준 종목 순위

    Args:
        market_type: "KOSPI" 또는 "KOSDAQ"
        sort_by: 정렬 기준 ("zscore" | "std_20d" | "bb_position")
        ascending: 오름차순 여부
        limit: 조회 개수

    Returns:
        VolatilityData 리스트
    """
    from .kr_market import get_top_by_market_cap

    # 시총 상위 종목
    top_stocks = get_top_by_market_cap(market_type, limit=50)

    results = []
    for stock in top_stocks:
        vol_data = calculate_volatility(stock.symbol, stock.name)
        if vol_data:
            results.append(vol_data)

    # 정렬
    if sort_by == "zscore":
        results.sort(key=lambda x: x.zscore, reverse=not ascending)
    elif sort_by == "std_20d":
        results.sort(key=lambda x: x.std_20d, reverse=not ascending)
    elif sort_by == "bb_position":
        results.sort(key=lambda x: x.bb_position, reverse=not ascending)

    return results[:limit]

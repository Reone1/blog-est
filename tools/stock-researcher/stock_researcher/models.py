"""
데이터 모델 정의
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class Market(Enum):
    """시장 구분"""
    US = "us"      # 미국
    KR = "kr"      # 한국


class Sector(Enum):
    """섹터 구분 (미국 기준, 한국은 매핑)"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCIALS = "financials"
    CONSUMER_CYCLICAL = "consumer_cyclical"
    CONSUMER_DEFENSIVE = "consumer_defensive"
    INDUSTRIALS = "industrials"
    ENERGY = "energy"
    UTILITIES = "utilities"
    REAL_ESTATE = "real_estate"
    MATERIALS = "materials"
    COMMUNICATION = "communication"
    # 테마 섹터
    SEMICONDUCTOR = "semiconductor"
    AI = "ai"
    EV = "ev"
    BATTERY = "battery"
    BIO = "bio"


@dataclass
class StockInfo:
    """종목 정보"""
    symbol: str                    # 티커/종목코드
    name: str                      # 종목명
    market: Market                 # 시장
    sector: Optional[str] = None   # 섹터
    industry: Optional[str] = None # 산업

    # 가격 정보
    price: Optional[float] = None           # 현재가
    change_percent: Optional[float] = None  # 등락률 (%)
    volume: Optional[int] = None            # 거래량

    # 시가총액
    market_cap: Optional[float] = None      # 시가총액

    # 추가 정보
    pe_ratio: Optional[float] = None        # PER
    pb_ratio: Optional[float] = None        # PBR
    dividend_yield: Optional[float] = None  # 배당수익률

    # 메타
    fetched_at: Optional[date] = None       # 조회 일시


@dataclass
class MarketSummary:
    """시장 요약 정보"""
    market: Market
    date: date

    # 지수 정보
    index_name: str                # 지수명 (KOSPI, S&P500 등)
    index_value: float             # 지수
    index_change: float            # 등락
    index_change_percent: float    # 등락률

    # 시장 통계
    advancing: int = 0             # 상승 종목 수
    declining: int = 0             # 하락 종목 수
    unchanged: int = 0             # 보합 종목 수

    total_volume: Optional[int] = None      # 총 거래량
    total_value: Optional[float] = None     # 총 거래대금


@dataclass
class TopMovers:
    """급등/급락 종목"""
    gainers: list[StockInfo]       # 상승 TOP
    losers: list[StockInfo]        # 하락 TOP
    most_active: list[StockInfo]   # 거래량 TOP

    market: Market
    date: date


class VolatilitySignal(Enum):
    """변동성 시그널"""
    OVERSOLD = "oversold"           # 과매도 (하단 밴드 이탈)
    NEUTRAL = "neutral"             # 중립
    OVERBOUGHT = "overbought"       # 과매수 (상단 밴드 이탈)


@dataclass
class VolatilityData:
    """종목 변동성 분석 데이터"""
    symbol: str                     # 티커/종목코드
    name: str                       # 종목명
    market: Market                  # 시장

    # 현재가 정보
    price: float                    # 현재가
    change_percent: float           # 당일 등락률

    # 이동평균
    ma_20: float                    # 20일 이동평균
    ma_60: float                    # 60일 이동평균

    # 표준편차
    std_20d: float                  # 20일 표준편차
    std_60d: float                  # 60일 표준편차

    # 볼린저 밴드
    bb_upper: float                 # 상단 밴드 (MA20 + 2σ)
    bb_lower: float                 # 하단 밴드 (MA20 - 2σ)
    bb_position: float              # 밴드 내 위치 (0=하단, 0.5=중간, 1=상단)

    # Z-score (현재가가 평균에서 몇 표준편차 떨어져 있는지)
    zscore: float

    # 시그널
    signal: VolatilitySignal

    # 메타
    fetched_at: Optional[date] = None


@dataclass
class StdSignal:
    """표준편차 매매 시그널"""
    stock: VolatilityData           # 종목 변동성 데이터
    signal_type: str                # "buy" | "sell" | "watch"
    signal_strength: float          # 시그널 강도 (0-1)
    description: str                # 시그널 설명


@dataclass
class MarketBreadth:
    """시장 심리 지표"""
    market: Market
    date: date

    # 등락 비율
    advance_count: int              # 상승 종목 수
    decline_count: int              # 하락 종목 수
    advance_decline_ratio: float    # 상승/하락 비율

    # 신고가/신저가
    new_highs_52w: int              # 52주 신고가 종목 수
    new_lows_52w: int               # 52주 신저가 종목 수

    # 거래량
    volume_breadth: float           # 상승종목 거래량 / 전체 거래량

    # 변동성 분포
    oversold_count: int             # 과매도 종목 수
    overbought_count: int           # 과매수 종목 수

"""
MCP (Model Context Protocol) 서버

Claude Desktop 또는 다른 MCP 클라이언트에서 사용 가능한 도구로 노출

설치:
    pip install stock-researcher[mcp]

Claude Desktop 설정 (claude_desktop_config.json):
    {
      "mcpServers": {
        "stock-researcher": {
          "command": "python",
          "args": ["-m", "stock_researcher.mcp_server"]
        }
      }
    }
"""

import json
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP 패키지가 설치되지 않았습니다. pip install stock-researcher[mcp] 실행")

from . import kr_market, us_market
from .models import StockInfo


def stock_to_dict(stock: StockInfo) -> dict[str, Any]:
    """StockInfo를 딕셔너리로 변환"""
    return {
        "symbol": stock.symbol,
        "name": stock.name,
        "market": stock.market.value,
        "sector": stock.sector,
        "price": stock.price,
        "change_percent": stock.change_percent,
        "volume": stock.volume,
        "market_cap": stock.market_cap,
        "pe_ratio": stock.pe_ratio,
        "fetched_at": str(stock.fetched_at) if stock.fetched_at else None,
    }


if MCP_AVAILABLE:
    server = Server("stock-researcher")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """사용 가능한 도구 목록"""
        return [
            Tool(
                name="stock_top_market_cap",
                description="시가총액 상위 종목 조회. 미국(us) 또는 한국(kr) 시장의 TOP N 종목 반환",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "market": {
                            "type": "string",
                            "enum": ["us", "kr"],
                            "description": "시장 선택 (us: 미국, kr: 한국)",
                            "default": "us"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "조회할 종목 수",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50
                        }
                    }
                }
            ),
            Tool(
                name="stock_top_movers",
                description="급등/급락/거래량 상위 종목 조회. 당일 가장 많이 오르거나 내린 종목, 거래량 상위 종목 반환",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "market": {
                            "type": "string",
                            "enum": ["us", "kr"],
                            "description": "시장 선택",
                            "default": "us"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["gainers", "losers", "most_active", "all"],
                            "description": "카테고리 (gainers: 상승, losers: 하락, most_active: 거래량, all: 전체)",
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "각 카테고리별 조회할 종목 수",
                            "default": 10
                        }
                    }
                }
            ),
            Tool(
                name="stock_sector_top",
                description="섹터별 상위 종목 조회. technology, semiconductor, ai, bio, ev, battery 등 섹터의 대표 종목 반환",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sector": {
                            "type": "string",
                            "description": "섹터 키 (technology, semiconductor, ai, bio, healthcare, financials, ev, battery 등)",
                        },
                        "market": {
                            "type": "string",
                            "enum": ["us", "kr"],
                            "description": "시장 선택",
                            "default": "us"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "조회할 종목 수",
                            "default": 10
                        }
                    },
                    "required": ["sector"]
                }
            ),
            Tool(
                name="stock_search",
                description="종목 검색. 티커 심볼이나 종목명으로 검색",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "검색어 (티커 또는 종목명)"
                        },
                        "market": {
                            "type": "string",
                            "enum": ["us", "kr", "all"],
                            "description": "시장 선택 (all: 전체)",
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "조회할 종목 수",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="stock_market_summary",
                description="시장 요약 정보 조회. 지수, 상승/하락 종목 수 등",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "market": {
                            "type": "string",
                            "enum": ["us", "kr"],
                            "description": "시장 선택",
                            "default": "us"
                        }
                    }
                }
            ),
            Tool(
                name="stock_available_sectors",
                description="사용 가능한 섹터 목록 조회",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """도구 실행"""

        if name == "stock_top_market_cap":
            market = arguments.get("market", "us")
            limit = arguments.get("limit", 10)

            if market == "us":
                stocks = us_market.get_top_by_market_cap(limit=limit)
            else:
                stocks = kr_market.get_top_by_market_cap(market_type="KOSPI", limit=limit)

            result = {
                "market": market,
                "count": len(stocks),
                "stocks": [stock_to_dict(s) for s in stocks]
            }

        elif name == "stock_top_movers":
            market = arguments.get("market", "us")
            category = arguments.get("category", "all")
            limit = arguments.get("limit", 10)

            if market == "us":
                movers = us_market.get_top_movers(limit=limit)
            else:
                movers = kr_market.get_top_movers(market_type="KOSPI", limit=limit)

            result = {"market": market, "date": str(movers.date)}

            if category == "all":
                result["gainers"] = [stock_to_dict(s) for s in movers.gainers]
                result["losers"] = [stock_to_dict(s) for s in movers.losers]
                result["most_active"] = [stock_to_dict(s) for s in movers.most_active]
            elif category == "gainers":
                result["gainers"] = [stock_to_dict(s) for s in movers.gainers]
            elif category == "losers":
                result["losers"] = [stock_to_dict(s) for s in movers.losers]
            elif category == "most_active":
                result["most_active"] = [stock_to_dict(s) for s in movers.most_active]

        elif name == "stock_sector_top":
            sector = arguments.get("sector")
            market = arguments.get("market", "us")
            limit = arguments.get("limit", 10)

            if market == "us":
                stocks = us_market.get_sector_top(sector, limit=limit)
            else:
                stocks = kr_market.get_sector_top(sector, limit=limit)

            result = {
                "sector": sector,
                "market": market,
                "count": len(stocks),
                "stocks": [stock_to_dict(s) for s in stocks]
            }

        elif name == "stock_search":
            query = arguments.get("query")
            market = arguments.get("market", "all")
            limit = arguments.get("limit", 10)

            stocks = []
            if market in ["us", "all"]:
                stocks.extend(us_market.search_stocks(query, limit=limit))
            if market in ["kr", "all"]:
                stocks.extend(kr_market.search_stocks(query, limit=limit))

            result = {
                "query": query,
                "count": len(stocks),
                "stocks": [stock_to_dict(s) for s in stocks[:limit]]
            }

        elif name == "stock_market_summary":
            market = arguments.get("market", "us")

            if market == "us":
                sp500 = us_market.get_market_summary("SP500")
                nasdaq = us_market.get_market_summary("NASDAQ")
                result = {
                    "market": "us",
                    "indices": [
                        {
                            "name": "S&P 500",
                            "value": sp500.index_value,
                            "change": sp500.index_change,
                            "change_percent": sp500.index_change_percent
                        },
                        {
                            "name": "NASDAQ",
                            "value": nasdaq.index_value,
                            "change": nasdaq.index_change,
                            "change_percent": nasdaq.index_change_percent
                        }
                    ]
                }
            else:
                kospi = kr_market.get_market_summary("KOSPI")
                kosdaq = kr_market.get_market_summary("KOSDAQ")
                result = {
                    "market": "kr",
                    "indices": [
                        {
                            "name": "KOSPI",
                            "advancing": kospi.advancing,
                            "declining": kospi.declining,
                            "unchanged": kospi.unchanged,
                            "total_volume": kospi.total_volume,
                            "total_value": kospi.total_value
                        },
                        {
                            "name": "KOSDAQ",
                            "advancing": kosdaq.advancing,
                            "declining": kosdaq.declining,
                            "unchanged": kosdaq.unchanged,
                            "total_volume": kosdaq.total_volume,
                            "total_value": kosdaq.total_value
                        }
                    ]
                }

        elif name == "stock_available_sectors":
            result = {
                "sectors": [
                    {"key": "technology", "name": "기술/IT", "us": True, "kr": False},
                    {"key": "semiconductor", "name": "반도체", "us": True, "kr": True},
                    {"key": "ai", "name": "인공지능", "us": True, "kr": False},
                    {"key": "healthcare", "name": "헬스케어", "us": True, "kr": False},
                    {"key": "bio", "name": "바이오", "us": True, "kr": True},
                    {"key": "financials", "name": "금융", "us": True, "kr": False},
                    {"key": "consumer_cyclical", "name": "경기소비재", "us": True, "kr": False},
                    {"key": "consumer_defensive", "name": "필수소비재", "us": True, "kr": False},
                    {"key": "energy", "name": "에너지", "us": True, "kr": False},
                    {"key": "industrials", "name": "산업재", "us": True, "kr": False},
                    {"key": "communication", "name": "커뮤니케이션", "us": True, "kr": False},
                    {"key": "utilities", "name": "유틸리티", "us": True, "kr": False},
                    {"key": "real_estate", "name": "부동산", "us": True, "kr": False},
                    {"key": "materials", "name": "소재", "us": True, "kr": False},
                    {"key": "ev", "name": "전기차", "us": True, "kr": False},
                    {"key": "battery", "name": "배터리/2차전지", "us": True, "kr": True},
                ]
            }

        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


    async def main():
        """MCP 서버 실행"""
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())


    if __name__ == "__main__":
        import asyncio
        asyncio.run(main())

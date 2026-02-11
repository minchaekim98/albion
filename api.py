"""Albion Online Data Project API 호출 모듈"""

import aiohttp
from config import API_BASE_URL, CITIES


async def fetch_prices(session: aiohttp.ClientSession, item_id: str, locations: list[str] | None = None) -> list[dict]:
    """아이템의 현재 시세를 조회한다.

    Args:
        session: aiohttp 클라이언트 세션
        item_id: 아이템 ID (예: T4_BAG)
        locations: 도시 목록 (None이면 전 도시)

    Returns:
        도시별 가격 정보 리스트
    """
    if locations is None:
        locations = CITIES
    locations_param = ",".join(locations)
    url = f"{API_BASE_URL}/api/v2/stats/prices/{item_id}?locations={locations_param}"
    async with session.get(url) as resp:
        if resp.status == 200:
            return await resp.json()
        return []


async def fetch_gold(session: aiohttp.ClientSession, count: int = 24) -> list[dict]:
    """골드 시세를 조회한다.

    Args:
        session: aiohttp 클라이언트 세션
        count: 조회할 데이터 포인트 수

    Returns:
        골드 시세 리스트 (timestamp, price)
    """
    url = f"{API_BASE_URL}/api/v2/stats/gold?count={count}"
    async with session.get(url) as resp:
        if resp.status == 200:
            return await resp.json()
        return []


async def fetch_history(
    session: aiohttp.ClientSession,
    item_id: str,
    location: str,
    time_scale: int = 6,
) -> list[dict]:
    """아이템의 가격 히스토리를 조회한다.

    Args:
        session: aiohttp 클라이언트 세션
        item_id: 아이템 ID
        location: 도시명
        time_scale: 시간 단위 (6 = 일별)

    Returns:
        히스토리 데이터 리스트
    """
    url = (
        f"{API_BASE_URL}/api/v2/stats/history/{item_id}"
        f"?locations={location}&time-scale={time_scale}"
    )
    async with session.get(url) as resp:
        if resp.status == 200:
            return await resp.json()
        return []

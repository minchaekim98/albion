"""아이템 검색과 이름/ID 변환 모듈.

item_db.json (build_item_db.py로 생성)에서 아이템 정보를 불러온다.
"""

import json
import os

_DB_PATH = os.path.join(os.path.dirname(__file__), "item_db.json")

ITEM_DB: dict[str, dict[str, str]] = {}
KO_TO_ID: dict[str, str] = {}
ID_TO_NAME: dict[str, str] = {}

if os.path.exists(_DB_PATH):
    with open(_DB_PATH, "r", encoding="utf-8") as f:
        ITEM_DB = json.load(f)

    for item_id, names in ITEM_DB.items():
        ko = names.get("ko", "")
        if ko:
            KO_TO_ID[ko] = item_id
            ID_TO_NAME[item_id] = ko

ALIASES: dict[str, str] = {
    "가방": "T4_BAG",
    "말": "T3_MOUNT_HORSE",
    "소": "T3_MOUNT_OX",
    "갑옷말": "T5_MOUNT_ARMORED_HORSE",
    "갑옷 말": "T5_MOUNT_ARMORED_HORSE",
    "체력포션": "T4_POTION_HEALTH",
    "에너지포션": "T4_POTION_ENERGY",
    "집중포션": "T4_POTION_FOCUS",
    "헤르틱망토": "T4_CAPEITEM_HERETIC",
    "악마망토": "T4_CAPEITEM_DEMON",
    "언데드망토": "T4_CAPEITEM_UNDEAD",
    "키퍼망토": "T4_CAPEITEM_KEEPER",
    "모르가나망토": "T4_CAPEITEM_MORGANA",
}


def _normalize(text: str) -> str:
    return text.lower().replace(" ", "")


def resolve_item(query: str) -> str | None:
    """사용자 입력을 아이템 ID로 변환한다.

    우선순위:
    1. 아이템 ID 형식이면 그대로 반환 (T숫자_...)
    2. 별칭 매핑 정확히 일치
    3. 한글 DB 정확히 일치
    4. 한글 DB 부분 일치 (결과가 1개일 때)
    """
    q = query.strip()
    q_norm = _normalize(q)

    upper = q.upper()
    if upper.startswith("T") and "_" in upper and upper in ITEM_DB:
        return upper
    if upper.startswith("T") and "_" in upper:
        return upper

    if q in ALIASES:
        return ALIASES[q]
    for alias, item_id in ALIASES.items():
        if _normalize(alias) == q_norm:
            return item_id

    for ko, item_id in KO_TO_ID.items():
        if _normalize(ko) == q_norm:
            return item_id

    partial = [(ko, iid) for ko, iid in KO_TO_ID.items() if q_norm in _normalize(ko)]
    if len(partial) == 1:
        return partial[0][1]

    return None


def search_items(keyword: str, limit: int = 20) -> list[tuple[str, str]]:
    """키워드로 아이템을 검색한다."""
    kw = _normalize(keyword)
    results: list[tuple[str, str]] = []
    seen: set[str] = set()

    for alias, item_id in ALIASES.items():
        if kw in _normalize(alias) and item_id not in seen:
            ko = ID_TO_NAME.get(item_id, alias)
            results.append((f"{ko} ({alias})", item_id))
            seen.add(item_id)

    for item_id, names in ITEM_DB.items():
        if len(results) >= limit:
            break
        if item_id in seen:
            continue
        ko = names.get("ko", "")
        en = names.get("en", "")
        if kw in _normalize(ko) or kw in _normalize(en) or kw in item_id.lower():
            display = ko if ko else en
            results.append((display, item_id))
            seen.add(item_id)

    return results[:limit]

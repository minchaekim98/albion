import sys
sys.stdout.reconfigure(encoding="utf-8")

from items import search_items, resolve_item, ITEM_DB

print(f"DB 로드: {len(ITEM_DB)}개 아이템")
print()

print("=== 검색: 활 ===")
for name, iid in search_items("활"):
    print(f"  {name} -> {iid}")

print()
print("=== 검색: 대검 ===")
for name, iid in search_items("대검"):
    print(f"  {name} -> {iid}")

print()
print("=== resolve 테스트 ===")
tests = ["숙련자의 가방", "가방", "숙련자의 활", "T4_BAG", "체포"]
for t in tests:
    result = resolve_item(t)
    print(f"  '{t}' -> {result}")

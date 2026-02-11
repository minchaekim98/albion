import sys
sys.stdout.reconfigure(encoding="utf-8")
from items import search_items, ITEM_DB

# crossbow 관련 아이템 찾기
print("=== 영문 CROSSBOW 검색 ===")
for name, iid in search_items("crossbow"):
    print(f"  {name} -> {iid}")

print()
print("=== 석궁 검색 ===")
for name, iid in search_items("석궁"):
    print(f"  {name} -> {iid}")

print()
print("=== 크로스 검색 ===")
for name, iid in search_items("크로스"):
    print(f"  {name} -> {iid}")

print()
print("=== DB에서 CROSSBOW ID로 직접 찾기 ===")
for iid, names in ITEM_DB.items():
    if "CROSSBOW" in iid and "DESC" not in iid:
        print(f"  {iid} -> {names.get('ko', '?')} / {names.get('en', '?')}")

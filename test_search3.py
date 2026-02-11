import sys
sys.stdout.reconfigure(encoding="utf-8")
from items import search_items, resolve_item

tests = ["크로스 보우", "크로스보우", "크로스  보우"]
for t in tests:
    results = search_items(t)
    print(f"검색: '{t}' -> {len(results)}개 결과")
    for name, iid in results[:3]:
        print(f"  {name} -> {iid}")
    print()

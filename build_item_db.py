"""로컬라이제이션 XML에서 한국어 아이템명 매핑을 추출하는 스크립트.

실행: python build_item_db.py
결과: item_db.json 파일 생성
"""

import json
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding="utf-8")

INPUT_FILE = "localization.xml"
OUTPUT_FILE = "item_db.json"


def main():
    print("로컬라이제이션 파일 파싱 중...")
    tree = ET.parse(INPUT_FILE)
    root = tree.getroot()

    # item_id -> {"ko": 한국어명, "en": 영문명}
    items = {}
    count = 0

    for tu in root.iter("tu"):
        tuid = tu.get("tuid", "")

        # @ITEMS_로 시작하고 _DESC로 끝나지 않는 것만 (이름만, 설명 제외)
        if not tuid.startswith("@ITEMS_"):
            continue
        if tuid.endswith("_DESC"):
            continue

        # 아이템 ID 추출: @ITEMS_T4_BAG -> T4_BAG
        item_id = tuid[7:]  # "@ITEMS_" 제거

        ko = ""
        en = ""
        for tuv in tu.findall("tuv"):
            lang = tuv.get("{http://www.w3.org/XML/1998/namespace}lang", "")
            seg = tuv.find("seg")
            if seg is not None and seg.text:
                if lang == "KO-KR":
                    ko = seg.text.strip()
                elif lang == "EN-US":
                    en = seg.text.strip()

        if ko and en:
            items[item_id] = {"ko": ko, "en": en}
            count += 1

    print(f"총 {count}개 아이템 추출 완료")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=None, separators=(",", ":"))

    size_mb = len(json.dumps(items, ensure_ascii=False)) / 1024 / 1024
    print(f"{OUTPUT_FILE} 저장 완료 ({size_mb:.1f}MB)")


if __name__ == "__main__":
    main()

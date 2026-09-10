"""한국관광 데이터랩에서 성지 소재 지자체 방문자 수를 뽑아
Firestore에 저장하는 스크립트.
"""

import requests
import json
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.firebase import get_db
from app.schemas.data import DataCreate
from app.services.data_service import create_data

# 성지 소재 지자체 (한국관광 데이터랩 지역 코드)
REGIONS = {
    "서울": "1000000",      # 명동성당
    "익산": "3320000",      # 나바위성지
    "대구": "2730000",      # 관덕정
}

API_URL = "https://datalab.visitkorea.or.kr/visualize/getTempleteData.do"
QID = "NAT_07_01_001"  # 지역별 월별 방문자 수


def fetch_region_data(region_name: str, region_code: str) -> list[dict]:
    """한 지자체의 월별 방문자 수 데이터를 조회한다."""
    params = {
        "natCd": "",
        "tarCd": region_code,
        "BASE_YM1": "201501",
        "BASE_YM2": "202608",
        "srchAreaDate": "1",
        "qid": QID,
    }

    try:
        response = requests.post(API_URL, data=params, timeout=10)
        response.raise_for_status()
        result = response.json()

        rows = []
        for item in result.get("list", []):
            try:
                month_str = item.get("BASE_DATE", "")  # "201501" 형식
                if len(month_str) == 6:
                    month = f"{month_str[:4]}-{month_str[4:]}"  # "2015-01"
                    value = float(item.get("PSON_NUM", 0))
                    rows.append({
                        "date": month,
                        "value": value,
                        "memo": region_name,
                    })
            except (ValueError, KeyError):
                continue

        return sorted(rows, key=lambda x: x["date"])
    except Exception as e:
        print(f"❌ {region_name} 조회 실패: {e}")
        return []


def main():
    print("🌍 한국관광 데이터랩에서 성지 방문자 수 조회 중...\n")

    all_data = []
    for region_name, region_code in REGIONS.items():
        print(f"⏳ {region_name} ({region_code}) 조회 중...")
        data = fetch_region_data(region_name, region_code)
        print(f"   → {len(data)}개 월별 데이터 확보")
        all_data.extend(data)

    print(f"\n📊 총 {len(all_data)}개 데이터포인트")

    if len(all_data) < 100:
        print("❌ 100개 이상 필요합니다.")
        return

    # Firestore에 저장
    print("\n💾 Firestore에 저장 중...")
    try:
        for row in all_data:
            create_data(DataCreate(**row))
        print(f"✅ {len(all_data)}개 저장 완료")
    except Exception as e:
        print(f"❌ 저장 실패: {e}")


if __name__ == "__main__":
    main()

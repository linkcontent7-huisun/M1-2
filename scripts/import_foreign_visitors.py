"""M1-2에 포함된 월별 방한 외래관광객 CSV를 Firestore에 적재한다.

실행 전에는 --dry-run으로 행 수와 기간을 확인한다. 실제 적재는 같은 날짜가
이미 있으면 건너뛰므로 재실행해도 중복 문서를 만들지 않는다.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.firebase import get_db
from app.schemas.data import DataCreate
from app.services.data_service import COLLECTION, create_data

CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "foreign_visitors_monthly.csv"
MEMO = "전국 월별 방한 외래관광객 수 (한국관광공사)"
MINIMUM_ROWS = 100


def load_rows(path: Path = CSV_PATH) -> list[DataCreate]:
    """CSV를 API의 data 스키마로 변환하고 기본 무결성을 확인한다."""
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        required_columns = {"base_ym", "foreign_visitors"}
        if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
            raise ValueError("CSV에는 base_ym, foreign_visitors 열이 필요합니다.")

        rows = []
        for item in reader:
            base_ym = item["base_ym"].strip()
            if len(base_ym) != 6 or not base_ym.isdigit():
                raise ValueError(f"잘못된 월 형식: {base_ym}")
            rows.append(
                DataCreate(
                    date=f"{base_ym[:4]}-{base_ym[4:]}",
                    value=float(item["foreign_visitors"]),
                    memo=MEMO,
                )
            )

    if len(rows) < MINIMUM_ROWS:
        raise ValueError(f"과제 요건인 {MINIMUM_ROWS}건에 못 미칩니다: {len(rows)}건")
    if len({row.date for row in rows}) != len(rows):
        raise ValueError("날짜가 중복되었습니다.")
    return rows


def import_rows(rows: list[DataCreate]) -> tuple[int, int]:
    """이미 저장된 날짜는 건너뛰고, 나머지 문서만 생성한다."""
    db = get_db()
    existing_dates = {
        document.to_dict().get("date")
        for document in db.collection(COLLECTION).stream()
    }
    created = 0
    skipped = 0
    for row in rows:
        if row.date in existing_dates:
            skipped += 1
            continue
        create_data(row)
        created += 1
    return created, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="월별 방한 외래관광객 데이터를 Firestore에 적재합니다.")
    parser.add_argument("--dry-run", action="store_true", help="Firestore에 쓰지 않고 CSV만 검증합니다.")
    args = parser.parse_args()

    rows = load_rows()
    print(f"CSV 검증 완료: {len(rows)}건, {rows[0].date} ~ {rows[-1].date}")
    if args.dry_run:
        return

    created, skipped = import_rows(rows)
    print(f"Firestore 적재 완료: 신규 {created}건, 기존 날짜 건너뜀 {skipped}건")


if __name__ == "__main__":
    main()

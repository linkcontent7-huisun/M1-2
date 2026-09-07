"""`data` 컬렉션 CRUD와 요약 통계 계산을 담당한다.

라우터는 HTTP 요청/응답만 다루고, Firestore를 직접 건드리거나 통계를
계산하는 로직은 전부 이 파일에 모아둔다 — 나중에 데이터 출처를 바꾸거나
(예: 실제 visitholykorea 스탬프 데이터) 통계 방식을 바꿀 때 라우터를
건드릴 필요가 없게 하려는 목적이다.
"""

from app.firebase import get_db
from app.schemas.data import DataCreate, DataMetrics, DataOut, DataSummary, DataUpdate

COLLECTION = "data"


def create_data(payload: DataCreate) -> DataOut:
    db = get_db()
    doc_ref = db.collection(COLLECTION).document()
    doc_ref.set(payload.model_dump())
    return DataOut(id=doc_ref.id, **payload.model_dump())


def list_data() -> list[DataOut]:
    db = get_db()
    docs = db.collection(COLLECTION).order_by("date").stream()
    return [DataOut(id=doc.id, **doc.to_dict()) for doc in docs]


def update_data(doc_id: str, payload: DataUpdate) -> DataOut:
    db = get_db()
    doc_ref = db.collection(COLLECTION).document(doc_id)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        raise KeyError(doc_id)

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if updates:
        doc_ref.update(updates)

    merged = {**snapshot.to_dict(), **updates}
    return DataOut(id=doc_id, **merged)


def delete_data(doc_id: str) -> None:
    db = get_db()
    doc_ref = db.collection(COLLECTION).document(doc_id)
    if not doc_ref.get().exists:
        raise KeyError(doc_id)
    doc_ref.delete()


def get_summary() -> DataSummary:
    rows = list_data()

    if not rows:
        return DataSummary(
            period="데이터 없음",
            count=0,
            metrics=DataMetrics(total=0, average=0, max=0, min=0),
            trend="데이터 없음",
        )

    values = [row.value for row in rows]
    dates = [row.date for row in rows]

    metrics = DataMetrics(
        total=sum(values),
        average=sum(values) / len(values),
        max=max(values),
        min=min(values),
    )

    trend = _calc_trend(values)

    return DataSummary(
        period=f"{dates[0]} ~ {dates[-1]}",
        count=len(rows),
        metrics=metrics,
        trend=trend,
    )


def _calc_trend(values: list[float], flat_threshold_pct: float = 3.0) -> str:
    """시계열을 앞·뒤 절반으로 나눠 평균 변화율로 추세를 판단한다.

    데이터 포인트가 100개 이상이라는 전제(과제 요구사항)에서는 단순 절반
    비교로도 최근 추세를 충분히 요약할 수 있다. 더 정교한 회귀 분석은
    이 과제 범위를 넘어서 쓰지 않는다.
    """
    midpoint = len(values) // 2
    first_half, second_half = values[:midpoint], values[midpoint:]
    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)

    if first_avg == 0:
        return "보합"

    pct_change = (second_avg - first_avg) / first_avg * 100

    if abs(pct_change) < flat_threshold_pct:
        return "보합"
    if pct_change > 0:
        return f"상승 (평균 +{pct_change:.1f}%)"
    return f"하락 (평균 {pct_change:.1f}%)"

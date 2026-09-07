from pydantic import BaseModel, Field


class DataCreate(BaseModel):
    date: str = Field(..., description="YYYY-MM 형식 월", examples=["2025-03"])
    value: float = Field(..., description="해당 월 방문자 수 등 수치")
    memo: str = Field("", description="지역명 등 부가 설명")


class DataUpdate(BaseModel):
    date: str | None = None
    value: float | None = None
    memo: str | None = None


class DataOut(DataCreate):
    id: str


class DataMetrics(BaseModel):
    total: float
    average: float
    max: float
    min: float


class DataSummary(BaseModel):
    period: str
    count: int
    metrics: DataMetrics
    trend: str

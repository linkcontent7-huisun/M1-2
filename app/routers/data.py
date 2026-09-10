from fastapi import APIRouter, HTTPException

from app.schemas.data import DataCreate, DataOut, DataStatistics, DataSummary, DataUpdate
from app.services import data_service

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("", response_model=DataOut)
def create_data(payload: DataCreate):
    return data_service.create_data(payload)


@router.get("", response_model=list[DataOut])
def list_data():
    return data_service.list_data()


@router.get("/summary", response_model=DataSummary)
def get_data_summary():
    return data_service.get_summary()


@router.get("/statistics", response_model=DataStatistics)
def get_data_statistics():
    return data_service.get_statistics()


@router.put("/{data_id}", response_model=DataOut)
def update_data(data_id: str, payload: DataUpdate):
    try:
        return data_service.update_data(data_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")


@router.delete("/{data_id}", status_code=204)
def delete_data(data_id: str):
    try:
        data_service.delete_data(data_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")

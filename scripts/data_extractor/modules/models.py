from pydantic import BaseModel
from typing import List, Optional

class PartResult(BaseModel):
    """개별 Part 데이터 모델"""
    serial_num: str
    measured_time: str
    worked_cnc: str
    worker: Optional[str] = None
    dims: List[Optional[float]]
    is_pass: List[Optional[bool]]

class LotInfo(BaseModel):
    """Lot 헤더 정보 모델"""
    lot_num: str
    process: str
    part_name: str
    dim_basic_name: List[str]
    dim_basic_float: List[float]
    tol_upper: List[float]
    tol_lower: List[float]

class LotDataContainer(BaseModel):
    """최종적으로 Web/JSON으로 나갈 Lot 전체 데이터 구조"""
    info: LotInfo
    parts: List[PartResult]

class BasicDataSpecs(BaseModel):
    """services.PartService.basic_data 내부 구조"""
    dim_name: List[str]
    dim_float: List[float]
    upper: List[float]
    lower: List[float]
    cell: List[str]

class ProductInfo(BaseModel):
    """services.IndexReader.get_product_info 반환 구조"""
    basic_data: BasicDataSpecs
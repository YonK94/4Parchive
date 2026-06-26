import json
from typing import Optional
from .models import LotDataContainer
from .services import PartService

class DataCollector:
    """
    외부 시스템과의 데이터 수집 인터페이스 역할 수행.
    (실제 로직은 PartService 위임.)
    """
    def __init__(self):
        self.service = PartService()
        # PartService: 실질적인 데이터 처리 로직.
        # IndexReader 등 모든 의존성 관리는 PartService 내부에서 처리.

    def collect_container(
            self, lot_num: str, process: str,
            part_name: Optional[str]=None, include_ng: bool=True
            ) -> LotDataContainer:
        """
        PartService를 호출, LotDataContainer 객체(Pydantic 모델) 반환.
        가장 순수한 형태의 데이터 객체 반환 메서드.
        """
        return self.service.process_lot(
            lot_num, process, part_name, include_ng
            )

    def collect_json(
            self, lot_num: str, process: str,
            part_name: Optional[str] = None, include_ng: bool=True
            ) -> str:
        """
        LotDataContainer를 JSON 문자열로 변환하여 반환.
        """
        container = self.collect_container(
            lot_num, process, part_name, include_ng
            )
        return container.model_dump_json(indent=4, ensure_ascii=False)

# ----------------------------------------------------------------------
# 외부 호출용 Wrapper 함수 (가장 권장되는 외부 API 형태)
# ----------------------------------------------------------------------

def get_lot_json(
        lot_num: str, process: str,
        part_name: Optional[str] = None, include_ng: bool=True
        ) -> str:
    """
    Lot 번호와 공정을 기반으로 1 Lot 전체 JSON 반환.
    """
    collector = DataCollector()
    return collector.collect_json(lot_num, process, part_name, include_ng)

def get_lot_data_dict(
        lot_num: str, process: str,
        part_name: Optional[str] = None, include_ng: bool=True
        ) -> dict:
    """
    외부(web, CLI)에서 호출하기 가장 편한 최종 API.
    데이터를 딕셔너리로 반환, 에러 발생 시 에러 정보 딕셔너리를 반환.
    """
    try:
        json_str = get_lot_json(lot_num, process, part_name, include_ng)
        return json.loads(json_str)

    except FileNotFoundError as e:
        # 파일이 없을 때 (Service에서 raise한 에러)
        return {"status": "error", "message": f"Error: {str(e)}"}
        
    except KeyError as e:
        # JSON 설정 파일에 정보가 없을 때 (IndexReader에서 발생)
        return {"status": "error", "message": f"Configuration Error: {str(e)}"}
        
    except Exception as e:
        # 그 외 예상치 못한 모든 에러
        return {"status": "error", "message": f"Data Extraction Failed: {str(e)}"}
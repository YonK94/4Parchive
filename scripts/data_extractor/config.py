from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    # 1. 파일 경로

    # ***** 원본 데이터 경로 *****
    DATA_ROOT = Path(r"C:\Users\YKim\BOX\Code\source\6PART")

    # 리소스 경로
    PATH_RESOURCES = BASE_DIR / "resources"
    FILE_INDEX_PART_DATA = PATH_RESOURCES / "index_part_data.json"
    FILE_MAP_PART_NAME = PATH_RESOURCES / "map_part_name.json"
    FILE_MAP_DATA_PATH = PATH_RESOURCES / "map_data_path.json"

    # 2. 정규표현식 패턴 (유효성 검사)
    
    # 폴더명 (예: "01호 SINGLE RING 1차")
    PATTERN_DIRNAME = r"^\d{2}호\s.+"
    
    # 파일명1 (예: "KK20240701001_2024년07월01일11시24분12초.xlsx")
    # 파일명2 (예: "KK20240701001_2024년07월01일11시24분12초_01호_ABC123_김연용.xlsx")
    PATTERN_FILENAME_1 = r"^KK\d{11}_\d{4}년\d{2}월\d{2}일\d{2}시\d{2}분\d{2}초\.xlsx$"
    PATTERN_FILENAME_2 = r"^KK\d{11}_\d{4}년\d{2}월\d{2}일\d{2}시\d{2}분\d{2}초_\d{2}호_[a-zA-Z0-9]+_[가-힣]+\.xlsx$"
    
    # 파일명3 (예: "KK20240701001_1차_2024년07월01일11시24분12초_01호_ABC123_김연용_D109-12992C(U1).xlsx")

    
    # PATTERN_FILENAME_OLD = r"^KK\d{11}_\d{4}년\d{1,2}월\d{1,2}일\d{1,2}시\d{1,2}분(\d{1,2}초)?\.xlsx$"
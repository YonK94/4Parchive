import sys

if not __package__:
    print("[Error] Must be run with package mode.")
    print("  Run by 'python -m scripts.data_extractor.extractor'.")
    sys.exit(1)

import json
from .modules.collector import get_lot_data_dict

def run():
    if len(sys.argv) >= 3:
        lot_no = sys.argv[1]
        process = sys.argv[2]
        part_name = sys.argv[3] if len(sys.argv) > 3 else None
        result = get_lot_data_dict(lot_no, process, part_name)
        print(json.dumps(result, indent=4, ensure_ascii=False))
    else:
        print("  [Error] Required Args: [LOT_NO] [PROCESS] (Optional: [PART_NAME])\n")

if __name__ == "__main__":
    run()
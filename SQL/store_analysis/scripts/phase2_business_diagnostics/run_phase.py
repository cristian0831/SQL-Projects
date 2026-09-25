import re
from pathlib import Path

from src.config import PROJECT_ROOT
from src.db_utils import run_query

PHASE_DIR = Path(__file__).parent
QUERIES_DIR = PHASE_DIR / "queries"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "phase2_business_diagnostics" / "tables"


def title_from_stem(stem: str) -> str:
    """"01_growth_trends" -> "Growth Trends" """
    name = re.sub(r"^\d+_", "", stem)
    return name.replace("_", " ").title()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for sql_file in sorted(QUERIES_DIR.glob("*.sql")):
        title = title_from_stem(sql_file.stem)
        result = run_query(sql_file)

        print(f"=== {title} ===")
        print(result.to_string(index=False))
        print()

        csv_path = OUTPUT_DIR / f"{sql_file.stem}.csv"
        result.to_csv(csv_path, index=False)
        print(f"Saved {len(result)} rows to {csv_path.relative_to(PROJECT_ROOT)}\n")


if __name__ == "__main__":
    main()

"""
src/reporter.py
Module responsible for exporting candidate rankings into CSV, JSON, and terminal summaries.
"""

from pathlib import Path
import pandas as pd
import json


def generate_reports(ranked_candidates: list, output_dir: str = None) -> dict:
    """
    Saves ranked screening results to CSV and JSON formats.
    Returns the file paths of generated outputs.
    """
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "outputs"

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    csv_path = out_path / "screening_report.csv"
    json_path = out_path / "screening_report.json"

    # Convert candidate list to pandas DataFrame
    df = pd.DataFrame(ranked_candidates)

    # Sort candidates by score descending
    if "score" in df.columns:
        df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
        df.insert(0, "rank", df.index + 1)

    # Export to CSV
    df.to_csv(csv_path, index=False, encoding="utf-8")

    # Export to JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

    return {
        "csv_path": str(csv_path),
        "json_path": str(json_path),
        "total_processed": len(df),
        "shortlisted_count": int((df["status"] == "SHORTLISTED").sum()) if "status" in df.columns else 0
    }


def print_terminal_summary(df_or_candidates) -> None:
    """
    Displays a structured, visually appealing terminal summary table of ranked candidates.
    """
    if isinstance(df_or_candidates, list):
        df = pd.DataFrame(df_or_candidates)
    else:
        df = df_or_candidates

    print("\n" + "=" * 90)
    print("                    AUTOMATED RESUME SCREENING RESULTS")
    print("=" * 90)
    print(f"{'Rank':<5} | {'Candidate Name':<20} | {'Score (%)':<10} | {'Status':<14} | {'Exp (Yrs)':<10} | {'Must-Have Gaps':<20}")
    print("-" * 90)

    for idx, row in df.iterrows():
        rank = row.get("rank", idx + 1)
        name = str(row.get("candidate_name", "Unknown"))[:19]
        score = f"{row.get('score', 0):.1f}%"
        status = str(row.get("status", "N/A"))
        exp = f"{row.get('experience_years', 0):.1f}"
        
        # Missing skills formatting
        missing = row.get("missing_must_haves", [])
        if isinstance(missing, list):
            missing_str = ", ".join(missing) if missing else "None (All match)"
        else:
            missing_str = str(missing)
        missing_str = missing_str[:20]

        print(f"{rank:<5} | {name:<20} | {score:<10} | {status:<14} | {exp:<10} | {missing_str:<20}")

    print("=" * 90 + "\n")

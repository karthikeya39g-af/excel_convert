
import pandas as pd
from pathlib import Path
import sys

import os

OUTPUT_FOLDER = os.environ.get("OUTPUT_FOLDER", "output")


def load_file(file_path):

    ext = Path(file_path).suffix.lower()

    if ext == ".csv":

        return pd.read_csv(
            file_path,
            dtype=str
        )

    elif ext in [".xls", ".xlsx"]:

        return pd.read_excel(
            file_path,
            sheet_name="TSheet",
            header=3,
            dtype=str
        )

    else:
        raise Exception(
            "Supported formats: csv, xls, xlsx"
        )


def clean_value(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


def main(input_file):

    print("Reading file...")

    df = load_file(input_file)

    print(f"Loaded {len(df)} rows")

    # ----------------------------------------
    # Clean columns
    # ----------------------------------------

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # ----------------------------------------
    # Remove blank HT No rows
    # ----------------------------------------

    df = df[
        df["HT No"].notna()
    ]

    # ----------------------------------------
    # Data Science Students only
    # HT No -> 237Z1A6705
    #            ^^
    #            67
    # ----------------------------------------

    df = df[
        df["HT No"]
        .astype(str)
        .str[6:8]
        == "67"
    ]

    print(
        f"DS Student Rows: {len(df)}"
    )

    # ----------------------------------------
    # Failed subjects only
    # ----------------------------------------

    df = df[
        df["Status"]
        .astype(str)
        .str.strip()
        .str.upper()
        == "FAIL"
    ]

    print(
        f"Failed Subject Rows: {len(df)}"
    )

    # ----------------------------------------
    # Group by student
    # ----------------------------------------

    grouped = df.groupby(
        "HT No",
        sort=False
    )

    students = []

    for ht_no, subjects in grouped:

        first = subjects.iloc[0]

        student = {}

        # ------------------------------------
        # Student details
        # ------------------------------------

        student["REGN_NO"] = ht_no
        student["RROLL"] = ht_no
        student["SNAME"] = clean_value(
            first["Name"]
        )

        student["GPA_PR"] = clean_value(
            first["SGPA"]
        )

        # ------------------------------------
        # Failed subjects only
        # ------------------------------------

        for idx, (_, sub) in enumerate(
            subjects.iterrows(),
            start=1
        ):

            prefix = f"SUB{idx}"

            student[prefix] = clean_value(
                sub["Sub Code"]
            )

            student[f"{prefix}NM"] = clean_value(
                sub["Sub Name"]
            )

            student[f"{prefix}_TH_MRKS"] = clean_value(
                sub["External"]
            )

            student[f"{prefix}_TOT"] = clean_value(
                sub["Total"]
            )

            student[f"{prefix}_GRADE"] = clean_value(
                sub["Grade"]
            )

            student[f"{prefix}_GRADE_POINTS"] = clean_value(
                sub["Points"]
            )

            student[f"{prefix}_CREDIT"] = clean_value(
                sub["Credits"]
            )

            student[f"{prefix}_CREDIT_POINTS"] = ""

            student[f"{prefix}_TYPE"] = "THEORY"

            student[f"{prefix}_REMARKS"] = clean_value(
                sub["Status"]
            )

        students.append(student)

    # ----------------------------------------
    # Output DataFrame
    # ----------------------------------------

    output_df = pd.DataFrame(students)

    # ----------------------------------------
    # Ensure SUB1..SUB9 exist
    # ----------------------------------------

    columns = [
        "REGN_NO",
        "RROLL",
        "SNAME",
        "GPA_PR"
    ]

    for i in range(1, 10):

        columns.extend([
            f"SUB{i}",
            f"SUB{i}NM",
            f"SUB{i}_TH_MRKS",
            f"SUB{i}_TOT",
            f"SUB{i}_GRADE",
            f"SUB{i}_GRADE_POINTS",
            f"SUB{i}_CREDIT",
            f"SUB{i}_CREDIT_POINTS",
            f"SUB{i}_TYPE",
            f"SUB{i}_REMARKS"
        ])

    for col in columns:

        if col not in output_df.columns:
            output_df[col] = ""

    output_df = output_df[columns]

    # ----------------------------------------
    # Output file
    # ----------------------------------------

    input_path = Path(input_file)

    output_dir = Path(
        OUTPUT_FOLDER
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir /
        f"{input_path.stem}.csv"
    )

    output_df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("=" * 50)
    print("SUPPLY FILE CREATED")
    print("=" * 50)
    print(
        f"Students Processed : {len(output_df)}"
    )
    print(
        f"Output File : {output_file}"
    )
    print("=" * 50)

    return output_file, len(output_df)


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "Usage:\n"
            "python3 supply.py input.xls"
        )

        sys.exit()

    main(sys.argv[1])

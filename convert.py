from openpyxl.drawing import spreadsheet_drawing
import pandas as pd
from pathlib import Path
import sys
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

ORG_NAME = "Nalla Narasimha Reddy Group of Institutions"
ACADEMIC_COURSE_ID = "67"
COURSE_NAME = "BTECH"

BATCH = ""
STREAM = ""

import os

YEAR = "2025"
MONTH = "JAN"
EXAM_TYPE = "I-I SEM Supplementary Examinations (R21)"

OUTPUT_FOLDER = os.environ.get("OUTPUT_FOLDER", "output")

# ============================================================
# READ CSV / XLSX / XLS
# ============================================================

def load_file(file_path):
    """
    Load CSV/XLS/XLSX file and automatically detect
    the header row containing 'HT No'
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = file_path.suffix.lower()

    # ----------------------------
    # CSV FILE
    # ----------------------------
    if extension == ".csv":

        # Try normal read first
        try:
            df = pd.read_csv(file_path, dtype=str)

            if "HT No" in df.columns:
                return df

        except:
            pass

        # Detect header row manually
        raw = pd.read_csv(
            file_path,
            header=None,
            dtype=str
        )

        header_row = None

        for i in range(len(raw)):
            row_values = raw.iloc[i].fillna("").astype(str).tolist()

            if "HT No" in row_values:
                header_row = i
                break

        if header_row is None:
            raise Exception("Header row containing 'HT No' not found.")

        return pd.read_csv(
            file_path,
            header=header_row,
            dtype=str
        )

    # ----------------------------
    # EXCEL FILES
    # ----------------------------
    elif extension in [".xlsx", ".xls"]:

        return pd.read_excel(
            file_path,
            sheet_name="TSheet",
            header=3,
            dtype=str
        )
        header_row = None

        for i in range(len(raw)):
            row_values = raw.iloc[i].fillna("").astype(str).tolist()

            if "HT No" in row_values:
                header_row = i
                break

        if header_row is None:
            raise Exception("Header row containing 'HT No' not found.")

        return pd.read_excel(
            file_path,
            header=header_row,
            dtype=str
        )

    else:
        raise Exception(
            "Unsupported file type. Use CSV, XLSX or XLS."
        )


# ============================================================
# MAIN CONVERSION
# ============================================================

def convert_to_university_format(input_file):
    input_path = Path(input_file)

    output_dir = Path(OUTPUT_FOLDER)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir /
        f"{input_path.stem}.csv"
    )    
    try:

        # ----------------------------------------------------
        # LOAD FILE
        # ----------------------------------------------------
        print("Reading file...")

        df = load_file(input_file)

        print(f"Loaded {len(df)} rows")


        print("\nColumns found:")
        for col in df.columns:
            print(repr(col))

        # ----------------------------------------------------
        # CLEAN COLUMN NAMES
        # ----------------------------------------------------
        df.columns = df.columns.astype(str).str.strip()

        # Remove spaces from string columns
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = (
                    df[col]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

        # ----------------------------------------------------
        # REQUIRED COLUMNS
        # ----------------------------------------------------
        required_cols = [
            "HT No",
            "Name",
            "Sub Code",
            "Sub Name",
            "External",
            "Total",
            "Grade",
            "Points",
            "Credits",
            "Status",
            "SGPA"
        ]

        missing = [
            col
            for col in required_cols
            if col not in df.columns
        ]

        if missing:
            raise Exception(
                "Missing columns: "
                + ", ".join(missing)
            )

        # ----------------------------------------------------
        # REMOVE BLANK HT NO ROWS
        # ----------------------------------------------------
        df = df[
            (df["HT No"].notna())
            & (df["HT No"] != "")
            & (df["HT No"].str.lower() != "nan")
        ]

        print(f"Valid rows: {len(df)}")

        if len(df) == 0:
            raise Exception("No valid data found.")

        # ----------------------------------------------------
        # GROUP BY STUDENT
        # ----------------------------------------------------
        grouped = df.groupby(
            "HT No",
            sort=False
        )

        student_records = []

        max_subjects = 0

        for ht_no, student_df in grouped:

            max_subjects = max(
                max_subjects,
                len(student_df)
            )

            first = student_df.iloc[0]

            # ------------------------------------------------
            # BASE STUDENT RECORD
            # ------------------------------------------------
            student = {

                "ORG_NAME": ORG_NAME,
                "ACADEMIC_COURSE_ID": ACADEMIC_COURSE_ID,
                "COURSE_NAME": COURSE_NAME,

                "BATCH": BATCH,
                "STREAM": STREAM,

                "REGN_NO": ht_no,
                "RROLL": ht_no,

                "CNAME": first["Name"],

                "GENDER": "",
                "DOB": "",
                "FNAME": "",
                "MNAME": "",

                "MRKS_REC_STATUS": "O",

                "YEAR": YEAR,
                "MONTH": MONTH,
                "EXAM_TYPE": EXAM_TYPE,

                "TOT_TH_MRKS": "",
                "TOT_PR_MRKS": "",

                "ABC_ACCOUNT_ID": "",

                "TOT_GRADE": "",
                "TH_GRADE": "",
                "PR_GRADE": "",

                "GPA_TH": "",
                "GPA_PR": first["SGPA"]
            }

            # ------------------------------------------------
            # TOTAL MARKS
            # ------------------------------------------------
            total_marks = 0

            # ------------------------------------------------
            # SUBJECTS
            # ------------------------------------------------
            for idx, (_, sub) in enumerate(
                student_df.iterrows(),
                start=1
            ):

                prefix = f"SUB{idx}"

                try:
                    total_marks += float(sub["Total"])
                except:
                    pass

                # Credit Points
                try:
                    credit_points = (
                        float(sub["Credits"])
                        * float(sub["Points"])
                    )
                except:
                    credit_points = ""

                student[f"{prefix}"] = sub["Sub Code"]

                student[f"{prefix}NM"] = sub["Sub Name"]

                student[f"{prefix}_TH_MRKS"] = sub["External"]

                student[f"{prefix}_TOT"] = sub["Total"]

                student[f"{prefix}_GRADE"] = sub["Grade"]

                student[f"{prefix}_GRADE_POINTS"] = sub["Points"]

                student[f"{prefix}_CREDIT"] = sub["Credits"]

                student[f"{prefix}_CREDIT_POINTS"] = credit_points

                student[f"{prefix}_TYPE"] = "Theory"

                student[f"{prefix}_REMARKS"] = sub["Status"]

            student["TOT_TH_MRKS"] = total_marks

            student_records.append(student)

        # ----------------------------------------------------
        # CREATE OUTPUT DF
        # ----------------------------------------------------
        output_df = pd.DataFrame(student_records)

        # ----------------------------------------------------
        # COLUMN ORDER
        # ----------------------------------------------------
        columns = [

            "ORG_NAME",
            "ACADEMIC_COURSE_ID",
            "COURSE_NAME",

            "BATCH",
            "STREAM",

            "REGN_NO",
            "RROLL",
            "CNAME",

            "GENDER",
            "DOB",
            "FNAME",
            "MNAME",

            "MRKS_REC_STATUS",

            "YEAR",
            "MONTH",
            "EXAM_TYPE",

            "TOT_TH_MRKS",
            "TOT_PR_MRKS",

            "ABC_ACCOUNT_ID",

            "TOT_GRADE",
            "TH_GRADE",
            "PR_GRADE",

            "GPA_TH",
            "GPA_PR"
        ]

        # ----------------------------------------------------
        # SUBJECT COLUMN ORDER
        # ----------------------------------------------------
        for i in range(1, max_subjects + 1):

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

        # Missing columns
        for col in columns:
            if col not in output_df.columns:
                output_df[col] = ""

        output_df = output_df[columns]
        # ----------------------------------------------------
# SAVE CSV
        # ----------------------------------------------------
        output_df.to_csv(
            output_file,
            index=False,
            encoding="utf-8-sig"
        )
        # ----------------------------------------------------
        # EXPORT
        # ----------------------------------------------------
        print(f"Output File : {output_file}")

        print("\n===================================")
        print("CONVERSION SUCCESSFUL")
        print("===================================")
        print(f"Students Processed : {len(output_df)}")
        print(f"Output File        : {output_file}")
        print("===================================\n")

        return output_file, len(output_df)

    except Exception as e:
        print("\nERROR:")
        print(str(e))
        raise e


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "\nUsage:\n"
            "python convert.py input.xlsx\n"
            "python convert.py input.xls\n"
            "python convert.py input.csv\n"
        )


    input_file = sys.argv[1]

    convert_to_university_format(input_file)
import pandas as pd

df = pd.read_excel(
    "1. I-II B.TECH R-22 24 BATCH REGULAR TSHEETS JULY-25.xls",
    sheet_name="TSheet",
    header=None,
    dtype=str
)

for i in range(20):
    print("\nROW", i)
    print(df.iloc[i].tolist())
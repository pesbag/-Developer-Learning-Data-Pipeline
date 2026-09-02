import pandas as pd
from pathlib import Path
BASE_DIR = Path(__file__).parent.parent
file_path=BASE_DIR/"AllDataFiles"/"developer_ai_learning_raw.csv"

def main():
    try:
        df=load_data()
    except FileNotFoundError:
        print("Error file not found")
        return
    shape_of_data(df)
    info_of_table(df)
    count_null_rows(df)

def count_null_rows(df):
    print("count_null_rows:\n",df.isna().sum())
def  info_of_table(df):
    print("table info:\n",df.info)
def shape_of_data(df):
    print(f"num of rows:{df.shape[0]}, num of columns: {df.shape[1]}")

def load_data():
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"Error file{file_path} was not found")
    try:
        df=pd.read_csv(file_path)
        return df
    except Exception:
        print("Error while processing the csv file")

if __name__== "__main__":
    main()
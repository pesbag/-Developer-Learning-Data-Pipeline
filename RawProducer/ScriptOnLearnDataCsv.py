import pandas as pd
from pathlib import Path

from unicodedata import numeric

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
    columns_exists(df)
    describe_data(df)
    is_valid=check_for_valid_columns(df)
    if not is_valid:
        return
    valid_type_age=validate_age(df)
    if not valid_type_age:
        fix_age_type(df)
    valid_type_years_code=validate_years_code(df)
    if not valid_type_years_code:
        fix_years_code_type(df)
    info_of_table(df)
    # check_for_semicolon(df)

def check_for_semicolon(df):
    text_cols=df.select_dtypes(include=['object','string']).columns
    for c in text_cols:
        if df[c].str.contains(';'):
            df[c]=df[c].str.split(";")

def validate_years_code(df):
    print("check for years code type validity:", df["YearsCode"].dtype)
    return pd.api.types.is_numeric_dtype(df["YearsCode"])

def fix_age_type(df):
    # df["Age"]=df["Age"].astype(int)
    df["Age"]=pd.to_numeric(df["Age"],errors='coerce')

def fix_years_code_type(df):
    df["YearsCode"]=df["YearsCode"].astype('Int64')

def check_for_valid_columns(df):
    valid_columns=['ResponseId', 'Age', 'YearsCode', 'DevType',
                   'LearnCodeChoose', 'LearnCode', 'LearnCodeAI',
                   'AILearnHow', 'AISelect', 'AIAcc', 'AISent']
    non_valid_columns=[]
    for c in df.columns:
        if c not in valid_columns:
            non_valid_columns.append(c)
    if non_valid_columns:
        print(f"Error: invalid columns: {non_valid_columns}")
        return False
    else:
        return True
def validate_age(df):
    print("check for age type validity:",df["Age"].dtype)
    return not isinstance(df["Age"].dtype,int)
def columns_exists(df):
    print("columns exists:\n",list(df.columns))
def count_null_rows(df):
    print("count_null_rows:\n",df.isna().sum())
def  info_of_table(df):
    print("table info:\n",df.info())
def shape_of_data(df):
    print(f"num of rows:{df.shape[0]}, num of columns: {df.shape[1]}")
def describe_data(df):
    print(df.describe())
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
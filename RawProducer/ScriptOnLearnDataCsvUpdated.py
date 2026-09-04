import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
file_path=BASE_DIR/"AllDataFiles"/"developer_ai_learning_raw.csv"


OPERATIONAL_FIELDS = [
    "age",
    "aiLearningMethods",
    "aiSentiment",
    "aiTrust",
    "aiUsage",
    "devType",
    "experienceLevel",
    "learnCodeAI",
    "learnCodeChoose",
    "learningMethods",
    "responseId",
    "usesAIForLearning",
    "usesDocumentation",
    "usesStackOverflow",
    "yearsCode",
]

RENAME_MAP = {
    "ResponseId": "responseId",
    "Age": "age",
    "YearsCode": "yearsCode",
    "DevType": "devType",
    "LearnCodeChoose": "learnCodeChoose",
    "LearnCode": "learningMethods",
    "LearnCodeAI": "learnCodeAI",
    "AILearnHow": "aiLearningMethods",
    "AISelect": "aiUsage",
    "AIAcc": "aiTrust",
    "AISent": "aiSentiment",
}
TECH_DOC = "Technical documentation (is generated for/by the tool or system)"
AI_CODEGEN = "AI CodeGen tools or AI-enabled apps"
STACK_OVERFLOW = "Stack Overflow or Stack Exchange"

def clean_script(df):
    is_valid=check_for_valid_columns(df)
    if not is_valid:
        return
    valid_type_years_code=validate_years_code(df)
    if not valid_type_years_code:
        fix_years_code_type(df)
    check_for_semicolon(df)
    add_new_columns(df)
    add_experienceLevel_column(df)
    df = rename_columns_camel_case(df)
    return df

def get_clean_row(json_file_name):
    try:
        with open(json_file_name, "r") as f:
            all_lines=f.readlines()
            return all_lines
    except FileNotFoundError:
        print(f"error file: {json_file_name} was not found")

def rename_columns_camel_case(df):
    df=df.rename(columns=RENAME_MAP)
    return df

def check_for_semicolon(df):
    for col in ['LearnCode', 'AILearnHow']:
        df[col] = df[col].astype(str).str.split(';')

def validate_years_code(df):
    # print("check for years code type validity:", df["YearsCode"].dtype)
    return pd.api.types.is_integer_dtype(df["YearsCode"])

def fix_age_type(df):
    df["Age"]=pd.to_numeric(df["Age"],errors='coerce')

def fix_years_code_type(df):
    df["YearsCode"]=pd.to_numeric(df["YearsCode"],errors='coerce').astype('Int64')

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
def add_experienceLevel_column(df):
    def experienceLevel_func(level):
        if pd.isna(level) or level is None:
            return "Unknown"
        elif 0 <= level <= 2:
            return "Beginner"
        elif level <= 5:
            return "Early Career"
        elif level <= 10:
            return "Experienced"
        elif level > 10:
            return "Highly Experienced"

    df["experienceLevel"] = df["YearsCode"].apply(experienceLevel_func)
    df["experienceLevel"].value_counts()

def validate_age(df):
    print("check for age type validity:",df["Age"].dtype)
    return isinstance(df["Age"].dtype,int)
def columns_exists(df):
    print("columns exists:\n",list(df.columns))
def count_null_rows(df):
    print("count_null_rows:\n",df.isna().sum())
def  info_of_table(df):
    print("table info:\n")
    df.info()
def shape_of_data(df):
    print(f"num of rows:{df.shape[0]}, num of columns: {df.shape[1]}")

def describe_data(df):
    print("describe:\n",df.describe())

def load_data():
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"Error file{file_path} was not found")
    try:
        df=pd.read_csv(file_path)
        return df
    except Exception:
        print("Error while processing the csv file")

def add_new_columns(df):
    def has_option(options, target):
        if isinstance(options, list):
            return target in options
        return False
    df['usesDocumentation'] = df['LearnCode'].apply(lambda x: has_option(x, TECH_DOC))
    df['usesAIForLearning'] = df['LearnCode'].apply(lambda x: has_option(x, AI_CODEGEN))
    df['usesStackOverflow'] = df['LearnCode'].apply(lambda x: has_option(x, STACK_OVERFLOW))

def save_to_json_clean(df):
    df.to_json("cleaned_data.jsonl",orient='records',lines=True)
def  save_to_json_processed(df):
    df.to_json("processed_data.jsonl",orient='records',lines=True)

# if __name__== "__main__":
#     clean_script()
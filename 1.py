# 1. 自己造一个 qa.csv（含空值、重复行）放项目目录
# 2. 跑：
import pandas as pd
from data_utils import *

df = load_qa_csv("qa.csv")
print(df.shape)            # 清洗前几行几列
clean = clean_qa(df)
print(clean.shape)         # 对比清洗后（行数应该变少）
save_qa_jsonl(clean, "qa_clean.jsonl")
# 3. 打开 qa_clean.jsonl 检查每行是不是一个合法的 JSON
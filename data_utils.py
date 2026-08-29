import pandas as pd
from text_utils import wash_text


def load_qa_csv(path: str) -> pd.DataFrame:
    """
    读取问答数据集 csv
    :param path: csv 文件路径
    :return: 包含 question/answer 等列的 DataFrame
    """
    return pd.read_csv(path)


def clean_qa(df: pd.DataFrame) -> pd.DataFrame:
    """
    问答数据集清洗：先删空行→再去重→最后批量清洗文本列
    :param df: 原始 DataFrame
    :return: 清洗后的 DataFrame
    """
    df = df.dropna(subset=["question", "answer"])
    df = df.drop_duplicates()
    df["question"] = df["question"].apply(wash_text)
    df["answer"] = df["answer"].apply(wash_text)
    return df


def save_qa_jsonl(df: pd.DataFrame, path: str) -> None:
    """
    保存为标准 jsonl（每行一个 JSON 对象，RAG 知识库的标准输入格式）
    :param df: 清洗后的 DataFrame
    :param path: 输出文件路径
    :return: None
    """
    df.to_json(path, orient="records", lines=True, force_ascii=False)
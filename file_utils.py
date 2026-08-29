import os
import json
import logging


logger = logging.getLogger(__name__)


def read_text_auto(path: str) -> str:
    """
    自动适配编码读取文本文件（先 utf-8，失败再试 gbk）
    :param path: 文件路径
    :return: 文件内容字符串
    :raises UnicodeDecodeError: 所有编码都识别失败时
    """
    for enc in ("utf-8-sig", "gbk"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"无法识别文件编码：{path}")


def read_json(path: str) -> dict:
    """
    读取json文件,出错异常直接报出去（不吞异常，由调用方处理）
    :param path: 文件路径
    :return: 解析后的 dict
    :raises FileNotFoundError / json.JSONDecodeError: 文件不存在或格式错误时
    """
    return json.loads(read_text_auto(path))


def write_json(path: str, data, ensure_ascii: bool = False) -> None:
    """
    这是将文件转为保存json格式的函数
    :param path: 文件保存路径
    :param data: 要保存的 Python 对象（dict/list）
    :param ensure_ascii: True 时中文转义为 \\uXXXX，False 保持中文原样（默认）
    :return: None
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=ensure_ascii, indent=2)


def walk_text_files(src_dir: str) -> list[str]:
    """
    这是递归遍历目录下所有 txt/md 文件的函数
    :param src_dir: 源文件路径
    :return: 所有 .txt/.md 文件的绝对路径列表
    """
    files = []
    for root, _, filenames in os.walk(src_dir):
        for filename in filenames:
            if filename.lower().endswith((".txt", ".md")):
                files.append(os.path.join(root, filename))
    return files


def batch_read_texts(src_dir: str) -> dict[str, str]:
    """
    这是批量读取文本文件的函数（编码自动适配，单文件失败跳过）
    :param src_dir: 源文件路径
    :return: {相对路径: 内容} 字典
    """
    result = {}
    for file_path in walk_text_files(src_dir):
        try:
            rel = os.path.relpath(file_path, src_dir)
            result[rel] = read_text_auto(file_path)
        except Exception as e:
            logger.error(f"跳过失败文件{file_path},错误原因为:{e}")
    return result


def batch_save_texts(data: dict[str, str], tgt_dir: str) -> None:
    """
    这是批量保存文本文件的函数（保持相对目录结构，单文件失败不中断）
    :param data: {相对路径: 内容} 字典（与 batch_read_texts 的 key 对应）
    :param tgt_dir: 目标文件夹，会自动创建
    :return: None（完成后打印汇总统计）
    """
    os.makedirs(tgt_dir, exist_ok=True)
    fail_count = 0
    for rel_path, content in data.items():
        tgt_path = os.path.join(tgt_dir, rel_path)
        try:
            os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
            with open(tgt_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            fail_count += 1
            logger.error(f"保存失败{rel_path},失败原因:{e}")
    print(f"共保存了{len(data)}个文件,失败了{fail_count}个文件")
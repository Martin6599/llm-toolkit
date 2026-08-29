import os
import re


def wash_text(rtext: str) -> str:
    """
    这是清洗原生文本,去除多余的换行，空格，删除多余的控制字符
    :param rtext: raw text 未经清洗的源文本
    :return: 清洗后的文本：控制字符已删除、连续空行压成段落分隔、保留行首缩进
    """
    text = re.sub(r'[\x00-\x08\x0b-\x1f\u3000\u200b-\u200d]', '', rtext)
    text = re.sub(r'\n\s+', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [line.rstrip() for line in text.splitlines()]
    valid_lines = [line for line in lines if line]
    return "\n\n".join(valid_lines)


def batch_wash_text(src_dir: str, tgt_dir: str):
    """
    这是批量清洗文件夹内所有txt文本的函数
    :param src_dir: 源文件夹
    :param tgt_dir: 清洗完成后输出的文件夹
    :return: None（每个文件的处理结果打印在控制台）
    """
    os.makedirs(tgt_dir, exist_ok=True)
    if not os.path.isdir(src_dir):
        raise FileNotFoundError(f"源目录不存在：{src_dir}")

    file_list = []
    for f in os.listdir(src_dir):
        full_path = os.path.join(src_dir, f)
        # 是文件，并且后缀txt
        if os.path.isfile(full_path) and f.lower().endswith(".txt"):
            file_list.append(f)
    for filename in file_list:
        src_path = os.path.join(src_dir, filename)
        tgt_path = os.path.join(tgt_dir, filename)
        try:
            with open(src_path, 'r', encoding='utf-8') as f:
                raw = f.read()
            clean_context = wash_text(raw)
            with open(tgt_path, 'w', encoding='utf-8') as f:
                f.write(clean_context)
            print(f"处理完毕：{tgt_path}")
        except Exception as e:
            print(f"{filename}处理失败,失败原因：{e}")
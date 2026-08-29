"""
P1 通用 LLM 工具库 · 全链路演示
运行：先激活 venv，再 python demo.py
覆盖：文件批量处理 / 数据集清洗 / 向量检索 / LLM 对话 / 异步并发对比
"""
import asyncio
import time

import numpy as np

from config import load_config
from file_utils import batch_read_texts, batch_save_texts
from text_utils import wash_text
from data_utils import load_qa_csv, clean_qa, save_qa_jsonl
from vector_utils import cosine_similarity, top_k_similar
from llm_client import LLMClient, batch_achat


def demo_file_pipeline():
    """① 文件批量处理：读 → 洗 → 存（镜像目录结构）"""
    print("=== ① 文件批量处理：读 → 洗 → 存 ===")
    raw = batch_read_texts("test_data")
    clean = {k: wash_text(v) for k, v in raw.items()}
    batch_save_texts(clean, "out")
    print(f"    处理 {len(clean)} 个文件 → out/（含 GBK 编码回退）\n")


def demo_qa_cleaning():
    """② 问答数据集清洗 → jsonl（RAG 标准输入）"""
    print("=== ② 问答数据集清洗 → jsonl ===")
    df = load_qa_csv("qa.csv")
    clean_df = clean_qa(df)
    save_qa_jsonl(clean_df, "qa_clean.jsonl")
    print(f"    {df.shape[0]} 行 → {clean_df.shape[0]} 行（去空+去重）→ qa_clean.jsonl\n")


def demo_vector():
    """③ 向量检索（RAG 核心预演）"""
    print("=== ③ 向量相似度 & top_k 检索 ===")
    query = np.array([1.0, 0.0])
    vectors = np.array([[1.0, 1.0], [0.0, 1.0], [-1.0, 0.0], [1.0, 0.0]])
    sim = cosine_similarity(query, vectors[3])
    print(f"    query 与 [1,0] 的余弦相似度: {sim:.3f}（应为 1.0）")
    print(f"    最相似的 2 条下标: {top_k_similar(query, vectors, k=2)}（期望 [3, 0]）\n")


def demo_llm():
    """④ 本地 LLM 对话（Ollama qwen3.5:4b）"""
    print("=== ④ LLM 对话（本地 qwen3.5:4b）===")
    client = LLMClient(load_config().get_default())
    answer = client.chat([{"role": "user", "content": "用一句话介绍你自己"}])
    print(f"    模型回答: {answer}\n")


def demo_async():
    """⑤ 同步 vs 异步 并发对比（README 效果数据来源）"""
    print("=== ⑤ 同步 vs 异步 并发对比 ===")
    client = LLMClient(load_config().get_default())
    prompts = ["你好"] * 5

    t0 = time.time()
    for p in prompts:
        client.chat([{"role": "user", "content": p}])
    sync_t = time.time() - t0

    t0 = time.time()
    asyncio.run(batch_achat(client, prompts))
    async_t = time.time() - t0

    print(f"    同步 5 个请求: {sync_t:.2f}s | 异步 5 个请求: {async_t:.2f}s | 提速 {sync_t / async_t:.1f} 倍\n")


if __name__ == "__main__":
    demo_file_pipeline()
    demo_qa_cleaning()
    demo_vector()
    try:
        demo_llm()
        demo_async()
    except Exception as e:
        print(f"    ⚠️ LLM 演示跳过（Ollama 未启动或接口异常）：{e}")
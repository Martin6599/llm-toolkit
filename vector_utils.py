import numpy as np


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    余弦相似度：两个向量方向有多像，范围 [-1, 1]，越大越像
    :param a: 向量 a（1 维 numpy 数组）
    :param b: 向量 b（1 维 numpy 数组）
    :return: 相似度 float；全零向量按 0 处理
    :raises TypeError: 参数不是 numpy 数组时
    """
    if not (isinstance(a, np.ndarray) and isinstance(b, np.ndarray)):
        raise TypeError(f"错误,必须是numpy数组")

    dot_product = np.dot(a, b)
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    cos_sim = dot_product / (norm_a * norm_b)
    return float(np.clip(cos_sim, -1.0, 1.0))


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    """
    欧氏距离：两点间的直线距离，越小越近（0 表示完全相同）
    :param a: 向量 a（1 维 numpy 数组）
    :param b: 向量 b（1 维 numpy 数组）
    :return: 距离 float
    :raises TypeError: 参数不是 numpy 数组时
    :raises ValueError: 两向量维度不一致时
    """
    if not (isinstance(a, np.ndarray) and isinstance(b, np.ndarray)):
        raise TypeError(f"错误,不是numpy数组")
    if a.shape != b.shape:
        raise ValueError(f"向量维度不一致：{a.shape} vs {b.shape}")
    return float(np.linalg.norm(a - b))


def top_k_similar(query_vec: np.ndarray, vectors: np.ndarray, k: int = 5) -> list[int]:
    """
    在 N×D 向量矩阵中找与 query_vec 最相似的 k 条（RAG 检索核心）
    :param query_vec: 查询向量（1 维，D 个元素）
    :param vectors: 向量矩阵（2 维，N 行 D 列，每行一条向量）
    :param k: 返回最相似的条数，默认 5
    :return: 最相似向量的下标列表，按相似度从高到低
    :raises ValueError: 维度数或维度大小不匹配时
    """
    if query_vec.ndim != 1 or vectors.ndim != 2:
        raise ValueError(f"错误,query_vec应该是1维,vectors应该是二维")
    if vectors.shape[1] != query_vec.shape[0]:
        raise ValueError(f"向量维度不匹配：{query_vec.shape} vs {vectors.shape}")
    k = min(k, vectors.shape[0])
    dots = np.dot(query_vec, vectors.T)
    norms = np.linalg.norm(vectors, axis=1)
    sims = dots / (np.linalg.norm(query_vec) * norms)
    sims = np.nan_to_num(sims)
    return np.argsort(sims)[::-1][:k].tolist()
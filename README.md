# llm-toolkit · 通用 LLM 工具库（我的 P1 项目）

> 这是我学习计划第一阶段的产出：一套大模型应用开发最常用的 Python 工具库。后面做 RAG 和 Agent 项目，我会直接复用这套东西。

## 这个项目是干嘛的

把大模型应用开发里高频使用 的能力——**文本处理、文件批量、接口调用、数据校验、向量计算、数据集清洗**——封装成一个个独立小模块。每个模块能单独用，也能串成一条流水线（见 `demo.py`）。

## 功能一览

| 模块 | 功能 | 状态 |
|---|---|---|
| `config.py` | LLM 配置：yaml 加载 + Pydantic 校验，改 `base_url` 就能切换本地 Ollama / 云端 DeepSeek | ✅ |
| `retry.py` | 同步接口重试装饰器：只重试 429/5xx，401 这类 4xx 直接抛 | ✅ |
| `async_retry.py` | 异步版重试装饰器（包 async 函数用） | ✅ |
| `text_utils.py` | 文本清洗：控制字符、全角空格、零宽字符、空行处理，保留段落边界 | ✅ |
| `file_utils.py` | 文件批量：utf-8/gbk 编码自动适配、递归遍历、镜像目录保存、json 读写 | ✅ |
| `validators.py` | Pydantic 三套模型：请求体 / 问答入参 / 返回结果，自动校验 | ✅ |
| `llm_client.py` | LLM 客户端：同步 `chat()` + 异步 `achat()` + 并发批量，OpenAI 兼容协议 | ✅ |
| `vector_utils.py` | 向量工具：余弦相似度、欧氏距离、top_k 检索（RAG 检索核心） | ✅ |
| `data_utils.py` | 问答数据集清洗：csv → jsonl（RAG 知识库标准输入） | ✅ |

## 环境部署

**依赖**：Python 3.11+，包见 `requirements.txt`

```powershell
# 1. 建虚拟环境并激活（重要：别用系统 Python）
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. 装依赖
pip install -r requirements.txt

# 3. （可选）本地模型：装 Ollama 并拉模型
ollama pull qwen3.5:4b

# 4. 配置 config.yaml（本地 api_key 填 EMPTY；云端用环境变量 ${DEEPSEEK_API_KEY}，别把 key 写进文件）
```

## 使用教程

**我做了一个全链路演示的Demo,可以直接测试。**

```powershell
python demo.py
```

依次演示了我做的工具的使用情况：文件批量处理 → 数据集清洗 → 向量检索 → 本地 LLM 对话 → 同步/异步并发对比。

**各模块用法示例**：

```python
# 配置
from config import load_config
cfg = load_config()

# 文件：读 → 清洗 → 存（镜像目录结构）
from file_utils import batch_read_texts, batch_save_texts
from text_utils import wash_text
raw = batch_read_texts("test_data")
clean = {k: wash_text(v) for k, v in raw.items()}
batch_save_texts(clean, "out")

# LLM 对话（本地/云端改 config.yaml 切换）
from llm_client import LLMClient
client = LLMClient(cfg.get_default())
print(client.chat([{"role": "user", "content": "你好"}]))

# 向量检索
import numpy as np
from vector_utils import top_k_similar
print(top_k_similar(np.array([1.0, 0.0]), np.array([[1.0, 1.0], [1.0, 0.0]]), k=1))
```

## 效果展示

**异步并发提速**（使用本地ollama模型qwen3.5:4b，跑10 个请求）：

| 方式 | 总耗时 |
|---|---|
| 同步（串行） | 11.4 秒 |
| 异步（并发） | 1.8 秒 |
| **提速** | **6.3 倍** |

> 理论上来说提速应该在 10 倍：瓶颈在本地单 GPU 推理的串行队列，异步只吃到了"网络等待重叠"的收益。

**数据集清洗**：原数据集从 10 行 → 7 行（去掉了 1 行空问题 + 2 行完全重复），文本里的全角空格、零宽字符、控制字符全部清理掉了。

**GBK 编码兼容**：读取 utf-8/gbk 文件自动适配，不用自己猜编码。

## 踩坑记录

1. Pydantic v2 可变默认值要用 `default_factory`，直接传实例会让所有实例共享同一个对象
2. pandas 的 `dropna` / `drop_duplicates` 不改原表，默认返回的是原表，必须接返回值（`df = df.dropna(...)`）
3. 同步重试装饰器包不住 async 函数的异常（异常发生在 await 之后）→ 需要单独的 async_retry
4. API key 这类需要保密的内容，用环境变量（如果发生泄密，建议直接吊销重建）



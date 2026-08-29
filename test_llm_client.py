import asyncio, time
from config import load_config
from llm_client import LLMClient, batch_achat


client = LLMClient(load_config().get_default())

prompts = ["你好"] * 10

# 同步耗时
t0 = time.time()
for p in prompts:
    client.chat([{"role": "user", "content": p}])
sync_time = time.time() - t0

# 异步耗时
t0 = time.time()
results = asyncio.run(batch_achat(client, prompts))
async_time = time.time() - t0

print(f"同步 10 个请求：{sync_time:.1f} 秒")
print(f"异步 10 个请求：{async_time:.1f} 秒")
print(f"提速 {sync_time / async_time:.1f} 倍")
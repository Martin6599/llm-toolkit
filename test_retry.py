
import logging
import requests
from retry import llm_retry
from config import load_config

logging.basicConfig(level=logging.INFO)      # 让重试日志显示出来

cfg = load_config()
llm = cfg.get_default()

count = 0

#场景1:先失败再成功

@llm_retry(max_retry=llm.max_retry, sleep_seconds=llm.sleep_seconds)
def fake_call():
    global count
    count += 1
    if count < 3:
        raise requests.exceptions.Timeout(f"模拟超时（第 {count} 次调用失败）")
    return "终于成功了"

print(fake_call())                    # 应该打印：终于成功了
print(f"实际调用次数: {count}")        # 应该打印：3


# 场景2：一直失败 → 必须 raise，不能返回 None
@llm_retry(max_retry=3, sleep_seconds=0.1)
def always_fail():
    raise requests.exceptions.Timeout("永远失败")

try:
    result = always_fail()
    print(f"❌ 有问题：竟然返回了 {result}")
except requests.exceptions.Timeout:
    print("✅ 正确：重试耗尽后抛出了异常")
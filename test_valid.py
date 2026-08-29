from validators import Message, ChatRequestModel, UserQueryModel, ChatResponseModel

# 用例1：合法请求 → 校验通过
req = ChatRequestModel(model="qwen3.5:4b", messages=[{"role": "user", "content": "你好"}])
print("用例1 ✅", req.model)

# 用例2：空问题 → 必须报错
try:
    UserQueryModel(question="")
    print("用例2 ❌ 没报错，有问题")
except Exception as e:
    print("用例2 ✅ 报错符合预期:", type(e).__name__)

# 用例3：非法 role → 必须报错
try:
    Message(role="admin", content="hi")
    print("用例3 ❌ 没报错，有问题")
except Exception as e:
    print("用例3 ✅ 报错符合预期:", type(e).__name__)

# 用例4：残缺的返回 dict → 自动补默认值
resp = ChatResponseModel.model_validate({"content": "回答"})
print("用例4 ✅", resp.model, resp.usage.total_tokens, resp.latency)
import asyncio
import httpx
from validators import ChatRequestModel, ChatResponseModel


class LLMClient:
    """LLM 客户端：封装对话请求，只改 base_url 即可切换本地/云端服务"""

    def __init__(self, config):
        """
        :param config: LLMconfig 实例（含 base_url/api_key/model/temperature 等）
        """
        self.config = config
        self.url = f"{config.base_url}/chat/completions"
        self.headers = {"Authorization": f"Bearer {config.api_key}"}

    def _build_payload(self, messages, **kwargs) -> dict:
        """
        构造并校验请求体（走 ChatRequestModel 自动校验）
        :param messages: 消息列表，如 [{"role": "user", "content": "你好"}]
        :param kwargs: 可覆盖 temperature / max_tokens
        :return: 校验通过的请求体 dict
        """
        req = ChatRequestModel(
            model=self.config.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        return req.model_dump()

    def _parse(self, resp_json: dict) -> ChatResponseModel:
        """
        把接口原始返回解析成标准模型
        :param resp_json: 接口返回的 JSON dict
        :return: ChatResponseModel 实例
        """
        return ChatResponseModel(
            content=resp_json["choices"][0]["message"]["content"],
            model=resp_json.get("model", ""),
            usage=resp_json.get("usage", {})
        )

    def chat(self, messages) -> str:
        """
        同步对话（一次请求，阻塞等待）
        :param messages: 消息列表，如 [{"role": "user", "content": "你好"}]
        :return: 模型回答文本
        """
        resp = httpx.post(self.url, json=self._build_payload(messages),
                          headers=self.headers, timeout=self.config.timeout)
        resp.raise_for_status()
        return self._parse(resp.json()).content

    async def achat(self, messages) -> str:
        """
        异步对话（await 让出事件循环，可并发批量请求）
        :param messages: 消息列表，如 [{"role": "user", "content": "你好"}]
        :return: 模型回答文本
        """
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            resp = await client.post(self.url, json=self._build_payload(messages),
                                     headers=self.headers, timeout=self.config.timeout)
            resp.raise_for_status()
            return self._parse(resp.json()).content


async def batch_achat(client: LLMClient, prompts: list[dict]) -> list[str]:
    """
    并发批量对话（异步的价值所在：等待时间重叠利用）
    :param client: LLMClient 实例
    :param prompts: 提示词列表，如 ["你好", "介绍RAG"]
    :return: 每个提示词的回答文本列表
    """
    tasks = [client.achat([{"role": "user", "content": p}]) for p in prompts]
    return await asyncio.gather(*tasks)
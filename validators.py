from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional


class Message(BaseModel):
    """单条对话消息模型：谁说的 + 说了什么"""

    role: str = Field(..., description="角色=system/user/assistant/tool")
    content: str = Field(..., description="输入文本")

    @field_validator("role")
    @classmethod
    def check_role(cls, value):
        """
        校验消息角色是否合法
        :param value: 传入的 role 值
        :return: 合法时原样返回
        :raises ValueError: 角色不在 system/user/assistant/tool 中时
        """
        if value not in ("system", "user", "assistant", "tool"):
            raise ValueError(f"非法角色{value}")
        return value


class ChatRequestModel(BaseModel):
    """发给 LLM 接口的请求体模型（OpenAI 兼容格式，多余字段直接报错）"""

    model_config = ConfigDict(extra="forbid")
    model: str = Field(..., description="模型名称")
    messages: list[Message] = Field(..., min_length=1, description="用户输入的信息")
    temperature: float = Field(default=0.7, lt=2.0, ge=0.1)
    max_tokens: int = Field(default=2048, lt=32768, ge=1)
    stream: bool = Field(default=False)


class UserQueryModel(BaseModel):
    """用户问答入参模型（RAG/Agent 阶段复用）"""

    question: str = Field(..., min_length=1, max_length=1000, description="用户问题,不能为空")
    session_id: Optional[str] = Field(default=None, description="本次会话ID,为多轮对话用")
    top_k: int = Field(default=5, ge=1, le=20, description="检索条数，RAG 用")


class UsageModel(BaseModel):
    """token 用量统计模型"""

    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)


class ChatResponseModel(BaseModel):
    """LLM 接口返回的标准化模型（字段缺失时自动补默认值）"""

    content: str = Field(default="", description="模型回答内容")
    model: str = Field(default="", description="实际使用的模型名")
    usage: UsageModel = Field(default_factory=UsageModel, description="token 用量")
    latency: float = Field(default=0.0, ge=0.0, description="请求耗时秒数，llm_client 填充")
    finish_reason: str = Field(default="", description="结束原因：stop/length")
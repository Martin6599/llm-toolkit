# 这是llm配置模块,配置文件从config.yaml读取,定义了配置模型,和自动校验


from pydantic import BaseModel, Field, field_validator
from pathlib import Path
from typing import Union
import os
import yaml


class LLMconfig(BaseModel):
    """单个 LLM 服务配置模型：定义每个服务的字段与校验规则，具体值来自 config.yaml"""

    base_url: str = Field(..., description="LLM的api地址")
    api_key: str = Field(default="EMPTY", description="我的api_key")
    model: str = Field(..., description="我使用的模型名称")
    temperature: float = Field(default=0.7, le=2.0, ge=0.0, description="随机性控制")
    max_tokens: int = Field(default=2048, gt=0, description="最长生成长度")
    timeout: int = Field(default=120, gt=0, description="最大请求超时时长")
    max_retry: int = Field(default=3, le=5, description="最大重试次数")
    sleep_seconds: float = Field(default=1.0, ge=0.1, lt=3.0, description="重试休眠时间")

    @field_validator("api_key")
    @classmethod
    def _fill_placeholder(cls, v: str) -> str:
        """
        api_key 为空时填充占位符，避免请求头报错
        :param v: 配置里填写的 api_key
        :return: 非空 key 原样返回，空值返回 "EMPTY"
        """
        return v or "EMPTY"


class AppSettings(BaseModel):
    """整体配置模型：默认服务 + 多服务集合"""

    default_provider: str = "local"
    providers: dict[str, LLMconfig]

    def get_default(self) -> LLMconfig:
        """
        获取当前默认使用的服务配置
        :return: default_provider 对应的 LLMconfig 实例
        """
        return self.providers[self.default_provider]


def _resolve_env(value):
    """
    把 ${环境变量名} 占位符解析成真实值
    :param value: 配置里的原始值
    :return: 环境变量值；非占位符的普通值原样返回
    :raises ValueError: 占位符对应的环境变量未设置时
    """
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        name = value[2:-1]
        if name not in os.environ:
            raise ValueError(f"缺少环境变量{name}")
        return os.environ[name]
    return value


def load_config(path: Union[str, Path] = "config.yaml") -> AppSettings:
    """
    从 yaml 文件加载并校验配置
    :param path: 配置文件路径，默认 config.yaml
    :return: 校验通过的 AppSettings 对象
    :raises FileNotFoundError: 配置文件不存在时
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"找不到配置文件{path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    for provider in raw.get("providers", {}).values():
        for key, value in provider.items():
            provider[key] = _resolve_env(value)
    return AppSettings(**raw)
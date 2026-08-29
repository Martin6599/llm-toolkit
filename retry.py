#这是一个接口重试装饰器

import time
import functools
import requests
import logging

RETRYABLE_STATUS = (429, 500, 502, 503, 504)
logger = logging.getLogger(__name__)


def llm_retry(max_retry: int, sleep_seconds: float = 1.0):
    """
    这是接口重试装饰器：对网络类错误自动重试，重试耗尽后抛出最后一次异常
    :param max_retry: 最大尝试次数（含首次）
    :param sleep_seconds: 重试前休眠时间（秒）
    :return: 包装后的函数；重试耗尽时抛出最后一次异常
    """

    def decorator(func):
        """装饰器工厂：接收被装饰函数，返回带重试逻辑的包装函数"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """带重试逻辑的包装函数：捕获网络异常→判断是否可重试→重试或抛出"""
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    status = e.response.status_code if e.response is not None else None
                    if status is not None and status not in RETRYABLE_STATUS:
                        raise
                    attempt += 1
                    logger.warning(f"接口未能成功调用，第{attempt}次重试，错误信息：{e}")
                    if attempt >= max_retry:
                        raise
                    time.sleep(sleep_seconds)

        return wrapper

    return decorator
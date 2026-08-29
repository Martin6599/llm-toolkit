import asyncio


def async_llm_retry(max_retry=3, sleep_seconds=1.0):
    """
    异步接口重试装饰器：包 async 函数用（同步重试包不住 await 之后的异常）
    :param max_retry: 最大尝试次数（含首次）
    :param sleep_seconds: 重试前休眠时间（秒）
    :return: 包装后的协程函数；重试耗尽时抛出最后一次异常
    """

    def decorator(func):
        """装饰器工厂：接收异步函数，返回带重试逻辑的异步包装函数"""

        async def wrapper(*args, **kwargs):
            """带重试逻辑的异步包装函数：await 处捕获异常→重试或抛出"""
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)   # ← 区别2：await
                except Exception:
                    attempt += 1
                    if attempt >= max_retry:
                        raise
                    await asyncio.sleep(sleep_seconds)   # ← 区别3：异步 sleep

        return wrapper

    return decorator
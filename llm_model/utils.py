import time
from functools import wraps
import logging

def retry_on_error(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    重试装饰器
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟时间的增长倍数
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries == max_retries:
                        logging.error(f"最大重试次数已达到 ({max_retries}次), 最后一次错误: {str(e)}")
                        raise
                    
                    logging.warning(f"调用失败 (第{retries}次重试): {str(e)}")
                    logging.info(f"等待 {current_delay} 秒后重试...")
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return func(*args, **kwargs)
        return wrapper
    return decorator 
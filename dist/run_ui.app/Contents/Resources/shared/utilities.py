import os
import time
from typing import Callable
from functools import wraps
from core.logger import get_logger

logger = get_logger('utilities')

def retry(times: int = 3, delay: float = 1.0):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == times - 1:
                        logger.error(f"重试{times}次后仍然失败: {str(e)}")
                        raise
                    logger.warning(f"第{i+1}次尝试失败，{delay}秒后重试")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def take_screenshot(page, name: str, directory: str = 'screenshots'):
    try:
        os.makedirs(directory, exist_ok=True)
        filename = f"{name}_{time.strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(directory, filename)
        page.save_screenshot(filepath)
        logger.info(f"截图保存成功: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"截图失败: {str(e)}")
        return None 
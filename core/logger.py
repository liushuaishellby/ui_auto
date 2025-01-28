import logging
import os
from datetime import datetime
from typing import Optional

class LoggerManager:
    """
    日志管理器类
    管理所有日志实例，确保每个模块使用独立的日志器
    """
    
    _loggers = {}  # 存储所有日志器实例
    
    @classmethod
    def get_logger(cls, name: str, log_dir: str = "logs") -> logging.Logger:
        """
        获取或创建日志器实例
        
        Args:
            name: 日志器名称
            log_dir: 日志文件存储目录
            
        Returns:
            logging.Logger: 日志器实例
        """
        # 如果已存在该名称的日志器，直接返回
        if name in cls._loggers:
            return cls._loggers[name]
            
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建新的日志器
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # 创建文件处理器
        log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器到日志器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # 保存日志器实例
        cls._loggers[name] = logger
        return logger

def get_logger(name: str) -> logging.Logger:
    """
    获取日志器的便捷函数
    
    Args:
        name: 日志器名称
        
    Returns:
        logging.Logger: 日志器实例
    """
    return LoggerManager.get_logger(name) 
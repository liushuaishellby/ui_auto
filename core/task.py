import logging
import importlib.util
import os

class Task:
    def __init__(self, task_path=None):
        self.logger = logging.getLogger(__name__)
        self.task_path = task_path
        self.task_module = None
        if task_path and os.path.exists(task_path):
            try:
                # 动态加载任务脚本
                spec = importlib.util.spec_from_file_location("task_module", task_path)
                self.task_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.task_module)
            except Exception as e:
                self.logger.error(f"加载任务脚本失败: {str(e)}")

    def execute(self, browser):
        """执行任务的具体逻辑"""
        try:
            self.logger.info(f"开始执行任务，浏览器ID: {browser.user_id}")
            if not self.task_module:
                self.logger.error("任务脚本未加载")
                return False
                
            if hasattr(self.task_module, 'run_task'):
                # 执行任务脚本中的run_task函数
                return self.task_module.run_task(browser)
            else:
                self.logger.error("任务脚本中未找到run_task函数")
                return False
        except Exception as e:
            self.logger.error(f"任务执行失败: {str(e)}")
            return False 
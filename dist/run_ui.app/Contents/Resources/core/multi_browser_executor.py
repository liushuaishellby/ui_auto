from core.browser_manager import BrowserManager
from core.logger import get_logger
from core.ads_browser import AbsManager
import concurrent.futures
from typing import List, Dict, Any
import time
from shared.config import ADSB_CONFIG


logger = get_logger('multi_browser_executor')

class MultiBrowserExecutor:
    """多浏览器执行器"""
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0, max_concurrent_browsers: int = 3):
        self.browser_manager = BrowserManager()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_concurrent_browsers = max_concurrent_browsers
    
    def execute_with_retry(self, task: Any, page, browser_id: str) -> Dict:
        """执行单个任务（带重试机制）"""
        attempt = 0
        while attempt < self.max_retries:
            attempt += 1
            try:
                start_time = time.time()
                # 创建browser对象
                browser = self.browser_manager.get_browser(page)
                browser.user_id = browser_id
                result = task.execute(browser)
                execution_time = time.time() - start_time
                
                # 关闭当前浏览器页面
                try:
                    self.browser_manager.close_page(page)
                except Exception as close_error:
                    logger.error(f"关闭浏览器页面失败: {str(close_error)}")

                return {
                    'success': result,
                    'execution_time': execution_time,
                    'attempt': attempt
                }

            except Exception as e:
                logger.error(f"浏览器 {browser_id} 第 {attempt} 次尝试失败: {str(e)}")
                if attempt < self.max_retries:
                    logger.info(f"浏览器 {browser_id} 等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # 失败时也要关闭当前浏览器页面
                    try:
                        self.browser_manager.close_page(page)
                    except Exception as close_error:
                        logger.error(f"关闭浏览器页面失败: {str(close_error)}")
                    return {
                        'success': False,
                        'error': str(e),
                        'attempt': attempt
                    }
    
    def execute_browser_task(self, user_id: str, task: Any):
        """在线程中执行单个浏览器任务"""
        try:
            logger.info(f"正在启动浏览器: {user_id}")
            # 添加延迟，避免请求过于频繁
            time.sleep(2)  # 增加延迟到2秒
            # 启动浏览器获得debugport
            try:
                dp = self.ads_manager.start_and_get_debug_port(user_id)
            except (TimeoutError, RuntimeError, ValueError) as e:
                logger.error(f"浏览器 {user_id} 启动失败: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'attempt': 0
                }
                
            try:
                page = self.browser_manager.create_page(
                    page_id=f"page_{dp}",
                    debugger_address=dp
                )
            except Exception as e:
                logger.error(f"浏览器 {user_id} 页面创建失败: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'attempt': 0
                }
                
            logger.info(f"浏览器 {user_id} 启动成功，开始执行任务")
            return self.execute_with_retry(task, page, user_id)
                
        except Exception as e:
            logger.error(f"浏览器 {user_id} 任务执行失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'attempt': 0
            }
            
    def execute(self, task: Any) -> Dict[str, Dict]:
        """执行任务"""
        results = {}
        # 获取所有浏览器id
        self.ads_manager = AbsManager()
        if ADSB_CONFIG['group_name']:
            try:
                g_id = self.ads_manager.get_group_ids(ADSB_CONFIG)
                ADSB_CONFIG['group_id'] = g_id
            except Exception as e:
                logger.error(f"获取分组ID失败: {str(e)}")
                return results
                
        try:
            user_ids = self.ads_manager.get_ads_user_ids(ADSB_CONFIG)
        except Exception as e:
            logger.error(f"获取用户ID列表失败: {str(e)}")
            return results
            
        if not user_ids:
            logger.error("没有找到可用的浏览器")
            return results
            
        logger.info(f"Total browsers: {len(user_ids)}")
        logger.info(f"Max concurrent browsers: {self.max_concurrent_browsers}")
        
        # 使用设定的最大并发数
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_browsers) as executor:
            # 直接提交任务，包括浏览器启动
            future_to_id = {
                executor.submit(self.execute_browser_task, user_id, task): user_id 
                for user_id in user_ids
            }
            
            # 处理完成的任务
            for future in concurrent.futures.as_completed(future_to_id):
                browser_id = future_to_id[future]
                try:
                    results[browser_id] = future.result()
                    logger.info(f"浏览器 {browser_id} 任务完成")
                except Exception as e:
                    logger.error(f"浏览器 {browser_id} 任务执行失败: {str(e)}")
                    results[browser_id] = {
                        'success': False,
                        'error': str(e),
                        'attempt': 0
                    }
        
        return results

    def start_browser(self, user_id):
        try:
            # 添加延迟，避免请求过于频繁
            time.sleep(1)  # 每次启动浏览器前等待1秒
            browser = self.browser_class(user_id)
            browser.start()
            return browser
        except Exception as e:
            self.logger.error(f"浏览器 {user_id} 启动失败: {str(e)}")
            return None

    def execute_task(self, browser, user_id):
        try:
            if browser and browser.is_running():
                self.logger.info(f"浏览器 {user_id} 启动成功，开始执行任务")
                # 确保任务对象存在
                if hasattr(self, 'task') and self.task:
                    self.task.execute(browser)
                else:
                    self.logger.error(f"浏览器 {user_id} 没有可执行的任务")
            else:
                self.logger.error(f"浏览器 {user_id} 未正常启动，无法执行任务")
        except Exception as e:
            self.logger.error(f"浏览器 {user_id} 任务执行失败: {str(e)}")
        finally:
            self.logger.info(f"浏览器 {user_id} 任务完成") 
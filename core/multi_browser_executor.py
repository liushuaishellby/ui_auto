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
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.browser_manager = BrowserManager()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def execute_with_retry(self, task: Any, page, browser_id: str) -> Dict:
        """执行单个任务（带重试机制）"""
        try:
                start_time = time.time()
                result = task.execute(page)
                execution_time = time.time() - start_time
                self.browser_manager.close_all()

                return {
                    'success': result,
                    'execution_time': execution_time
                }
                
        except Exception as e:
                logger.error(f"浏览器 {browser_id} : {str(e)}")
                return {
                    'success': False,
                    'error': str(e)
                }
    
    def execute(self, task: Any) -> Dict[str, Dict]:
        """执行任务"""
        results = {}
        #获取所有浏览器id
        ads =  AbsManager()
        if ADSB_CONFIG['group_name']:
            g_id= ads.get_group_ids(ADSB_CONFIG)
            ADSB_CONFIG['group_id'] = g_id
        user_ids =ads.get_ads_user_ids(ADSB_CONFIG)
        print(user_ids)
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(user_ids)) as executor:
            futures = []

            for user_id in user_ids:
                try:
                    #启动浏览器 获得debugport
                    dp= ads.start_and_get_debug_port(user_id)
                    page = self.browser_manager.create_page(
                        page_id=f"page_{dp}",
                        debugger_address=dp
                    )
                    
                    future = executor.submit(self.execute_with_retry, task, page, user_id)
                    futures.append((user_id, future))
                    
                except Exception as e:
                    logger.error(f"浏览器 {user_id} 任务提交失败: {str(e)}")
                    results[user_id] = {
                        'success': False,
                        'error': str(e),
                        'attempt': 0
                    }
            
            for browser_id, future in futures:
                try:
                    result = future.result()
                    results[browser_id] = result
                except Exception as e:
                    logger.error(f"浏览器 {browser_id} 任务执行失败: {str(e)}")
                    results[browser_id] = {
                        'success': False,
                        'error': str(e),
                        'attempt': 0
                    }
                finally:
                   print(browser_id)
        
        return results 
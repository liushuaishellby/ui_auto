from DrissionPage import ChromiumPage, ChromiumOptions,Chromium
from typing import Dict, Optional
import threading
from core.logger import get_logger

logger = get_logger('browser_manager')

class BrowserManager:
    """浏览器管理器类
    使用 DrissionPage 的 URL 方式来启动和管理浏览器
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'pages'):
            self.pages: Dict[str, ChromiumPage] = {}
    
    def create_page(self, 
                   page_id: str = None,
                   debugger_address: str = None,
                   browser_config: str = None) -> ChromiumPage:
        """创建新的页面实例
        
        Args:
            page_id: 页面实例的唯一标识，如果为None则自动生成
            url: 要访问的URL，如果为None则使用默认URL
            debugger_address: 调试地址，如果为None则使用默认地址
            browser_config: 浏览器配置名称，如果指定则使用该配置
        
        Returns:
            ChromiumPage: 页面实例
        """
        # 使用默认配置或指定配置
        # if browser_config:
        #     config = BROWSER_CONFIG.get(browser_config, DEFAULT_BROWSER_CONFIG)
        # else:
        #     config = DEFAULT_BROWSER_CONFIG
        
        # 生成默认page_id
        if page_id is None:
            page_id = f"page_{len(self.pages) + 1}"
            
        if page_id in self.pages:
            raise ValueError(f"页面ID '{page_id}' 已存在")
        
        
        try:
            # 创建浏览器选项
            # chrome_options = ChromiumOptions(debugger_address)
            
            # 创建页面实例并访问URL
            page = Chromium(debugger_address)
            
            # 保存页面实例
            self.pages[page_id] = page
            logger.info(f"创建页面成功: {page_id}")
            
            return page
            
        except Exception as e:
            logger.error(f"创建页面失败: {str(e)}")
            raise
    
    def get_page(self, page_id: str) -> Optional[ChromiumPage]:
        """获取已存在的页面实例"""
        return self.pages.get(page_id)
    
    def close_page(self, page):
        """关闭指定页面实例"""
        # page = self.pages.pop(page_id, None)
        # if page:
        #     page.quit()
        #     logger.info(f"关闭页面: {page_id}")
        #关闭tab

        page.quit()
        logger.info(f"关闭页面: ")

    def get_browser(self, page) -> Chromium:
        """从页面实例获取浏览器实例"""
        if isinstance(page, Chromium):
            return page
        else:
            logger.error("无效的页面实例")
            return None

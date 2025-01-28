from core.logger import get_logger
from projects.project1.pages.login_page import LoginPage
from shared.constants import LOGIN_SELECTORS

logger = get_logger('login_task')

class LoginTask:
    """登录任务类"""
    def __init__(self, username: str = 'test_user', password: str = 'test_pass'):
        self.username = username
        self.password = password
        self.url = LOGIN_SELECTORS['login_url']
    
    def execute(self, page) -> bool:
        """执行登录任务
        
        Args:
            page: 浏览器页面实例
        
        Returns:
            bool: 登录是否成功
        """
        try:
            login_page = LoginPage(page)
            success = login_page.login(self.username, self.password)
            
            if success:
                logger.info(f"用户 {self.username} 登录成功")
                return True
            return False
            
        except Exception as e:
            logger.error(f"登录任务执行失败: {str(e)}")
            return False 
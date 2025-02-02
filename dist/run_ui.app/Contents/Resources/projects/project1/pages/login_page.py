from core.base_page import BasePage
from shared.constants import LOGIN_SELECTORS
from shared.utilities import retry

class LoginPage(BasePage):
    """登录页面类"""
    
    def __init__(self, page):
        super().__init__(page)
        self.selectors = LOGIN_SELECTORS
    
    @retry(times=3)
    def login(self, username: str, password: str) -> bool:
        """执行登录操作
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            bool: 登录是否成功
        """
        try:
            # 确保在登录页面
            if not self.page.url.endswith('/login'):
                self.page.get(self.selectors['login_url'])
            
            self.input_text(self.selectors['username_input'], username)
            self.input_text(self.selectors['password_input'], password)
            self.click(self.selectors['login_button'])
            
            # 等待登录成功标志
            self.find_element(self.selectors['login_success'], timeout=15)
            self.logger.info(f"用户 {username} 登录成功")
            return True
            
        except Exception as e:
            self.logger.error(f"登录失败: {str(e)}")
            raise 
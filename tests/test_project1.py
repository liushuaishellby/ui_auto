import unittest
from core.browser_manager import BrowserManager
from projects.project1.pages.login_page import LoginPage

class TestProject1(unittest.TestCase):
    def setUp(self):
        self.browser_manager = BrowserManager()
        self.browser = self.browser_manager.create_browser('test_browser')
    
    def tearDown(self):
        self.browser_manager.close_all()
    
    def test_login(self):
        login_page = LoginPage(self.browser)
        result = login_page.login('test_user', 'test_pass')
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main() 
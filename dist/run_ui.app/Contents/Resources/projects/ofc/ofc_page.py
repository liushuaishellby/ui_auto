from core.base_page import BasePage
from shared.constants import OFC_CONFIG


class OfcPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.selectors = OFC_CONFIG
        self.visit(self.selectors['url'])
        page.wait(3)



    def click_letgo(self):
        self.click(self.selectors['let_go'])
        self.logger.info('点击lets go 成功')

    def click_verify(self):
        self.click(self.selectors['verify'])
        self.logger.info('点击lets go 成功')

    def check_status(self):
        self.wait_s(3)
        return self.find_element(self.selectors['verify_time'])
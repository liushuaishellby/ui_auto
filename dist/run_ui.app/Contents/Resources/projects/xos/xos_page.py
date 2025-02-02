from core.base_page import BasePage
from shared.constants import XOS_CONFIG


class XosPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.selectors = XOS_CONFIG
        self.visit(self.selectors['url'])



    def check_in(self):
        self.click(self.selectors['check_in'])
        self.logger.info('点击签到 成功')

    def check_status(self):
        self.wait_s(3)
        return self.find_element(self.selectors['verify'])
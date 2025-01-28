from core.base_page import BasePage
from shared.constants import LE
from shared.utilities import retry
import time


class LePage(BasePage):
    """ly页面页面类"""

    def __init__(self, page):
        tab = page.new_tab()
        super().__init__(tab)
        self.selectors = LE
        self.visit(self.selectors['url'])
        self.tab.wait(3)
        self.ref_tab()
    def watch(self) -> bool:
        """执行观看操作
        """
        try:
            self.click(self.selectors['watch_btn'])
            # 等待搜索结果加载
            return True

        except Exception as e:
            print(e)
            self.logger.error(f"观看失败: {str(e)}")
            raise


    def share(self):
        """执行观看操作
        """
        try:
            self.cliks(self.selectors['share_btn'], 'span',1)
        except Exception as e:
            self.logger.error(f"分享失败: {str(e)}")
            raise

    def quote(self) -> bool:
        """执行观看操作
        """
        try:
            self.cliks(self.selectors['quote_btn'],'span')

            # 等待搜索结果加载
            return True

        except Exception as e:
            self.logger.error(f"引用失败: {str(e)}")
            raise

    def rf(self):
        """执行观看操作
        """
        try:
            self.cliks(self.selectors['rf_btn'],'span')
            # 等待搜索结果加载
        except Exception as e:
            self.logger.error(f"回复失败: {str(e)}")
            raise

    def rg(self):
        """执行观看操作
        """
        try:
            self.cliks(self.selectors['rg'], 'span')
        except Exception as e:
            self.logger.error(f"点赞失败: {str(e)}")
            raise

    def _verify(self,ele):
        try:
            ele.click()
            self.wait_s(3)
            # ele.click()
            result = self.find_elements(self.selectors['verify_text'])
            return result
        except Exception as e:
            raise e
    def verify_all(self):
        max_retries = 3  # 最大重试次数
        retry_count = 0  # 当前重试次数

        while retry_count < max_retries:
            try:
                eles = self.find_elements(self.selectors['verify_btn'])
                    # 等待搜索结果加载
                for ele in eles:
                    if ele.tag == 'span':
                        result = self._verify(ele)
                            #查看是否是提交不通过的情况
                        if  len(result) >= 3:
                            self.ref_tab()
                            retry_count += 1  # 增加重试次数
                            break

                            # self.verify_all()
                            # new_r = self._verify(ele)
                            # result = new_r
                        self.click(self.selectors['success'])
                else:
                    # 如果所有按钮都成功，返回 True
                    return True
            except Exception as e:
                self.logger.error(f"验证失败: {str(e)}")
                retry_count += 1  # 增加重试次数
                self.ref_tab()  # 刷新页面
        self.logger.error("达到最大重试次数，验证失败")
        return False

    def verify_(self):
        """
        处理弹窗
        """
        try:
            self.click(self.selectors['success'])
        except Exception as e:
            raise

    def if_verify(self):
        self.wait_s(3)
        ele = self.find_element(self.selectors['success'])
        if ele:
            ele.click()


from typing import Union, Optional, List
from DrissionPage import ChromiumPage
from core.logger import get_logger

class BasePage:
    """页面基类
    封装常用的页面操作方法
    """
    
    def __init__(self, tab):
        """
        Args:
            tab: DrissionPage的Tab对象
        """
        self.tab = tab
        self.logger = get_logger(self.__class__.__name__)
        
        # 设置滚动相关配置
        # self.tab.set.scroll.smooth(on_off=False)  # 关闭平滑滚动
        # self.tab.set.scroll.wait_complete(on_off=True)  # 等待滚动完成
    def visit(self, url: str):
        """访问指定URL
        
        Args:
            url: 要访问的网址
        """
        try:
            self.tab.get(url)
            self.logger.info(f"访问页面成功: {url}")
        except Exception as e:
            self.logger.error(f"访问页面失败: {url}, 错误: {str(e)}")
            raise
    
    def find_element(self, selector: str, timeout: int = 10):
        """查找单个元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间(秒)
        """
        try:

            return self.tab.ele(selector, timeout=timeout)

        except Exception as e:
            self.logger.error(f"查找元素失败: {selector}, 错误: {str(e)}")
            raise
    
    def find_elements(self, selector: str, timeout: int = 10) -> List:
        """查找多个元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间(秒)
        """
        try:
            return self.tab.eles(selector, timeout=timeout)
        except Exception as e:
            self.logger.error(f"查找元素失败: {selector}, 错误: {str(e)}")
            raise
    
    def click(self, selector: str, timeout: int = 10):
        """点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间(秒)
        """
        try:
            ele = self.find_element(selector, timeout).wait.clickable(raise_err=False)
            # self.tab.actions.move_to(ele_or_loc=ele)

            self.tab.wait(1)
            ele.click()
            self.logger.info(f"点击元素成功: {selector}")
        except Exception as e:
            self.logger.error(f"点击元素失败: {selector}, 错误: {str(e)}")
            raise

    def cliks(self, selector: str, tag = None,num : int = 0,timeout: int = 10):
        try:
            if tag :
                eles = self.find_elements(selector)
                for ele in eles:
                    if ele.tag == tag:
                        ele.click()
                        self.logger.info(f"点击元素成功: {selector}")
                        return True
                eles[num].click()
        except Exception as e:
            self.logger.error(f"点击元素失败: {selector}, 错误: {str(e)}")
            raise

    def input_text(self, selector: str, text: str, timeout: int = 10):
        """输入文本
        
        Args:
            selector: 元素选择器
            text: 要输入的文本
            timeout: 超时时间(秒)
        """
        try:
            self.tab.ele(selector, timeout=timeout).input(text)
            self.logger.info(f"输入文本成功: {selector}, 文本: {text}")
        except Exception as e:
            self.logger.error(f"输入文本失败: {selector}, 错误: {str(e)}")
            raise
    
    def get_text(self, selector: str, timeout: int = 10) -> str:
        """获取元素文本
        
        Args:
            selector: 元素选择器
            timeout: 超时时间(秒)
        """
        try:
            return self.tab.ele(selector, timeout=timeout).text
        except Exception as e:
            self.logger.error(f"获取文本失败: {selector}, 错误: {str(e)}")
            raise
    def get_tab_id(self):
        return self.tab.tab_id

    def get_handle(self):
        return self.tab.handle_alert()


    def wait_s(self,s=1):
        self.tab.wait(s)


    def ref_tab(self):
        self.tab.refresh()
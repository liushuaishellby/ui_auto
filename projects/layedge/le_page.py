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

    
    def check_task_status(self, selector: str,task_name:str) -> bool:
        """检查任务状态"""
        try:
            self.wait_s(2)
            eles = self.find_elements(selector)
            if not eles:
                self.logger.info(f"{task_name}任务未找到")
                return True
            if task_name in '点赞回复引用':
                if len(eles) <= 2:
                    self.logger.info(f"{task_name}任务未找到")
                    return True
            if len(eles) < 2:
                self.logger.info(f"{task_name}任务未找到")
                return True

            return False
        except Exception as e:
            self.logger.error(f"检查任务状态失败: {str(e)}")
            raise
    
    def watch(self) -> bool:
        """执行观看操作
        """
        try:
            if self.check_task_status(self.selectors['watch_btn'],'观看'):
                self.logger.info("观看任务已完成，跳过")
                return 
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
            if self.check_task_status(self.selectors['share_btn'],'分享'):
                self.logger.info("分享任务已完成，跳过")
                return 
            self.cliks(self.selectors['share_btn'], 'span',1)
        except Exception as e:
            self.logger.error(f"分享失败: {str(e)}")
            raise

    def quote(self) -> bool:
        """执行观看操作
        """
        try:
            if self.check_task_status(self.selectors['quote_btn'],'引用'):
                self.logger.info("引用任务已完成，跳过")
                return 
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
            if self.check_task_status(self.selectors['rf_btn'],'回复'):
                self.logger.info("回复任务已完成，跳过")
                return 
            self.cliks(self.selectors['rf_btn'],'span')
            # 等待搜索结果加载
        except Exception as e:
            self.logger.error(f"回复失败: {str(e)}")
            raise

    def rg(self):
        """执行观看操作
        """
        try:
            if self.check_task_status(self.selectors['rg'],'点赞'):
                self.logger.info("点赞任务已完成，跳过")
                return 
            self.cliks(self.selectors['rg'], 'span')
        except Exception as e:
            self.logger.error(f"点赞失败: {str(e)}")
            raise

    def _verify(self, ele):
        """单个验证按钮的验证处理"""
        try:
            # 验证前稍作等待，避免操作过快
            self.wait_s(2)
            ele.click()
            self.wait_s(3)
            result = self.find_elements(self.selectors['verify_text'])
            self.logger.info(f"验证结果数量: {len(result)}")
            return result
        except Exception as e:
            self.logger.error(f"验证处理失败: {str(e)}")
            raise

    def handle_verify_fail(self):
        """处理验证失败的情况"""
        try:
            self.click(self.selectors['verify_fail_close'])
            self.logger.info("关闭验证失败弹窗")
            self.logger.info("等待60秒后可重新验证...")
            self.wait_s(60)
            return True
        except Exception as e:
            self.logger.error(f"处理验证失败弹窗失败: {str(e)}")
            return False

    def verify_single_button(self, ele):
        """验证单个按钮直到成功"""
        while True:  # 一直尝试直到成功
            try:
                self.logger.info("开始验证尝试")
                result = self._verify(ele)
                
                # 验证失败的情况
                if len(result) >= 3:
                    self.logger.warning("验证未通过")
                    # 处理验证失败，等待60秒
                    if not self.handle_verify_fail():
                        self.logger.error("处理验证失败弹窗失败")
                        continue
                    continue
                
                # 验证成功
                try:
                    self.wait_s(2)  # 稍等一下再点击确认
                    self.click(self.selectors['success'])
                    self.logger.info("验证确认成功")
                    return True
                except Exception as e:
                    self.logger.error(f"点击确认按钮失败: {str(e)}")
            
            except Exception as e:
                self.logger.error(f"验证过程发生错误: {str(e)}")
                self.wait_s(2)

    def verify_all(self):
        """处理所有验证按钮"""
        try:
            # 查找所有验证按钮
            self.wait_s(2)
            eles = self.find_elements(self.selectors['verify_btn'])
            if not eles:
                self.logger.info("未找到验证按钮")
                return True

            self.logger.info(f"找到 {len(eles)} 个验证按钮")
            
            # 处理每个验证按钮
            for ele in eles:
                if ele.tag != 'span':
                    continue
                    
                # 验证当前按钮直到成功
                self.verify_single_button(ele)
            
            self.logger.info("所有验证按钮处理完成")
            return True
                    
        except Exception as e:
            self.logger.error(f"验证过程发生错误: {str(e)}")
            return False

    def verify_(self):
        """处理弹窗"""
        try:
            self.click(self.selectors['success'])
        except Exception as e:
            self.logger.error(f"处理弹窗失败: {str(e)}")
            raise

    def if_verify(self):
        """检查并处理验证按钮"""
        self.wait_s(3)
        ele = self.find_element(self.selectors['success'])
        if ele:
            ele.click()


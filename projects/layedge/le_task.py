from core.logger import get_logger
from projects.layedge.le_page import LePage
from shared.constants import BAIDU_SELECTORS

logger = get_logger('lay_task')


class LeTaske:
    """百度搜索任务类"""

    def execute(self, page) -> bool:
        """执行搜索任务

        Args:
            page: 浏览器页面实例

        Returns:
            bool: 搜索是否成功
        """
        try:
            le_page = LePage(page)
            tab_id = le_page.get_tab_id()
            le_page.if_verify()

            le_page.watch()
             # 切回之前的tab
            page.wait(3.5, 8.5)
            page.activate_tab(tab_id)

            le_page.share()
            page.wait(3.5, 8.5)
            page.activate_tab(tab_id)

            le_page.quote()
            page.wait(3.5, 8.5)
            page.activate_tab(tab_id)

            le_page.rf()
            page.wait(3.5, 8.5)
            page.activate_tab(tab_id)

            le_page.rg()
            page.wait(3.5, 8.5)
            page.activate_tab(tab_id)

            le_page.ref_tab()
            page.wait(3.5, 8.5)
            le_page.verify_all()
            page.wait(3.5, 8.5)

            page.close_tabs(tabs_or_ids=tab_id,others=True)
            logger.info(f'{page}已完成')
            return True

        except Exception as e:
            logger.error(f"{page}任务执行失败: {str(e)}")
            raise e
from projects.xos.xos_page import XosPage
from core.logger import get_logger

logger = get_logger(__name__)
class XosTask:
    @staticmethod
    def execute(page):
        xos_page = XosPage(page)
        tab_id = xos_page.get_tab_id()
        try:
            if  xos_page.check_status():
                logger.info('签到任务已完成')
                return
            xos_page.check_in()
            if not xos_page.check_status():
                logger.error('签到任务校验失败')
                return
            logger.info('签到任务校验失败')
        finally:
            page.close_tabs(tabs_or_ids=tab_id, others=True)
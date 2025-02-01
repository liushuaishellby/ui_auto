from core.logger import get_logger
from projects.ofc.ofc_page import OfcPage

logger = get_logger('ofc_task')


class OfcTask:
    @staticmethod
    def execute(page) :
        try:
            ofc_page = OfcPage(page)
            tab_id = ofc_page.get_tab_id()
            ofc_page.click_letgo()
            ofc_page.click_verify()
            if not ofc_page.check_status():
                logger.error('签到任务校验失败')
                return
            logger.info('签到任务校验失败')

        finally:
            page.close_tabs(tabs_or_ids=tab_id, others=True)


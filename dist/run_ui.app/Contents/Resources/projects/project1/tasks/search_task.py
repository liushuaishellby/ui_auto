from core.logger import get_logger
from projects.project1.pages.search_page import SearchPage

logger = get_logger('search_task')

class SearchTask:
    def __init__(self, keyword: str = '手机'):
        self.keyword = keyword
        self.url = 'https://example.com/search'
    
    def execute(self, page) -> bool:
        try:
            search_page = SearchPage(page)
            return search_page.search(self.keyword)
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return False 
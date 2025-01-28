from core.multi_browser_executor import MultiBrowserExecutor
from projects.project1.tasks.login_task import LoginTask
from core.browser_manager import BrowserManager

def main():
    # 1. 使用默认配置创建浏览器
    browser_manager = BrowserManager()
    page = browser_manager.create_page()  # 使用所有默认值
    
    # 2. 只指定页面ID
    page = browser_manager.create_page(page_id='my_page')
    
    # 3. 使用预定义的浏览器配置
    page = browser_manager.create_page(browser_config='chrome_1')
    
    # 4. 在多浏览器执行器中使用
    login_task = LoginTask(
        username='test_user',
        password='test_pass'
    )
    
    # 如果不指定browser_ids，使用默认配置
    executor = MultiBrowserExecutor(max_retries=3, retry_delay=2.0)
    results = executor.execute(login_task, ['chrome_1'])  # 或者不传browser_ids
    
    # 输出详细结果
    for browser_id, result in results.items():
        success = result['success']
        attempts = result.get('attempt', 0)
        execution_time = result.get('execution_time', 0)
        error = result.get('error', '')
        
        status = '成功' if success else f'失败 ({error})'
        print(f"浏览器 {browser_id}:")
        print(f"  状态: {status}")
        print(f"  尝试次数: {attempts}")
        print(f"  执行时间: {execution_time:.2f}秒")
        print("---")

if __name__ == '__main__':
    main() 
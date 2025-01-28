from core.multi_browser_executor import MultiBrowserExecutor
from projects.layedge.le_task import LeTaske


def main():
    le_task = LeTaske()


    # 创建执行器并运行任务
    executor = MultiBrowserExecutor(max_retries=3, retry_delay=2.0)
    results = executor.execute(le_task)

    # 输出结果
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


if __name__ == '__main__':
    main()

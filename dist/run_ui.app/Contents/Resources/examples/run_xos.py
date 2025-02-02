from core.multi_browser_executor import MultiBrowserExecutor
from projects.xos.xos_task import XosTask

# 在任务脚本文件中
task_desc = "xos每日签到"

def main():

    # 创建执行器并运行任务
    executor = MultiBrowserExecutor(max_retries=3, retry_delay=2.0,max_concurrent_browsers=2)
    results = executor.execute(XosTask)
    print(results)




if __name__ == '__main__':
    main()

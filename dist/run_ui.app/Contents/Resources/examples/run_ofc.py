from core.multi_browser_executor import MultiBrowserExecutor
from projects.ofc.ofc_task import OfcTask

# 在任务脚本文件中
task_desc = "ofcfotall每日签到"

def main():

    # 创建执行器并运行任务
    executor = MultiBrowserExecutor(max_retries=3, retry_delay=2.0,max_concurrent_browsers=2)
    results = executor.execute(OfcTask)
    print(results)




if __name__ == '__main__':
    main()

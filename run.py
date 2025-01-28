import argparse
from core.config import Config
from projects.project1.tasks.login_task import execute_login
from core.logger import get_logger

logger = get_logger('main')

def main():
    parser = argparse.ArgumentParser(description='自动化任务运行器')
    parser.add_argument('--task', type=str, required=True, help='要执行的任务名称')
    parser.add_argument('--config', type=str, default='config.json', help='配置文件路径')
    
    args = parser.parse_args()
    config = Config(args.config)
    
    if args.task == 'login':
        username = config.get('username', 'default_user')
        password = config.get('password', 'default_pass')
        success = execute_login(username, password)
        
        if success:
            logger.info("任务执行成功")
        else:
            logger.error("任务执行失败")
    else:
        logger.error(f"未知的任务类型: {args.task}")

if __name__ == '__main__':
    main() 
import requests
from requests.exceptions import SSLError, RequestException
import urllib3
import json

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AbsManager:
    def __init__(self):
        self.BASE_URL = 'http://127.0.0.1:50325'  # 修改为本地地址

    def start_and_get_debug_port(self, data):
        """
        启动并获取debug_port
        """
        try:
            tab = requests.get(f'{self.BASE_URL}/api/v1/browser/start', params={"user_id":data}, verify=False)
            port = tab.json()['data']['debug_port']
            return f'127.0.0.1:{port}'
        except RequestException as e:
            print(f"Error starting browser: {e}")
            raise

    def get_ads_user_ids(self, data) -> list[str]:
        """
        获取用户ID列表
        Returns:
            list[str]: 用户ID列表
        """
        try:
            response = requests.get(f'{self.BASE_URL}/api/v1/user/list', 
                                   params=data, 
                                   verify=False,
                                   timeout=10)
            
            # 检查响应状态码
            response.raise_for_status()
            
            # 打印响应内容以便调试
            
            try:
                json_data = response.json()
                return [item['user_id'] for item in json_data['data']['list']]
            except json.JSONDecodeError as e:
                raise
            except KeyError as e:
                raise
                
        except RequestException as e:
            raise

    # def get_ads_debug_(self):
    #     info_list = requests.get(self.BASE_URLf + ':50325/api/v1/user/list')
    #     return info_list.json()['data']


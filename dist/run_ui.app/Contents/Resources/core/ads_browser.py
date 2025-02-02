import requests
from requests.exceptions import SSLError, RequestException
import urllib3
import json
from core.logger import get_logger

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger('ads_browser')

class AbsManager:
    def __init__(self):
        self.BASE_URL = 'http://127.0.0.1:50325'  # 修改为本地地址

    def start_and_get_debug_port(self, data):
        """
        启动并获取debug_port
        """
        try:
            logger.info(f"正在启动浏览器，user_id: {data}")
            response = requests.get(
                f'{self.BASE_URL}/api/v1/browser/start',
                params={"user_id": data},
                verify=False,
                timeout=10
            )
            
            # 检查响应状态码
            response.raise_for_status()
            
            # 记录原始响应
            logger.debug(f"启动浏览器响应: {response.text}")
            
            # 解析响应数据
            try:
                json_data = response.json()
                if 'data' not in json_data:
                    logger.error(f"响应中缺少data字段: {json_data}")
                    raise ValueError(f"Invalid response format: {json_data}")
                if 'debug_port' not in json_data['data']:
                    logger.error(f"响应中缺少debug_port字段: {json_data['data']}")
                    raise ValueError(f"Invalid response format: {json_data}")
                    
                port = json_data['data']['debug_port']
                debug_address = f'127.0.0.1:{port}'
                logger.info(f"浏览器启动成功，debug地址: {debug_address}")
                return debug_address
                
            except json.JSONDecodeError as e:
                logger.error(f"解析响应JSON失败: {e}, 响应内容: {response.text}")
                raise ValueError(f"Failed to parse response: {e}")
            except KeyError as e:
                logger.error(f"响应格式错误: {e}, 响应内容: {json_data}")
                raise ValueError(f"Missing required field in response: {e}")
                
        except requests.exceptions.Timeout:
            logger.error(f"启动浏览器超时")
            raise TimeoutError("Request timed out while starting browser")
        except requests.exceptions.RequestException as e:
            logger.error(f"启动浏览器请求失败: {e}")
            raise RuntimeError(f"Failed to start browser: {e}")
        except Exception as e:
            logger.error(f"启动浏览器时发生未知错误: {e}")
            raise RuntimeError(f"Unexpected error while starting browser: {e}")

    def get_ads_user_ids(self, data) -> list[str]:
        """
        获取用户ID列表
        Returns:
            list[str]: 用户ID列表
        """
        try:
            logger.info("正在获取用户ID列表")
            response = requests.get(
                f'{self.BASE_URL}/api/v1/user/list', 
                params=data, 
                verify=False,
                timeout=10
            )
            
            # 检查响应状态码
            response.raise_for_status()
            
            # 记录原始响应
            logger.debug(f"获取用户列表响应: {response.text}")
            
            try:
                json_data = response.json()
                if 'data' not in json_data or 'list' not in json_data['data']:
                    logger.error(f"响应格式错误: {json_data}")
                    raise ValueError(f"Invalid response format: {json_data}")
                    
                user_ids = [item['user_id'] for item in json_data['data']['list']]
                logger.info(f"成功获取到 {len(user_ids)} 个用户ID")
                return user_ids
                
            except json.JSONDecodeError as e:
                logger.error(f"解析响应JSON失败: {e}, 响应内容: {response.text}")
                raise ValueError(f"Failed to parse response: {e}")
            except KeyError as e:
                logger.error(f"响应格式错误: {e}, 响应内容: {json_data}")
                raise ValueError(f"Missing required field in response: {e}")
                
        except requests.exceptions.Timeout:
            logger.error("获取用户列表超时")
            raise TimeoutError("Request timed out while getting user list")
        except requests.exceptions.RequestException as e:
            logger.error(f"获取用户列表请求失败: {e}")
            raise RuntimeError(f"Failed to get user list: {e}")
        except Exception as e:
            logger.error(f"获取用户列表时发生未知错误: {e}")
            raise RuntimeError(f"Unexpected error while getting user list: {e}")

    def get_group_ids(self, data) -> list[str]:
        """
        获取分组ID列表
        Returns:
            list[str]: 分组ID列表
        """
        try:
            logger.info("正在获取分组ID列表")
            response = requests.get(
                f'{self.BASE_URL}/api/v1/group/list',
                params=data,
                verify=False,
                timeout=10
            )
            
            # 检查响应状态码
            response.raise_for_status()
            
            # 记录原始响应
            logger.debug(f"获取分组列表响应: {response.text}")
            
            try:
                json_data = response.json()
                if 'data' not in json_data or 'list' not in json_data['data']:
                    logger.error(f"响应格式错误: {json_data}")
                    raise ValueError(f"Invalid response format: {json_data}")
                    
                group_ids = [item['group_id'] for item in json_data['data']['list']]
                logger.info(f"成功获取到 {len(group_ids)} 个分组ID")
                return group_ids
                
            except json.JSONDecodeError as e:
                logger.error(f"解析响应JSON失败: {e}, 响应内容: {response.text}")
                raise ValueError(f"Failed to parse response: {e}")
            except KeyError as e:
                logger.error(f"响应格式错误: {e}, 响应内容: {json_data}")
                raise ValueError(f"Missing required field in response: {e}")
                
        except requests.exceptions.Timeout:
            logger.error("获取分组列表超时")
            raise TimeoutError("Request timed out while getting group list")
        except requests.exceptions.RequestException as e:
            logger.error(f"获取分组列表请求失败: {e}")
            raise RuntimeError(f"Failed to get group list: {e}")
        except Exception as e:
            logger.error(f"获取分组列表时发生未知错误: {e}")
            raise RuntimeError(f"Unexpected error while getting group list: {e}")
    # def get_ads_debug_(self):
    #     info_list = requests.get(self.BASE_URLf + ':50325/api/v1/user/list')
    #     return info_list.json()['data']


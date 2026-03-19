import requests
from requests.exceptions import RequestException

def get(url, headers=None, params=None, timeout=10):
    """发送GET请求"""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        return response
    except RequestException as e:
        from .logger import logger
        logger.error(f"HTTP请求失败: {url} - {str(e)}")
        return None

def post(url, headers=None, data=None, timeout=10):
    """发送POST请求"""
    try:
        response = requests.post(url, headers=headers, data=data, timeout=timeout)
        response.raise_for_status()
        return response
    except RequestException as e:
        from .logger import logger
        logger.error(f"HTTP请求失败: {url} - {str(e)}")
        return None
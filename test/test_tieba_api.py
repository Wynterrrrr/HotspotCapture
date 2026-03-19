import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

def fetch_tieba_topic_list():
    """
    安全获取百度贴吧热榜数据，包含重试和超时处理
    """
    # 目标URL
    url = "http://tieba.baidu.com/hottopic/browse/topicList"
    
    # 配置请求头，模拟浏览器访问，避免被识别为爬虫
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive"
    }
    
    # 创建会话并配置重试策略
    session = requests.Session()
    # 配置重试规则：重试3次，针对指定的状态码和异常类型
    retry_strategy = Retry(
        total=3,  # 总重试次数
        backoff_factor=1,  # 重试间隔时间（秒），每次重试间隔 = backoff_factor * (2 ^ (重试次数-1))
        status_forcelist=[429, 500, 502, 503, 504],  # 遇到这些状态码时重试
        allowed_methods=["GET"],  # 只对GET请求重试
        raise_on_status=False  # 不抛出状态码异常
    )
    
    # 挂载重试适配器
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    try:
        # 发送请求，设置更合理的超时时间（连接超时5秒，读取超时20秒）
        response = session.get(
            url=url,
            headers=headers,
            timeout=(5, 20),  # (connect_timeout, read_timeout)
            verify=True  # 验证SSL证书
        )
        
        # 检查响应状态码
        response.raise_for_status()
        
        # 返回响应数据
        return response.json()
    
    except requests.exceptions.ConnectTimeout:
        print("错误：连接百度贴吧服务器超时")
        return None
    except requests.exceptions.ReadTimeout:
        print("错误：读取百度贴吧响应数据超时")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"错误：HTTP请求失败，状态码：{e.response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"错误：请求发生异常 - {str(e)}")
        return None
    finally:
        # 关闭会话
        session.close()

# 测试调用
if __name__ == "__main__":
    # 增加请求间隔，避免频繁请求被限流
    time.sleep(1)
    result = fetch_tieba_topic_list()
    if result:
        print("请求成功，数据示例：", result.get("data", {}).get("topic_list", [])[:1])
    else:
        print("请求失败，请检查网络或稍后重试")
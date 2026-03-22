"""
AI 深度分析模块 - 直接调用大模型 API
支持火山引擎和 SiliconFlow 作为备用
"""

import asyncio
import httpx
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# 火山引擎配置
VOLC_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
VOLC_API_KEY = "eddc9c36-e7d6-460a-93b9-8f8b9be7829d"
VOLC_MODELS = [
    "deepseek-v3-2-251201",
    "glm-4-7-251222",
    "deepseek-r1-250528",
]

# SiliconFlow 备用配置
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
SILICONFLOW_API_KEY = "sk-rsxpfypqyycvubfcagyemeodihizltjmpwhasmsgufmttukm"
SILICONFLOW_MODEL = "Pro/MiniMaxAI/MiniMax-M2.5"  # SiliconFlow 的模型 ID

# 分析提示词
ANALYSIS_PROMPT = """你是热点新闻分析专家。请对以下热点数据进行深度分析，生成一份结构化的分析报告。

要求：
1. 总结热点要类型和趋势
2. 分析不同平台热点之间的关联性
3. 识别重要社会议题和潜在影响
4. 总结各个平台的热点差异，特别上热点了但是各平台排序不一的
输出格式要求（Markdown）：
- 使用中文
- 结构清晰，分点论述
- 避免冗长重复

以下是今日热点数据：

{hotnews_content}
"""


def log(msg: str):
    """简单日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


async def call_llm_api(
    client: httpx.AsyncClient,
    base_url: str,
    api_key: str,
    model: str,
    content: str,
    timeout: float = 120.0,
) -> Tuple[bool, str]:
    """
    调用大模型 API
    返回: (成功与否, 响应内容或错误信息)
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.7,
        "max_tokens": 4096,
    }

    url = f"{base_url}/chat/completions"

    try:
        response = await client.post(
            url,
            headers=headers,
            json=payload,
            timeout=timeout,
        )

        if response.status_code == 200:
            data = response.json()
            result = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return True, result
        else:
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            return False, error_msg

    except httpx.TimeoutException:
        return False, "请求超时"
    except Exception as e:
        return False, str(e)


async def try_all_models(md_content: str) -> Tuple[Optional[str], Optional[str]]:
    """
    尝试所有模型，返回成功的模型ID和分析结果
    返回: (模型ID, 分析结果) 或 (None, 错误信息)
    """
    async with httpx.AsyncClient() as client:
        prompt = ANALYSIS_PROMPT.format(hotnews_content=md_content[:32000])  # 限制长度

        # 1. 尝试火山引擎的三个模型
        for model in VOLC_MODELS:
            log(f"🔄 尝试火山引擎模型: {model}")
            success, result = await call_llm_api(
                client, VOLC_BASE_URL, VOLC_API_KEY, model, prompt
            )
            if success:
                log(f"✅ 火山引擎模型 {model} 调用成功")
                return model, result
            else:
                log(f"❌ 火山引擎模型 {model} 失败: {result}")

        # 2. 所有火山引擎模型失败，尝试 SiliconFlow
        log("🔄 火山引擎全部失败，尝试 SiliconFlow 备用接口...")
        success, result = await call_llm_api(
            client, SILICONFLOW_BASE_URL, SILICONFLOW_API_KEY, SILICONFLOW_MODEL, prompt
        )
        if success:
            log(f"✅ SiliconFlow 调用成功")
            return "siliconflow-deepseek-v3", result
        else:
            log(f"❌ SiliconFlow 失败: {result}")
            return None, result


def generate_analysis_markdown(
    analysis: str, model_id: str, exec_time: datetime
) -> str:
    """生成分析报告 Markdown"""
    return f"""# 🧠 AI 热点分析报告

> 生成时间：{exec_time.strftime("%Y-%m-%d %H:%M:%S")} (北京时间)
> 分析模型：{model_id}

---

## 📊 分析结果

{analysis}

---

<p align="center">
<i>自动生成 | {exec_time.strftime("%Y-%m-%d")}</i>
</p>
"""


def generate_failure_markdown(exec_time: datetime, error: str) -> str:
    """生成失败报告 Markdown"""
    return f"""# ❌ AI 分析失败报告

> 生成时间：{exec_time.strftime("%Y-%m-%d %H:%M:%S")} (北京时间)
> 状态：失败

---

## ⚠️ 失败原因

{error}

---

## 🔧 重试建议

1. 检查网络连接
2. 确认 API Key 是否有效
3. 稍后手动重试

---

<p align="center">
<i>自动生成 | {exec_time.strftime("%Y-%m-%d")}</i>
</p>
"""


async def run_deep_analysis(
    md_content: str, output_dir: Path, exec_time: datetime
) -> Optional[Path]:
    """
    执行深度分析并保存结果
    返回生成的文件路径，失败返回 None
    """
    log("🚀 启动 AI 深度分析...")

    # 尝试调用所有模型
    model_id, result = await try_all_models(md_content)

    # 生成文件名基础部分
    time_str = exec_time.strftime("%Y-%m-%d_%H-%M")

    if model_id:
        # 成功：文件名加模型ID
        content = generate_analysis_markdown(
            result or "分析结果为空", model_id, exec_time
        )
        filename = f"{time_str}_{model_id}.md"
    else:
        # 失败：文件名加"失败"后缀
        content = generate_failure_markdown(exec_time, result or "未知错误")
        filename = f"{time_str}_失败.md"

    # 保存文件
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    if model_id:
        log(f"✅ 分析报告已保存: {filepath}")
    else:
        log(f"⚠️ 失败报告已保存: {filepath}")

    return filepath


# 测试入口
if __name__ == "__main__":

    async def test():
        test_content = """
# 测试热点数据
1. 微博热搜测试
2. B站热门测试
"""
        result = await run_deep_analysis(
            test_content,
            Path(__file__).parent / "hotnews_output",
            datetime.now(),
        )
        print(f"结果文件: {result}")

    asyncio.run(test())

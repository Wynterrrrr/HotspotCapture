"""
热点数据定时抓取与推送系统
每日执行四次：北京时间 6:00, 11:00, 16:00, 21:00
"""

import asyncio
import os
import sys
import base64
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import urllib.request
import urllib.error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# ===================== 配置 =====================
OUTPUT_DIR = Path(__file__).parent / "hotnews_output"

# GitHub API 推送配置（无需克隆仓库）
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # 从环境变量读取
GITHUB_REPO = os.environ.get(
    "GITHUB_REPO", "Wynterrrrr/ObsdianDrive"
)  # 仓库：owner/repo
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")  # 目标分支
GITHUB_TARGET_DIR = "hotnews"  # 仓库内目标目录

# 邮件配置
EMAIL_FROM = "1784151291@qq.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "fdtbxvedkjwrfagf")
EMAIL_TO = "wenzhonghua163@163.com"
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))


# ===================== 平台配置 =====================
# 格式: (显示名称, 模块路径, 函数名)
PLATFORMS = [
    ("虎扑", "routers.hupu", "get_hupu_hot"),
    ("抖音", "routers.douyin", "get_douyin_hot"),
    ("微博", "routers.weibo", "get_weibo_hot"),
    ("今日头条", "routers.toutiao", "get_toutiao_hot"),
    ("掘金", "routers.juejin", "get_juejin_hot"),
    ("哔哩哔哩", "routers.bilibili", "get_bilibili_hot"),
    ("知乎", "routers.zhihu", "get_zhihu_hot"),
    ("豆瓣电影", "routers.douban_movie", "get_douban_movie_hot"),
    ("贴吧", "routers.tieba", "get_tieba_hot"),
    ("GitHub", "routers.github", "get_github_hot"),
    ("汽车之家", "routers.autohome", "get_autohome_hot"),
    ("财联社", "routers.cls", "get_cls_hot"),
    ("网易新闻", "routers.netease_news", "get_netease_news_hot"),
    ("腾讯新闻", "routers.qq_news", "get_qq_news_hot"),
    # 新增平台
    ("快手", "routers.kuaishou", "get_kuaishou_hot"),
    ("NGA玩家社区", "routers.ngabbs", "get_ngabbs_hot"),
    ("V2EX", "routers.v2ex", "get_v2ex_hot"),
    ("少数派", "routers.sspai", "get_sspai_hot"),
]


def log(msg: str):
    """简单日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


async def fetch_platform(
    display_name: str, module_path: str, func_name: str
) -> Dict[str, Any]:
    """抓取单个平台数据"""
    import importlib

    try:
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)

        # 调用异步函数获取数据
        result = await func()

        return {"name": display_name, "data": result, "success": True, "error": None}
    except Exception as e:
        log(f"❌ {display_name} 抓取失败: {str(e)}")
        return {"name": display_name, "data": None, "success": False, "error": str(e)}


async def fetch_all_platforms() -> Dict[str, Dict[str, Any]]:
    """并行抓取所有平台"""
    log("🚀 开始抓取所有平台热点数据...")

    tasks = [fetch_platform(*platform) for platform in PLATFORMS]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output = {}
    for platform, result in zip(PLATFORMS, results):
        display_name = platform[0]
        if isinstance(result, Exception):
            output[display_name] = {
                "name": display_name,
                "data": None,
                "success": False,
                "error": str(result),
            }
        else:
            output[display_name] = result

    success_count = sum(1 for r in output.values() if r["success"])
    log(f"✅ 抓取完成: {success_count}/{len(PLATFORMS)} 成功")

    return output


def generate_markdown(results: Dict[str, Dict[str, Any]], exec_time: datetime) -> str:
    """生成Markdown文档"""

    md = f"""# 📰 今日热点汇总

> 生成时间：{exec_time.strftime("%Y-%m-%d %H:%M:%S")} (北京时间)

---

"""

    for display_name, result in results.items():
        if not result["success"]:
            md += f"""## 🔴 {display_name}

> ⚠️ 数据获取失败: {result.get("error", "未知错误")}

---

"""
            continue

        data = result.get("data") or {}
        items = data.get("data", [])
        title = data.get("title", display_name)
        url = data.get("url", data.get("link", ""))

        md += f"""## 🔥 {title}

"""
        if url:
            md += f"> 来源: [{url}]({url})\n"
        md += f"> 共 {len(items)} 条热点\n\n"

        for i, item in enumerate(items[:20], 1):
            item_title = item.get("title", "无标题")
            item_url = item.get("url", item.get("mobileUrl", ""))
            item_hot = item.get("hot", item.get("stars", ""))

            # 格式化热度
            hot_text = ""
            if item_hot:
                try:
                    hot_val = (
                        int(item_hot) if not isinstance(item_hot, int) else item_hot
                    )
                    if hot_val >= 10000:
                        hot_text = f"🔥 {hot_val / 10000:.1f}万"
                    else:
                        hot_text = f"🔥 {hot_val}"
                except:
                    hot_text = f"🔥 {item_hot}"

            if item_url:
                md += f"{i}. [{item_title}]({item_url})"
            else:
                md += f"{i}. {item_title}"

            if hot_text:
                md += f" {hot_text}"
            md += "\n"

        md += "\n---\n\n"

    md += f"""
---

<p align="center">
<i>{exec_time.strftime("%Y-%m-%d")}</i>
</p>
"""

    return md


def save_markdown(content: str, exec_time: datetime) -> Path:
    """保存Markdown文件"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 文件名: YYYY-MM-DD_HH-MM.md
    filename = f"{exec_time.strftime('%Y-%m-%d_%H-%M')}.md"
    filepath = OUTPUT_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    log(f"📄 Markdown文件已保存: {filepath}")
    return filepath


async def run_deepseek_analysis(md_content: str, exec_time: datetime) -> Optional[Path]:
    """运行DeepSeek深度思考分析"""
    try:
        from deepseek_thinker import run_deep_analysis

        log("🧠 启动 DeepSeek 深度思考分析...")
        think_filepath = await run_deep_analysis(md_content, OUTPUT_DIR, exec_time)

        if think_filepath:
            log(f"✅ 深度思考文档已生成: {think_filepath}")
            return think_filepath
        else:
            log("⚠️ 深度思考分析未生成结果")
            return None

    except ImportError:
        log("⚠️ deepseek_thinker 模块未找到，跳过深度思考")
        return None
    except Exception as e:
        log(f"❌ DeepSeek 深度思考失败: {str(e)}")
        return None


def github_api_request(
    method: str, path: str, data: Optional[dict] = None
) -> tuple[int, dict]:
    """发送 GitHub API 请求"""
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "HotspotCapture/1.0",
    }

    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        return e.code, {"error": error_body}
    except Exception as e:
        return 0, {"error": str(e)}


def push_file_to_github(local_path: Path, remote_path: str, commit_msg: str) -> bool:
    """通过 GitHub API 推送单个文件"""
    if not GITHUB_TOKEN:
        log("❌ 未配置 GITHUB_TOKEN 环境变量")
        return False

    # 读取并编码文件内容
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # 检查文件是否已存在（获取 sha）
    status, result = github_api_request(
        "GET", f"/repos/{GITHUB_REPO}/contents/{remote_path}?ref={GITHUB_BRANCH}"
    )

    sha = None
    if status == 200:
        sha = result.get("sha")
        log(f"📄 文件已存在，将更新: {remote_path}")
    elif status == 404:
        log(f"📄 创建新文件: {remote_path}")
    else:
        log(f"⚠️ 检查文件状态异常: {result.get('error', '未知')}")

    # 构建请求体
    payload = {"message": commit_msg, "content": content, "branch": GITHUB_BRANCH}
    if sha:
        payload["sha"] = sha

    # 推送文件
    status, result = github_api_request(
        "PUT", f"/repos/{GITHUB_REPO}/contents/{remote_path}", payload
    )

    if status in (200, 201):
        log(f"✅ 推送成功: {remote_path}")
        return True
    else:
        log(f"❌ 推送失败: {result.get('message', result.get('error', '未知'))}")
        return False


def push_to_github(
    filepath: Path, exec_time: datetime, thinking_filepath: Optional[Path] = None
) -> bool:
    """推送到 GitHub（通过 REST API，无需克隆仓库）"""
    try:
        commit_msg = f"docs: 更新热点数据 {exec_time.strftime('%Y-%m-%d %H:%M')}"
        success = True

        # 推送热点文件
        remote_path = f"{GITHUB_TARGET_DIR}/{filepath.name}"
        if not push_file_to_github(filepath, remote_path, commit_msg):
            success = False

        # 推送深度思考文件（如果有）
        if thinking_filepath and thinking_filepath.exists():
            thinking_remote = f"{GITHUB_TARGET_DIR}/{thinking_filepath.name}"
            if not push_file_to_github(thinking_filepath, thinking_remote, commit_msg):
                success = False

        if success:
            log(f"✅ 已成功推送到 GitHub ({GITHUB_REPO})")
        return success

    except Exception as e:
        log(f"❌ 推送 GitHub 失败: {str(e)}")
        return False


def send_email_notification(
    filepath: Path, thinking_filepath: Optional[Path] = None
) -> bool:
    """发送邮件通知新产生的文件"""
    try:
        # 读取主文件内容
        with open(filepath, "r", encoding="utf-8") as f:
            file_content = f.read()

        file_name = filepath.name
        file_url = f"https://github.com/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/{GITHUB_TARGET_DIR}/{file_name}"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[HotNews] 新文件通知 - {file_name}"
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        # 构建纯文本内容
        text_content = f"""
HotNews 文件夹新增文件通知

文件名: {file_name}
时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
链接: {file_url}

{"=" * 50}
文件内容:
{"=" * 50}

{file_content}
"""

        # 构建 HTML 内容
        html_content = f"""
<html>
<body>
    <h2>HotNews 文件夹新增文件通知</h2>
    <p><strong>文件名:</strong> {file_name}</p>
    <p><strong>时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p><strong>链接:</strong> <a href="{file_url}">{file_url}</a></p>
    <hr>
    <h3>文件内容:</h3>
    <pre style="background-color:#f5f5f5;padding:15px;border-radius:5px;white-space:pre-wrap;word-wrap:break-word;">{file_content}</pre>
</body>
</html>
"""

        msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        log(f"📧 正在连接SMTP服务器: {SMTP_SERVER}:{SMTP_PORT}")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            log(f"📧 SMTP连接成功，正在登录...")
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            log(f"📧 登录成功，正在发送邮件...")
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

        log(f"✅ 邮件已发送: {file_name}")

        # 如果有深度思考文件，也发送邮件
        if thinking_filepath and thinking_filepath.exists():
            # 等待1分钟后发送第二封邮件
            log(f"⏳ 等待60秒后发送深度思考文件...")
            time.sleep(60)

            with open(thinking_filepath, "r", encoding="utf-8") as f:
                think_content = f.read()

            think_name = thinking_filepath.name
            think_url = f"https://github.com/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/{GITHUB_TARGET_DIR}/{think_name}"

            msg2 = MIMEMultipart("alternative")
            msg2["Subject"] = f"[HotNews] 深度思考文件 - {think_name}"
            msg2["From"] = EMAIL_FROM
            msg2["To"] = EMAIL_TO

            text2 = f"""
深度思考文件通知

文件名: {think_name}
时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
链接: {think_url}

{"=" * 50}
文件内容:
{"=" * 50}

{think_content}
"""

            html2 = f"""
<html>
<body>
    <h2>深度思考文件通知</h2>
    <p><strong>文件名:</strong> {think_name}</p>
    <p><strong>时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p><strong>链接:</strong> <a href="{think_url}">{think_url}</a></p>
    <hr>
    <h3>文件内容:</h3>
    <pre style="background-color:#f5f5f5;padding:15px;border-radius:5px;white-space:pre-wrap;word-wrap:break-word;">{think_content}</pre>
</body>
</html>
"""

            msg2.attach(MIMEText(text2, "plain", "utf-8"))
            msg2.attach(MIMEText(html2, "html", "utf-8"))

            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.sendmail(EMAIL_FROM, EMAIL_TO, msg2.as_string())

            log(f"✅ 邮件已发送: {think_name}")

        return True

    except Exception as e:
        log(f"❌ 邮件发送失败: {str(e)}")
        return False


def clear_output_folder():
    """清空 hotnews_output 文件夹"""
    try:
        if OUTPUT_DIR.exists():
            for file in OUTPUT_DIR.iterdir():
                if file.is_file():
                    file.unlink()
                    log(f"🗑️ 已删除: {file.name}")
            log(f"✅ hotnews_output 文件夹已清空")
    except Exception as e:
        log(f"❌ 清空文件夹失败: {str(e)}")


def generate_failure_report(
    exec_time: datetime, results: Dict[str, Dict[str, Any]]
) -> str:
    """生成数据采集失败的报告"""
    fail_details = []
    for name, result in results.items():
        if not result["success"]:
            error = result.get("error", "未知错误")
            fail_details.append(f"- **{name}**: {error}")

    return f"""# 数据采集失败报告

> 生成时间：{exec_time.strftime("%Y-%m-%d %H:%M:%S")} (北京时间)
> 状态：全部数据源采集失败

---

## 失败详情

{chr(10).join(fail_details)}

---

## 可能原因

1. 网络连接异常
2. 目标网站接口变更
3. 请求被限流或封禁

---

<p align="center">
<i>{exec_time.strftime("%Y-%m-%d")}</i>
</p>
"""


def save_failure_report(content: str, exec_time: datetime) -> Path:
    """保存数据采集失败报告"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 文件名: YYYY-MM-DD_HH-MM_数据采集失败.md
    filename = f"{exec_time.strftime('%Y-%m-%d_%H-%M')}_数据采集失败.md"
    filepath = OUTPUT_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    log(f"📄 数据采集失败报告已保存: {filepath}")
    return filepath


async def main():
    """主函数"""
    exec_time = datetime.now()
    log(f"{'=' * 50}")
    log(f"🎯 开始执行热点抓取任务")
    log(f"{'=' * 50}")

    # 0. 清空 hotnews_output 文件夹（在生成新文件之前）
    clear_output_folder()

    # 1. 抓取数据
    results = await fetch_all_platforms()

    # 检查数据采集成功率
    success_count = sum(1 for r in results.values() if r["success"])
    total_count = len(results)

    # 如果全部失败，生成失败报告并中止
    if success_count == 0:
        log("❌ 所有数据源采集失败，中止任务")
        fail_content = generate_failure_report(exec_time, results)
        filepath = save_failure_report(fail_content, exec_time)

        log(f"{'=' * 50}")
        log(f"🏁 任务中止 - 数据采集失败")
        log(f"   - 失败报告: {filepath}")
        log(f"{'=' * 50}")

        return {
            "execution_time": exec_time,
            "filepath": str(filepath),
            "thinking_filepath": None,
            "github_push": False,
            "success_count": 0,
            "total_count": total_count,
            "status": "data_fetch_failed",
        }

    # 2. 生成Markdown
    md_content = generate_markdown(results, exec_time)

    # 3. 保存文件
    filepath = save_markdown(md_content, exec_time)

    # 4. DeepSeek深度思考分析
    thinking_filepath = await run_deepseek_analysis(md_content, exec_time)

    # 5. 发送邮件通知（推送之前发送，确保文件内容完整）
    email_success = send_email_notification(filepath, thinking_filepath)

    # 6. 推送到GitHub（包含深度思考文件）
    push_success = push_to_github(filepath, exec_time, thinking_filepath)

    # 完成
    log(f"{'=' * 50}")
    log(f"🏁 任务完成!")
    log(f"   - 抓取成功: {success_count}/{total_count}")
    log(f"   - 热点文件: {filepath}")
    if thinking_filepath:
        log(f"   - 思考文件: {thinking_filepath}")
    log(f"   - GitHub推送: {'✅ 成功' if push_success else '❌ 失败'}")
    log(f"   - 邮件通知: {'✅ 成功' if email_success else '❌ 失败'}")
    log(f"{'=' * 50}")

    return {
        "execution_time": exec_time,
        "filepath": str(filepath),
        "thinking_filepath": str(thinking_filepath) if thinking_filepath else None,
        "github_push": push_success,
        "success_count": success_count,
        "total_count": total_count,
    }


if __name__ == "__main__":
    asyncio.run(main())

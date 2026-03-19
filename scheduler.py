"""
热点数据定时抓取与推送系统
每日执行四次：北京时间 6:00, 11:00, 16:00, 21:00
"""

import asyncio
import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置
OUTPUT_DIR = Path(__file__).parent / "hotnews_output"
# 本地Obsidian仓库路径（已clone到本地）
LOCAL_REPO_DIR = Path(r"C:\Users\Wynter\Documents\obsidian\WynterS\ObsdianDrive")
GITHUB_TARGET_DIR = "hotnews"


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
    ("游民星空", "routers.gamersky", "get_gamersky_hot"),
    ("财联社", "routers.cls", "get_cls_hot"),
    ("TapTap", "routers.taptap", "get_taptap_hot"),
    ("网易新闻", "routers.netease_news", "get_netease_news_hot"),
    ("腾讯新闻", "routers.qq_news", "get_qq_news_hot"),
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


def push_to_github(
    filepath: Path, exec_time: datetime, thinking_filepath: Optional[Path] = None
) -> bool:
    """推送到GitHub（使用本地已clone的仓库）"""

    try:
        # 检查本地仓库是否存在
        if not LOCAL_REPO_DIR.exists():
            log(f"❌ 本地仓库目录不存在: {LOCAL_REPO_DIR}")
            return False

        # 目标目录
        target_dir = LOCAL_REPO_DIR / GITHUB_TARGET_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        # 复制热点文件
        target_file = target_dir / filepath.name
        shutil.copy(filepath, target_file)
        log(f"📄 热点文件已复制: {target_file}")

        # 复制深度思考文件（如果有）
        thinking_target = None
        if thinking_filepath and thinking_filepath.exists():
            thinking_target = target_dir / thinking_filepath.name
            shutil.copy(thinking_filepath, thinking_target)
            log(f"📄 深度思考文件已复制: {thinking_target}")

        # Git操作
        commit_msg = f"docs: 更新热点数据 {exec_time.strftime('%Y-%m-%d %H:%M')}"

        # 先拉取最新代码
        subprocess.run(
            ["git", "pull"],
            cwd=str(LOCAL_REPO_DIR),
            capture_output=True,
            encoding="utf-8",
            errors="ignore",
            timeout=60,
        )

        subprocess.run(
            ["git", "add", "."],
            cwd=str(LOCAL_REPO_DIR),
            capture_output=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
        )
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=str(LOCAL_REPO_DIR),
            capture_output=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
        )

        # 检查是否有变更
        if result.stdout and "nothing to commit" in result.stdout:
            log("ℹ️ 没有需要提交的变更（文件可能已存在）")
            return True

        result = subprocess.run(
            ["git", "push"],
            cwd=str(LOCAL_REPO_DIR),
            capture_output=True,
            encoding="utf-8",
            errors="ignore",
            timeout=120,
        )

        if result.returncode != 0:
            log(f"❌ 推送失败: {result.stderr if result.stderr else '未知错误'}")
            return False

        log(f"✅ 已成功推送到 GitHub")
        log(f"   - 热点文件: {GITHUB_TARGET_DIR}/{filepath.name}")
        if thinking_target:
            log(f"   - 思考文件: {GITHUB_TARGET_DIR}/{thinking_target.name}")
        return True

    except subprocess.TimeoutExpired:
        log("❌ Git操作超时")
        return False
    except Exception as e:
        log(f"❌ 推送 GitHub 失败: {str(e)}")
        return False


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

    # 5. 推送到GitHub（包含深度思考文件）
    push_success = push_to_github(filepath, exec_time, thinking_filepath)

    # 完成
    log(f"{'=' * 50}")
    log(f"🏁 任务完成!")
    log(f"   - 抓取成功: {success_count}/{total_count}")
    log(f"   - 热点文件: {filepath}")
    if thinking_filepath:
        log(f"   - 思考文件: {thinking_filepath}")
    log(f"   - GitHub推送: {'✅ 成功' if push_success else '❌ 失败'}")
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

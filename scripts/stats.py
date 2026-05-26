"""
刷题统计脚本
用法：
  python stats.py            → 查看总览
  python stats.py --daily    → 查看每日刷题记录
  python stats.py --update   → 自动更新 README.md 的统计区域
  python stats.py --check    → 检查 README 数据是否过期
"""
import os
import re
import sys
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent

# ── 要统计的平台目录 ──
TRACK = {
    "洛谷": "洛谷",
    "C语言网": "C语言网",
    "蓝桥云课": "蓝桥云课",
}

# ── 排除规则：这些文件不会被统计 ──
# 根目录文件（脚本/配置类，不是题目）
ROOT_EXCLUDE = {
    "stats.py",          # 本脚本
    "generate_readme.py",# 可能的生成脚本
    "stats_dashboard.py",# GitHub Pages 面板生成器
}
# 文件名包含这些关键词的会被跳过
EXCLUDE_KEYWORDS = [
    "temp",              # 临时文件
    "__pycache__",       # Python 缓存
]

# ── README 中统计区域的标记 ──
STATS_START = "<!-- stats -->"
STATS_END   = "<!-- /stats -->"


# ═══════════════════════════════════════════════════
#  核心统计函数
# ═══════════════════════════════════════════════════

def should_exclude_py(file_path: Path) -> bool:
    """判断一个 .py 文件是否应该被排除（不是刷题代码）"""
    # 根目录下的 .py 文件不是题目
    if file_path.parent == ROOT:
        return True
    # 按文件名排除
    if file_path.name in ROOT_EXCLUDE:
        return True
    # 按关键词排除
    name_lower = file_path.name.lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in name_lower:
            return True
    return False


def count_problems() -> dict[str, dict[str, int]]:
    """扫描各平台目录，统计 .py 文件数（按子目录分类）"""
    result = {}
    for folder, label in TRACK.items():
        path = ROOT / folder
        if not path.exists():
            continue
        cats = {}
        total = 0
        for sub in sorted(path.iterdir()):
            if not sub.is_dir():
                continue
            # 统计该子目录下所有合法的 .py 文件
            py_files = [
                f for f in sub.rglob("*.py")
                if not should_exclude_py(f)
            ]
            n = len(py_files)
            if n > 0:
                cats[sub.name] = n
                total += n
        cats["_total"] = total
        result[label] = cats
    return result


def count_total_problems() -> int:
    """直接统计所有题目总数（不分类）"""
    counts = count_problems()
    return sum(c["_total"] for c in counts.values())


# ═══════════════════════════════════════════════════
#  Git 日志分析
# ═══════════════════════════════════════════════════

def get_daily_files(days: int = 30) -> dict[str, list[str]]:
    """
    从 git log 提取最近 N 天每天新增/修改的 .py 文件。
    返回 {日期字符串: [文件名列表]}

    注意：使用文件相对于仓库根目录的完整路径来去重，
    避免不同目录下同名文件被错误合并。
    """
    try:
        out = subprocess.check_output(
            [
                "git", "-c", "core.quotepath=false",
                "log",
                "--format=@@%ad",           # 日期标记行
                "--date=short",             # YYYY-MM-DD 格式
                "--name-only",              # 只显示文件名
                f"--since={days} days ago",
            ],
            cwd=ROOT,
            encoding="utf-8",
        )
    except Exception:
        return {}

    day_files: dict[str, set[str]] = defaultdict(set)
    current_day = ""

    for line in out.strip().splitlines():
        if not line:
            continue

        # 日期标记行：@@2026-05-07
        if line.startswith("@@"):
            current_day = line[2:].strip()
            continue

        # 文件行：只处理 .py 文件
        if not line.endswith(".py"):
            continue

        # 清理路径中的引号
        clean_path = line.strip('"').strip("'")

        # 排除非题目文件（根目录脚本、临时文件等）
        filename = Path(clean_path).name
        if filename in ROOT_EXCLUDE:
            continue
        name_lower = filename.lower()
        if any(kw in name_lower for kw in EXCLUDE_KEYWORDS):
            continue

        # ★ 使用相对于仓库根目录的路径来保证唯一性
        # 这样 洛谷/A/test.py 和 C语言网/B/test.py 不会被当成同一个文件
        day_files[current_day].add(clean_path)

    # 转回有序列表
    return {k: sorted(v) for k, v in day_files.items()}


def get_daily_commit_count(days: int = 30) -> dict[str, int]:
    """从 git log 提取最近 N 天每天的提交次数"""
    try:
        out = subprocess.check_output(
            ["git", "log", "--format=%ad", "--date=short",
             f"--since={days} days ago"],
            cwd=ROOT, encoding="utf-8",
        )
    except Exception:
        return {}

    day_count = defaultdict(int)
    for line in out.strip().splitlines():
        if line:
            day_count[line] += 1
    return dict(day_count)


# ═══════════════════════════════════════════════════
#  输出
# ═══════════════════════════════════════════════════

def print_overview(counts: dict, daily_files: dict):
    """打印总览统计"""
    print("=" * 55)
    print("  刷题统计")
    print("=" * 55)

    grand = 0
    for label, cats in counts.items():
        t = cats.get("_total", 0)
        grand += t
        print(f"\n  [{label}]  ({t} 题)")
        for name, n in sorted(cats.items()):
            if name == "_total":
                continue
            print(f"     {name:<28} {n:>3} 题")
        cats["_total"] = t   # 恢复

    print(f"\n  {'─' * 35}")
    print(f"  总计：{grand} 题\n")

    # 最近每日
    if daily_files:
        print("  最近每日新增题数：")
        for day, files in sorted(daily_files.items(), reverse=True):
            # 只显示文件名（去掉路径前缀）
            short_names = [Path(f).name for f in files]
            print(f"     {day}   +{len(files)} 题")
            for name in short_names:
                print(f"        · {name}")


def print_daily_detail(daily_files: dict, daily_commits: dict):
    """打印每日详细记录"""
    print("每日刷题记录（最近30天）\n")

    all_days = sorted(set(list(daily_files.keys()) + list(daily_commits.keys())), reverse=True)

    for day in all_days:
        files = daily_files.get(day, [])
        commits = daily_commits.get(day, 0)
        short_names = [Path(f).name for f in files]

        print(f"{day}  {commits} 次提交, {len(files)} 题")
        for name in short_names:
            print(f"  · {name}")
        print()


# ═══════════════════════════════════════════════════
#  README 更新
# ═══════════════════════════════════════════════════

def build_stats_markdown(counts: dict, daily_files: dict) -> str:
    """生成统计区域的 Markdown 内容"""
    grand = sum(c.get("_total", 0) for c in counts.values())

    lines = []
    lines.append("<table>")
    lines.append("  <tr>")
    for label, cats in counts.items():
        t = cats.get("_total", 0)
        lines.append(
            f'    <td align="center"><a href="./{label}/"><b>{label}</b></a><br><sub>{t} 题</sub></td>'
        )
    lines.append(f'    <td align="center"><b>总计</b><br><sub>{grand} 题</sub></td>')
    lines.append("  </tr>")
    lines.append("</table>")

    return "\n".join(lines)


def update_readme(counts: dict, daily_files: dict):
    """更新 README.md 中统计区域的内容"""
    readme_path = ROOT / "README.md"
    text = readme_path.read_text(encoding="utf-8")

    new_content = build_stats_markdown(counts, daily_files)
    replacement = f"{STATS_START}\n{new_content}\n{STATS_END}"

    pattern = re.compile(rf"{re.escape(STATS_START)}.*?{re.escape(STATS_END)}", re.DOTALL)
    if pattern.search(text):
        new_text = pattern.sub(replacement, text)
    else:
        new_text = text + f"\n\n{replacement}\n"

    readme_path.write_text(new_text, encoding="utf-8")
    print("README.md 已更新。")


def check_stale(counts: dict, daily_files: dict):
    """检查 README 中的数据是否和当前扫描结果一致"""
    readme_path = ROOT / "README.md"
    text = readme_path.read_text(encoding="utf-8")

    pattern = re.compile(rf"{re.escape(STATS_START)}(.*?){re.escape(STATS_END)}", re.DOTALL)
    match = pattern.search(text)
    if not match:
        print("⚠️  README 中没有找到统计区域，请先运行 --update")
        return

    current_in_readme = match.group(1).strip()
    expected = build_stats_markdown(counts, daily_files).strip()

    if current_in_readme == expected:
        print("[OK] README 统计数据是最新的。")
    else:
        print("[!!] README 数据已过期！")
        print("     当前实际数据与 README 中的不一致。")
        print("     请运行: python stats.py --update")


# ═══════════════════════════════════════════════════
#  入口
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    counts = count_problems()
    daily_files = get_daily_files()
    daily_commits = get_daily_commit_count()

    if "--daily" in sys.argv:
        print_daily_detail(daily_files, daily_commits)

    elif "--update" in sys.argv:
        update_readme(counts, daily_files)

    elif "--check" in sys.argv:
        check_stale(counts, daily_files)

    else:
        print_overview(counts, daily_files)

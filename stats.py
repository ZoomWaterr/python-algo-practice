"""
刷题统计脚本
用法：
  python stats.py            → 查看总览
  python stats.py --daily    → 查看每日刷题记录
  python stats.py --update   → 自动更新 README.md 的统计区域
"""
import os
import re
import sys
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime

ROOT = Path(__file__).parent

# 要统计的目录 → 显示名称
TRACK = {
    "洛谷": "洛谷",
    "C语言网": "C语言网",
    "蓝桥云课": "蓝桥云课",
}


def count_problems() -> dict[str, dict[str, int]]:
    """扫描目录，统计每个子分类的 .py 文件数（排除临时文件）"""
    result = {}
    for folder, label in TRACK.items():
        path = ROOT / folder
        if not path.exists():
            continue
        cats = {}
        total = 0
        for sub in sorted(path.iterdir()):
            if sub.is_dir():
                n = len([f for f in sub.rglob("*.py") if not f.name.startswith("temp")])
                cats[sub.name] = n
                total += n
        cats["_total"] = total
        result[label] = cats
    return result


def get_daily_stats(days: int = 30) -> list[tuple[str, int]]:
    """从 git log 提取最近 N 天的每日提交数"""
    try:
        out = subprocess.check_output(
            ["git", "log", "--format=%ad", "--date=short", f"--since={days} days ago"],
            cwd=ROOT, encoding="utf-8",
        )
    except Exception:
        return []
    day_count = defaultdict(int)
    for line in out.strip().splitlines():
        if line:
            day_count[line] += 1
    return sorted(day_count.items(), reverse=True)


def get_daily_files(days: int = 30) -> dict[str, list[str]]:
    """从 git log 提取最近 N 天每天新增/修改的 .py 文件"""
    try:
        out = subprocess.check_output(
            ["git", "-c", "core.quotepath=false", "log",
             "--format=@@%ad", "--date=short", "--name-only",
             f"--since={days} days ago"],
            cwd=ROOT, encoding="utf-8",
        )
    except Exception:
        return {}
    day_files: dict[str, set[str]] = defaultdict(set)
    current_day = ""
    for line in out.strip().splitlines():
        if line.startswith("@@"):
            current_day = line[2:].strip()
        elif line.endswith(".py"):
            clean = line.strip('"')
            if not clean.startswith("temp"):
                day_files[current_day].add(Path(clean).name)
    return {k: sorted(v) for k, v in day_files.items()}


def total_all(counts: dict) -> int:
    return sum(c["_total"] for c in counts.values())


def print_overview(counts: dict, daily_files: dict):
    print("=" * 50)
    print("  刷题统计")
    print("=" * 50)
    grand = 0
    for label, cats in counts.items():
        t = cats.pop("_total", 0)
        grand += t
        print(f"\n  [{label}]  ({t} 题)")
        for name, n in sorted(cats.items()):
            print(f"     {name:<20} {n:>3} 题")
        cats["_total"] = t
    print(f"\n  {'─' * 20}")
    print(f"  总计：{grand} 题")
    print()

    if daily_files:
        print("  最近每日新增题数：")
        for day, files in sorted(daily_files.items(), reverse=True):
            print(f"     {day}   +{len(files)} 题")
            for f in files:
                print(f"        · {f}")


def update_readme(counts: dict, daily_files: dict):
    """更新 README.md 中 <!-- stats --> ... <!-- /stats --> 之间的内容"""
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")

    grand = total_all(counts)
    lines = []
    lines.append("| 平台 | 题数 |")
    lines.append("|------|------|")
    for label, cats in counts.items():
        t = cats.get("_total", 0)
        lines.append(f"| [{label}](./{label}/) | {t} |")
    lines.append(f"| **总计** | **{grand}** |")
    lines.append("")
    if daily_files:
        lines.append("**最近刷题记录**")
        lines.append("")
        for day, files in sorted(daily_files.items(), reverse=True)[:7]:
            lines.append(f"- {day}  +{len(files)} 题")
    table = "\n".join(lines)

    pattern = re.compile(r"<!-- stats -->.*?<!-- /stats -->", re.DOTALL)
    if pattern.search(text):
        new_text = pattern.sub(f"<!-- stats -->\n{table}\n<!-- /stats -->", text)
    else:
        new_text = text + f"\n\n<!-- stats -->\n{table}\n<!-- /stats -->\n"

    readme.write_text(new_text, encoding="utf-8")
    print("README.md 已更新。")


if __name__ == "__main__":
    counts = count_problems()
    daily_files = get_daily_files()

    if "--daily" in sys.argv:
        print("每日刷题记录（最近30天）")
        daily_stats = get_daily_stats()
        for day, n in daily_stats:
            files = daily_files.get(day, [])
            print(f"\n{day}  {n} 次提交, {len(files)} 题")
            for f in files:
                print(f"  · {f}")

    elif "--update" in sys.argv:
        update_readme(counts, daily_files)

    else:
        print_overview(counts, daily_files)

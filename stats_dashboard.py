"""
Generate the GitHub Pages dashboard for the algorithm practice repository.

The page is a single static HTML file with no third-party dependencies. Data
comes from the repository tree and git history, so every push can rebuild the
dashboard in GitHub Actions.
"""

from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).parent
TRACK = {
    "洛谷": "洛谷",
    "C语言网": "C语言网",
    "蓝桥云课": "蓝桥云课",
}
ROOT_EXCLUDE = {
    "stats.py",
    "generate_readme.py",
    "stats_dashboard.py",
}
EXCLUDE_KEYWORDS = {"temp", "__pycache__"}
CST = timezone(timedelta(hours=8))


def should_exclude_problem_file(file_path: Path) -> bool:
    """Return True when a Python file is infrastructure instead of a solution."""
    if file_path.parent == ROOT:
        return True
    if file_path.name in ROOT_EXCLUDE:
        return True
    lowered = str(file_path).lower()
    return any(keyword in lowered for keyword in EXCLUDE_KEYWORDS)


def should_exclude_history_path(raw_path: str) -> bool:
    path = Path(raw_path.strip('"').strip("'"))
    if path.suffix != ".py":
        return True
    if len(path.parts) <= 1:
        return True
    if path.name in ROOT_EXCLUDE:
        return True
    lowered = raw_path.lower()
    return any(keyword in lowered for keyword in EXCLUDE_KEYWORDS)


def count_problems() -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for folder, label in TRACK.items():
        root = ROOT / folder
        if not root.exists():
            continue

        categories: dict[str, int] = {}
        total = 0
        for subdir in sorted(root.iterdir(), key=lambda item: item.name):
            if not subdir.is_dir():
                continue
            files = [
                file
                for file in subdir.rglob("*.py")
                if not should_exclude_problem_file(file)
            ]
            if files:
                categories[subdir.name] = len(files)
                total += len(files)

        categories["_total"] = total
        result[label] = categories
    return result


def run_git(args: list[str]) -> str:
    return subprocess.check_output(args, cwd=ROOT, encoding="utf-8", errors="replace")


def get_git_history(days: int = 420) -> dict[str, dict[str, object]]:
    try:
        out = run_git(
            [
                "git",
                "-c",
                "core.quotepath=false",
                "log",
                "--format=@@%ad",
                "--date=short",
                "--name-only",
                f"--since={days} days ago",
            ]
        )
    except Exception:
        return {}

    day_data: dict[str, dict[str, object]] = defaultdict(
        lambda: {"commits": 0, "files": set()}
    )
    current_day = ""
    for line in out.splitlines():
        if not line:
            continue
        if line.startswith("@@"):
            current_day = line[2:].strip()
            day_data[current_day]["commits"] = int(day_data[current_day]["commits"]) + 1
            continue
        if not current_day or should_exclude_history_path(line):
            continue
        day_data[current_day]["files"].add(line.strip('"').strip("'"))

    result: dict[str, dict[str, object]] = {}
    for day, data in day_data.items():
        files = sorted(data["files"])
        result[day] = {
            "commits": data["commits"],
            "files": len(files),
            "filenames": files,
        }
    return result


def get_first_commit_date() -> str:
    try:
        out = run_git(["git", "log", "--reverse", "--format=%ad", "--date=short"])
    except Exception:
        return ""
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    return lines[0] if lines else ""


def get_total_commit_count() -> int:
    try:
        return int(run_git(["git", "rev-list", "--count", "HEAD"]).strip())
    except Exception:
        return 0


def parse_day(value: str) -> date | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def streaks(active_days: set[str], today: date) -> tuple[int, int]:
    current = 0
    cursor = today
    while cursor.isoformat() in active_days:
        current += 1
        cursor -= timedelta(days=1)

    longest = 0
    running = 0
    previous: date | None = None
    for raw_day in sorted(active_days):
        day = parse_day(raw_day)
        if not day:
            continue
        if previous and day == previous + timedelta(days=1):
            running += 1
        else:
            running = 1
        longest = max(longest, running)
        previous = day
    return current, longest


def build_payload(counts: dict[str, dict[str, int]], history: dict[str, dict[str, object]]) -> dict[str, object]:
    now = datetime.now(CST)
    today = now.date()
    first_commit = get_first_commit_date()
    first_day = parse_day(first_commit) or today
    early_context = first_day - timedelta(days=28)
    six_month_window = today - timedelta(days=182)
    range_start = max(min(early_context, six_month_window), today - timedelta(days=371))

    platforms = []
    for label, categories in counts.items():
        subdirs = [
            {"name": name, "count": count}
            for name, count in sorted(
                categories.items(), key=lambda item: (-item[1], item[0])
            )
            if name != "_total"
        ]
        platforms.append(
            {
                "name": label,
                "total": categories.get("_total", 0),
                "subdirs": subdirs,
            }
        )

    grand_total = sum(platform["total"] for platform in platforms)
    active_days = {
        day for day, info in history.items() if int(info.get("files", 0)) > 0
    }
    current_streak, longest_streak = streaks(active_days, today)
    recent = [
        {
            "date": day,
            "commits": info["commits"],
            "files": info["files"],
            "filenames": info["filenames"],
        }
        for day, info in sorted(history.items(), reverse=True)
        if int(info.get("files", 0)) > 0
    ][:12]
    best_day = max(
        recent,
        key=lambda item: int(item["files"]),
        default={"date": "", "files": 0, "commits": 0, "filenames": []},
    )

    today_key = today.isoformat()
    heatmap = {
        day: {"files": info["files"], "commits": info["commits"]}
        for day, info in history.items()
    }

    return {
        "summary": {
            "grandTotal": grand_total,
            "totalCommits": get_total_commit_count(),
            "activeDays": len(active_days),
            "currentStreak": current_streak,
            "longestStreak": longest_streak,
            "todayFiles": int(history.get(today_key, {}).get("files", 0)),
            "latestDay": recent[0] if recent else None,
            "bestDay": best_day,
        },
        "platforms": platforms,
        "recent": recent,
        "heatmap": heatmap,
        "firstCommit": first_commit,
        "today": today_key,
        "rangeStart": range_start.isoformat(),
        "updatedAt": now.strftime("%Y-%m-%d %H:%M CST"),
        "repoUrl": "https://github.com/ZoomWaterr/python-algo-practice",
    }


def build_html(payload: dict[str, object]) -> str:
    data_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    data_json = data_json.replace("</", "<\\/")
    return HTML_TEMPLATE.replace("__DASHBOARD_DATA__", data_json)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ZoomWaterr 刷题面板</title>
<style>
  :root {
    color-scheme: light;
    --bg: #f5f8f4;
    --paper: #fffef9;
    --paper-strong: #fdfbf2;
    --ink: #1d2420;
    --muted: #657168;
    --faint: #8a968e;
    --line: #dfe8dc;
    --line-strong: #c9d7cc;
    --green: #227a55;
    --green-soft: #dff0df;
    --blue: #3f6f99;
    --amber: #b56e21;
    --rose: #a94f5d;
    --shadow: 0 18px 50px rgba(35, 65, 48, 0.08);
    --cell: 13px;
    --gap: 4px;
    --h0: #e8eee7;
    --h1: #bfe3bf;
    --h2: #76c884;
    --h3: #2f965f;
    --h4: #155f3d;
  }

  * { box-sizing: border-box; }
  html { min-width: 0; }
  body {
    margin: 0;
    min-height: 100vh;
    background:
      linear-gradient(180deg, rgba(255, 254, 249, 0.9), rgba(245, 248, 244, 0.95) 260px),
      var(--bg);
    color: var(--ink);
    font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    letter-spacing: 0;
  }
  a { color: inherit; }
  .shell {
    width: min(1180px, calc(100% - 32px));
    margin: 0 auto;
    padding: 28px 0 34px;
  }
  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 22px;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
  }
  .brand-mark {
    width: 46px;
    height: 46px;
    border: 1px solid var(--line-strong);
    border-radius: 8px;
    display: grid;
    place-items: center;
    background: var(--paper);
    box-shadow: inset 0 0 0 4px rgba(34, 122, 85, 0.05);
    color: var(--green);
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-weight: 800;
  }
  .brand-title {
    display: block;
    font-size: 18px;
    font-weight: 780;
    line-height: 1.1;
  }
  .brand-subtitle {
    display: block;
    margin-top: 4px;
    color: var(--muted);
    font-size: 13px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .repo-link {
    min-height: 40px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0 13px;
    border: 1px solid var(--line-strong);
    border-radius: 8px;
    background: var(--paper);
    color: var(--ink);
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
    box-shadow: 0 8px 18px rgba(35, 65, 48, 0.05);
    transition: transform 180ms ease, border-color 180ms ease;
  }
  .repo-link:hover { transform: translateY(-1px); border-color: var(--green); }
  .repo-link:active { transform: translateY(0); }
  .repo-link svg { width: 16px; height: 16px; }

  .hero {
    display: grid;
    grid-template-columns: minmax(0, 1.2fr) minmax(310px, 0.8fr);
    gap: 18px;
    align-items: stretch;
    margin-bottom: 18px;
  }
  .hero-main,
  .pulse {
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--paper);
    box-shadow: var(--shadow);
    min-width: 0;
  }
  .hero-main {
    padding: 26px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 246px;
  }
  .eyebrow {
    display: inline-flex;
    width: fit-content;
    align-items: center;
    gap: 8px;
    color: var(--green);
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .eyebrow::before {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 0 5px rgba(34, 122, 85, 0.1);
  }
  h1 {
    margin: 15px 0 12px;
    max-width: 720px;
    font-size: 38px;
    line-height: 1.08;
    letter-spacing: 0;
  }
  .lead {
    margin: 0;
    max-width: 68ch;
    color: var(--muted);
    font-size: 15px;
    line-height: 1.75;
  }
  .hero-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    margin-top: 24px;
  }
  .meta-pill {
    display: inline-flex;
    align-items: center;
    min-height: 30px;
    padding: 0 10px;
    border: 1px solid var(--line);
    border-radius: 999px;
    background: var(--paper-strong);
    color: var(--muted);
    font-size: 12px;
  }
  .meta-pill strong {
    margin-left: 5px;
    color: var(--ink);
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 12px;
  }
  .pulse {
    padding: 22px;
    display: grid;
    grid-template-rows: auto 1fr auto;
    gap: 18px;
    overflow: hidden;
  }
  .pulse-head {
    display: flex;
    justify-content: space-between;
    gap: 14px;
    align-items: flex-start;
  }
  .pulse-title {
    margin: 0;
    color: var(--muted);
    font-size: 13px;
    font-weight: 750;
  }
  .pulse-date {
    color: var(--faint);
    font-size: 12px;
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
  }
  .pulse-number {
    align-self: center;
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 86px;
    line-height: 0.9;
    font-weight: 850;
    color: var(--green);
    font-variant-numeric: tabular-nums;
  }
  .pulse-foot {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }
  .mini-stat {
    border-top: 1px solid var(--line);
    padding-top: 10px;
  }
  .mini-stat span {
    display: block;
    color: var(--muted);
    font-size: 12px;
  }
  .mini-stat strong {
    display: block;
    margin-top: 4px;
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 19px;
    font-variant-numeric: tabular-nums;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 18px;
  }
  .stat-card {
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--paper);
    padding: 16px 14px;
    min-height: 96px;
  }
  .stat-label {
    color: var(--muted);
    font-size: 12px;
    font-weight: 700;
  }
  .stat-value {
    margin-top: 12px;
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 29px;
    line-height: 1;
    font-weight: 850;
    font-variant-numeric: tabular-nums;
  }
  .stat-card:nth-child(2) .stat-value { color: var(--blue); }
  .stat-card:nth-child(3) .stat-value { color: var(--amber); }
  .stat-card:nth-child(4) .stat-value { color: var(--rose); }
  .stat-card:nth-child(5) .stat-value { color: var(--green); }

  .content-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.6fr) minmax(300px, 0.8fr);
    gap: 18px;
    align-items: start;
  }
  .content-grid > * {
    min-width: 0;
  }
  .panel {
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--paper);
    box-shadow: 0 12px 34px rgba(35, 65, 48, 0.06);
    min-width: 0;
  }
  .panel + .panel { margin-top: 18px; }
  .panel-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 14px;
    padding: 18px 20px 0;
  }
  .panel-title {
    margin: 0;
    font-size: 16px;
    font-weight: 800;
  }
  .panel-note {
    color: var(--muted);
    font-size: 12px;
    text-align: right;
  }
  .panel-body { padding: 18px 20px 20px; }

  .heatmap-wrap {
    overflow-x: auto;
    padding-bottom: 4px;
    width: 100%;
  }
  .heatmap {
    width: max-content;
    min-width: 100%;
  }
  .month-row {
    display: grid;
    grid-template-columns: repeat(var(--weeks), var(--cell));
    gap: var(--gap);
    margin-left: 26px;
    margin-bottom: 7px;
    color: var(--muted);
    font-size: 11px;
    line-height: 1;
  }
  .month-label {
    min-width: var(--cell);
    white-space: nowrap;
  }
  .heatmap-body {
    display: grid;
    grid-template-columns: 18px auto;
    gap: 8px;
    align-items: start;
  }
  .day-labels {
    display: grid;
    grid-template-rows: repeat(7, var(--cell));
    gap: var(--gap);
    color: var(--muted);
    font-size: 11px;
    line-height: var(--cell);
  }
  .day-labels span:nth-child(even) { color: transparent; }
  .week-grid {
    display: grid;
    grid-template-columns: repeat(var(--weeks), var(--cell));
    grid-auto-flow: column;
    gap: var(--gap);
  }
  .week {
    display: grid;
    grid-template-rows: repeat(7, var(--cell));
    gap: var(--gap);
  }
  .cell {
    width: var(--cell);
    height: var(--cell);
    border-radius: 3px;
    background: var(--h0);
    border: 1px solid rgba(31, 53, 39, 0.05);
    position: relative;
  }
  .cell.h1 { background: var(--h1); }
  .cell.h2 { background: var(--h2); }
  .cell.h3 { background: var(--h3); }
  .cell.h4 { background: var(--h4); }
  .cell.future {
    background: transparent;
    border-color: transparent;
  }
  .cell:not(.future):hover {
    outline: 2px solid rgba(29, 36, 32, 0.44);
    outline-offset: 1px;
  }
  .cell[data-tip]:hover::after {
    content: attr(data-tip);
    position: absolute;
    left: 50%;
    bottom: calc(100% + 9px);
    transform: translateX(-50%);
    z-index: 4;
    width: max-content;
    max-width: 260px;
    padding: 7px 10px;
    border-radius: 7px;
    background: #1f2923;
    color: #f7fbf5;
    font-size: 12px;
    line-height: 1.3;
    box-shadow: 0 12px 26px rgba(31, 41, 35, 0.22);
    pointer-events: none;
  }
  .legend {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 6px;
    margin-top: 12px;
    color: var(--muted);
    font-size: 12px;
  }
  .legend span:not(.legend-label) {
    width: var(--cell);
    height: var(--cell);
    border-radius: 3px;
    display: inline-block;
  }
  .legend .h0 { background: var(--h0); }
  .legend .h1 { background: var(--h1); }
  .legend .h2 { background: var(--h2); }
  .legend .h3 { background: var(--h3); }
  .legend .h4 { background: var(--h4); }

  .platforms {
    display: grid;
    gap: 16px;
  }
  .platform-row {
    display: grid;
    grid-template-columns: 74px minmax(0, 1fr) 44px;
    gap: 12px;
    align-items: center;
  }
  .platform-name {
    font-size: 13px;
    font-weight: 800;
    text-align: right;
  }
  .bar-track {
    height: 28px;
    border-radius: 999px;
    background: #edf3ec;
    border: 1px solid var(--line);
    overflow: hidden;
  }
  .bar-fill {
    width: var(--pct);
    min-width: 28px;
    height: 100%;
    border-radius: 999px;
    background: var(--green);
    transition: width 700ms cubic-bezier(0.16, 1, 0.3, 1);
  }
  .platform-row:nth-child(2) .bar-fill { background: var(--blue); }
  .platform-row:nth-child(3) .bar-fill { background: var(--amber); }
  .platform-count {
    color: var(--ink);
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 13px;
    font-weight: 800;
    font-variant-numeric: tabular-nums;
  }
  .subdir-list {
    grid-column: 2 / 4;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: -7px;
  }
  .tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    min-height: 25px;
    padding: 0 9px;
    border: 1px solid var(--line);
    border-radius: 999px;
    background: var(--paper-strong);
    color: var(--muted);
    font-size: 12px;
  }
  .tag strong {
    color: var(--ink);
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 12px;
  }

  .activity {
    display: grid;
  }
  .activity-row {
    display: grid;
    grid-template-columns: 80px 1fr;
    gap: 14px;
    padding: 14px 0;
    border-top: 1px solid var(--line);
  }
  .activity-row:first-child { border-top: 0; padding-top: 0; }
  .activity-date {
    color: var(--muted);
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 12px;
    line-height: 1.7;
  }
  .activity-main {
    min-width: 0;
  }
  .activity-title {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: baseline;
    font-size: 13px;
    font-weight: 800;
  }
  .activity-title span {
    color: var(--muted);
    font-weight: 600;
  }
  .file-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 9px;
  }
  .file-pill {
    max-width: 100%;
    min-height: 25px;
    padding: 4px 8px;
    border-radius: 7px;
    background: #eef4ef;
    color: #33443a;
    font-size: 12px;
    line-height: 1.35;
    overflow-wrap: anywhere;
  }
  .empty {
    padding: 18px 0;
    color: var(--muted);
    font-size: 13px;
  }
  .footer {
    margin-top: 22px;
    padding-top: 18px;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 12px;
    line-height: 1.7;
  }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      scroll-behavior: auto !important;
      transition-duration: 0.01ms !important;
    }
  }
  @media (max-width: 940px) {
    .hero,
    .content-grid {
      grid-template-columns: 1fr;
    }
    .stats-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
  }
  @media (max-width: 640px) {
    .shell {
      width: min(100% - 22px, 1180px);
      padding-top: 16px;
    }
    .topbar {
      align-items: flex-start;
      flex-direction: column;
    }
    .repo-link {
      width: 100%;
      justify-content: center;
    }
    .brand-subtitle {
      white-space: normal;
    }
    h1 {
      font-size: 30px;
    }
    .hero-main,
    .pulse,
    .panel-body,
    .panel-head {
      padding-left: 16px;
      padding-right: 16px;
    }
    .pulse-number {
      font-size: 66px;
    }
    .stats-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .platform-row {
      grid-template-columns: 1fr 54px;
      gap: 8px;
    }
    .platform-name {
      grid-column: 1 / 3;
      text-align: left;
    }
    .subdir-list {
      grid-column: 1 / 3;
    }
    .activity-row {
      grid-template-columns: 1fr;
      gap: 7px;
    }
  }
</style>
</head>
<body>
<div class="shell">
  <header class="topbar">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">ZW</div>
      <div>
        <span class="brand-title">ZoomWaterr 刷题面板</span>
        <span class="brand-subtitle">Python 算法练习记录，按 push 自动更新</span>
      </div>
    </div>
    <a class="repo-link" id="repo-link" href="#" aria-label="打开 GitHub 仓库">
      <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path d="M6.5 3.5H4.2A2.2 2.2 0 0 0 2 5.7v6.1A2.2 2.2 0 0 0 4.2 14h6.1a2.2 2.2 0 0 0 2.2-2.2V9.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        <path d="M9 2h5v5M8.4 7.6 13.7 2.3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      GitHub
    </a>
  </header>

  <section class="hero" aria-labelledby="dashboard-title">
    <div class="hero-main">
      <div>
        <span class="eyebrow">practice dashboard</span>
        <h1 id="dashboard-title">把刷题轨迹变成一张可以每天回看的地图。</h1>
        <p class="lead">统计来自仓库里的题解文件和 git 历史。热力图按每天新增或修改的题目数上色，平台分布按目录实时汇总。</p>
      </div>
      <div class="hero-meta" id="hero-meta"></div>
    </div>
    <aside class="pulse" aria-label="今日刷题摘要">
      <div class="pulse-head">
        <p class="pulse-title">今日题目变动</p>
        <span class="pulse-date" id="today-label"></span>
      </div>
      <div class="pulse-number" id="today-files">0</div>
      <div class="pulse-foot">
        <div class="mini-stat"><span>当前连续</span><strong id="current-streak">0 天</strong></div>
        <div class="mini-stat"><span>最长连续</span><strong id="longest-streak">0 天</strong></div>
      </div>
    </aside>
  </section>

  <section class="stats-grid" id="stats-grid" aria-label="刷题统计"></section>

  <main class="content-grid">
    <div>
      <section class="panel" aria-labelledby="heatmap-title">
        <div class="panel-head">
          <h2 class="panel-title" id="heatmap-title">刷题热力图</h2>
          <span class="panel-note" id="heatmap-note"></span>
        </div>
        <div class="panel-body">
          <div class="heatmap-wrap">
            <div class="heatmap" id="heatmap"></div>
          </div>
          <div class="legend" aria-label="热力图颜色图例">
            <span class="legend-label">少</span>
            <span class="h0"></span><span class="h1"></span><span class="h2"></span><span class="h3"></span><span class="h4"></span>
            <span class="legend-label">多</span>
          </div>
        </div>
      </section>

      <section class="panel" aria-labelledby="activity-title">
        <div class="panel-head">
          <h2 class="panel-title" id="activity-title">最近活动</h2>
          <span class="panel-note">只显示题解文件</span>
        </div>
        <div class="panel-body">
          <div class="activity" id="activity"></div>
        </div>
      </section>
    </div>

    <aside>
      <section class="panel" aria-labelledby="platform-title">
        <div class="panel-head">
          <h2 class="panel-title" id="platform-title">平台分布</h2>
          <span class="panel-note">按目录扫描</span>
        </div>
        <div class="panel-body">
          <div class="platforms" id="platforms"></div>
        </div>
      </section>
    </aside>
  </main>

  <footer class="footer" id="footer"></footer>
</div>

<script type="application/json" id="dashboard-data">__DASHBOARD_DATA__</script>
<script>
(() => {
  const DATA = JSON.parse(document.getElementById("dashboard-data").textContent);
  const summary = DATA.summary;

  const escapeHtml = (value) => String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const parseDate = (value) => {
    const [year, month, day] = value.split("-").map(Number);
    return new Date(year, month - 1, day);
  };

  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const addDays = (date, count) => {
    const copy = new Date(date);
    copy.setDate(copy.getDate() + count);
    return copy;
  };

  const monthName = (date) => `${date.getMonth() + 1}月`;
  const level = (files) => {
    if (!files) return 0;
    if (files <= 2) return 1;
    if (files <= 6) return 2;
    if (files <= 12) return 3;
    return 4;
  };

  document.getElementById("repo-link").href = DATA.repoUrl;
  document.getElementById("today-label").textContent = DATA.today;
  document.getElementById("today-files").textContent = summary.todayFiles;
  document.getElementById("current-streak").textContent = `${summary.currentStreak} 天`;
  document.getElementById("longest-streak").textContent = `${summary.longestStreak} 天`;

  const latest = summary.latestDay;
  const best = summary.bestDay || {};
  document.getElementById("hero-meta").innerHTML = [
    ["首次提交", DATA.firstCommit || "暂无"],
    ["最近活跃", latest ? latest.date : "暂无"],
    ["单日最高", best.date ? `${best.files} 题` : "暂无"],
    ["更新时间", DATA.updatedAt],
  ].map(([label, value]) => `<span class="meta-pill">${label}<strong>${escapeHtml(value)}</strong></span>`).join("");

  const statItems = [
    ["总题数", summary.grandTotal],
    ["总提交", summary.totalCommits],
    ["活跃天", summary.activeDays],
    ["当前连续", summary.currentStreak],
    ["最长连续", summary.longestStreak],
  ];
  document.getElementById("stats-grid").innerHTML = statItems.map(([label, value]) => `
    <article class="stat-card">
      <div class="stat-label">${label}</div>
      <div class="stat-value">${value}</div>
    </article>
  `).join("");

  function renderHeatmap() {
    const start = parseDate(DATA.rangeStart);
    const today = parseDate(DATA.today);
    const startOffset = (start.getDay() + 6) % 7;
    const alignedStart = addDays(start, -startOffset);
    const totalDays = Math.round((today - alignedStart) / 86400000) + 1;
    const weeks = Math.max(1, Math.ceil(totalDays / 7));
    const heatmap = DATA.heatmap || {};
    let monthHtml = "";
    let lastMonth = -1;
    let weekHtml = "";

    for (let week = 0; week < weeks; week += 1) {
      const weekStart = addDays(alignedStart, week * 7);
      const monthChanged = weekStart.getMonth() !== lastMonth;
      monthHtml += `<span class="month-label">${monthChanged ? monthName(weekStart) : ""}</span>`;
      if (monthChanged) lastMonth = weekStart.getMonth();

      let cells = "";
      for (let dayIndex = 0; dayIndex < 7; dayIndex += 1) {
        const day = addDays(weekStart, dayIndex);
        const key = formatDate(day);
        if (day > today) {
          cells += '<span class="cell future" aria-hidden="true"></span>';
          continue;
        }
        const item = heatmap[key] || { files: 0, commits: 0 };
        const files = Number(item.files || 0);
        const commits = Number(item.commits || 0);
        const tip = files > 0
          ? `${key}: ${files} 题, ${commits} 次提交`
          : `${key}: 无题解变动`;
        cells += `<span class="cell h${level(files)}" title="${escapeHtml(tip)}" data-tip="${escapeHtml(tip)}" aria-label="${escapeHtml(tip)}"></span>`;
      }
      weekHtml += `<span class="week">${cells}</span>`;
    }

    const activeRange = `${formatDate(alignedStart)} 至 ${DATA.today}`;
    document.getElementById("heatmap-note").textContent = activeRange;
    document.getElementById("heatmap").style.setProperty("--weeks", weeks);
    document.getElementById("heatmap").innerHTML = `
      <div class="month-row">${monthHtml}</div>
      <div class="heatmap-body">
        <div class="day-labels" aria-hidden="true"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span></div>
        <div class="week-grid">${weekHtml}</div>
      </div>
    `;
  }

  function renderPlatforms() {
    const maxTotal = Math.max(...DATA.platforms.map((platform) => platform.total), 1);
    document.getElementById("platforms").innerHTML = DATA.platforms.map((platform) => {
      const pct = `${Math.max(8, Math.round((platform.total / maxTotal) * 100))}%`;
      const subdirs = (platform.subdirs || []).map((subdir) => `
        <span class="tag">${escapeHtml(subdir.name)}<strong>${subdir.count}</strong></span>
      `).join("");
      return `
        <div class="platform-row">
          <div class="platform-name">${escapeHtml(platform.name)}</div>
          <div class="bar-track"><div class="bar-fill" style="--pct:${pct}"></div></div>
          <div class="platform-count">${platform.total}</div>
          <div class="subdir-list">${subdirs}</div>
        </div>
      `;
    }).join("");
  }

  function renderActivity() {
    const recent = DATA.recent || [];
    if (!recent.length) {
      document.getElementById("activity").innerHTML = '<div class="empty">还没有题解活动。</div>';
      return;
    }
    document.getElementById("activity").innerHTML = recent.map((item) => {
      const files = (item.filenames || []).slice(0, 6).map((path) => {
        const parts = path.split(/[\\/]/);
        const name = parts[parts.length - 1] || path;
        return `<span class="file-pill">${escapeHtml(name)}</span>`;
      }).join("");
      const more = (item.filenames || []).length > 6
        ? `<span class="file-pill">还有 ${item.filenames.length - 6} 题</span>`
        : "";
      return `
        <article class="activity-row">
          <time class="activity-date" datetime="${escapeHtml(item.date)}">${escapeHtml(item.date.slice(5))}</time>
          <div class="activity-main">
            <div class="activity-title">${item.files} 题 <span>${item.commits} 次提交</span></div>
            <div class="file-list">${files}${more}</div>
          </div>
        </article>
      `;
    }).join("");
  }

  renderHeatmap();
  renderPlatforms();
  renderActivity();

  document.getElementById("footer").innerHTML = `
    由 <strong>stats_dashboard.py</strong> 生成，GitHub Actions 每次 push 后部署到 Pages。
    数据范围从 ${escapeHtml(DATA.firstCommit || DATA.rangeStart)} 开始，页面生成时间为 ${escapeHtml(DATA.updatedAt)}。
  `;
})();
</script>
</body>
</html>
"""


def main() -> None:
    counts = count_problems()
    history = get_git_history()
    payload = build_payload(counts, history)
    out = ROOT / "index.html"
    out.write_text(build_html(payload), encoding="utf-8")

    summary = payload["summary"]
    print(f"[OK] {out}")
    print(
        "     "
        f"Total: {summary['grandTotal']} | "
        f"Active days: {summary['activeDays']} | "
        f"Today: {summary['todayFiles']}"
    )


if __name__ == "__main__":
    main()

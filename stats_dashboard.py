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
from typing import Any


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


def get_git_history(days: int = 420) -> dict[str, dict[str, Any]]:
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

    day_data: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"commits": 0, "files": set()}
    )
    current_day = ""
    current_files: set[str] = set()

    def flush_commit() -> None:
        if not current_day or not current_files:
            return
        day_data[current_day]["commits"] += 1
        day_data[current_day]["files"].update(current_files)

    for line in out.splitlines():
        if line.startswith("@@"):
            flush_commit()
            current_day = line[2:].strip()
            current_files = set()
            continue
        if not line or not current_day or should_exclude_history_path(line):
            continue
        current_files.add(line.strip('"').strip("'"))

    flush_commit()

    result: dict[str, dict[str, Any]] = {}
    for day, data in day_data.items():
        files = sorted(data["files"])
        result[day] = {
            "commits": int(data["commits"]),
            "files": len(files),
            "filenames": files,
        }
    return result


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


def build_payload(
    counts: dict[str, dict[str, int]], history: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    now = datetime.now(CST)
    today = now.date()
    today_key = today.isoformat()

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
    parsed_active_days = sorted(day for day in (parse_day(day) for day in active_days) if day)
    first_active = parsed_active_days[0] if parsed_active_days else today
    latest_active = parsed_active_days[-1] if parsed_active_days else None
    current_streak, longest_streak = streaks(active_days, today)

    recent = [
        {
            "date": day,
            "commits": int(info["commits"]),
            "files": int(info["files"]),
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

    early_context = first_active - timedelta(days=28)
    six_month_window = today - timedelta(days=182)
    range_start = max(min(early_context, six_month_window), today - timedelta(days=371))
    span_days = (today - first_active).days + 1 if parsed_active_days else 0
    idle_days = (today - latest_active).days if latest_active else 0
    solution_commits = sum(
        int(info.get("commits", 0))
        for info in history.values()
        if int(info.get("files", 0)) > 0
    )

    heatmap = {
        day: {"files": int(info["files"]), "commits": int(info["commits"])}
        for day, info in history.items()
    }

    return {
        "summary": {
            "grandTotal": grand_total,
            "solutionCommits": solution_commits,
            "activeDays": len(active_days),
            "spanDays": span_days,
            "currentStreak": current_streak,
            "longestStreak": longest_streak,
            "todayFiles": int(history.get(today_key, {}).get("files", 0)),
            "idleDays": idle_days,
            "latestDay": recent[0] if recent else None,
            "bestDay": best_day,
        },
        "platforms": platforms,
        "recent": recent,
        "heatmap": heatmap,
        "firstActive": first_active.isoformat() if parsed_active_days else "",
        "today": today_key,
        "rangeStart": range_start.isoformat(),
        "updatedAt": now.strftime("%Y-%m-%d %H:%M CST"),
        "repoUrl": "https://github.com/ZoomWaterr/python-algo-practice",
    }


def build_html(payload: dict[str, Any]) -> str:
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
    --bg: oklch(0.965 0.018 168);
    --bg-2: oklch(0.938 0.022 202);
    --surface: oklch(0.988 0.006 96);
    --surface-soft: oklch(0.962 0.014 154);
    --surface-blue: oklch(0.947 0.019 225);
    --ink: oklch(0.205 0.028 165);
    --muted: oklch(0.48 0.027 170);
    --faint: oklch(0.62 0.024 170);
    --line: oklch(0.865 0.024 162);
    --line-strong: oklch(0.78 0.034 162);
    --green: oklch(0.47 0.116 154);
    --green-deep: oklch(0.36 0.095 154);
    --blue: oklch(0.49 0.095 235);
    --copper: oklch(0.56 0.116 63);
    --rose: oklch(0.52 0.105 15);
    --paper-shadow: 0 18px 54px oklch(0.28 0.038 160 / 0.12);
    --soft-shadow: 0 10px 26px oklch(0.28 0.038 160 / 0.08);
    --cell: 14px;
    --gap: 4px;
    --h0: oklch(0.91 0.017 154);
    --h1: oklch(0.78 0.07 148);
    --h2: oklch(0.66 0.112 149);
    --h3: oklch(0.53 0.13 151);
    --h4: oklch(0.39 0.112 154);
  }

  * { box-sizing: border-box; }
  html { min-width: 0; }
  body {
    margin: 0;
    min-height: 100vh;
    background:
      linear-gradient(135deg, var(--bg), var(--bg-2) 58%, oklch(0.95 0.016 74));
    color: var(--ink);
    font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    letter-spacing: 0;
  }
  body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
      linear-gradient(to right, oklch(0.5 0.02 160 / 0.05) 1px, transparent 1px),
      linear-gradient(to bottom, oklch(0.5 0.02 160 / 0.04) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: linear-gradient(180deg, oklch(0 0 0 / 0.34), transparent 62%);
  }
  a { color: inherit; }
  .shell {
    width: min(1280px, calc(100% - 36px));
    margin: 0 auto;
    padding: 20px 0 34px;
    position: relative;
  }
  .masthead {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 14px;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
  }
  .brand-mark {
    width: 42px;
    height: 42px;
    display: grid;
    place-items: center;
    border: 1px solid var(--line-strong);
    border-radius: 8px;
    background: var(--surface);
    color: var(--green-deep);
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 13px;
    font-weight: 850;
    box-shadow: inset 0 0 0 4px oklch(0.78 0.08 150 / 0.16);
  }
  .brand-title {
    display: block;
    font-size: 17px;
    font-weight: 800;
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
    min-height: 42px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0 14px;
    border: 1px solid var(--line-strong);
    border-radius: 8px;
    background: oklch(0.99 0.005 96 / 0.82);
    color: var(--ink);
    font-size: 13px;
    font-weight: 750;
    text-decoration: none;
    box-shadow: var(--soft-shadow);
    transition: transform 180ms cubic-bezier(0.16, 1, 0.3, 1), border-color 180ms ease, background 180ms ease;
  }
  .repo-link:hover {
    transform: translateY(-1px);
    border-color: var(--green);
    background: var(--surface);
  }
  .repo-link:active { transform: translateY(0); }
  .repo-link:focus-visible {
    outline: 3px solid oklch(0.68 0.11 154 / 0.38);
    outline-offset: 2px;
  }
  .repo-link svg { width: 16px; height: 16px; }

  .overview {
    display: grid;
    grid-template-columns: minmax(0, 1.45fr) minmax(270px, 0.55fr);
    gap: 1px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--line);
    box-shadow: var(--paper-shadow);
    overflow: hidden;
  }
  .overview-copy,
  .today-panel {
    background: oklch(0.99 0.006 96 / 0.9);
    min-width: 0;
  }
  .overview-copy {
    padding: 24px 30px 22px;
  }
  .eyebrow {
    margin: 0 0 10px;
    color: var(--green-deep);
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 12px;
    font-weight: 850;
    text-transform: uppercase;
  }
  h1 {
    margin: 0;
    max-width: 760px;
    font-size: 36px;
    line-height: 1.1;
    letter-spacing: 0;
  }
  .lead {
    max-width: 70ch;
    margin: 14px 0 0;
    color: var(--muted);
    font-size: 15px;
    line-height: 1.7;
  }
  .hero-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 20px;
  }
  .meta-pill {
    display: inline-flex;
    align-items: center;
    min-height: 30px;
    padding: 0 10px;
    border: 1px solid var(--line);
    border-radius: 999px;
    background: var(--surface-soft);
    color: var(--muted);
    font-size: 12px;
  }
  .meta-pill strong {
    margin-left: 5px;
    color: var(--ink);
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 12px;
    font-variant-numeric: tabular-nums;
  }
  .today-panel {
    padding: 23px 26px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 216px;
  }
  .today-kicker {
    margin: 0;
    color: var(--muted);
    font-size: 13px;
    font-weight: 750;
  }
  .today-date {
    color: var(--faint);
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 12px;
  }
  .today-number {
    margin: 20px 0 10px;
    color: var(--green-deep);
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 72px;
    line-height: 0.9;
    font-weight: 900;
    font-variant-numeric: tabular-nums;
  }
  .today-copy {
    margin: 0;
    color: var(--muted);
    font-size: 13px;
    line-height: 1.6;
  }

  .metric-strip {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    margin: 12px 0;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: oklch(0.99 0.006 96 / 0.86);
    overflow: hidden;
  }
  .metric {
    min-width: 0;
    padding: 12px 16px;
    border-left: 1px solid var(--line);
  }
  .metric:first-child { border-left: 0; }
  .metric-label {
    color: var(--muted);
    font-size: 12px;
    font-weight: 720;
  }
  .metric-value {
    margin-top: 8px;
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 23px;
    line-height: 1;
    font-weight: 900;
    font-variant-numeric: tabular-nums;
  }
  .metric-note {
    margin-top: 6px;
    color: var(--faint);
    font-size: 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .metric:nth-child(2) .metric-value { color: var(--blue); }
  .metric:nth-child(3) .metric-value { color: var(--copper); }
  .metric:nth-child(5) .metric-value { color: var(--green-deep); }

  .content-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.52fr) minmax(310px, 0.78fr);
    gap: 14px;
    align-items: start;
  }
  .stack {
    display: grid;
    gap: 14px;
    min-width: 0;
  }
  .panel {
    border: 1px solid var(--line);
    border-radius: 8px;
    background: oklch(0.99 0.006 96 / 0.88);
    box-shadow: var(--soft-shadow);
    min-width: 0;
  }
  .panel-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    padding: 20px 22px 0;
  }
  .panel-title {
    margin: 0;
    font-size: 17px;
    font-weight: 850;
  }
  .panel-note {
    color: var(--muted);
    font-size: 12px;
    text-align: right;
  }
  .panel-body { padding: 18px 22px 22px; }

  .heatmap-wrap {
    overflow-x: auto;
    overflow-y: visible;
    padding: 10px 0 8px;
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
    margin-left: 28px;
    margin-bottom: 9px;
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
    grid-template-columns: 20px auto;
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
    border: 1px solid oklch(0.28 0.03 160 / 0.05);
    border-radius: 4px;
    background: var(--h0);
    transition: transform 120ms ease, outline-color 120ms ease, background 160ms ease;
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
    transform: translateY(-1px);
    outline: 2px solid oklch(0.24 0.02 160 / 0.5);
    outline-offset: 1px;
  }
  .legend {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 7px;
    margin-top: 12px;
    color: var(--muted);
    font-size: 12px;
  }
  .legend span:not(.legend-label) {
    width: var(--cell);
    height: var(--cell);
    border-radius: 4px;
    display: inline-block;
  }
  .legend .h0 { background: var(--h0); }
  .legend .h1 { background: var(--h1); }
  .legend .h2 { background: var(--h2); }
  .legend .h3 { background: var(--h3); }
  .legend .h4 { background: var(--h4); }

  .rhythm {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--line);
    overflow: hidden;
  }
  .rhythm-item {
    background: var(--surface);
    padding: 16px;
  }
  .rhythm-item span {
    display: block;
    color: var(--muted);
    font-size: 12px;
  }
  .rhythm-item strong {
    display: block;
    margin-top: 8px;
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 26px;
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }
  .rhythm-copy {
    margin: 14px 0 0;
    color: var(--muted);
    font-size: 13px;
    line-height: 1.65;
  }

  .platforms {
    display: grid;
    gap: 16px;
  }
  .platform-row {
    display: grid;
    grid-template-columns: 74px minmax(0, 1fr) 42px;
    gap: 12px;
    align-items: center;
  }
  .platform-name {
    font-size: 13px;
    font-weight: 850;
    text-align: right;
  }
  .bar-track {
    height: 26px;
    border: 1px solid var(--line);
    border-radius: 999px;
    background: var(--surface-soft);
    overflow: hidden;
  }
  .bar-fill {
    width: var(--pct);
    min-width: 26px;
    height: 100%;
    border-radius: inherit;
    background: var(--accent, var(--green));
    transition: width 700ms cubic-bezier(0.16, 1, 0.3, 1);
  }
  .platform-count {
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 13px;
    font-weight: 850;
    font-variant-numeric: tabular-nums;
  }
  .subdir-list {
    grid-column: 2 / 4;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: -6px;
  }
  .tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    min-height: 24px;
    padding: 0 8px;
    border: 1px solid var(--line);
    border-radius: 999px;
    background: var(--surface);
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
    grid-template-columns: 82px 1fr;
    gap: 16px;
    padding: 15px 0;
    border-top: 1px solid var(--line);
  }
  .activity-row:first-child { border-top: 0; padding-top: 0; }
  .activity-date {
    color: var(--muted);
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 12px;
    line-height: 1.8;
  }
  .activity-main { min-width: 0; }
  .activity-title {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 8px;
    font-size: 13px;
    font-weight: 850;
  }
  .activity-title span {
    color: var(--muted);
    font-weight: 650;
  }
  .file-list {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-top: 9px;
  }
  .file-pill {
    max-width: 100%;
    min-height: 25px;
    padding: 4px 8px;
    border: 1px solid oklch(0.86 0.024 170);
    border-radius: 7px;
    background: var(--surface-soft);
    color: oklch(0.31 0.035 164);
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
    margin-top: 20px;
    color: var(--muted);
    font-size: 12px;
    line-height: 1.7;
  }
  .heat-tooltip {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 30;
    max-width: min(320px, calc(100vw - 28px));
    padding: 9px 11px;
    border: 1px solid oklch(0.72 0.03 160);
    border-radius: 8px;
    background: oklch(0.2 0.026 165 / 0.96);
    color: oklch(0.97 0.006 130);
    font-size: 12px;
    line-height: 1.45;
    box-shadow: 0 18px 38px oklch(0.18 0.03 165 / 0.28);
    pointer-events: none;
    opacity: 0;
    transform: translate(-999px, -999px);
    transition: opacity 110ms ease;
  }
  .heat-tooltip.visible { opacity: 1; }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      scroll-behavior: auto !important;
      transition-duration: 0.01ms !important;
    }
  }
  @media (max-width: 1040px) {
    .overview,
    .content-grid {
      grid-template-columns: 1fr;
    }
    .today-panel {
      min-height: 0;
    }
    .metric-strip {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    .metric:nth-child(4) { border-left: 0; border-top: 1px solid var(--line); }
    .metric:nth-child(5) { border-top: 1px solid var(--line); }
  }
  @media (max-width: 680px) {
    :root {
      --cell: 13px;
      --gap: 4px;
    }
    .shell {
      width: min(100% - 22px, 1280px);
      padding-top: 16px;
    }
    .masthead {
      align-items: flex-start;
      flex-direction: column;
    }
    .brand-subtitle {
      white-space: normal;
    }
    .repo-link {
      width: 100%;
      justify-content: center;
    }
    .overview-copy,
    .today-panel {
      padding: 22px 18px;
    }
    h1 {
      font-size: 28px;
      line-height: 1.13;
    }
    .today-number {
      margin-top: 20px;
      font-size: 64px;
    }
    .metric-strip {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .metric {
      border-top: 1px solid var(--line);
    }
    .metric:nth-child(-n + 2) {
      border-top: 0;
    }
    .metric:nth-child(odd) {
      border-left: 0;
    }
    .panel-head,
    .panel-body {
      padding-left: 16px;
      padding-right: 16px;
    }
    .panel-head {
      align-items: flex-start;
      flex-direction: column;
      gap: 5px;
    }
    .platform-row {
      grid-template-columns: 1fr 48px;
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
  <header class="masthead">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">ZW</div>
      <div>
        <span class="brand-title">ZoomWaterr 刷题面板</span>
        <span class="brand-subtitle">Python 3.14 题解记录，随仓库 push 自动刷新</span>
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

  <main>
    <section class="overview" aria-labelledby="dashboard-title">
      <div class="overview-copy">
        <p class="eyebrow">practice ledger</p>
        <h1 id="dashboard-title">把每天写过的题，沉到热力图里。</h1>
        <p class="lead">面板读取题解目录和 git 历史。没有提交的日期也会保留为空白格，等下一次 push 时自动补齐到当天。</p>
        <div class="hero-meta" id="hero-meta"></div>
      </div>
      <aside class="today-panel" aria-label="今日题解摘要">
        <div>
          <p class="today-kicker">今日题解变动</p>
          <span class="today-date" id="today-label"></span>
        </div>
        <div>
          <div class="today-number" id="today-files">0</div>
          <p class="today-copy" id="today-copy"></p>
        </div>
      </aside>
    </section>

    <section class="metric-strip" id="metric-strip" aria-label="刷题统计"></section>

    <section class="content-grid">
      <div class="stack">
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
            <span class="panel-note">只统计题解文件</span>
          </div>
          <div class="panel-body">
            <div class="activity" id="activity"></div>
          </div>
        </section>
      </div>

      <aside class="stack">
        <section class="panel" aria-labelledby="rhythm-title">
          <div class="panel-head">
            <h2 class="panel-title" id="rhythm-title">连续性</h2>
            <span class="panel-note">按自然日计算</span>
          </div>
          <div class="panel-body">
            <div class="rhythm" id="rhythm"></div>
            <p class="rhythm-copy" id="rhythm-copy"></p>
          </div>
        </section>

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
    </section>

    <footer class="footer" id="footer"></footer>
  </main>
</div>
<div class="heat-tooltip" id="heat-tooltip" role="status" aria-live="polite"></div>

<script type="application/json" id="dashboard-data">__DASHBOARD_DATA__</script>
<script>
(() => {
  const DATA = JSON.parse(document.getElementById("dashboard-data").textContent);
  const summary = DATA.summary;
  const platformColors = [
    "var(--green)",
    "var(--blue)",
    "var(--copper)",
    "var(--rose)",
  ];

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

  const dayPhrase = (days) => {
    if (days === 0) return "今天有记录，热力图最右侧已经上色。";
    if (days === 1) return "今天还没有题解变动，空白格已经自动补上。";
    return `已经 ${days} 天没有题解变动，下一次 push 会把中间空白天数一起补齐。`;
  };

  document.getElementById("repo-link").href = DATA.repoUrl;
  document.getElementById("today-label").textContent = DATA.today;
  document.getElementById("today-files").textContent = summary.todayFiles;
  document.getElementById("today-copy").textContent = dayPhrase(summary.idleDays);

  const latest = summary.latestDay;
  const best = summary.bestDay || {};
  document.getElementById("hero-meta").innerHTML = [
    ["首次记录", DATA.firstActive || "暂无"],
    ["最近活跃", latest ? latest.date : "暂无"],
    ["单日最高", best.date ? `${best.files} 题` : "暂无"],
    ["更新时间", DATA.updatedAt],
  ].map(([label, value]) => `<span class="meta-pill">${label}<strong>${escapeHtml(value)}</strong></span>`).join("");

  const metrics = [
    ["总题数", summary.grandTotal, "题解文件"],
    ["题解提交", summary.solutionCommits, "只算题解变动"],
    ["活跃天", summary.activeDays, `${summary.spanDays} 天跨度`],
    ["当前连续", `${summary.currentStreak} 天`, summary.currentStreak ? "保持中" : "等待今天开张"],
    ["最长连续", `${summary.longestStreak} 天`, "历史最佳"],
  ];
  document.getElementById("metric-strip").innerHTML = metrics.map(([label, value, note]) => `
    <article class="metric">
      <div class="metric-label">${escapeHtml(label)}</div>
      <div class="metric-value">${escapeHtml(value)}</div>
      <div class="metric-note">${escapeHtml(note)}</div>
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
    let weekHtml = "";

    for (let week = 0; week < weeks; week += 1) {
      const weekStart = addDays(alignedStart, week * 7);
      let monthLabel = "";
      for (let dayIndex = 0; dayIndex < 7; dayIndex += 1) {
        const day = addDays(weekStart, dayIndex);
        if (week === 0 && dayIndex === 0) monthLabel = monthName(day);
        if (day.getDate() === 1) monthLabel = monthName(day);
      }
      monthHtml += `<span class="month-label">${monthLabel}</span>`;

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
          ? `${key}: ${files} 题, ${commits} 次题解提交`
          : `${key}: 无题解变动`;
        cells += `<span class="cell h${level(files)}" data-tip="${escapeHtml(tip)}" aria-label="${escapeHtml(tip)}"></span>`;
      }
      weekHtml += `<span class="week">${cells}</span>`;
    }

    const activeRange = `${formatDate(alignedStart)} 至 ${DATA.today}`;
    const heatmapEl = document.getElementById("heatmap");
    document.getElementById("heatmap-note").textContent = activeRange;
    heatmapEl.style.setProperty("--weeks", weeks);
    heatmapEl.innerHTML = `
      <div class="month-row">${monthHtml}</div>
      <div class="heatmap-body">
        <div class="day-labels" aria-hidden="true"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span></div>
        <div class="week-grid">${weekHtml}</div>
      </div>
    `;
  }

  function renderRhythm() {
    document.getElementById("rhythm").innerHTML = `
      <div class="rhythm-item"><span>当前连续</span><strong>${summary.currentStreak} 天</strong></div>
      <div class="rhythm-item"><span>最长连续</span><strong>${summary.longestStreak} 天</strong></div>
    `;
    document.getElementById("rhythm-copy").textContent = dayPhrase(summary.idleDays);
  }

  function renderPlatforms() {
    const maxTotal = Math.max(...DATA.platforms.map((platform) => platform.total), 1);
    document.getElementById("platforms").innerHTML = DATA.platforms.map((platform, index) => {
      const pct = `${Math.max(8, Math.round((platform.total / maxTotal) * 100))}%`;
      const subdirs = (platform.subdirs || []).map((subdir) => `
        <span class="tag">${escapeHtml(subdir.name)}<strong>${subdir.count}</strong></span>
      `).join("");
      return `
        <div class="platform-row">
          <div class="platform-name">${escapeHtml(platform.name)}</div>
          <div class="bar-track"><div class="bar-fill" style="--pct:${pct};--accent:${platformColors[index % platformColors.length]}"></div></div>
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
            <div class="activity-title">${item.files} 题 <span>${item.commits} 次题解提交</span></div>
            <div class="file-list">${files}${more}</div>
          </div>
        </article>
      `;
    }).join("");
  }

  function wireHeatTooltip() {
    const heatmap = document.getElementById("heatmap");
    const tooltip = document.getElementById("heat-tooltip");
    let activeCell = null;

    const position = (event) => {
      const margin = 14;
      const rect = tooltip.getBoundingClientRect();
      let x = event.clientX + 14;
      let y = event.clientY - rect.height - 14;

      if (x + rect.width > window.innerWidth - margin) {
        x = event.clientX - rect.width - 14;
      }
      if (y < margin) {
        y = event.clientY + 14;
      }
      x = Math.max(margin, Math.min(x, window.innerWidth - rect.width - margin));
      y = Math.max(margin, Math.min(y, window.innerHeight - rect.height - margin));
      tooltip.style.transform = `translate(${Math.round(x)}px, ${Math.round(y)}px)`;
    };

    const show = (cell, event) => {
      activeCell = cell;
      tooltip.textContent = cell.dataset.tip || "";
      tooltip.classList.add("visible");
      position(event);
    };

    const hide = () => {
      activeCell = null;
      tooltip.classList.remove("visible");
      tooltip.style.transform = "translate(-999px, -999px)";
    };

    heatmap.addEventListener("pointerover", (event) => {
      const cell = event.target.closest(".cell[data-tip]");
      if (!cell || !heatmap.contains(cell)) return;
      show(cell, event);
    });
    heatmap.addEventListener("pointermove", (event) => {
      if (activeCell) position(event);
    });
    heatmap.addEventListener("pointerout", (event) => {
      const next = event.relatedTarget;
      if (activeCell && (!next || !activeCell.contains(next))) hide();
    });
    window.addEventListener("scroll", hide, { passive: true });
    window.addEventListener("resize", hide);
  }

  renderHeatmap();
  renderRhythm();
  renderPlatforms();
  renderActivity();
  wireHeatTooltip();

  document.getElementById("footer").innerHTML = `
    由 <strong>stats_dashboard.py</strong> 生成。页面每次 push 后重建，统计范围从 ${escapeHtml(DATA.firstActive || DATA.rangeStart)} 到 ${escapeHtml(DATA.today)}，生成时间 ${escapeHtml(DATA.updatedAt)}。
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

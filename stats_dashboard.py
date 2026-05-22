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
TEMPLATE_PATH = ROOT / "dashboard_template.html"


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
        "pagesUrl": "https://zoomwaterr.github.io/python-algo-practice/",
    }


def build_html(payload: dict[str, Any]) -> str:
    data_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    data_json = data_json.replace("</", "<\\/")
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.replace("__DASHBOARD_DATA__", data_json)


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

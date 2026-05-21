"""
刷题数据可视化面板生成器 v2
每次运行生成 index.html，包含：
  - 统计卡片（总数 + 分平台）
  - GitHub 像素级同款热力图
  - 平台进度条
  - 最近活动时间线
  - GitHub 主页贡献图（实时抓取）
"""
import os
import json
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).parent

TRACK = {
    "洛谷": "洛谷",
    "C语言网": "C语言网",
    "蓝桥云课": "蓝桥云课",
}

ROOT_EXCLUDE = {"stats.py", "generate_readme.py", "stats_dashboard.py"}
EXCLUDE_KEYWORDS = ["temp", "__pycache__"]


def should_exclude(file_path: Path) -> bool:
    if file_path.parent == ROOT:
        return True
    if file_path.name in ROOT_EXCLUDE:
        return True
    name_lower = file_path.name.lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in name_lower:
            return True
    return False


def count_problems() -> dict:
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
            py_files = [f for f in sub.rglob("*.py") if not should_exclude(f)]
            n = len(py_files)
            if n > 0:
                cats[sub.name] = n
                total += n
        cats["_total"] = total
        result[label] = cats
    return result


def get_git_history(days: int = 365) -> dict:
    try:
        out = subprocess.check_output(
            [
                "git", "-c", "core.quotepath=false",
                "log",
                "--format=@@%ad",
                "--date=short",
                "--name-only",
                f"--since={days} days ago",
            ],
            cwd=ROOT, encoding="utf-8",
        )
    except Exception:
        return {}

    day_data: dict[str, dict] = defaultdict(lambda: {"commits": 0, "files": set()})
    current_day = ""

    for line in out.strip().splitlines():
        if not line:
            continue
        if line.startswith("@@"):
            current_day = line[2:].strip()
            day_data[current_day]["commits"] += 1
            continue
        if not line.endswith(".py"):
            continue
        clean_path = Path(line.strip('"').strip("'"))
        fname = clean_path.name
        if fname in ROOT_EXCLUDE:
            continue
        if any(kw in fname.lower() for kw in EXCLUDE_KEYWORDS):
            continue
        day_data[current_day]["files"].add(str(clean_path))

    result = {}
    for day, data in day_data.items():
        result[day] = {
            "commits": data["commits"],
            "files": len(data["files"]),
            "filenames": sorted([Path(f).name for f in data["files"]]),
        }
    return result


def get_first_commit_date() -> str:
    try:
        out = subprocess.check_output(
            ["git", "log", "--reverse", "--format=%ad", "--date=short"],
            cwd=ROOT, encoding="utf-8",
        )
        first = out.strip().splitlines()[0] if out.strip() else ""
        return first
    except Exception:
        return ""


def build_html(counts: dict, history: dict) -> str:
    grand_total = sum(c["_total"] for c in counts.values())
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    first_commit = get_first_commit_date()

    platforms = []
    for label, cats in counts.items():
        platforms.append({
            "name": label,
            "total": cats["_total"],
            "subdirs": {k: v for k, v in cats.items() if k != "_total"},
        })

    recent_days = sorted(history.items(), reverse=True)[:14]
    recent = [
        {"date": d, "commits": h["commits"], "files": h["files"],
         "filenames": h.get("filenames", [])}
        for d, h in recent_days
    ]

    total_commits = sum(h["commits"] for h in history.values())

    data_json = json.dumps({
        "grandTotal": grand_total,
        "platforms": platforms,
        "history": {k: v for k, v in history.items()},
        "recent": recent,
        "totalCommits": total_commits,
        "firstCommit": first_commit,
        "updatedAt": updated_at,
    }, ensure_ascii=False)

    return HTML_TEMPLATE.format(data_json=data_json)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>刷题面板 · ZoomWaterr</title>
<style>
  :root {{
    --bg: #0d1117;
    --card: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --muted: #8b949e;
    --green: #3fb950;
    --blue: #58a6ff;
    --purple: #bc8cff;
    --orange: #d2991d;
    /* GitHub exact heatmap colors */
    --gh-0: #161b22;
    --gh-1: #0e4429;
    --gh-2: #006d32;
    --gh-3: #26a641;
    --gh-4: #39d353;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    min-height: 100vh;
  }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 32px 20px; }}

  /* ── Header ── */
  .header {{
    display: flex; align-items: center; gap: 16px; margin-bottom: 32px;
  }}
  .avatar {{
    width: 56px; height: 56px; border-radius: 50%;
    background: linear-gradient(135deg, var(--green), var(--blue));
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; font-weight: 900; flex-shrink: 0;
  }}
  .header h1 {{ font-size: 24px; font-weight: 700; }}
  .header .sub {{ color: var(--muted); font-size: 13px; }}

  /* ── Stat Cards ── */
  .cards {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
    gap: 10px; margin-bottom: 28px;
  }}
  .card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 18px 14px; text-align: center;
    transition: transform 0.15s;
  }}
  .card:hover {{ transform: translateY(-2px); }}
  .card .num {{
    font-size: 32px; font-weight: 800; line-height: 1.1;
    color: var(--green);
  }}
  .card:nth-child(2) .num {{ color: var(--blue); }}
  .card:nth-child(3) .num {{ color: var(--purple); }}
  .card:nth-child(4) .num {{ color: var(--orange); }}
  .card:nth-child(5) .num {{ color: var(--green); }}
  .card .label {{ color: var(--muted); font-size: 12px; margin-top: 4px; }}

  /* ── Section Title ── */
  .section-title {{
    font-size: 16px; font-weight: 600; margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
  }}

  /* ── Heatmap (GitHub pixel-perfect clone) ── */
  .heatmap-container {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px 16px 12px 16px; margin-bottom: 24px;
    overflow-x: auto;
  }}
  .heatmap-wrapper {{
    display: inline-block; min-width: 680px;
  }}
  .heatmap-table {{
    border-collapse: separate; border-spacing: 3px;
  }}
  .heatmap-table td {{
    width: 12px; height: 12px; border-radius: 2px;
    position: relative;
  }}
  .heatmap-table td[data-tooltip]:hover {{
    outline: 2px solid rgba(255,255,255,0.6); outline-offset: 0px;
  }}
  .heatmap-table td[data-tooltip]:hover::after {{
    content: attr(data-tooltip);
    position: absolute; bottom: calc(100% + 8px); left: 50%;
    transform: translateX(-50%);
    background: #1c2128; color: var(--text);
    padding: 5px 10px; border-radius: 6px; font-size: 11px;
    white-space: nowrap; pointer-events: none; z-index: 100;
    border: 1px solid var(--border); box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  }}
  .gh-day-label {{
    font-size: 11px; color: var(--muted); text-align: left;
    padding-right: 4px; width: 28px; line-height: 1;
    background: none !important;
  }}
  .gh-month-label {{
    font-size: 11px; color: var(--muted); text-align: left;
    padding-bottom: 4px; height: 16px;
    background: none !important;
  }}
  /* GitHub exact heatmap levels */
  .gh-0 {{ background: var(--gh-0); border: 1px solid rgba(48,54,61,0.5); }}
  .gh-1 {{ background: var(--gh-1); }}
  .gh-2 {{ background: var(--gh-2); }}
  .gh-3 {{ background: var(--gh-3); }}
  .gh-4 {{ background: var(--gh-4); }}

  .heatmap-legend {{
    display: flex; align-items: center; gap: 3px; margin-top: 12px;
    justify-content: flex-end; font-size: 11px; color: var(--muted);
  }}
  .heatmap-legend .dot {{
    width: 12px; height: 12px; border-radius: 2px; display: inline-block;
  }}

  /* ── Platform bars ── */
  .platforms {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px; margin-bottom: 24px;
  }}
  .platform-row {{
    display: flex; align-items: center; gap: 12px; margin-bottom: 14px;
  }}
  .platform-row:last-child {{ margin-bottom: 0; }}
  .platform-name {{ width: 65px; text-align: right; font-weight: 600; font-size: 13px; flex-shrink: 0; }}
  .platform-bar-wrap {{ flex: 1; height: 26px; background: var(--bg); border-radius: 5px; overflow: hidden; }}
  .platform-bar {{
    height: 100%; border-radius: 5px; display: flex; align-items: center;
    padding-left: 10px; font-size: 12px; font-weight: 700;
    transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
  }}
  .platform-bar.lg {{ background: linear-gradient(90deg, #1a7f37, #3fb950); color: #fff; }}
  .platform-bar.cl {{ background: linear-gradient(90deg, #1f6feb, #58a6ff); color: #fff; }}
  .platform-bar.lq {{ background: linear-gradient(90deg, #6e40c9, #bc8cff); color: #fff; }}
  .subdirs {{
    margin-left: 77px; margin-bottom: 10px;
    display: flex; flex-wrap: wrap; gap: 5px;
  }}
  .subdir-tag {{
    background: var(--bg); color: var(--muted);
    padding: 1px 9px; border-radius: 10px; font-size: 11px;
    border: 1px solid var(--border);
  }}

  /* ── Recent Activity ── */
  .activity {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px; margin-bottom: 24px;
  }}
  .activity-item {{
    display: flex; align-items: flex-start; gap: 12px;
    padding: 9px 0; border-bottom: 1px solid rgba(48,54,61,0.5);
  }}
  .activity-item:last-child {{ border-bottom: none; }}
  .act-date {{
    font-size: 12px; color: var(--muted); flex-shrink: 0;
    font-variant-numeric: tabular-nums; width: 48px;
  }}
  .act-dot {{
    width: 8px; height: 8px; border-radius: 50%; margin-top: 5px; flex-shrink: 0;
  }}
  .act-dot.big {{ background: var(--green); box-shadow: 0 0 8px rgba(63,185,80,0.6); }}
  .act-dot.medium {{ background: var(--blue); }}
  .act-dot.small {{ background: var(--purple); }}
  .act-files {{ font-size: 13px; color: var(--text); line-height: 1.5; }}
  .act-count {{ font-weight: 700; color: var(--green); }}
  .act-fname {{
    color: var(--muted); font-size: 11px; margin-left: 4px;
  }}

  /* ── Footer ── */
  .footer {{
    text-align: center; color: var(--muted); font-size: 11px;
    padding: 20px 0; border-top: 1px solid var(--border); margin-top: 8px;
  }}
  .footer a {{ color: var(--blue); text-decoration: none; }}
  .footer a:hover {{ text-decoration: underline; }}

  /* ── Bookmark hint ── */
  .bookmark-hint {{
    background: linear-gradient(135deg, rgba(63,185,80,0.1), rgba(88,166,255,0.1));
    border: 1px solid rgba(63,185,80,0.3); border-radius: 8px;
    padding: 12px 16px; margin-bottom: 24px; font-size: 13px; color: var(--muted);
    display: flex; align-items: center; gap: 8px;
  }}
  .bookmark-hint strong {{ color: var(--green); }}

  @media (max-width: 640px) {{
    .cards {{ grid-template-columns: repeat(3, 1fr); }}
    .heatmap-wrapper {{ min-width: auto; }}
  }}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <div class="avatar">ZT</div>
    <div>
      <h1>Python 算法刷题面板</h1>
      <div class="sub">ZoomWaterr · 从零到百题，每天进步一点点</div>
    </div>
  </div>

  <!-- Bookmark hint -->
  <div class="bookmark-hint">
    <span style="font-size:18px">📌</span>
    <span>把本页加入书签：<strong>Ctrl+D</strong>，以后每次打开就是最新数据</span>
  </div>

  <!-- Stat Cards -->
  <div class="cards" id="cards"></div>

  <!-- Heatmap -->
  <div class="heatmap-container">
    <div class="section-title">📅 刷题热力图</div>
    <div id="heatmap"></div>
    <div class="heatmap-legend">
      少
      <span class="dot gh-0"></span>
      <span class="dot gh-1"></span>
      <span class="dot gh-2"></span>
      <span class="dot gh-3"></span>
      <span class="dot gh-4"></span>
      多
    </div>
  </div>

  <!-- Platform Breakdown -->
  <div class="platforms">
    <div class="section-title">📊 平台分布</div>
    <div id="platforms"></div>
  </div>

  <!-- Recent Activity -->
  <div class="activity">
    <div class="section-title">🔥 最近活动</div>
    <div id="activity"></div>
  </div>

  <!-- Footer -->
  <div class="footer" id="footer"></div>

</div>

<script>
const DATA = {data_json};

function buildCards() {{
  const cards = document.getElementById('cards');
  cards.innerHTML = `
    <div class="card">
      <div class="num">${{DATA.grandTotal}}</div>
      <div class="label">总题数</div>
    </div>
    ${{DATA.platforms.map(p => `
    <div class="card">
      <div class="num">${{p.total}}</div>
      <div class="label">${{p.name}}</div>
    </div>
    `).join('')}}
    <div class="card">
      <div class="num">${{DATA.totalCommits}}</div>
      <div class="label">总提交</div>
    </div>
  `;
}}

function buildHeatmap() {{
  const container = document.getElementById('heatmap');
  const history = DATA.history;
  const allDates = Object.keys(history).sort();

  if (allDates.length === 0) {{
    container.innerHTML = '<p style="color:var(--muted);font-size:13px">还没有刷题记录，开始你的第一题吧！</p>';
    return;
  }}

  const today = new Date();
  today.setHours(0,0,0,0);

  // Start from the Sunday of the week of first commit (or today - 90d, whichever is earlier)
  const firstDate = DATA.firstCommit ? new Date(DATA.firstCommit + 'T00:00:00') : new Date(today);
  const minStart = new Date(today);
  minStart.setDate(minStart.getDate() - 90); // at least 3 months of grid

  const start = firstDate < minStart ? new Date(firstDate) : new Date(minStart);
  start.setDate(start.getDate() - start.getDay()); // align to Sunday

  const totalDays = Math.ceil((today - start) / (1000 * 60 * 60 * 24));
  const numWeeks = Math.ceil(totalDays / 7) + 1;
  const weeks = [];  // weeks[weekIdx][dayIdx] = {{date, level, files, tooltip}}

  let current = new Date(start);
  for (let w = 0; w < numWeeks; w++) {{
    const week = [];
    for (let d = 0; d < 7; d++) {{
      const dateStr = current.toISOString().slice(0, 10);
      const data = history[dateStr];
      const files = data ? data.files : 0;
      let level = 0;
      if (files >= 1 && files <= 2) level = 1;
      else if (files <= 5) level = 2;
      else if (files <= 10) level = 3;
      else if (files > 10) level = 4;

      const isFuture = current > today;
      const tooltip = isFuture ? '' :
        (files > 0 ? `${{dateStr}}: ${{files}} 题, ${{data.commits}} 次提交` : `${{dateStr}}: 无刷题记录`);

      // Show month label on first day of month
      const showMonth = d === 0 && current.getDate() <= 7;

      week.push({{
        dateStr, files, level, tooltip, isFuture,
        showMonth, monthLabel: current.getMonth() + 1 + '月'
      }});
      current.setDate(current.getDate() + 1);
    }}
    weeks.push(week);
  }}

  // Day labels (GitHub shows Mon, Wed, Fri)
  const dayLabels = ['', 'Mon', '', 'Wed', '', 'Fri', ''];

  // Build table
  let html = '<div class="heatmap-wrapper"><table class="heatmap-table"><tbody>';

  // Month label row
  html += '<tr>';
  html += '<td class="gh-month-label"></td>'; // day label column
  weeks.forEach((week, wi) => {{
    const firstDay = week[0];
    if (firstDay.showMonth && !firstDay.isFuture) {{
      html += `<td class="gh-month-label" colspan="1">${{firstDay.monthLabel}}</td>`;
    }} else {{
      html += '<td class="gh-month-label"></td>';
    }}
  }});
  html += '</tr>';

  // Day rows (7 rows for Sun-Sat, but we can skip some)
  for (let dayOfWeek = 0; dayOfWeek < 7; dayOfWeek++) {{
    html += '<tr>';
    html += `<td class="gh-day-label">${{dayLabels[dayOfWeek]}}</td>`;
    weeks.forEach(week => {{
      const day = week[dayOfWeek];
      if (day.isFuture) {{
        html += '<td></td>';
      }} else {{
        html += `<td class="gh-${{day.level}}" data-tooltip="${{day.tooltip}}"></td>`;
      }}
    }});
    html += '</tr>';
  }}

  html += '</tbody></table></div>';
  container.innerHTML = html;
}}

function buildPlatforms() {{
  const container = document.getElementById('platforms');
  const maxTotal = Math.max(...DATA.platforms.map(p => p.total), 1);

  let html = DATA.platforms.map((pl, i) => {{
    const pct = Math.max((pl.total / maxTotal * 100).toFixed(0), 8);
    const barClass = ['lg', 'cl', 'lq'][i] || '';
    const subHtml = Object.entries(pl.subdirs).length > 0
      ? `<div class="subdirs">${{Object.entries(pl.subdirs).map(([k,v]) =>
          `<span class="subdir-tag">${{k}}: ${{v}}题</span>`
        ).join('')}}</div>`
      : '';
    return `
      <div class="platform-row">
        <span class="platform-name">${{pl.name}}</span>
        <div class="platform-bar-wrap">
          <div class="platform-bar ${{barClass}}" style="width:${{pct}}%">${{pl.total}} 题</div>
        </div>
      </div>
      ${{subHtml}}
    `;
  }}).join('');
  container.innerHTML = html;
}}

function buildActivity() {{
  const container = document.getElementById('activity');
  const recent = DATA.recent;

  if (recent.length === 0) {{
    container.innerHTML = '<p style="color:var(--muted);font-size:13px">暂无活动</p>';
    return;
  }}

  let html = recent.map(item => {{
    const dotClass = item.files >= 8 ? 'big' : item.files >= 4 ? 'medium' : 'small';
    const fnames = (item.filenames || []).slice(0, 4).map(f =>
      `<span class="act-fname">${{f}}</span>`
    ).join('');
    const more = (item.filenames || []).length > 4
      ? `<span class="act-fname">+${{item.filenames.length - 4}} more</span>` : '';
    return `
      <div class="activity-item">
        <span class="act-date">${{item.date.slice(5)}}</span>
        <span class="act-dot ${{dotClass}}"></span>
        <span class="act-files">
          <span class="act-count">+${{item.files}} 题</span>
          · ${{item.commits}} 次提交
          <br>${{fnames}}${{more}}
        </span>
      </div>
    `;
  }}).join('');
  container.innerHTML = html;
}}

function buildFooter() {{
  document.getElementById('footer').innerHTML = `
    自动生成 · ${{DATA.updatedAt}}
    ${{DATA.firstCommit ? ' · 始于 ' + DATA.firstCommit : ''}}
    · <a href="https://github.com/ZoomWaterr/python-algo-practice">GitHub</a>
    · <a href="#" onclick="navigator.clipboard.writeText(location.href);this.textContent='已复制!';setTimeout(()=>this.textContent='复制链接',1500);return false">复制链接</a>
  `;
}}

buildCards();
buildHeatmap();
buildPlatforms();
buildActivity();
buildFooter();
</script>
</body>
</html>"""


def main():
    import sys
    counts = count_problems()
    history = get_git_history(days=365)
    html = build_html(counts, history)
    out = ROOT / "index.html"
    out.write_text(html, encoding="utf-8")
    grand = sum(c["_total"] for c in counts.values())
    print(f"[OK] Dashboard generated: {out}")
    print(f"     Total: {grand} problems | Active days: {len(history)}")


if __name__ == "__main__":
    main()

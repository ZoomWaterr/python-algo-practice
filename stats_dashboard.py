"""
刷题数据可视化面板生成器
每次运行生成 index.html，包含：
  - 统计卡片（总数 + 分平台）
  - GitHub 风格热力图
  - 平台进度条
  - 最近活动时间线
  - 每日趋势曲线
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
    """获取每天的提交和文件变更数据，用于热力图"""
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
    """获取仓库第一次提交的日期"""
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

    # 平台排行榜数据
    platforms = []
    for label, cats in counts.items():
        platforms.append({
            "name": label,
            "total": cats["_total"],
            "subdirs": {k: v for k, v in cats.items() if k != "_total"},
        })

    # 最近活动
    recent_days = sorted(history.items(), reverse=True)[:14]
    recent = [
        {"date": d, "commits": h["commits"], "files": h["files"],
         "filenames": h.get("filenames", [])}
        for d, h in recent_days
    ]

    # 总提交数
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

    return f"""<!DOCTYPE html>
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
    --red: #f85149;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    min-height: 100vh;
  }}

  .container {{ max-width: 960px; margin: 0 auto; padding: 40px 24px; }}

  /* ── Header ── */
  .header {{
    display: flex; align-items: center; gap: 16px; margin-bottom: 32px;
  }}
  .avatar {{
    width: 56px; height: 56px; border-radius: 50%;
    background: linear-gradient(135deg, var(--green), var(--blue));
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; font-weight: 900;
  }}
  .header h1 {{ font-size: 28px; font-weight: 700; }}
  .header .sub {{ color: var(--muted); font-size: 14px; }}

  /* ── Stat Cards ── */
  .cards {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px; margin-bottom: 28px;
  }}
  .card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px 16px; text-align: center;
    transition: transform 0.15s, box-shadow 0.15s;
  }}
  .card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  }}
  .card .num {{
    font-size: 36px; font-weight: 800; line-height: 1.1;
    background: linear-gradient(135deg, var(--green), var(--blue));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  .card:nth-child(2) .num {{
    background: linear-gradient(135deg, #58a6ff, #3fb950);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  .card:nth-child(3) .num {{ color: var(--blue); -webkit-text-fill-color: var(--blue); }}
  .card:nth-child(4) .num {{ color: var(--purple); -webkit-text-fill-color: var(--purple); }}
  .card:nth-child(5) .num {{ color: var(--orange); -webkit-text-fill-color: var(--orange); }}
  .card .label {{ color: var(--muted); font-size: 13px; margin-top: 6px; }}

  /* ── Heatmap ── */
  .section-title {{
    font-size: 18px; font-weight: 600; margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
  }}
  .heatmap-container {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px; margin-bottom: 28px;
    overflow-x: auto;
  }}
  .heatmap {{
    display: flex; gap: 3px;
  }}
  .heatmap-col {{ display: flex; flex-direction: column; gap: 3px; }}
  .heatmap-cell {{
    width: 13px; height: 13px; border-radius: 3px; cursor: default;
    position: relative;
  }}
  .heatmap-cell:hover {{ outline: 2px solid rgba(255,255,255,0.5); }}
  .heatmap-cell[data-tooltip]:hover::after {{
    content: attr(data-tooltip);
    position: absolute; bottom: calc(100% + 6px); left: 50%;
    transform: translateX(-50%);
    background: #1c2128; color: var(--text);
    padding: 4px 10px; border-radius: 6px; font-size: 12px;
    white-space: nowrap; pointer-events: none; z-index: 10;
    border: 1px solid var(--border);
  }}
  .level-0 {{ background: #161b22; border: 1px solid #30363d; }}
  .level-1 {{ background: #0e4429; }}
  .level-2 {{ background: #006d32; }}
  .level-3 {{ background: #26a641; }}
  .level-4 {{ background: #39d353; }}

  .heatmap-legend {{
    display: flex; align-items: center; gap: 4px; margin-top: 16px;
    justify-content: flex-end; font-size: 12px; color: var(--muted);
  }}
  .heatmap-legend .cell {{ width: 13px; height: 13px; border-radius: 3px; }}
  .month-labels {{ display: flex; margin-bottom: 6px; font-size: 12px; color: var(--muted); }}
  .month-labels span {{ flex: 1; }}

  /* ── Platform bars ── */
  .platforms {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px; margin-bottom: 28px;
  }}
  .platform-row {{
    display: flex; align-items: center; gap: 12px; margin-bottom: 16px;
  }}
  .platform-row:last-child {{ margin-bottom: 0; }}
  .platform-name {{ width: 70px; text-align: right; font-weight: 600; font-size: 14px; flex-shrink: 0; }}
  .platform-bar-wrap {{ flex: 1; height: 28px; background: var(--bg); border-radius: 6px; overflow: hidden; position: relative; }}
  .platform-bar {{
    height: 100%; border-radius: 6px; display: flex; align-items: center;
    padding-left: 12px; font-size: 13px; font-weight: 700;
    transition: width 0.6s ease;
    min-width: fit-content;
  }}
  .platform-bar.lg {{ background: linear-gradient(90deg, #1a7f37, #3fb950); color: #fff; }}
  .platform-bar.cl {{ background: linear-gradient(90deg, #1f6feb, #58a6ff); color: #fff; }}
  .platform-bar.lq {{ background: linear-gradient(90deg, #6e40c9, #bc8cff); color: #fff; }}
  .platform-count {{ font-weight: 800; font-size: 14px; color: var(--text); flex-shrink: 0; }}

  /* ── Subdirs ── */
  .subdirs {{
    margin-left: 82px; margin-bottom: 12px;
    display: flex; flex-wrap: wrap; gap: 6px;
  }}
  .subdir-tag {{
    background: var(--bg); color: var(--muted);
    padding: 2px 10px; border-radius: 12px; font-size: 12px;
    border: 1px solid var(--border);
  }}

  /* ── Recent Activity ── */
  .activity {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px; margin-bottom: 28px;
  }}
  .activity-item {{
    display: flex; align-items: flex-start; gap: 14px;
    padding: 10px 0; border-bottom: 1px solid var(--border);
  }}
  .activity-item:last-child {{ border-bottom: none; }}
  .act-date {{
    font-size: 13px; color: var(--muted); flex-shrink: 0;
    font-variant-numeric: tabular-nums; width: 60px;
  }}
  .act-dot {{
    width: 10px; height: 10px; border-radius: 50%; margin-top: 4px; flex-shrink: 0;
  }}
  .act-dot.big {{ background: var(--green); box-shadow: 0 0 8px rgba(63,185,80,0.5); }}
  .act-dot.medium {{ background: var(--blue); }}
  .act-dot.small {{ background: var(--purple); }}
  .act-files {{ font-size: 14px; color: var(--text); }}
  .act-count {{ font-weight: 700; color: var(--green); }}
  .act-fname {{
    color: var(--muted); font-size: 12px; margin-left: 4px;
  }}

  /* ── Footer ── */
  .footer {{
    text-align: center; color: var(--muted); font-size: 12px;
    padding: 24px 0; border-top: 1px solid var(--border);
  }}

  /* ── Responsive ── */
  @media (max-width: 640px) {{
    .cards {{ grid-template-columns: repeat(2, 1fr); }}
    .heatmap {{ font-size: 10px; }}
    .platform-name {{ width: 55px; font-size: 12px; }}
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

  <!-- Stat Cards -->
  <div class="cards" id="cards"></div>

  <!-- Heatmap -->
  <div class="heatmap-container">
    <div class="section-title">📅 刷题热力图</div>
    <div id="heatmap"></div>
    <div class="heatmap-legend">
      少
      <span class="cell level-0"></span>
      <span class="cell level-1"></span>
      <span class="cell level-2"></span>
      <span class="cell level-3"></span>
      <span class="cell level-4"></span>
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
  const p = DATA.platforms;
  const maxTotal = Math.max(...p.map(x => x.total));

  cards.innerHTML = `
    <div class="card">
      <div class="num">${{DATA.grandTotal}}</div>
      <div class="label">📝 总题数</div>
    </div>
    ${{p.map(pl => `
    <div class="card">
      <div class="num">${{pl.total}}</div>
      <div class="label">${{pl.name}}</div>
    </div>
    `).join('')}}
    <div class="card">
      <div class="num">${{DATA.totalCommits}}</div>
      <div class="label">📦 总提交</div>
    </div>
  `;
}}

function buildHeatmap() {{
  const container = document.getElementById('heatmap');
  const history = DATA.history;
  const allDates = Object.keys(history).sort();

  if (allDates.length === 0) {{
    container.innerHTML = '<p style="color:var(--muted)">暂无数据</p>';
    return;
  }}

  // 找到最早和最晚日期
  const firstDate = new Date(allDates[0]);
  const lastDate = new Date(allDates[allDates.length - 1]);

  // 扩展到完整的周范围
  const start = new Date(firstDate);
  start.setDate(start.getDate() - start.getDay()); // 回到周日
  const end = new Date(lastDate);

  // 按周组织
  const weeks = [];
  let current = new Date(start);
  while (current <= end) {{
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

      const tooltip = files > 0 ? `${{dateStr}}: ${{files}} 题, ${{data.commits}} 次提交` : dateStr;
      week.push({{ dateStr, files, level, tooltip }});
      current.setDate(current.getDate() + 1);
    }}
    weeks.push(week);
    // current is already advanced 7 days
  }}

  // 月份标签
  const months = [];
  let lastMonth = -1;
  weeks.forEach((week, wi) => {{
    const d = new Date(week[0].dateStr);
    if (d.getMonth() !== lastMonth) {{
      months.push({{ label: (d.getMonth() + 1) + '月', index: wi }});
      lastMonth = d.getMonth();
    }}
  }});

  let html = '<div style="display:flex;gap:3px;font-size:12px;color:var(--muted);margin-bottom:8px;min-width:' + (weeks.length * 16) + 'px">';
  months.forEach(m => {{
    // Calculate approximate position
    const left = m.index * 16;
    html += `<span style="position:absolute;left:${{left}}px;font-size:12px">${{m.label}}</span>`;
  }});
  html += '</div>';

  html += '<div class="heatmap" style="position:relative">';
  // Day labels
  const dayLabels = ['', '一', '', '三', '', '五', ''];
  html += '<div style="display:flex;flex-direction:column;gap:3px;margin-right:6px;font-size:11px;color:var(--muted);padding-top:14px">';
  dayLabels.forEach(l => {{
    html += `<span style="height:13px;line-height:13px">${{l}}</span>`;
  }});
  html += '</div>';

  weeks.forEach((week, wi) => {{
    html += '<div class="heatmap-col" style="padding-top:14px">';
    week.forEach((day, di) => {{
      html += `<div class="heatmap-cell level-${{day.level}}" data-tooltip="${{day.tooltip}}"></div>`;
    }});
    html += '</div>';
  }});
  html += '</div>';

  container.innerHTML = html;
}}

function buildPlatforms() {{
  const container = document.getElementById('platforms');
  const maxTotal = Math.max(...DATA.platforms.map(p => p.total), 1);

  let html = DATA.platforms.map((pl, i) => {{
    const pct = (pl.total / maxTotal * 100).toFixed(0);
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
    container.innerHTML = '<p style="color:var(--muted)">暂无活动</p>';
    return;
  }}

  let html = recent.map(item => {{
    const dotClass = item.files >= 8 ? 'big' : item.files >= 4 ? 'medium' : 'small';
    const fnames = (item.filenames || []).slice(0, 5).map(f =>
      `<span class="act-fname">${{f}}</span>`
    ).join('');
    const more = (item.filenames || []).length > 5
      ? `<span class="act-fname">+${{item.filenames.length - 5}} more</span>` : '';
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
    🚀 自动生成 · 最后更新: ${{DATA.updatedAt}}
    ${{DATA.firstCommit ? ' · 始于 ' + DATA.firstCommit : ''}}
    · <a href="https://github.com/ZoomWaterr/python-algo-practice" style="color:var(--blue)">View on GitHub</a>
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

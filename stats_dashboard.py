"""
刷题数据可视化面板 v4
- cal-heatmap (wa0x6e/cal-heatmap) — GitHub 官方同款热力图引擎
- 清新暖色主题
"""
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
    for kw in EXCLUDE_KEYWORDS:
        if kw in file_path.name.lower():
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
            ["git", "-c", "core.quotepath=false", "log",
             "--format=@@%ad", "--date=short", "--name-only",
             f"--since={days} days ago"],
            cwd=ROOT, encoding="utf-8")
    except Exception:
        return {}

    day_data = defaultdict(lambda: {"commits": 0, "files": set()})
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
            cwd=ROOT, encoding="utf-8")
        return out.strip().splitlines()[0] if out.strip() else ""
    except Exception:
        return ""


def build_html(counts: dict, history: dict) -> str:
    grand_total = sum(c["_total"] for c in counts.values())
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    first_commit = get_first_commit_date()

    # Build heatmap data array for cal-heatmap
    heatmap_data = []
    for date_str, info in sorted(history.items()):
        heatmap_data.append({"date": date_str, "value": info["files"]})

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

    # Date range: start from 2 months before first commit, rounded to month start
    if first_commit:
        fc = datetime.strptime(first_commit, "%Y-%m-%d")
    else:
        fc = datetime.now()
    range_start = (fc.replace(day=1) - timedelta(days=60)).replace(day=1)
    # Number of months to show (from range_start to now + 1)
    now = datetime.now()
    range_months = (now.year - range_start.year) * 12 + (now.month - range_start.month) + 1
    range_start_js = range_start.strftime("%Y-%m-%d")

    data_json = json.dumps({
        "grandTotal": grand_total,
        "platforms": platforms,
        "recent": recent,
        "totalCommits": total_commits,
        "firstCommit": first_commit,
        "updatedAt": updated_at,
        "heatmapData": heatmap_data,
        "rangeStart": range_start_js,
        "rangeMonths": min(range_months, 12),
    }, ensure_ascii=False)

    return HTML_TEMPLATE.format(data_json=data_json)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>刷题面板 · ZoomWaterr</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/cal-heatmap@4.2.4/dist/cal-heatmap.min.js"></script>
<script>
const DATA = {data_json};
document.addEventListener('DOMContentLoaded', function() {{
const cal = new CalHeatmap();
cal.paint({{
  itemSelector: '#cal-heatmap',
  range: DATA.rangeMonths,
  domain: {{ type: 'month', gutter: 4, label: {{ text: 'M月', textAlign: 'start', position: 'top' }} }},
  subDomain: {{ type: 'ghDay', radius: 2, width: 12, height: 12, gutter: 4 }},
  date: {{ start: new Date(DATA.rangeStart) }},
  data: {{
    source: DATA.heatmapData,
    type: 'json',
    x: 'date',
    y: d => d.value,
  }},
  scale: {{
    color: {{
      type: 'threshold',
      range: ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127'],
      domain: [1, 3, 6, 11],
    }},
  }},
  theme: 'light',
}});
}});
</script>
<style>
  :root {{
    --bg: #faf7f2;
    --card: #fffcf8;
    --border: #ede4d8;
    --text: #3d322b;
    --muted: #8c7b6e;
    --accent: #c8956c;
    --green: #40a578;
    --blue: #5b8fb4;
    --purple: #a080b4;
    --orange: #d4a058;
    --shadow: 0 2px 12px rgba(180,160,140,0.10);
    --shadow-lg: 0 4px 24px rgba(180,160,140,0.14);
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    min-height: 100vh;
  }}
  .container {{ max-width: 860px; margin: 0 auto; padding: 32px 20px; }}

  .header {{ display: flex; align-items: center; gap: 16px; margin-bottom: 28px; }}
  .avatar {{
    width: 52px; height: 52px; border-radius: 50%;
    background: linear-gradient(135deg, #c8956c, #e8c4a0);
    display: flex; align-items: center; justify-content: center;
    font-size: 26px; font-weight: 900; color: #fff; flex-shrink: 0;
  }}
  .header h1 {{ font-size: 22px; font-weight: 700; }}
  .header .sub {{ color: var(--muted); font-size: 13px; }}

  .bookmark-hint {{
    background: linear-gradient(135deg, #fef9f0, #fdf5e6);
    border: 1px solid #e8d5c4; border-radius: 8px;
    padding: 10px 16px; margin-bottom: 24px; font-size: 12px; color: var(--muted);
    display: flex; align-items: center; gap: 8px;
  }}
  .bookmark-hint strong {{ color: var(--accent); }}

  .cards {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 10px; margin-bottom: 24px;
  }}
  .card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 18px 14px; text-align: center;
    box-shadow: var(--shadow); transition: transform 0.15s;
  }}
  .card:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-lg); }}
  .card .num {{ font-size: 30px; font-weight: 800; line-height: 1.1; color: var(--accent); }}
  .card:nth-child(2) .num {{ color: var(--blue); }}
  .card:nth-child(3) .num {{ color: var(--purple); }}
  .card:nth-child(4) .num {{ color: var(--orange); }}
  .card:nth-child(5) .num {{ color: var(--green); }}
  .card .label {{ color: var(--muted); font-size: 12px; margin-top: 4px; }}

  .section-title {{ font-size: 15px; font-weight: 600; margin-bottom: 14px; color: var(--text); }}
  .panel {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px; margin-bottom: 20px;
    box-shadow: var(--shadow);
  }}

  #cal-heatmap {{ font-size: 11px; }}

  .platform-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }}
  .platform-row:last-child {{ margin-bottom: 0; }}
  .platform-name {{ width: 60px; text-align: right; font-weight: 600; font-size: 13px; flex-shrink: 0; }}
  .platform-bar-wrap {{ flex: 1; height: 24px; background: var(--bg); border-radius: 5px; overflow: hidden; }}
  .platform-bar {{
    height: 100%; border-radius: 5px; display: flex; align-items: center;
    padding-left: 10px; font-size: 12px; font-weight: 700;
    transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
  }}
  .platform-bar.lg {{ background: linear-gradient(90deg, #7bc96f, #40a578); color: #fff; }}
  .platform-bar.cl {{ background: linear-gradient(90deg, #7bb4e0, #5b8fb4); color: #fff; }}
  .platform-bar.lq {{ background: linear-gradient(90deg, #c4a0d8, #a080b4); color: #fff; }}
  .subdirs {{ margin-left: 72px; margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 5px; }}
  .subdir-tag {{
    background: var(--bg); color: var(--muted);
    padding: 1px 9px; border-radius: 10px; font-size: 11px; border: 1px solid var(--border);
  }}

  .activity-item {{
    display: flex; align-items: flex-start; gap: 12px;
    padding: 9px 0; border-bottom: 1px solid #f0ebe0;
  }}
  .activity-item:last-child {{ border-bottom: none; }}
  .act-date {{ font-size: 12px; color: var(--muted); flex-shrink: 0; width: 48px; }}
  .act-dot {{ width: 8px; height: 8px; border-radius: 50%; margin-top: 5px; flex-shrink: 0; }}
  .act-dot.big {{ background: var(--green); box-shadow: 0 0 6px rgba(64,165,120,0.5); }}
  .act-dot.medium {{ background: var(--blue); }}
  .act-dot.small {{ background: var(--purple); }}
  .act-files {{ font-size: 13px; color: var(--text); line-height: 1.5; }}
  .act-count {{ font-weight: 700; color: var(--green); }}
  .act-fname {{ color: var(--muted); font-size: 11px; margin-left: 4px; }}

  .footer {{
    text-align: center; color: var(--muted); font-size: 11px;
    padding: 20px 0; border-top: 1px solid var(--border); margin-top: 6px;
  }}
  .footer a {{ color: var(--accent); text-decoration: none; }}
  .footer a:hover {{ text-decoration: underline; }}

  @media (max-width: 640px) {{
    .cards {{ grid-template-columns: repeat(3, 1fr); }}
  }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <div class="avatar">ZT</div>
    <div>
      <h1>Python 算法刷题面板</h1>
      <div class="sub">ZoomWaterr · 从零到百题，每天进步一点点</div>
    </div>
  </div>

  <div class="bookmark-hint">
    📌 收藏本页 <strong>Ctrl+D</strong>，每次打开即最新数据
  </div>

  <div class="cards" id="cards"></div>

  <div class="panel">
    <div class="section-title">📅 刷题热力图</div>
    <div id="cal-heatmap"></div>
  </div>

  <div class="panel">
    <div class="section-title">📊 平台分布</div>
    <div id="platforms"></div>
  </div>

  <div class="panel">
    <div class="section-title">🔥 最近活动</div>
    <div id="activity"></div>
  </div>

  <div class="footer" id="footer"></div>

</div>

<script>
(function() {{
  const DATA = {data_json};

  document.getElementById('cards').innerHTML = `
    <div class="card"><div class="num">${{DATA.grandTotal}}</div><div class="label">总题数</div></div>
    ${{DATA.platforms.map(p => `<div class="card"><div class="num">${{p.total}}</div><div class="label">${{p.name}}</div></div>`).join('')}}
    <div class="card"><div class="num">${{DATA.totalCommits}}</div><div class="label">总提交</div></div>
  `;

  // Platform bars
  const maxTotal = Math.max(...DATA.platforms.map(p => p.total), 1);
  document.getElementById('platforms').innerHTML = DATA.platforms.map((pl, i) => {{
    const pct = Math.max((pl.total / maxTotal * 100).toFixed(0), 8);
    const barClass = ['lg', 'cl', 'lq'][i] || '';
    const subHtml = Object.entries(pl.subdirs).length > 0
      ? `<div class="subdirs">${{Object.entries(pl.subdirs).map(([k,v]) =>
          `<span class="subdir-tag">${{k}}: ${{v}}题</span>`).join('')}}</div>` : '';
    return `<div class="platform-row">
      <span class="platform-name">${{pl.name}}</span>
      <div class="platform-bar-wrap">
        <div class="platform-bar ${{barClass}}" style="width:${{pct}}%">${{pl.total}} 题</div>
      </div>
    </div>${{subHtml}}`;
  }}).join('');

  // Activity
  const recent = DATA.recent;
  if (recent.length === 0) {{
    document.getElementById('activity').innerHTML = '<p style="color:var(--muted);font-size:13px">还没有活动记录</p>';
  }} else {{
    document.getElementById('activity').innerHTML = recent.map(item => {{
      const dotClass = item.files >= 8 ? 'big' : item.files >= 4 ? 'medium' : 'small';
      const fnames = (item.filenames || []).slice(0, 4).map(f =>
        `<span class="act-fname">${{f}}</span>`).join('');
      const more = (item.filenames || []).length > 4
        ? `<span class="act-fname">+${{item.filenames.length - 4}} more</span>` : '';
      return `<div class="activity-item">
        <span class="act-date">${{item.date.slice(5)}}</span>
        <span class="act-dot ${{dotClass}}"></span>
        <span class="act-files">
          <span class="act-count">+${{item.files}} 题</span> · ${{item.commits}} 次提交
          <br>${{fnames}}${{more}}
        </span>
      </div>`;
    }}).join('');
  }}

  document.getElementById('footer').innerHTML = `
    自动生成 · ${{DATA.updatedAt}}
    ${{DATA.firstCommit ? ' · 始于 ' + DATA.firstCommit : ''}}
    · <a href="https://github.com/ZoomWaterr/python-algo-practice">GitHub</a>
    · <a href="#" onclick="navigator.clipboard.writeText(location.href);this.textContent='已复制!';setTimeout(()=>this.textContent='复制链接',1500);return false">复制链接</a>
  `;
}})();
</script>
</body>
</html>"""


def main():
    counts = count_problems()
    history = get_git_history(days=365)
    html = build_html(counts, history)
    out = ROOT / "index.html"
    out.write_text(html, encoding="utf-8")
    grand = sum(c["_total"] for c in counts.values())
    print(f"[OK] Dashboard: {out}")
    print(f"     Total: {grand} problems | Active days: {len(history)}")


if __name__ == "__main__":
    main()

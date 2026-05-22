<div align="center">

# PythonCode

Python 算法刷题记录。题解按平台归档，进度由 GitHub Pages 实时面板自动展示。

<p>
  <a href="https://zoomwaterr.github.io/python-algo-practice/"><b>打开实时刷题面板</b></a>
  ·
  <a href="./洛谷/">洛谷</a>
  ·
  <a href="./C语言网/">C语言网</a>
  ·
  <a href="./蓝桥云课/">蓝桥云课</a>
</p>

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13%2B-3f6f99?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Total" src="https://img.shields.io/badge/Problems-108-227a55?style=for-the-badge">
  <img alt="Pages" src="https://img.shields.io/badge/GitHub%20Pages-Auto%20Dashboard-b56e21?style=for-the-badge&logo=githubpages&logoColor=white">
</p>

</div>

## 实时面板

这个仓库的 README 只保留概览，真正的刷题进度放在网页里：

> [https://zoomwaterr.github.io/python-algo-practice/](https://zoomwaterr.github.io/python-algo-practice/)

面板会在每次 push 后自动更新，包含热力图、平台分布、最近活动、连续刷题等数据。

## 题库概览


<!-- stats -->
<table>
  <tr>
    <td align="center"><a href="./洛谷/"><b>洛谷</b></a><br><sub>52 题</sub></td>
    <td align="center"><a href="./C语言网/"><b>C语言网</b></a><br><sub>50 题</sub></td>
    <td align="center"><a href="./蓝桥云课/"><b>蓝桥云课</b></a><br><sub>6 题</sub></td>
    <td align="center"><b>总计</b><br><sub>108 题</sub></td>
  </tr>
</table>

<details>
<summary>最近刷题记录</summary>

| 日期 | 题数 |
| --- | ---: |
| 2026-05-22 | +4 |
| 2026-05-12 | +9 |
| 2026-05-07 | +10 |
| 2026-05-06 | +36 |
| 2026-05-05 | +52 |

</details>
<!-- /stats -->

## 自动化

每次推送到 `main` 后，GitHub Actions 会运行：

```bash
python stats_dashboard.py
```

然后把生成的 `index.html` 发布到 `gh-pages` 分支。

## 本地维护

```bash
python stats.py          # 查看统计
python stats.py --daily  # 查看每日记录
python stats.py --check  # 检查 README 统计块
```

Python 3.13+，只依赖标准库。


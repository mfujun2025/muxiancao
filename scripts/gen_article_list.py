# -*- coding: utf-8 -*-
"""生成 articles/行业文章.html 列表页，并把全站导航「行业文章」链接改为指向列表页。"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = r"C:\Users\Huawei\Doubao\chats\2026-10-12\new-chat-3\muxiancao-site"
ART = os.path.join(BASE, "articles")

# ---------- 1. 从首页提取 30 篇文章 ----------
index_html = open(os.path.join(BASE, "index.html"), encoding="utf-8").read()
m = re.search(r'<div class="articles">(.*?)</div>\s*</div>\s*</section>', index_html, re.S)
block = m.group(1)
cards = re.findall(
    r'<a class="article-card" href="([^"]+)">.*?<div class="cat">(.*?)</div>\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>',
    block, re.S)
cards = [(href.strip(), cat.strip(), title.strip(), desc.strip()) for href, cat, title, desc in cards]
print("提取文章数:", len(cards))

# 按分类分组（保持首次出现顺序）
groups = {}
for href, cat, title, desc in cards:
    groups.setdefault(cat, []).append((href, title, desc))

# ---------- 2. 生成列表页 ----------
CSS = """<style>
:root{--ink:#0B2540;--navy:#123A5E;--steel:#EAF0F6;--line:#D6DFE9;--paper:#FFFFFF;--accent:#E87A1F;--text:#23303F;--muted:#5B6B7C}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;color:var(--text);background:var(--paper);line-height:1.85;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.site-header{position:sticky;top:0;z-index:50;background:var(--ink);color:#fff}
.header-inner{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 20px;max-width:1120px;margin:0 auto}
.brand{display:flex;align-items:center;gap:10px;font-weight:900;font-size:1.15rem;letter-spacing:.5px}
.brand svg{width:30px;height:30px}.brand .cn{color:#F2B25C;font-weight:700}
.nav{display:flex;align-items:center;gap:6px}
.nav a{padding:8px 12px;border-radius:8px;font-size:.95rem;color:#E8EEF6}
.nav a:hover{background:rgba(255,255,255,.12)}
.nav a.on{background:rgba(232,122,31,.18);color:#F7B06A}
.nav .cta{background:var(--accent);color:#fff;font-weight:700}
.nav .cta:hover{background:#D16A15}
.list-wrap{max-width:960px;margin:0 auto;padding:40px 20px 60px}
.list-wrap h1{font-size:1.8rem;color:var(--ink);font-weight:900;margin-bottom:10px}
.list-wrap .sub{color:var(--muted);font-size:.95rem;border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:28px}
.group{margin-bottom:30px}
.group h2{font-size:1.15rem;color:var(--navy);font-weight:900;margin-bottom:12px;padding-left:12px;border-left:4px solid var(--accent)}
.entry{display:flex;gap:14px;align-items:baseline;background:#F7FAFD;border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin-bottom:10px}
.entry:hover{background:#EAF0F6;border-color:#123A5E}
.entry .n{color:var(--accent);font-weight:900;min-width:2em}
.entry .t{font-weight:700;color:var(--ink)}
.entry .d{color:var(--muted);font-size:.88rem;flex:1}
.site-footer{background:var(--ink);color:#9DB2C8;font-size:.88rem}
.footer-inner{max-width:1120px;margin:0 auto;padding:36px 20px;display:grid;grid-template-columns:1fr;gap:22px}
@media(min-width:760px){.footer-inner{grid-template-columns:1.4fr 1fr 1fr}}
.footer-inner h4{color:#fff;font-size:.95rem;margin-bottom:10px;font-weight:700}
.footer-inner a{display:block;color:#9DB2C8;padding:3px 0}
.footer-inner a:hover{color:#F7A25C}
.footer-bottom{border-top:1px solid rgba(255,255,255,.1);padding:16px 20px;text-align:center;color:#71879C}
</style>"""

HEADER = """<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="../index.html">
      <svg viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="14" fill="#16304F"/><path d="M16 20h32v6H16zM16 32h32v6H16zM16 44h32v6H16z" fill="#E87A1F"/><circle cx="12" cy="23" r="3" fill="#F2B25C"/><circle cx="52" cy="23" r="3" fill="#F2B25C"/><circle cx="12" cy="35" r="3" fill="#F2B25C"/><circle cx="52" cy="35" r="3" fill="#F2B25C"/><circle cx="12" cy="47" r="3" fill="#F2B25C"/><circle cx="52" cy="47" r="3" fill="#F2B25C"/></svg>
      <span>母线槽<span class="cn">.cn</span></span>
    </a>
    <nav class="nav" aria-label="主导航">
      <a href="../index.html">首页</a>
      <a href="../huangye.html">企业黄页</a>
      <a href="行业文章.html" class="on">行业文章</a>
      <a class="cta" href="../huangye.html#apply">免费入驻</a>
    </nav>
  </div>
</header>"""

FOOTER = """<footer class="site-footer">
  <div class="footer-inner">
    <div>
      <h4>母线槽.cn</h4>
      <p>专注母线槽行业的免费企业黄页平台，覆盖空气型、密集型、耐火、防水防潮、智能、照明母线槽的生产、经销、工程与设计咨询企业。</p>
    </div>
    <div>
      <h4>站点导航</h4>
      <a href="../index.html">首页</a>
      <a href="../huangye.html">企业黄页</a>
      <a href="母线槽是什么.html">母线槽百科</a>
      <a href="密集型与空气型母线槽的区别.html">选型对比</a>
      <a href="母线槽厂家怎么选.html">厂家采购指南</a>
      <a href="母线槽怎么安装.html">安装施工</a>
      <a href="母线槽和电缆的区别.html">母线槽与电缆对比</a>
      <a href="母线槽国家标准.html">执行标准</a>
      <a href="母线槽价格多少钱一米.html">母线槽价格</a>
      <a href="密集型母线槽规格型号.html">规格型号</a>
      <a href="母线槽维护保养.html">维护保养</a>
    </div>
    <div>
      <h4>合作推广</h4>
      <a href="https://172.lot-ml.com/ProductEn/Index/04a04744e3c8d9a6" target="_blank" rel="noopener">母线产品国际站 · 合作推广</a>
    </div>
  </div>
  <div class="footer-bottom">© 2026 母线槽.cn · 免费企业黄页 · 收录数据由管理员审核后自动同步</div>
</footer>"""

num = 0
group_html = []
for cat, items in groups.items():
    rows = []
    for href, title, desc in items:
        num += 1
        # 列表页位于 articles/ 目录内，链接需去掉 articles/ 前缀
        href_rel = href.replace("articles/", "")
        rows.append('<div class="entry"><span class="n">%02d</span><span class="t"><a href="%s">%s</a></span><span class="d">%s</span></div>'
                    % (num, href_rel, title, desc))
    group_html.append('<div class="group"><h2>%s（%d 篇）</h2>%s</div>' % (cat, len(items), "".join(rows)))

body = "".join(group_html)
page = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>母线槽行业文章大全 - 母线槽.cn</title>\n'
        '<meta name="description" content="母线槽行业文章大全：分类、选型、价格、安装、标准、应用与维护等 30 篇实用文章，覆盖采购与工程全流程。">\n'
        '<meta name="keywords" content="母线槽文章,母线槽知识,母线槽选购,母线槽安装,母线槽标准">\n'
        '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 64 64\'%3E%3Crect width=\'64\' height=\'64\' rx=\'14\' fill=\'%230B2540\'/%3E%3Cpath d=\'M16 20h32v6H16zM16 32h32v6H16zM16 44h32v6H16z\' fill=\'%23E87A1F\'/%3E%3Ccircle cx=\'12\' cy=\'23\' r=\'3\' fill=\'%23F2B25C\'/%3E%3Ccircle cx=\'52\' cy=\'23\' r=\'3\' fill=\'%23F2B25C\'/%3E%3Ccircle cx=\'12\' cy=\'35\' r=\'3\' fill=\'%23F2B25C\'/%3E%3Ccircle cx=\'52\' cy=\'35\' r=\'3\' fill=\'%23F2B25C\'/%3E%3Ccircle cx=\'12\' cy=\'47\' r=\'3\' fill=\'%23F2B25C\'/%3E%3Ccircle cx=\'52\' cy=\'47\' r=\'3\' fill=\'%23F2B25C\'/%3E%3C/svg%3E">\n'
        '<link rel="preconnect" href="https://miaoda.feishu.cn">\n'
        '<link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap">\n'
        + CSS + "\n</head>\n<body>\n" + HEADER +
        '\n<main class="list-wrap">\n  <h1>母线槽行业文章大全</h1>\n'
        '  <div class="sub">共 %d 篇，覆盖分类选型、价格采购、安装施工、执行标准、应用场景与故障维护，持续更新。</div>\n' % num
        + body + '\n</main>\n' + FOOTER + '\n</body>\n</html>\n')

out = os.path.join(ART, "行业文章.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(page)
print("已生成列表页:", out, "篇数:", num)

# ---------- 3. 批量改导航链接 ----------
# 文章页（articles/ 下）导航 + crumb：行业文章 -> 行业文章.html
pat_nav = r'(href=")母线槽是什么\.html(" class="on">行业文章</a>)'
pat_crumb = r'(<a href=")母线槽是什么\.html(">行业文章</a>)'
changed = 0
for fn in os.listdir(ART):
    if not fn.endswith(".html"):
        continue
    p = os.path.join(ART, fn)
    s = open(p, encoding="utf-8").read()
    s2 = re.sub(pat_nav, r'\1行业文章.html\2', s)
    s2 = re.sub(pat_crumb, r'\1行业文章.html\2', s2)
    if s2 != s:
        with open(p, "w", encoding="utf-8") as f:
            f.write(s2)
        changed += 1
print("文章页导航已更新:", changed)

# 根页面 index.html / huangye.html：导航 行业文章 -> articles/行业文章.html
for fn in ["index.html", "huangye.html"]:
    p = os.path.join(BASE, fn)
    s = open(p, encoding="utf-8").read()
    s2 = re.sub(r'(href=")articles/母线槽是什么\.html(" class="on">行业文章</a>)',
                r'\1articles/行业文章.html\2', s)
    if s2 != s:
        with open(p, "w", encoding="utf-8") as f:
            f.write(s2)
        print("根页面导航已更新:", fn)
print("完成")

# -*- coding: utf-8 -*-
"""母线槽.cn 黄页数据自动同步脚本（GitHub Actions 用）

通过飞书开放平台 API 拉取「黄页收录」表已收录企业，写入 index.html /
huangye.html 的 /*__COMPANIES_JSON__*/ 占位处。

环境变量：
  FEISHU_APP_ID      飞书自建应用 App ID
  FEISHU_APP_SECRET  飞书自建应用 App Secret
  MUXIANCAO_BASE     多维表格 app_token（默认内置）
  MUXIANCAO_TABLE    黄页收录表 table_id（默认内置）

飞书应用需开通权限：bitable:app（查看、评论和导出多维表格），并授权给
「母线槽黄页」多维表格所在文件夹/空间。
"""
import json
import os
import re
import sys
import urllib.request

BASE_TOKEN = os.environ.get("MUXIANCAO_BASE", "HjfmbxtUIatXrusg6SacKVGrn3d")
TABLE_ID = os.environ.get("MUXIANCAO_TABLE", "tblnhJDtoCbDXVtG")
SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = ["index.html", "huangye.html"]
PLACEHOLDER = "/*__COMPANIES_JSON__*/[]"
# 匹配整个占位数据块直到数组闭合的 "];"（避免被内层 products 数组的 "]" 截断）
PLACEHOLDER_RE = re.compile(r"/\*__COMPANIES_JSON__\*/\s*\[.*?\];", re.DOTALL)


def http_json(url, payload=None, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, data=data, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_token(app_id, app_secret):
    res = http_json(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        {"app_id": app_id, "app_secret": app_secret},
    )
    if res.get("code") != 0:
        sys.exit("获取 tenant_access_token 失败：{} {}".format(res.get("code"), res.get("msg")))
    return res["tenant_access_token"]


def fetch_records(token):
    url = ("https://open.feishu.cn/open-apis/bitable/v1/apps/{}/tables/{}/records"
           "?page_size=100".format(BASE_TOKEN, TABLE_ID))
    res = http_json(url, headers={"Authorization": "Bearer " + token})
    if res.get("code") != 0:
        sys.exit("拉取记录失败：{} {}".format(res.get("code"), res.get("msg")))
    items = res["data"]["items"]
    if res["data"].get("has_more"):
        print("警告：记录超过 100 条，仅同步第一页，请人工确认。")
    return items


def field_text(v):
    if isinstance(v, list):
        return [str(x.get("text", "")) for x in v if isinstance(x, dict)]
    if isinstance(v, dict):
        return str(v.get("text", ""))
    return str(v or "")


def clean_website(val):
    text = field_text(val)
    m = re.search(r"https?://[^\s)\]]+", text)
    return m.group(0) if m else ""


def main():
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    if not app_id or not app_secret:
        sys.exit("缺少 FEISHU_APP_ID / FEISHU_APP_SECRET 环境变量")
    token = get_token(app_id, app_secret)
    records = fetch_records(token)
    companies = []
    for rec in records:
        f = rec.get("fields", {})
        name = field_text(f.get("企业名称"))
        if not name:
            continue
        ctype = field_text(f.get("企业类型"))
        products = field_text(f.get("母线槽产品"))
        companies.append({
            "name": name.strip(),
            "type": ctype if isinstance(ctype, str) else (ctype[0] if ctype else ""),
            "products": [p for p in (products if isinstance(products, list) else [products]) if p],
            "region": field_text(f.get("所在省市")).strip(),
            "intro": field_text(f.get("企业简介")).strip(),
            "tel": field_text(f.get("联系电话")).strip(),
            "website": clean_website(f.get("企业官网")),
        })
    blob = json.dumps(companies, ensure_ascii=False, indent=2)
    new_block = PLACEHOLDER.replace("[]", blob)
    for target in TARGETS:
        path = os.path.join(SITE_DIR, target)
        with open(path, encoding="utf-8") as fp:
            html = fp.read()
        if not PLACEHOLDER_RE.search(html):
            sys.exit("{} 中未找到数据占位符 {}".format(target, PLACEHOLDER))
        html = PLACEHOLDER_RE.sub(new_block + ";", html)
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(html)
        print("已更新 {}：{} 家企业".format(target, len(companies)))
    print("同步完成。")


if __name__ == "__main__":
    main()

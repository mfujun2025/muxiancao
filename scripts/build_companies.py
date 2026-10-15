# -*- coding: utf-8 -*-
"""母线槽.cn 黄页数据同步脚本

从飞书多维表格「黄页收录」表拉取已收录企业，生成名录 JSON，并写入
index.html / huangye.html 的 /*__COMPANIES_JSON__*/ 占位处。

用法：
  python scripts/build_companies.py

依赖：本机已登录 lark-cli（用户态可读多维表格）。
"""
import json
import os
import re
import subprocess
import sys

BASE_TOKEN = "HjfmbxtUIatXrusg6SacKVGrn3d"
TABLE_ID = "tblnhJDtoCbDXVtG"
SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = ["index.html", "huangye.html"]
PLACEHOLDER = "/*__COMPANIES_JSON__*/[]"
# 匹配整个占位数据块直到数组闭合的 "];"（避免被内层 products 数组的 "]" 截断）
PLACEHOLDER_RE = re.compile(r"/\*__COMPANIES_JSON__\*/\s*\[.*?\];", re.DOTALL)


def fetch_records():
    """调用 lark-cli 拉取黄页收录表全部记录，返回解析后的记录列表。"""
    args = ["base", "+record-list", "--base-token", BASE_TOKEN,
            "--table-id", TABLE_ID, "--format", "json"]
    result = subprocess.run(["lark-cli"] + args, capture_output=True)
    if result.returncode != 0:
        sys.exit("lark-cli 调用失败：\n" + result.stderr.decode("utf-8", "ignore"))
    data = json.loads(result.stdout.decode("utf-8"))
    obj = data["data"]
    fields = obj["fields"]
    rows = obj["data"]
    has_more = obj.get("has_more", False)
    if has_more:
        sys.exit("存在未分页数据，请手动确认（当前记录数较小，一般不会触发）")
    return fields, rows


def pick(row, fields, name):
    try:
        idx = fields.index(name)
    except ValueError:
        return None
    return row[idx] if idx < len(row) else None


def clean_website(val):
    """企业官网可能是 '[url](url)' 或纯文本 url，统一提取链接。"""
    if not val:
        return ""
    text = str(val)
    m = re.search(r"\((https?://[^)\s]+)\)", text)
    if m:
        return m.group(1)
    m = re.search(r"https?://[^\s]+", text)
    return m.group(0) if m else ""


def main():
    fields, rows = fetch_records()
    companies = []
    for row in rows:
        name = pick(row, fields, "企业名称")
        if not name:
            continue
        ctype = pick(row, fields, "企业类型") or []
        if isinstance(ctype, str):
            ctype = [ctype]
        products = pick(row, fields, "母线槽产品") or []
        if isinstance(products, str):
            products = [products]
        companies.append({
            "name": str(name).strip(),
            "type": ctype[0] if ctype else "",
            "products": [str(p) for p in products],
            "region": str(pick(row, fields, "所在省市") or "").strip(),
            "intro": str(pick(row, fields, "企业简介") or "").strip(),
            "tel": str(pick(row, fields, "联系电话") or "").strip(),
            "website": clean_website(pick(row, fields, "企业官网")),
        })
    blob = json.dumps(companies, ensure_ascii=False, indent=2)
    new_block = PLACEHOLDER.replace("[]", blob)
    for target in TARGETS:
        path = os.path.join(SITE_DIR, target)
        with open(path, encoding="utf-8") as f:
            html = f.read()
        if not PLACEHOLDER_RE.search(html):
            sys.exit("{} 中未找到数据占位符 {}".format(target, PLACEHOLDER))
        html = PLACEHOLDER_RE.sub(new_block + ";", html)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("已更新 {}：{} 家企业".format(target, len(companies)))
    print("同步完成。提交 git 后网站即更新。")


if __name__ == "__main__":
    main()

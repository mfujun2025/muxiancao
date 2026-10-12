# 母线槽.cn — 母线槽企业黄页网站

专注母线槽行业的免费企业黄页平台：用户通过飞书表单申请入驻 → 管理员在多维表格审核 → 审核通过后自动上架展示。

## 站点结构

| 文件 | 说明 |
|---|---|
| `index.html` | 网站首页：最新收录企业预览（卡片式）、入驻流程、行业文章入口 |
| `huangye.html` | 企业黄页页：已收录企业名录（卡片式展示）+ 在线入驻申请表（内嵌飞书表单） |
| `articles/母线槽是什么.html` | SEO 文章：母线槽百科（信息型，约 800 字） |
| `articles/密集型与空气型母线槽的区别.html` | SEO 文章：选型对比（对比型，约 800 字） |
| `articles/母线槽厂家怎么选.html` | SEO 文章：厂家采购指南（交易型，约 800 字） |
| `assets/` | 母线槽实拍素材图（hero / 安装实景 / 车间成品） |
| `scripts/build_companies.py` | 本地一键同步：拉取飞书「黄页收录」表 → 写入两个页面的企业数据 |
| `scripts/fetch_feishu.py` | 全自动同步脚本（GitHub Actions 用，走飞书开放 API） |
| `.github/workflows/sync-companies.yml` | 定时自动同步工作流（需配置飞书应用凭证） |

## 核心业务流程（飞书侧）

1. **申请**：用户点击「免费入驻」→ 飞书表单（免登录、匿名可填）提交企业名称、企业类型、母线槽产品（多选）、所在省市、联系人、联系电话、企业官网、企业简介。
2. **审核**：管理员打开飞书多维表格「母线槽黄页」→「企业申请」表 →「待审核」视图，核对后将「状态」改为「已通过」或「已拒绝」并填写审核备注。
3. **自动上架**：多维表格自动化工作流「审核通过自动上架」监听「状态 = 已通过」，自动把企业信息写入「黄页收录」表；网站黄页页内嵌该表的公开视图，数据即时同步展示。

## 飞书资源

- 多维表格（Base）：https://my.feishu.cn/base/HjfmbxtUIatXrusg6SacKVGrn3d
- 入驻申请表（公开表单）：https://my.feishu.cn/share/base/shrcnn036BsQG9rwsI1Q5MUOHdg
- 黄页收录公开视图：https://my.feishu.cn/base/HjfmbxtUIatXrusg6SacKVGrn3d?table=tblnhJDtoCbDXVtG&view=vewJ1qiMYy

## 部署

本站为纯静态站点，可直接部署到 GitHub Pages / 任意静态托管 / 绑定中文域名 `母线槽.cn`：

- GitHub Pages：仓库 Settings → Pages → 选择分支 `main`、根目录即可。
- 域名绑定：在域名服务商把 `母线槽.cn` 解析到站点 CNAME，并在 Pages 设置里配置自定义域名。

## 数据同步机制

黄页页与首页的企业名录以卡片形式展示，数据内联在页面 `/*__COMPANIES_JSON__*/` 占位处。飞书「黄页收录」表审核通过的企业，通过以下两种方式同步到网站：

**方式一：本地一键刷新（推荐，零配置）**
```bash
python scripts/build_companies.py
git add -A && git commit -m "更新黄页数据" && git push
```
依赖本机已登录的 lark-cli（用户态），每次审核通过后运行一次即可。

**方式二：GitHub Actions 全自动（需配置飞书应用凭证）**
1. 飞书开放平台（open.feishu.cn）创建企业自建应用，开通「多维表格」权限 `bitable:app`（查看、评论和导出多维表格），并授权给「母线槽黄页」多维表格所在空间；
2. 仓库 Settings → Secrets and variables → Actions，添加 `FEISHU_APP_ID` 与 `FEISHU_APP_SECRET` 两个 secret；
3. 启用 `.github/workflows/sync-companies.yml`（默认每 2 小时自动同步一次，也可在 Actions 页面手动触发）。审核通过后，最多 2 小时网站自动更新。

## 后续维护

- 新增 SEO 文章：按 `articles/` 内已有页面结构复制一篇，替换正文与 `<title>/<meta name="description">` 即可；
- 申请表单字段变更后，同步更新 `huangye.html` 的「申请须知」文案；
- 企业名录数据以飞书「黄页收录」表为准，勿直接手改页面内数据块。

© 2026 母线槽.cn

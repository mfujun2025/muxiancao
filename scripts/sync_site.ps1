# 母线槽.cn 黄页数据自动同步脚本（本机计划任务用）
# 流程：lark-cli 用户态拉取飞书多维表格 -> 更新 HTML -> git 提交并推送 GitHub Pages
$ErrorActionPreference = 'Continue'
$site = 'C:\Users\Huawei\Doubao\chats\2026-10-12\new-chat-3\muxiancao-site'
Set-Location $site

# 1. 同步黄页数据（lark-cli 用户态，无需应用 API）
& python 'C:\Users\Huawei\Doubao\chats\2026-10-12\new-chat-3\muxiancao-site\scripts\build_companies.py' 2>&1 | Out-Null

# 2. 有改动则提交并推送
$status = & git status --porcelain 2>$null
if ($status) {
    & git add -A 2>$null
    & git commit -m ("auto-sync: 黄页数据自动同步 " + (Get-Date -Format 'yyyy-MM-dd HH:mm')) 2>$null
    & git push origin main 2>$null
    Write-Output ("[synced] " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
} else {
    Write-Output ("[no-change] " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
}

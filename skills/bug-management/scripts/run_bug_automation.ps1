# 缺陷管理自动化工具启动脚本 (PowerShell)
# 设置环境变量并运行自动化脚本

Write-Host "`u{2713} 启动缺陷管理自动化工具..." -ForegroundColor Green
Write-Host ""

# 设置环境变量
$env:CLOUD_EFFECT_USERNAME = "nick1821010462"
$env:CLOUD_EFFECT_PASSWORD = "R20250918"

Write-Host "`u{2713} 已设置环境变量" -ForegroundColor Green
Write-Host "  - CLOUD_EFFECT_USERNAME: $($env:CLOUD_EFFECT_USERNAME)" -ForegroundColor Cyan
Write-Host "  - CLOUD_EFFECT_PASSWORD: *** (已隐藏)" -ForegroundColor Cyan
Write-Host ""

# 运行Python脚本
Write-Host "【正在启动自动化脚本】" -ForegroundColor Yellow
python bug_management_web_workflow.py

Write-Host ""
Read-Host "按Enter关闭"

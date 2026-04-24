# 缺陷管理自动化工具启动脚本 (PowerShell)
# 设置环境变量并运行自动化脚本

Write-Host "`u{2713} 启动缺陷管理自动化工具..." -ForegroundColor Green
Write-Host ""

if (-not $env:CLOUD_EFFECT_USERNAME) {
	$env:CLOUD_EFFECT_USERNAME = Read-Host "请输入测试环境登录账号"
}

if (-not $env:CLOUD_EFFECT_PASSWORD) {
	$securePassword = Read-Host "请输入测试环境登录密码" -AsSecureString
	$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
	try {
		$env:CLOUD_EFFECT_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
	}
	finally {
		[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
	}
}

if (-not $env:CLOUD_EFFECT_BASE_URL) {
	$env:CLOUD_EFFECT_BASE_URL = Read-Host "请输入测试环境地址"
}

if (-not $env:CLOUD_EFFECT_USERNAME -or -not $env:CLOUD_EFFECT_PASSWORD -or -not $env:CLOUD_EFFECT_BASE_URL) {
	Write-Host "✗ 缺少测试环境必需变量，脚本终止" -ForegroundColor Red
	exit 1
}

Write-Host "`u{2713} 已检测到测试环境所需变量" -ForegroundColor Green
Write-Host ""

# 运行Python脚本
Write-Host "【正在启动自动化脚本】" -ForegroundColor Yellow
python bug_management_web_workflow.py

Write-Host ""
Read-Host "按Enter关闭"

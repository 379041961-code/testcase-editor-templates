@echo off
chcp 65001 >nul
echo ✓ 启动缺陷管理自动化工具...
echo.

if not defined CLOUD_EFFECT_USERNAME (
	set /p CLOUD_EFFECT_USERNAME=请输入测试环境登录账号: 
)
if not defined CLOUD_EFFECT_PASSWORD (
	set /p CLOUD_EFFECT_PASSWORD=请输入测试环境登录密码: 
)
if not defined CLOUD_EFFECT_BASE_URL (
	set /p CLOUD_EFFECT_BASE_URL=请输入测试环境地址: 
)

if not defined CLOUD_EFFECT_USERNAME (
	echo ✗ 未提供测试环境登录账号
	pause
	exit /b 1
)
if not defined CLOUD_EFFECT_PASSWORD (
	echo ✗ 未提供测试环境登录密码
	pause
	exit /b 1
)
if not defined CLOUD_EFFECT_BASE_URL (
	echo ✗ 未提供测试环境地址
	pause
	exit /b 1
)

echo ✓ 已检测到测试环境所需变量
echo.

:: 运行Python脚本
echo 【正在启动自动化脚本】
python bug_management_web_workflow.py

pause

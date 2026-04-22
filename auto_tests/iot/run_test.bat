@echo off
chcp 65001 >nul
title IOT 设备统计 UI 自动化测试

echo ============================================================
echo   IOT 2.0 设备统计 UI 自动化测试
echo   测试用例：excel/设备统计_测试用例.xlsx
echo ============================================================
echo.

:: 定位到脚本所在目录
cd /d "%~dp0"

:: 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 检查依赖
echo [1/3] 检查 Python 依赖...
python -c "import selenium, webdriver_manager, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在自动安装缺少的依赖...
    pip install selenium webdriver-manager openpyxl
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请手动执行：pip install selenium webdriver-manager openpyxl
        pause
        exit /b 1
    )
)
echo [1/3] 依赖检查完成 ✓

echo.
echo [2/3] 启动自动化测试...
echo       浏览器打开后，请在验证码框输入图形验证码
echo       脚本检测到验证码输入后将自动继续（最多等待 15 秒）
echo.

:: 执行测试脚本
python device_stats_ui_automation.py

echo.
echo [3/3] 测试执行完成
echo       查看 test_log_*.txt 获取详细结果
echo ============================================================
pause

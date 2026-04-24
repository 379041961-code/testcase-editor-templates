@echo off
chcp 65001 >nul
title IOT 2.0 设备统计 UI 自动化测试

echo ============================================================
echo   IOT 2.0 设备统计 UI 自动化测试
echo   测试用例：excel/设备统计_测试用例.xlsx
echo ============================================================
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 检查并安装依赖...
python -c "import selenium, webdriver_manager, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装缺少依赖，请稍候...
    pip install selenium webdriver-manager openpyxl
    if errorlevel 1 (
        echo [错误] 自动安装失败，请手动执行：
        echo         pip install selenium webdriver-manager openpyxl
        pause
        exit /b 1
    )
)
echo [1/3] 依赖检查完成

echo.
if not defined IOT_TEST_USERNAME (
    set /p IOT_TEST_USERNAME=请输入登录账号: 
)
if not defined IOT_TEST_PASSWORD (
    set /p IOT_TEST_PASSWORD=请输入登录密码: 
)
if not defined IOT_TEST_USERNAME (
    echo [错误] 未设置登录账号，无法继续执行
    pause
    exit /b 1
)
if not defined IOT_TEST_PASSWORD (
    echo [错误] 未设置登录密码，无法继续执行
    pause
    exit /b 1
)

echo [2/3] 启动测试脚本...
echo       当前会话已准备登录环境变量。
echo       如需手动设置，请在本窗口执行：
echo       set IOT_TEST_USERNAME=你的账号
echo       set IOT_TEST_PASSWORD=你的密码
echo       浏览器出现验证码后手动输入，脚本最多等待 15 秒。
echo.

python device_stats_ui_automation.py

echo.
echo [3/3] 执行完成
echo       请查看 log 目录下 test_log_*.txt 文件
echo ============================================================
pause

@echo off
REM IOT自动化测试 - auto_tests文件夹运行脚本
REM 用途: 从auto_tests文件夹中运行UI自动化测试脚本

echo.
echo ================================================================================
echo    IOT平台UI自动化测试脚本（auto_tests文件夹版）
echo ================================================================================
echo.

REM 获取脚本所在目录
cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 错误: 未找到Python环境
    echo   请先安装Python 3.x 并添加到PATH
    echo   下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python环境检查通过
echo.

REM 检查依赖包
echo 检查必要的Python包...
python -c "import selenium; print('  ✓ Selenium已安装')" 2>nul || (
    echo  ⚠ 安装Selenium...
    pip install selenium webdriver-manager
)

python -c "import openpyxl; print('  ✓ OpenPyXL已安装')" 2>nul || (
    echo  ⚠ 安装OpenPyXL...
    pip install openpyxl
)

echo.
echo ================================================================================
echo   任务选择
echo ================================================================================
echo.
echo 1. 运行完整的自动化测试
echo 2. 显示测试日志
echo 3. 打开配置文件
echo 4. 查看最近的页面快照
echo 5. 返回父目录
echo 6. 退出
echo.

set /p choice="请选择 (1-6): "

if "%choice%"=="1" (
    echo.
    echo 正在启动UI自动化测试...
    echo.
    python ui_automation_final.py
    if errorlevel 1 (
        echo.
        echo ✗ 测试执行失败
        pause
    ) else (
        echo.
        echo ✓ 测试执行完成
        pause
    )
) else if "%choice%"=="2" (
    echo.
    echo 查找最近的测试日志...
    for /f "tokens=*" %%A in ('dir /b /o-d test_log_*.txt 2^>nul ^| findstr /r "^" 2^>nul') do (
        set LATEST=%%A
        goto :found
    )
    :found
    if defined LATEST (
        echo 打开日志文件: %LATEST%
        type %LATEST%
    ) else (
        echo 未找到测试日志文件
    )
    pause
) else if "%choice%"=="3" (
    echo.
    echo 打开配置文件...
    notepad test_config.ini
) else if "%choice%"=="4" (
    echo.
    echo 找最近的页面快照...
    for /f "tokens=*" %%A in ('dir /b /o-d page_source_*.html 2^>nul ^| findstr /r "^" 2^>nul') do (
        set LATEST=%%A
        goto :found2
    )
    :found2
    if defined LATEST (
        echo 打开页面快照: %LATEST%
        start %LATEST%
    ) else (
        echo 未找到页面快照文件
    )
    pause
) else if "%choice%"=="5" (
    echo 返回到父目录...
    cd ..
    echo 当前目录: %cd%
) else if "%choice%"=="6" (
    echo 再见!
    exit /b 0
) else (
    echo 无效的选择
    pause
    goto :start
)

REM 循环菜单
goto :start

:start
goto :start

:end
echo.
echo ================================================================================
echo 程序已结束
echo ================================================================================
pause

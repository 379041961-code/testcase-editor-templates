@echo off
chcp 65001 >nul
echo ✓ 启动缺陷管理自动化工具...
echo.

:: 设置环境变量
set CLOUD_EFFECT_USERNAME=nick1821010462
set CLOUD_EFFECT_PASSWORD=R20250918

echo ✓ 已设置环境变量
echo   - CLOUD_EFFECT_USERNAME: %CLOUD_EFFECT_USERNAME%
echo   - CLOUD_EFFECT_PASSWORD: *** (已隐藏)
echo.

:: 运行Python脚本
echo 【正在启动自动化脚本】
python bug_management_web_workflow.py

pause

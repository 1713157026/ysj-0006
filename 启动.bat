@echo off
chcp 65001 >nul
title 中国象棋 Web UI

echo ========================================
echo   中国象棋 Web UI 启动程序
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.6 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python 环境正常
echo.

echo [2/3] 检查并安装依赖...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装 Flask 和 flask-cors...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
) else (
    echo [OK] 依赖已安装
)
echo.

echo [3/3] 启动 Web 服务器...
echo.
echo ========================================
echo   启动成功！
echo   请在浏览器中访问: http://localhost:5000
echo   按 Ctrl+C 可以停止服务器
echo ========================================
echo.

python app.py

pause

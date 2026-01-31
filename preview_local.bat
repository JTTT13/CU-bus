@echo off
chcp 65001 >nul
title CUHK Bus Local Preview
cd /d "%~dp0"

echo ---------------------------------------
echo   正在更新數據並啟動本地預覽...
echo ---------------------------------------

:: 1. 先執行 Python 轉檔
python export_data.py
if %errorlevel% neq 0 (
    echo [Error] 轉檔失敗，請檢查資料庫。
    pause
    exit /b
)

echo [Success] 數據已更新。
echo [Info] 正在啟動伺服器...
echo [Link] 請在瀏覽器打開: http://localhost:8000
echo [Tips] 按 Ctrl+C 可以停止伺服器。

:: 2. 自動打開預設瀏覽器
start http://localhost:8000

:: 3. 啟動 Python 伺服器
python -m http.server 8000
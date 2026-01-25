@echo off
chcp 65001 >nul
title GitHub Vibe Uploader
color 0A

:: ==========================================
:: 0. 自動抓取當前資料夾路徑
:: ==========================================
cd /d "%~dp0"

echo ==========================================
echo       準備上傳 Code 到 GitHub...
echo       位置: %CD%
echo ==========================================
echo.

if exist ".git" goto GitFound
color 0C
echo [Error] 呢度唔係一個 Git Repository
pause
exit /b

:GitFound
:: ==========================================
:: 1. Add all files
:: ==========================================
echo [Step 1] 加入所有檔案 (git add)...
git add .
if %errorlevel% neq 0 goto AddFail
goto Step2

:AddFail
color 0C
echo [Error] 加入檔案失敗 請檢查
pause
exit /b

:Step2
echo.
:: ==========================================
:: 2. Commit Message (修復空格問題)
:: ==========================================
set "CommitMsg="
set /p CommitMsg="請輸入更新備註 (直接 Enter 會用預設值): "

:: 如果無輸入，預設用 Auto_Update (用底線代替空格，避免報錯)
if "%CommitMsg%"=="" set CommitMsg=Auto_Update

:: ==========================================
:: 3. Commit
:: ==========================================
echo.
echo [Step 2] 提交版本 (git commit)...
:: 加左引號保護，就算有空格都唔怕
git commit -m "%CommitMsg%"

echo.
:: ==========================================
:: 4. Push
:: ==========================================
echo [Step 3] 推送到雲端 (git push)...
git push

set "PushResult=%errorlevel%"
echo.
echo ==========================================

if %PushResult% equ 0 goto Success
goto Fail

:Success
color 0A
echo       上傳成功 搞掂 (Success)
echo       記得去 GitHub Pages 睇下有無變
goto End

:Fail
color 0C
echo       上傳失敗 (Fail)
echo       如果是第一次 Push，請手動執行一次: git push --set-upstream origin master
goto End

:End
echo ==========================================
echo.
pause

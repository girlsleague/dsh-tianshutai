@echo off
chcp 65001 >nul
title 启动天枢台 · 命理中心
echo ========================================================
echo          天枢台 (Tianshu Workbench) 正在启动...
echo ========================================================
echo.

set PY="C:\Users\LH\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

:: 检查并启动服务
echo [1/2] 正在启动后台命理排盘引擎服务 (端口 58765)...
start "" /B %PY% "E:\workspace\dsh-tianshutai\server\app.py"

:: 等待服务响应
timeout /t 2 /nobreak >nul

:: 打开浏览器访问
echo [2/2] 正在打开天枢台可视化工作台...
start http://127.0.0.1:58765

echo.
echo 天枢台已成功运行在 http://127.0.0.1:58765
echo 您可以随时在浏览器中体验，或在 DSH 侧边栏中随时调取！
echo ========================================================
pause

@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if "%~1"=="" (
  py -3 module2_ai_test_runner.py --output results
) else (
  py -3 module2_ai_test_runner.py --source "%~1" --output results
)
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if "%EXIT_CODE%"=="0" (
  echo 全部源级检查通过。
) else if "%EXIT_CODE%"=="1" (
  echo 检查完成，存在NG项，请查看results目录。
) else (
  echo 脚本运行失败，请按README指定源码目录。
)
pause
exit /b %EXIT_CODE%

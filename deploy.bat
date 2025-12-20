@echo off
echo ========================================
echo   Git 커밋 및 배포
echo ========================================
echo.

set /p msg="커밋 메시지를 입력하세요: "

git add .
git commit -m "%msg%"
git push origin main

echo.
echo ========================================
echo   배포 완료!
echo   https://narse.github.io 에서 확인하세요
echo ========================================
pause

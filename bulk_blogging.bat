@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo  🚀 대량 포스팅 작업 시작 (20개)       
echo  간격: 4분(240초)
echo ========================================

rem 1. Python 가상환경 활성화
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ❌ 가상환경을 찾을 수 없습니다. (.venv)
    pause
    exit /b
)

rem 2. 스크립트 실행 (20개, 240초 간격)
echo.
echo ⏳ 글 생성을 시작합니다...
python scripts/gov24_content_generator.py --auto --count 20 --interval 240

rem 3. 배포 진행
echo.
echo 📤 GitHub 배포 중...
git add -A
git commit -m "Bulk post: 20 posts added"
git pull origin main
git push origin main

echo.
echo ========================================
echo  ✅ 모든 작업이 완료되었습니다!
echo  https://narse.github.io 확인
echo ========================================
pause

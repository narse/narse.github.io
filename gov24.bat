@echo off
echo ========================================
echo   정부24 공공서비스 글 자동 생성
echo ========================================
echo.

cd /d %~dp0scripts
python gov24_content_generator.py

echo.
pause

@echo off
echo ========================================
echo   SEO 글 자동 생성
echo ========================================
echo.

cd scripts
set /p keyword="키워드를 입력하세요: "

python seo_content_generator.py "%keyword%"

echo.
echo 생성된 파일을 확인하세요: src\content\posts\
pause

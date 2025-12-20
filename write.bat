@echo off
chcp 65001 > nul
echo.
echo ========================================================
echo ✍️ AI 블로그 글쓰기 도우미 (SkyScript GenAI)
echo ========================================================
echo.
echo 원하는 주제나 키워드를 입력하면,
echo SEO 최적화된 글과 썸네일을 자동으로 생성합니다.
echo.

cd scripts
..\.venv\Scripts\python seo_content_generator.py
pause

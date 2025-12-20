"""
SEO 블로그 콘텐츠 자동 생성기
Gemini API를 활용하여 SEO 최적화된 Markdown 파일 생성
"""

import os
import re
import io
import base64
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# 환경변수 로드
load_dotenv()

# Gemini 클라이언트 설정
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 콘텐츠 저장 경로
CONTENT_DIR = Path(__file__).parent.parent / "src" / "content" / "posts"
PUBLIC_DIR = Path(__file__).parent.parent / "public" / "images" / "posts"


def slugify(text: str) -> str:
    """한글/영어 텍스트를 URL-safe slug로 변환"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s가-힣-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text[:50]

def generate_thumbnail(keyword: str, slug: str, title: str = None) -> str | None:
    """Gemini 2.5 Flash Image로 아이소메트릭 썸네일 생성 (한글 제목 포함)"""
    try:
        print("   🎨 썸네일 생성 중...")
        
        display_title = title or keyword
        if len(display_title) > 15:
            display_title = display_title[:15]
        
        prompt = f"""Create a professional isometric 3D illustration thumbnail for a blog post.

Topic: "{keyword}"

1. Title Overlay (MUST):
- Render the text "{display_title}" clearly at the TOP CENTER.
- Font: Bold, modern Sans-serif Korean font (Malgun Gothic style).
- Color: Dark Navy (#2c3e50) or White with shadow.
- Size: Large and readable.

2. Scene Description:
- Isometric 3D miniature diorama style.
- Soft pastel blue-gray background (#a8c5d9 to #c5d8e8).
- Cute 3D characters and objects related to the topic.
- Clean, modern, professional aesthetic.

3. IMPORTANT CONSTRAINTS (NO TEXT IN SCENE):
- DO NOT generate any text, letters, or numbers on buildings, signs, shirts, or objects.
- The 3D scene elements must be completely text-free (clean surfaces).
- The ONLY text allowed is the top title overlay.
- No gibberish or illegible psuedo-text in the artwork.

Aspect ratio: 1:1 (square)"""

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT'],
            )
        )
        
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
                    image_filename = f"{slug}.png"
                    image_path = PUBLIC_DIR / image_filename
                    
                    image_data = part.inline_data.data
                    if isinstance(image_data, str):
                        image_data = base64.b64decode(image_data)
                    
                    image_path.write_bytes(image_data)
                    
                    print(f"   ✓ 썸네일 저장: {image_filename}")
                    return f"/images/posts/{image_filename}"
        
        print("   ⚠️ 이미지 생성 결과 없음")
        return None
        
    except Exception as e:
        print(f"   ⚠️ 썸네일 생성 실패: {str(e)[:60]}")
        return None


def generate_seo_content(keyword: str, additional_context: str = "") -> dict:
    """
    키워드를 기반으로 SEO 최적화 블로그 콘텐츠 생성
    
    Args:
        keyword: 메인 키워드
        additional_context: 추가 컨텍스트 (선택)
    
    Returns:
        dict: title, description, content, tags
    """
    prompt = f"""당신은 SEO 전문 블로그 작가입니다. 
다음 키워드에 대해 SEO 최적화된 블로그 글을 작성해주세요.

키워드: {keyword}
{f'추가 컨텍스트: {additional_context}' if additional_context else ''}

## 요구사항:
1. 제목: 클릭을 유도하는 매력적인 제목 (키워드 포함)
2. 메타 설명: 150자 이내의 검색 결과용 설명
3. 본문: 
   - H2, H3 헤딩을 적절히 사용
   - 1500자 이상의 풍부한 내용
   - 자연스러운 키워드 배치
   - 실용적인 정보와 팁 포함
   - FAQ 섹션 포함
4. 태그: 관련 키워드 5개

guide365.kr 스타일을 참고하여 상세하고 전문적으로 작성해주세요.
- 🏛️ 서론/개요
- 👥 상세 내용
- 📝 실용적인 팁/가이드
- 📋 요약 및 결론
- ❓ FAQ (자주 묻는 질문)
형식으로 구성해주세요.

## 출력 형식 (정확히 따라주세요):
[TITLE]
제목 내용
[/TITLE]

[DESCRIPTION]
메타 설명 내용
[/DESCRIPTION]

[TAGS]
태그1, 태그2, 태그3, 태그4, 태그5
[/TAGS]

[CONTENT]
마크다운 형식의 본문
[/CONTENT]
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=8192,
        )
    )
    
    text = response.text
    
    # 파싱
    title_match = re.search(r'\[TITLE\](.*?)\[/TITLE\]', text, re.DOTALL)
    desc_match = re.search(r'\[DESCRIPTION\](.*?)\[/DESCRIPTION\]', text, re.DOTALL)
    tags_match = re.search(r'\[TAGS\](.*?)\[/TAGS\]', text, re.DOTALL)
    content_match = re.search(r'\[CONTENT\](.*?)\[/CONTENT\]', text, re.DOTALL)
    
    title = title_match.group(1).strip() if title_match else keyword
    description = desc_match.group(1).strip() if desc_match else ""
    tags = [t.strip() for t in tags_match.group(1).split(',')] if tags_match else [keyword]
    content = content_match.group(1).strip() if content_match else text
    
    return {
        "title": title,
        "description": description,
        "tags": tags,
        "content": content
    }


def create_markdown_file(keyword: str, additional_context: str = "", author: str = "Admin") -> Path:
    """
    SEO 콘텐츠를 생성하고 Markdown 파일로 저장
    
    Args:
        keyword: 메인 키워드
        additional_context: 추가 컨텍스트
        author: 작성자 이름
    
    Returns:
        Path: 생성된 파일 경로
    """
    print(f"🔍 키워드 '{keyword}'로 콘텐츠 생성 중...")
    
    # 콘텐츠 생성
    result = generate_seo_content(keyword, additional_context)
    
    # 썸네일 생성
    slug = slugify(result["title"])
    cover_image = generate_thumbnail(keyword, slug, result["title"])
    if cover_image:
        result['coverImage'] = cover_image
    
    # 파일명 생성
    slug = slugify(result["title"])
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_prefix}-{slug}.md"
    filepath = CONTENT_DIR / filename
    
    # 디렉토리 생성
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Frontmatter + 본문 작성
    tags_str = str(result["tags"]).replace("'", '"')
    markdown_content = f'''---
title: "{result["title"]}"
description: "{result["description"]}"
publishedAt: {datetime.now().strftime("%Y-%m-%d")}
category: "blog"
tags: {tags_str}
author: "{author}"
coverImage: "{result.get('coverImage', '')}"
featured: false
draft: false
---

{result["content"]}
'''
    
    # 파일 저장
    filepath.write_text(markdown_content, encoding="utf-8")
    
    print(f"✅ 파일 생성 완료: {filepath}")
    return filepath


def batch_generate(keywords: list[str], author: str = "Admin") -> list[Path]:
    """
    여러 키워드에 대해 일괄 콘텐츠 생성
    
    Args:
        keywords: 키워드 목록
        author: 작성자
    
    Returns:
        list[Path]: 생성된 파일 경로 목록
    """
    created_files = []
    
    for i, keyword in enumerate(keywords, 1):
        print(f"\n📝 [{i}/{len(keywords)}] 처리 중...")
        try:
            filepath = create_markdown_file(keyword, author=author)
            created_files.append(filepath)
        except Exception as e:
            print(f"❌ '{keyword}' 처리 실패: {e}")
    
    print(f"\n🎉 완료! 총 {len(created_files)}개 파일 생성됨")
    return created_files


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 명령줄 인자로 키워드 전달
        keyword = " ".join(sys.argv[1:])
        create_markdown_file(keyword)
    else:
        # 대화형 모드
        print("=" * 50)
        print("🚀 SEO 블로그 콘텐츠 자동 생성기")
        print("=" * 50)
        
        while True:
            keyword = input("\n키워드를 입력하세요 (종료: q): ").strip()
            
            if keyword.lower() == 'q':
                print("👋 종료합니다.")
                break
            
            if not keyword:
                print("⚠️ 키워드를 입력해주세요.")
                continue
            
            try:
                create_markdown_file(keyword)
                print("\\n✨ 글 작성이 완료되었습니다!")
            except Exception as e:
                print(f"❌ 오류 발생: {e}")

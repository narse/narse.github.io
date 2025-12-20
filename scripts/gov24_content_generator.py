"""
정부24 공공서비스 자동 발행 모듈 (Astro 블로그용) - 썸네일 포함 버전
- 정부24 API에서 공공서비스 정보 조회
- Gemini AI로 SEO 최적화 콘텐츠 생성
- Gemini로 썸네일 이미지 생성 (OG Image용)
- Markdown 파일로 저장 (Astro 블로그 호환)
"""
import os
import re
import time
import base64
import logging
from datetime import datetime
from pathlib import Path
from io import BytesIO

import requests
from urllib.parse import unquote
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONTENT_DIR = PROJECT_DIR / "src" / "content" / "posts"
PUBLIC_DIR = PROJECT_DIR / "public" / "images" / "posts"


class Gov24API:
    def __init__(self, service_key: str = None):
        if not service_key:
            raw_key = os.getenv("GOV24_SERVICE_KEY", "")
            service_key = unquote(raw_key) if raw_key else ""
            
        self.service_key = service_key
        self.base_url = "https://api.odcloud.kr/api/gov24/v3"
        self.session = requests.Session()
        
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        if params is None:
            params = {}
        params['serviceKey'] = self.service_key
        params.setdefault('returnType', 'JSON')
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_service_list(self, page: int = 1, per_page: int = 10) -> dict:
        return self._make_request('serviceList', {'page': page, 'perPage': per_page})


class Gov24ContentGenerator:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        
    def generate_markdown_content(self, service_data: dict) -> dict:
        service_info = self._prepare_service_info(service_data)
        
        try:
            prompt = self._create_prompt(service_info)
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=8192)
            )
            
            if response.text:
                if "SKIP" in response.text.upper() and len(response.text) < 20:
                     logging.info(f"⏭️ 기간 만료 또는 유효하지 않은 서비스로 건너뜀: {info['name']}")
                     return None
                return self._parse_response(response.text, info)
        except Exception as e:
            logging.error(f"AI 생성 실패: {e}")
        
        return self._fallback_content(service_info)
    
    def generate_thumbnail(self, service_name: str, slug: str, title: str = None) -> str | None:
        """Gemini 2.5 Flash Image로 아이소메트릭 썸네일 생성 (한글 제목 포함)"""
        try:
            print("   🎨 썸네일 생성 중...")
            
            # 제목에서 핵심 키워드 추출 (짧게)
            display_title = title or service_name
            # 너무 길면 줄임
            if len(display_title) > 15:
                display_title = display_title[:15]
            
            prompt = f"""Create a professional isometric 3D illustration thumbnail for a Korean government service.

Topic: "{service_name}"

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

            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE', 'TEXT'],
                )
            )
            
            # 이미지 저장
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
                        image_filename = f"{slug}.png"
                        image_path = PUBLIC_DIR / image_filename
                        
                        # 이미지 데이터 저장
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
    
    def _prepare_service_info(self, data: dict) -> dict:
        return {
            'name': data.get('서비스명', ''),
            'agency': data.get('소관기관명', ''),
            'type': data.get('지원유형', ''),
            'purpose': data.get('서비스목적요약', ''),
            'target': data.get('지원대상', ''),
            'content': data.get('지원내용', ''),
            'method': data.get('신청방법', ''),
            'deadline': data.get('신청기한', ''),
            'contact': data.get('전화문의', ''),
            'url': data.get('상세조회URL', ''),
        }
    
    def _create_prompt(self, info: dict) -> str:
        # User context implies current date is late 2025
        current_date_str = "2025-12-21"
        
        return f"""You are a professional government policy analyst. Verify the validity of this service relative to today's date ({current_date_str}).

CRITICAL FILTERING RULE:
1. If the service's application period has ALREADY ENDED before today ({current_date_str}), you MUST output only one word: SKIP
2. If the service was only valid for a past year (e.g. 2023, 2024 specific) and not applicable to 2025/2026, output: SKIP
3. Only proceed if the service is valid for late 2025 or 2026.

서비스 정보:
- 서비스명: {info['name']}
- 소관기관: {info['agency']}
- 지원유형: {info['type']}
- 목적: {info['purpose']}
- 지원대상: {info['target']}
- 지원내용: {info['content']}
- 신청방법: {info['method']}
- 신청기한: {info['deadline']}
- 문의처: {info['contact']}
- URL: {info['url']}

If valid, write a detailed blog post in Markdown format (guide365.kr style).
출력 형식 (정확히 따르세요):

TITLE: (SEO 제목 40-60자, 느낌표/콜론 금지, 2025년/2026년 키워드 포함)
DESC: (메타설명 120-160자, 혜택과 신청 유도 포함)
TAGS: 정부지원금, 복지혜택, 키워드1, 키워드2, 키워드3


## 🏛️ 서비스 개요 및 혜택

(4-5문단으로 상세히 작성)
- 첫 문단: 서비스의 목적과 주관 기관 소개
- 둘째 문단: 이 서비스가 제공하는 구체적인 혜택과 기대 효과
- 셋째 문단: 최근 트렌드나 정책 변화와 연결지어 설명
- 넷째 문단: 이 서비스를 통해 얻을 수 있는 실질적 이점

## 👥 지원 대상 및 자격 요건

(상세히 작성)
- 지원 대상을 명확히 설명
- 목록 형태로 대상자 나열:
  - 대상 1
  - 대상 2
  - 대상 3
- 지원 제외 대상이 있다면 명시
- 우선 지원 대상 안내

## 📝 신청 방법 및 절차

(단계별로 상세히 작성)
1. 첫 번째 단계 설명
2. 두 번째 단계 설명
3. 세 번째 단계 설명
- 신청 시 유의사항 안내
- 심사 과정 설명 (있는 경우)

## 📋 필요 서류 및 준비사항

(필요 서류 목록)
- 필요 서류 1
- 필요 서류 2
- 필요 서류 3
- 서류 준비 시 팁이나 주의사항

## 📞 문의처 및 추가 정보

문의처 정보와 함께 추가 안내 작성:
- **담당 기관:** {info['agency']}
- **연락처:** {info['contact']}

📋 **정부24 공식 정보 바로가기**

[상세 정보 확인하기 →]({info['url']})

## ❔ 자주하는 질문 FAQ

### Q. 이 서비스는 누가 신청할 수 있나요?
A. (지원 대상 정보를 바탕으로 구체적으로 답변, 2-3문장)

### Q. 신청은 어떻게 하나요?
A. (신청 방법을 구체적으로 답변, 2-3문장)

### Q. 문의는 어디로 하나요?
A. {info['contact']}로 문의하시면 됩니다.

---
*본 정보는 정부24 공식 정보를 바탕으로 작성되었습니다.*
"""
    
    def _parse_response(self, text: str, info: dict) -> dict:
        result = {'title': '', 'description': '', 'tags': [], 'content': ''}
        
        # TITLE 추출
        title_match = re.search(r'TITLE:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            title = re.sub(r'[!:,]', ' ', title)
            result['title'] = ' '.join(title.split())
        else:
            result['title'] = f"{info['name']} 신청 방법 및 혜택 총정리"
        
        # DESC 추출
        desc_match = re.search(r'DESC:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if desc_match:
            result['description'] = desc_match.group(1).strip()
        else:
            result['description'] = f"{info['name']} 지원 대상과 신청 방법을 알아보세요."
        
        # TAGS 추출
        tags_match = re.search(r'TAGS:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if tags_match:
            result['tags'] = [t.strip() for t in tags_match.group(1).split(',') if t.strip()]
        else:
            result['tags'] = ['정부지원금', '복지혜택', info['name']]
        
        # 콘텐츠 추출 (## 부터)
        content_match = re.search(r'(##\s+.+)', text, re.DOTALL)
        if content_match:
            content = content_match.group(1).strip()
            content = re.sub(r'^TITLE:.*?\n', '', content, flags=re.MULTILINE | re.IGNORECASE)
            content = re.sub(r'^DESC:.*?\n', '', content, flags=re.MULTILINE | re.IGNORECASE)
            content = re.sub(r'^TAGS:.*?\n', '', content, flags=re.MULTILINE | re.IGNORECASE)
            result['content'] = content
        else:
            result['content'] = self._fallback_content(info)['content']
        
        return result
    
    def _fallback_content(self, info: dict) -> dict:
        content = f"""## 📊 핵심 정보 요약

| 항목 | 내용 |
|------|------|
| 🏛️ 서비스명 | {info['name']} |
| 👥 지원 대상 | {info['target'] or '해당 요건 충족자'} |
| 💰 지원 내용 | {(info['content'] or '상세 내용 참조')[:100]} |
| 📝 신청 방법 | {info['method'] or '온라인/방문 신청'} |
| 📅 신청 기한 | {info['deadline'] or '상시'} |
| 📞 문의처 | {info['contact'] or info['agency']} |

## 🏛️ 서비스 개요

{info['purpose'] or '정부에서 제공하는 지원 서비스입니다.'}

본 서비스는 **{info['agency']}**에서 제공합니다.

## 👥 지원 대상

{info['target'] or '해당 요건을 충족하는 분'}

## 📝 신청 방법

{info['method'] or '담당 기관에 문의하세요.'}

## 💰 지원 내용

{info['content'] or '상세 내용은 담당 기관에 문의하세요.'}

## 📞 문의처

- **담당 기관:** {info['agency']}
- **연락처:** {info['contact'] or '해당 기관 문의'}
- **상세 정보:** [정부24 바로가기]({info['url'] or 'https://www.gov.kr'})

---
*본 정보는 정부24 공식 정보를 바탕으로 작성되었습니다.*
"""
        return {
            'title': f"{info['name']} 신청 방법 및 혜택 총정리",
            'description': f"{info['name']} 지원 대상, 신청 방법을 알아보세요.",
            'tags': ['정부지원금', '복지혜택', info['name']],
            'content': content
        }


class DuplicateTracker:
    def __init__(self):
        self.file = SCRIPT_DIR / "processed_gov24_services.txt"
        self.processed = set()
        if self.file.exists():
            self.processed = set(self.file.read_text(encoding='utf-8').splitlines())
    
    def is_processed(self, sid: str) -> bool:
        return sid in self.processed
    
    def mark_processed(self, sid: str):
        self.processed.add(sid)
        with open(self.file, 'a', encoding='utf-8') as f:
            f.write(f"{sid}\n")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s가-힣-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text[:50]


def create_markdown_file(data: dict, cover_image: str = None) -> Path:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    
    slug = slugify(data['title'])
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date}-gov24-{slug}.md"
    filepath = CONTENT_DIR / filename
    
    tags_str = '["' + '", "'.join(data['tags'][:5]) + '"]'
    
    # coverImage 라인 (있으면 추가)
    cover_line = f'\ncoverImage: "{cover_image}"' if cover_image else ''
    
    md = f'''---
title: "{data['title']}"
description: "{data['description']}"
publishedAt: {date}
category: "정부지원금"
tags: {tags_str}
author: "지원금 25시"
featured: false
draft: false{cover_line}
---

{data['content']}
'''
    
    filepath.write_text(md, encoding='utf-8')
    return filepath, slug


def run():
    print("=" * 60)
    print("🏛️ 정부24 공공서비스 콘텐츠 자동 생성")
    print("   (썸네일 생성 + OG Image 지원)")
    print("=" * 60)
    
    gov24_key = os.getenv('GOV24_SERVICE_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not gov24_key:
        gov24_key = input("정부24 API 키: ").strip()
    if not gemini_key:
        gemini_key = input("Gemini API 키: ").strip()
    
    if not gov24_key or not gemini_key:
        print("❌ API 키가 필요합니다.")
        return
    
    api = Gov24API(gov24_key)
    generator = Gov24ContentGenerator(gemini_key)
    tracker = DuplicateTracker()
    
def run():
    import sys
    is_auto = "--auto" in sys.argv
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        return

    api = Gov24API()
    generator = Gov24ContentGenerator(gemini_key)
    tracker = DuplicateTracker()

    if is_auto:
        print("\n🤖 자동 모드 실행 (기본 5개, 썸네일 생성)")
        count = 5
        gen_thumb = True
    else:
        try:
            count = int(input("\n생성할 글 개수 (기본=5): ").strip() or "5")
        except:
            count = 5
        
        # 썸네일 생성 여부
        gen_thumb_input = input("썸네일 생성? (Y/n, 기본=Y): ").strip().lower()
        gen_thumb = gen_thumb_input != 'n'
    
    print(f"\n📝 {count}개 글 생성 시작...")
    if gen_thumb:
        print("🎨 썸네일도 함께 생성합니다.\n")
    else:
        print()
    
    created, page = 0, 1
    
    while created < count:
        try:
            services = api.get_service_list(page=page, per_page=10)
            if not services.get('data'):
                break
            
            for svc in services['data']:
                if created >= count:
                    break
                
                sid = svc.get('서비스ID')
                name = svc.get('서비스명', '')
                
                if not sid or tracker.is_processed(sid):
                    continue
                
                print(f"[{created+1}/{count}] 📰 {name[:35]}...")
                print("   ✍️ AI 콘텐츠 생성...")
                
                data = generator.generate_markdown_content(svc)
                if not data:
                    print("   ⏭️ 스킵됨 (기간 만료)")
                    tracker.mark_processed(sid) # 다시 처리하지 않도록 기록
                    continue
                    
                print(f"   ✓ 제목: {data['title'][:40]}...")
                
                # 썸네일 생성 (제목 텍스트 포함)
                cover_image = None
                if gen_thumb:
                    slug = slugify(data['title'])
                    cover_image = generator.generate_thumbnail(name, slug, data['title'])
                
                # 파일 저장
                filepath, _ = create_markdown_file(data, cover_image)
                print(f"   ✅ 저장: {filepath.name}")
                
                tracker.mark_processed(sid)
                created += 1
                time.sleep(2)  # API 제한 방지
            
            page += 1
        except Exception as e:
            print(f"❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print(f"\n{'='*60}")
    print(f"🎉 완료! {created}개 글 생성됨")
    print(f"📁 글 저장: {CONTENT_DIR}")
    if gen_thumb:
        print(f"🖼️ 이미지 저장: {PUBLIC_DIR}")
    print("=" * 60)
    print("\n💡 npm run dev 로 확인하세요!")


if __name__ == "__main__":
    run()

import re

KOR_ENG_MAPPING = {
    '유로빌리노겐': 'urobilinogen',
    '빌리루빈': 'bilirubin',
    '케톤체': 'ketone',
    '아질산염': 'nitrite',
    '백혈구': 'wbc',
    '적혈구': 'rbc',
    '혈색소': 'hb',
    '호중구': ['neutrophil', 'neutroph'],
    '요비중': ['specific gravity', 'sg', 's.g'],
    # 필요한 매핑을 더 추가할 수 있습니다
}

def normalize_text(text):
    """텍스트 정규화: 괄호 처리, 순서 통일, 한영 변환"""
    import re
    
    # 소문자로 변환
    text = text.lower()
    
    # 점(.) 제거하여 약어 통일 (예: s.g -> sg)
    text = text.replace('.', '')
    
    # 괄호 안의 텍스트 추출 (영문 약자 우선 처리)
    abbreviations = re.findall(r'\(([A-Za-z0-9]+)\)', text)
    # 나머지 괄호 내용 추출
    other_brackets = [b for b in re.findall(r'\((.*?)\)', text) if b not in abbreviations]
    
    # 괄호 제거한 기본 텍스트
    base_text = re.sub(r'[\(\)]', '', text).strip()
    
    # 슬래시로 구분된 텍스트를 분리
    parts = set([p.strip() for p in base_text.split('/')] + abbreviations + other_brackets)
    # 빈 문자열 제거
    parts = set(p for p in parts if p)
    
    # 한글이 있는 경우 영문 매핑 추가
    expanded_parts = set(parts)
    for part in parts:
        # 한글 매핑이 있는 경우 영문 버전 추가
        if part in KOR_ENG_MAPPING:
            mapping = KOR_ENG_MAPPING[part]
            if isinstance(mapping, list):
                expanded_parts.update(mapping)
            else:
                expanded_parts.add(mapping)
        # 영문 매핑이 있는 경우 한글 버전 추가
        for kor, eng in KOR_ENG_MAPPING.items():
            if isinstance(eng, list):
                if part in eng:
                    expanded_parts.add(kor)
            elif part == eng:
                expanded_parts.add(kor)
    
    return expanded_parts


def remove_duplicated_chars(text):
    """텍스트에서 연속된 특수문자와 한글 중복을 제거"""
    if not text:
        return text
        
    # 특수문자 패턴 정의
    special_chars = r'[,.<>{}[\]\/\\\(\)!@#$%^&*+=|;:"\']'
    
    # 연속된 특수문자 제거
    text = re.sub(f'{special_chars}+', lambda m: m.group()[0], text)
    
    result = []
    prev_char = None
    
    for char in text:
        # 한글인 경우: 이전 문자와 다를 때만 추가
        if re.match('[가-힣]', char):
            if char != prev_char:
                result.append(char)
        # 한글이 아닌 경우: 그대로 추가
        else:
            result.append(char)
        prev_char = char if re.match('[가-힣]', char) else None
    
    # 결과 문자열의 앞뒤 공백 제거
    return ''.join(result).strip()
"""
print문을 Logger로 자동 변환하는 스크립트
"""
import re
import sys

def convert_print_to_logger(file_path):
    """파일 내 모든 print문을 Logger로 변환"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 변환 규칙 (순서 중요 - 구체적인 것부터)
    replacements = [
        # 1. 명시적 태그가 있는 경우
        (r'print\(f"\[ERROR\]([^"]*)"', r'Logger.error(f"\1"'),
        (r"print\(f'\[ERROR\]([^']*)'", r"Logger.error(f'\1'"),
        
        (r'print\(f"\[WARN\]([^"]*)"', r'Logger.warn(f"\1"'),
        (r"print\(f'\[WARN\]([^']*)'", r"Logger.warn(f'\1'"),
        
        (r'print\(f"\[INFO\]([^"]*)"', r'Logger.info(f"\1"'),
        (r"print\(f'\[INFO\]([^']*)'", r"Logger.info(f'\1'"),
        
        (r'print\(f"\[DEBUG\]([^"]*)"', r'Logger.debug(f"\1"'),
        (r"print\(f'\[DEBUG\]([^']*)'", r"Logger.debug(f'\1'"),
        
        # 2. 다른 태그들 (SYSTEM, TABLE, SELECT, WEBHOOK, SCORE 등) -> debug
        (r'print\(f"\[[A-Z_]+\]([^"]*)"', r'Logger.debug(f"\1"'),
        (r"print\(f'\[[A-Z_]+\]([^']*)'", r"Logger.debug(f'\1'"),
        
        # 3. 일반 print (태그 없음) -> debug
        (r'print\(f"([^"]*)"', r'Logger.debug(f"\1"'),
        (r"print\(f'([^']*)'", r"Logger.debug(f'\1'"),
        
        # 4. f-string 아닌 일반 print
        (r'print\("([^"]*)"', r'Logger.debug("\1"'),
        (r"print\('([^']*)'", r"Logger.debug('\1'"),
        
        # 5. 변수만 출력하는 경우
        (r'print\(([^)]+)\)(?!\))', r'Logger.debug(str(\1))'),
    ]
    
    # 변환 적용
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # 변경사항이 있는지 확인
    if content != original_content:
        # 백업 생성
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"✅ 백업 생성: {backup_path}")
        
        # 변환된 내용 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 통계
        original_prints = len(re.findall(r'\bprint\(', original_content))
        remaining_prints = len(re.findall(r'\bprint\(', content))
        converted = original_prints - remaining_prints
        
        print(f"✅ 변환 완료: {file_path}")
        print(f"   - 변환됨: {converted}개")
        print(f"   - 남은 print: {remaining_prints}개")
        
        return True
    else:
        print(f"ℹ️  변경사항 없음: {file_path}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python convert_print_to_logger.py <파일경로>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    convert_print_to_logger(file_path)

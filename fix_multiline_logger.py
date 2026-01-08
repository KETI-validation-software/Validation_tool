import re
import sys

def fix_logger_multiline_calls(file_path):
    """Logger.xxx(str(f"...")) 패턴을 Logger.xxx(f"...")로 수정"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 패턴 1: Logger.debug(str(f"...{json.dumps(...))[:300]}"))
    # → Logger.debug(f"...{json.dumps(...)[:300]}")
    pattern1 = r'Logger\.(\w+)\(str\(\s*f"([^"]*{json\.dumps\([^)]+\))\)(\[:300\]"}"\)\)'
    
    # 간단한 방법: 수동으로 파일 줄별로 처리
    lines = content.split('\n')
    i = 0
    new_lines = []
    
    while i < len(lines):
        line = lines[i]
        
        # Logger.xxx(str( 패턴 찾기
        if 'Logger.' in line and '(str(' in line and i + 1 < len(lines):
            # 다음 줄과 결합
            next_line = lines[i + 1]
            
            # 2줄 패턴: Logger.xxx(str(\n    f"...{...))...}")
            if next_line.strip().startswith('f"'):
                # f-string 추출
                fstring_match = re.search(r'f"([^"]*)"', next_line)
                if fstring_match:
                    # Logger 레벨 추출
                    level_match = re.search(r'Logger\.(\w+)\(str\(', line)
                    if level_match:
                        level = level_match.group(1)
                        indent = len(line) - len(line.lstrip())
                        fstring_content = next_line.strip()
                        
                        # str( 제거, 마지막 )) 제거
                        # f"..." 부분만 추출
                        if '[:300]' in fstring_content:
                            # {json.dumps(...)[:300]} 형태 처리
                            fstring_content = fstring_content.replace('))[:300]', ')[:300]')
                        else:
                            # {len(...))}) 형태 처리  
                            fstring_content = fstring_content.rstrip(')')
                        
                        # DEBUG 태그 제거
                        fstring_content = fstring_content.replace('[DEBUG][', '[')
                        
                        # 새 줄 생성
                        new_line = ' ' * indent + f'Logger.{level}({fstring_content})'
                        new_lines.append(new_line)
                        i += 2  # 2줄 건너뛰기
                        continue
        
        new_lines.append(line)
        i += 1
    
    content = '\n'.join(new_lines)
    
    if content != original:
        # 백업 생성
        backup_path = f"{file_path}.manual_fix.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print(f"✅ 백업 생성: {backup_path}")
        
        # 수정된 내용 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 수정 완료: {file_path}")
    else:
        print(f"ℹ️  변경사항 없음: {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python fix_multiline_logger.py <파일경로>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    fix_logger_multiline_calls(file_path)

"""
잘못된 Logger 호출 패턴 수정 스크립트
Logger.debug("...", var) → Logger.debug(f"...: {var}")
"""
import re
import sys

def fix_logger_calls(file_path):
    """파일 내 잘못된 Logger 호출 수정"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 패턴 1: Logger.xxx("text", variable) → Logger.xxx(f"text: {variable}")
    pattern1 = r'Logger\.(debug|info|warn|error)\("([^"]+)":\s*,\s*([^)]+)\)'
    replacement1 = r'Logger.\1(f"\2: {\3}")'
    content = re.sub(pattern1, replacement1, content)
    
    # 패턴 2: Logger.xxx("text:", variable) → Logger.xxx(f"text: {variable}")
    pattern2 = r'Logger\.(debug|info|warn|error)\("([^"]+)",\s*([^)]+)\)'
    replacement2 = r'Logger.\1(f"\2: {\3}")'
    content = re.sub(pattern2, replacement2, content)
    
    if content != original_content:
        # 백업 생성
        backup_path = file_path + '.logger_fix.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"✅ 백업 생성: {backup_path}")
        
        # 수정된 내용 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 수정 완료: {file_path}")
        return True
    else:
        print(f"ℹ️  변경사항 없음: {file_path}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python fix_logger_calls.py <파일경로>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    fix_logger_calls(file_path)

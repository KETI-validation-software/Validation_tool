import re
import difflib
import sys

source_file = 'systemVal_all.py'
parent_file = 'ui/system_main_ui.py'

target_methods = [
    'initUI', 'resizeEvent', '_update_button_positions', 
    'init_centerLayout', 'create_spec_score_display_widget',
    'create_total_score_display_widget', 'group_score', '_toggle_placeholder', 
    'update_score_display', 'append_monitor_log', 'table_cell_clicked', 
    'show_combined_result', 'select_first_scenario', '_remove_api_number_suffix'
]

def normalize(text):
    # 모든 공백문자 제거 후 비교
    return re.sub(r'\s+', '', text)

def get_methods_with_ranges(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    methods = {}
    current_name = None
    start_idx = -1
    
    for i, line in enumerate(lines):
        match = re.match(r'^    def\s+(\w+)\s*\(', line)
        if match:
            if current_name:
                methods[current_name] = (start_idx, i, "".join(lines[start_idx:i]))
            current_name = match.group(1)
            start_idx = i
        elif current_name:
            if line.strip() and not line.startswith('    ') and not line.startswith('#') and not line.startswith('\n'):
                methods[current_name] = (start_idx, i, "".join(lines[start_idx:i]))
                current_name = None
                start_idx = -1
    if current_name:
        methods[current_name] = (start_idx, len(lines), "".join(lines[start_idx:]))
    return lines, methods

# 1. 부모 분석
_, parent_methods = get_methods_with_ranges(parent_file)
# 2. 자식 분석
child_lines, child_methods = get_methods_with_ranges(source_file)

to_remove_ranges = []
deferred = []

for name in target_methods:
    if name in child_methods and name in parent_methods:
        p_body = parent_methods[name][2]
        c_body = child_methods[name][2]
        
        if normalize(p_body) == normalize(c_body):
            to_remove_ranges.append(child_methods[name][:2])
        else:
            deferred.append(name)
    elif name in child_methods:
        deferred.append(name)

# 3. 삭제 수행 (뒤에서부터 삭제해야 인덱스가 안 꼬임)
new_lines = list(child_lines)
for start, end in sorted(to_remove_ranges, reverse=True):
    del new_lines[start:end]

# 4. 파일 쓰기
with open(source_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# 5. 결과 보고
if deferred:
    print(f"DEFERRED:{','.join(deferred)}")
else:
    print("ALL_REMOVED")

# 6. Diff 출력
diff = difflib.unified_diff(child_lines, new_lines, fromfile=source_file, tofile=source_file)
sys.stdout.writelines(diff)

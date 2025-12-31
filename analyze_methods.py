import re
import os

source_file = 'systemVal_all.py'
parent_file = 'ui/system_main_ui.py'

target_methods = [
    'initUI', 'resizeEvent', '_update_button_positions', 
    'init_centerLayout', 'create_spec_score_display_widget', 
    'create_total_score_display_widget', 'group_score', '_toggle_placeholder', 
    'update_score_display', 'append_monitor_log', 'table_cell_clicked', 
    'show_combined_result', 'select_first_scenario', '_remove_api_number_suffix'
]

def get_methods_map(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    methods = {}
    current_name = None
    body = []
    
    for line in lines:
        match = re.match(r'^    def\s+(\w+)\s*\(', line)
        if match:
            if current_name:
                methods[current_name] = body
            current_name = match.group(1)
            body = [line]
        elif current_name:
            if line.strip() and not line.startswith('    ') and not line.startswith('#') and not line.startswith('\n'):
                methods[current_name] = body
                current_name = None
                body = []
            else:
                body.append(line)
    if current_name:
        methods[current_name] = body
    return methods

# 1. 부모 메서드 추출
parent_map = get_methods_map(parent_file)
# 2. 자식 메서드 추출
child_map = get_methods_map(source_file)

to_remove = []
deferred = []

for name in target_methods:
    if name in child_map and name in parent_map:
        # 본문 비교 (들여쓰기 및 내용)
        if "".join(child_map[name]) == "".join(parent_map[name]):
            to_remove.append(name)
        else:
            deferred.append(name)
    elif name in child_map:
        # 부모에 없는데 자식에만 있으면 삭제하면 안 됨
        deferred.append(name)

print(f"REMOVE_LIST:{','.join(to_remove)}")
print(f"DEFERRED_LIST:{','.join(deferred)}")

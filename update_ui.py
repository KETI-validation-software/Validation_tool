import re
import sys
import difflib

source_file = 'systemVal_all.py'
target_file = 'ui/system_main_ui.py'

target_methods = [
    'initUI', 'create_spec_selection_panel', 'create_group_selection_table',
    'create_test_field_group', 'init_centerLayout', 'create_spec_score_display_widget',
    'create_total_score_display_widget', 'group_score', '_update_button_positions',
    'resizeEvent', '_toggle_placeholder', 'update_score_display', 'update_test_field_table',
    'append_monitor_log', 'table_cell_clicked', 'show_combined_result', 'select_first_scenario',
    '_remove_api_number_suffix'
]

# Read Source with encoding safety
try:
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except UnicodeDecodeError:
    with open(source_file, 'r', encoding='cp949') as f:
        lines = f.readlines()

imports = []
methods_content = []

# 1. Extract Imports
for line in lines:
    if line.strip().startswith('class MyApp'):
        break
    if line.startswith('import ') or line.startswith('from '):
        imports.append(line)

# 2. Extract Methods
current_method = None
method_lines = []

for i, line in enumerate(lines):
    match = re.match(r'^    def\s+(\w+)\s*\(', line)
    if match:
        if current_method:
            methods_content.extend(method_lines)
            methods_content.append('\n')
            current_method = None
            method_lines = []
        
        name = match.group(1)
        if name in target_methods:
            current_method = name
            method_lines.append(line)
            continue
    
    if current_method:
        if line.strip() and not line.startswith('    ') and not line.startswith('#') and not line.startswith('\n'):
             methods_content.extend(method_lines)
             methods_content.append('\n')
             current_method = None
             method_lines = []
        else:
            method_lines.append(line)

if current_method:
    methods_content.extend(method_lines)
    methods_content.append('\n')

# 3. Write New File
with open(target_file, 'w', encoding='utf-8') as f:
    f.writelines(imports)
    f.write('\n')
    f.write('class SystemMainUI(QWidget):\n')
    f.write('    def __init__():\n')
    f.write('        super().__init__()\n')
    f.write('\n')
    f.writelines(methods_content)

# 4. Success message (Diff will be handled by reading the file)
print("SUCCESS")
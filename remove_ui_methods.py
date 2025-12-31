import re
import sys
import difflib

source_file = 'systemVal_all.py'

target_methods = [
    'initUI', 'create_spec_selection_panel', 'create_group_selection_table',
    'create_test_field_group', 'init_centerLayout', 'create_spec_score_display_widget',
    'create_total_score_display_widget', 'group_score', '_update_button_positions',
    'resizeEvent', '_toggle_placeholder', 'update_score_display', 'update_test_field_table',
    'append_monitor_log', 'table_cell_clicked', 'show_combined_result', 'select_first_scenario',
    '_remove_api_number_suffix'
]

# Read Source
try:
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except UnicodeDecodeError:
    with open(source_file, 'r', encoding='cp949') as f:
        lines = f.readlines()

new_lines = []
current_method = None
skip_lines = False

for i, line in enumerate(lines):
    # Method start detection inside MyApp (4 spaces indent)
    match = re.match(r'^    def\s+(\w+)\s*\(', line)
    if match:
        name = match.group(1)
        if name in target_methods:
            current_method = name
            skip_lines = True
            # print(f"Removing method: {name}") # Debug
        else:
            current_method = None
            skip_lines = False
    
    # If we are inside a method to remove
    if skip_lines:
        # Check if the method ended (unindented line or new method start)
        # But 'match' above already handles new method start.
        # We need to handle end of class or unindented code block.
        
        # If line is NOT empty and NOT indented (and not comment), method ended
        if line.strip() and not line.startswith('    ') and not line.startswith('#') and not line.startswith('\n'):
             skip_lines = False
             current_method = None
             new_lines.append(line) # Keep this line
        else:
            # Skip this line (it belongs to the target method)
            pass
    else:
        new_lines.append(line)

# Write result
with open(source_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# Generate Diff
diff = difflib.unified_diff(lines, new_lines, fromfile=source_file, tofile=source_file)
try:
    sys.stdout.writelines(diff)
except:
    pass

import os

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join('static', 'auto_sheets')
print(current_dir)


relative_path = os.path.relpath(data_dir, current_dir)

print(relative_path)
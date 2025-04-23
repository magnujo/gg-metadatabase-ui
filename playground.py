from pathlib import Path
import os
import sys

def find_project_root():
    path = Path(os.getcwd()).resolve()
    while path != path.root:
        if (path / 'very_rootsy_file.txt').exists():
            return path
        path = path.parent
    return None  # Project root not found

project_root = find_project_root()

print(project_root)

import table_merges
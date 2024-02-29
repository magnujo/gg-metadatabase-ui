
import os
example_sheets_path = os.path.join(os.getcwd(), 'static', 'example_sheets_online')
example_sheets = os.listdir(example_sheets_path)

print(example_sheets)

from utils.misc import calculate_text_box_size

text = "Hello, World!"
font_path = "/path/to/font/arial.ttf"  # You can specify the font file path
font_size = 20
width, height = calculate_text_box_size(text, font_path, font_size)
print(f"Text box size: Width={width}, Height={height}")
import os
from constants import misc_constants
from pathlib import Path

s = r"N:\SUN-GI-metadb-test\Field Sample Geo Files\Sample specific files\GOR22AMTEST\Sub Samples\GOR22A_1TEST\Files\Reports\Age-Depth Reports"



def get_first_directory(path, root_path):
    '''
    Gets the first directory in a path from a given root path
    '''
    if path[:len(root_path)] == root_path: # If the first characters of s is equal to the root.
        path = path[len(root_path):]  # Remove the root from s. +1 is to remove the trailing / 
        split = path.split(os.sep)
        return split[1]

paths = [s]
p = set()
root = r"N:\SUN-GI-metadb-test\Field Sample Geo Files\Sample specific files" 

for path in paths:
    p.add(os.path.join(root, get_first_directory(path, root)))

print(p)    


# usag

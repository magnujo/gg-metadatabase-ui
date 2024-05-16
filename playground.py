import os

PATH_TO_MOUNT = os.path.join("/", "mnt")
GEO_DATA_NETWORK_DIR = os.path.join("SUN-GI-metadb-test", "Field Sample Projects")
GEO_DATA_NETWORK_DIR_DELETIONS = os.path.join("SUN-GI-metadb-test", "Deleted (DO NOT TOUCH)")

path_on_server = os.path.join(PATH_TO_MOUNT, GEO_DATA_NETWORK_DIR)
initial_folders = set(os.listdir(r"N:\SUN-GI-metadb-test"))
print(initial_folders)

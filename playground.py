import os
PATH_TO_N_MOUNT = os.path.join("/", "mnt")
GEO_DATA_NETWORK_DIR = "SUN-GI-metadb-test"

path = os.path.join(PATH_TO_N_MOUNT, GEO_DATA_NETWORK_DIR)
location_on_n_drive = f"N:\{str(path).split(str(os.path.sep))[-1]}"

print(PATH_TO_N_MOUNT)

print(os.path.sep)
print(os.path.altsep)
print(os.path.pardir)
print(os.path.extsep)
print(os.path.pathsep)
print(path)
print(location_on_n_drive)
network_drive = "N"
path_to_dir = os.path.join(GEO_DATA_NETWORK_DIR, "test")
print(path_to_dir)

path_on_network = os.path.join(f"{network_drive}:", str(path_to_dir))
test = os.path.join(f"N:\\{GEO_DATA_NETWORK_DIR}","test")
test2 = os.path.join("N",path_to_dir)

print(path_on_network)
print(test)
print(test2)



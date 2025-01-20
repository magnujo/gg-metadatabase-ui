
import os

def create_folders(parent_directory, folder_names):
    # Step 1: Record the initial state of the parent directory
    initial_folders = set(os.listdir(parent_directory))

    # Step 2: Create a list to keep track of newly created folders
    created_folders = []

    try:
        # Step 3: Attempt to create the new folders
        for folder_name in folder_names:
            folder_path = os.path.join(parent_directory, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                created_folders.append(folder_name)
        print("Folders created successfully:", created_folders)
    except Exception as e:
        print("An error occurred:", e)
        # Step 4: Revert by deleting newly created folders
        for folder_name in created_folders:
            folder_path = os.path.join(parent_directory, folder_name)
            if os.path.exists(folder_path):
                os.rmdir(folder_path)  # This will only work if the folder is empty
        print("Reverted the state of the directory")
    finally:
        # Step 5: Check the final state of the parent directory for debugging purposes
        final_folders = set(os.listdir(parent_directory))
        print("Final state of the directory:", final_folders)


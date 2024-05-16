import os
import tempfile
import shutil
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

from utils.create_folders import create_folders

def test_create_folders():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")

        # Define the test case
        folder_names = ['folder1', 'folder2', 'folder3']

        # Pre-create one of the folders to simulate an existing folder
        pre_existing_folder = os.path.join(temp_dir, 'folder2')
        os.makedirs(pre_existing_folder)

        print("Initial state (should contain 'folder2'):", os.listdir(temp_dir))

        # Invoke the function
        create_folders(temp_dir, folder_names)

        # Check the results
        final_state = os.listdir(temp_dir)
        print("Final state after function call:", final_state)

        # Expected result should contain all folder_names, including the pre-existing one
        expected_state = set(folder_names)
        assert set(final_state) == expected_state, f"Expected {expected_state}, but got {set(final_state)}"

        # Simulate an error during folder creation by adding a failing test case
        failing_folder_names = ['folder4', 'folder5']

        def mock_makedirs_fail(path):
            if 'folder5' in path:
                raise Exception("Simulated failure")
            os.makedirs(path)

        # Replace os.makedirs with the mock function that fails
        original_makedirs = os.makedirs
        os.makedirs = mock_makedirs_fail

        try:
            create_folders(temp_dir, failing_folder_names)
        except Exception as e:
            print("Caught an expected exception:", e)

        # Restore the original os.makedirs function
        os.makedirs = original_makedirs

        # Check the results after failure
        final_state_after_failure = os.listdir(temp_dir)
        print("Final state after simulated failure:", final_state_after_failure)

        # The state should be the same as before the failing call
        assert set(final_state_after_failure) == expected_state, f"Expected {expected_state}, but got {set(final_state_after_failure)}"

        print("All tests passed.")

# Run the test
test_create_folders()

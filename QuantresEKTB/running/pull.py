
import subprocess
import sys


def pull_main_branch():
    try:
        # Pull the latest changes from the main branch
        subprocess.run(['git', 'pull'], check=True)
        
        # Print a message indicating the update is complete
        print("Repository has been updated.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    pull_main_branch()
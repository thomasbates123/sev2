import subprocess
def git_push_all(commit_message):
    try:
        # Stage all changes
        subprocess.run(['git', 'add', '--all'], check=True)
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push changes to the remote repository
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("All changes have been pushed to the remote repository.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    commit_message = input("Enter commit message: ")
    git_push_all(commit_message)
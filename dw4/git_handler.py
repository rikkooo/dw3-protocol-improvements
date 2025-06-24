import subprocess
import sys
from pathlib import Path
from dw4.config import LAST_COMMIT_FILE

def get_current_commit_sha():
    """Returns the SHA of the current HEAD commit."""
    return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()

def has_new_commits():
    """Checks if there are new commits since the last recorded SHA."""
    if not LAST_COMMIT_FILE.exists():
        initialize_git_repo()
        save_current_commit_sha()
        return False

    last_commit_sha = LAST_COMMIT_FILE.read_text().strip()
    current_commit_sha = get_current_commit_sha()
    return last_commit_sha != current_commit_sha

def save_current_commit_sha():
    """Saves the current commit SHA to the tracking file."""
    current_commit_sha = get_current_commit_sha()
    LAST_COMMIT_FILE.write_text(current_commit_sha)
    print(f"[GIT] Saved current commit SHA: {current_commit_sha}")

def commit_changes(requirement_id):
    """Adds and commits all changes with a standardized message."""
    print("[GIT] Committing approved code...")
    subprocess.run(["git", "add", "."], check=True)
    
    result = subprocess.run(["git", "diff", "--staged", "--quiet"])
    
    if result.returncode == 0:
        print("[GIT] Working directory is clean. No new commit will be created.")
    else:
        commit_message = f"feat(req-{requirement_id}): Coder stage submission for requirement {requirement_id}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print(f"[GIT] Code committed: {commit_message}")

def push_changes():
    """Pushes all committed changes to the remote repository."""
    print("[GIT] Pushing changes to remote...")
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: Command 'git push' failed.", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return False
    print("[GIT] Push successful.")
    return True

def initialize_git_repo():
    """Initializes a git repository if one doesn't exist."""
    git_dir = Path.cwd() / ".git"
    if not git_dir.exists():
        print("[GIT] This is not a Git repository. Initializing...")
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit: Project setup"], check=True, capture_output=True)
        print("[GIT] Repository initialized and initial commit created.")

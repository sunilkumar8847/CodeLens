# from asyncio import subprocess
import os
import stat
import subprocess
import shutil
import time
from pathlib import Path
from config import REPOS_DIR

def extract_reponame(repo_url: str) -> str:
    url = repo_url.rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    return url.split("/")[-1]

def _force_remove_readonly(func, path, exc_info):
    """Error handler for shutil.rmtree on Windows.
    
    Git marks .git/ files as read-only, which causes rmtree to fail.
    This handler removes the read-only flag and retries the deletion.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _remove_directory(target_dir: Path):
    """Forcefully remove a directory, handling Windows file locks."""
    if not target_dir.exists():
        return

    # Attempt 1: shutil.rmtree with force-remove handler
    try:
        shutil.rmtree(str(target_dir), onerror=_force_remove_readonly)
    except Exception:
        pass

    if not target_dir.exists():
        return

    # Attempt 2: Windows rmdir command as fallback
    try:
        subprocess.run(
            ["cmd", "/c", "rmdir", "/s", "/q", str(target_dir)],
            check=True,
            capture_output=True,
            timeout=30,
        )
    except Exception:
        pass

    if not target_dir.exists():
        return

    # Attempt 3: Wait briefly for file locks to release, then try once more
    time.sleep(1)
    try:
        shutil.rmtree(str(target_dir), onerror=_force_remove_readonly)
    except Exception as e:
        raise RuntimeError(
            f"Cannot remove existing repo directory '{target_dir}'. "
            f"Close any programs using files in that folder and try again. Error: {e}"
        )

def clone_repo(repo_url: str) -> Path:
    repo_name = extract_reponame(repo_url)
    target_dir = REPOS_DIR/repo_name

    _remove_directory(target_dir)

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to clone repository: {e.stderr}") from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("Repository clone timed out (>120 seconds)")

    return target_dir
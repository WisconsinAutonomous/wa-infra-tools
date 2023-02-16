import subprocess
import re
import os
from tqdm import tqdm

def clone(git_url, branch=None, repo_dir=None):
    os.environ["GIT_LFS_SKIP_SMUDGE"] = "1"
    if repo_dir is None:
        repo_dir = re.split(r"/|\.", git_url)[-2]
    commands = ["git", "clone", git_url, "-o", repo_dir]
    if branch is not None:
        commands += ["-b", branch]
    subprocess.run(commands)
    os.environ["GIT_LFS_SKIP_SMUDGE"] = "0"

def pull(repo_dir, capture_output=True):
    cwd = os.getcwd()
    os.chdir(repo_dir)
    subprocess.run(["git", "pull"], capture_output=capture_output)
    os.chdir(cwd)

def add(repo_dir, items=None, capture_output=True):
    cwd = os.getcwd()
    os.chdir(repo_dir)
    if items is None:
        subprocess.run(["git", "add", "-A"], capture_output=capture_output)
    else:
        subprocess.run(["git", "add"] + items, capture_output=capture_output)
    os.chdir(cwd)

def commit(repo_dir, message, capture_output=True):
    cwd = os.getcwd()
    os.chdir(repo_dir)
    subprocess.run(["git", "commit", "-m", message], capture_output=capture_output)
    os.chdir(cwd)

def push(repo_dir, set_upstream=False, capture_output=True):
    cwd = os.getcwd()
    os.chdir(repo_dir)
    if set_upstream:
        subprocess.run(["git", "push", "-u"], capture_output=capture_output)
    else:
        subprocess.run(["git", "push"], capture_output=capture_output)
    os.chdir(cwd)

def lfs_pull(repo_dir, includes="", excludes="", capture_output=True):
    cwd = os.getcwd()
    os.chdir(repo_dir)
    subprocess.run(["git", "lfs", "pull", f"-I {includes}", f"-X {excludes}"], capture_output=capture_output)
    os.chdir(cwd)

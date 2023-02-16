from wa_infra_tools import git_utils
import argparse
import os

def parse_args():
    parent_parser = argparse.ArgumentParser(description="wa_git entry point")
    subparsers = parent_parser.add_subparsers(title="commands")
    cwd = os.getcwd()
    
    # clone
    clone_parser = subparsers.add_parser(
            "clone", 
            description="wa_git clone parser",
            help="clone a git repo without copying full LFS files (only pointers)")
    
    clone_parser.add_argument("git_url", type=str, help="git url of repo to clone")
    clone_parser.add_argument("-b", "--branch", type=str, help="branch to check out (default: remote repo's default branch)")
    clone_parser.add_argument("-o", "--output", type=str, help="where to clone the directory (default: repo name)")
    clone_parser.set_defaults(func=lambda args: git_utils.clone(args.git_url, args.branch, args.output, False))

    # pull
    pull_parser = subparsers.add_parser(
            "pull",
            description="wa_git pull parser",
            help="pulls latest LFS pointers and normal files into the repo")
    pull_parser.set_defaults(func=lambda args: git_utils.pull(cwd, False))

    # add 
    add_parser = subparsers.add_parser(
            "add",
            description="wa_git add parser",
            help="adds selected changes to git repo")

    add_parser.add_argument("items", nargs="*", help="list of directories/files to add")
    add_parser.add_argument("-A", "--all", action="store_true", help="add all changes")
    add_parser.set_defaults(func=lambda args: git_utils.add(cwd) if args.all else git_utils.add(cwd, args.items, False))

    # commit
    commit_parser = subparsers.add_parser(
            "commit",
            description="wa_git commit parser",
            help="commits changes to git repo with message")

    commit_parser.add_argument("-m", "--message", type=str, required=True, help="commit message")
    commit_parser.set_defaults(func=lambda args: git_utils.commit(cwd, args.message, False))

    # push
    push_parser = subparsers.add_parser(
            "push",
            description="wa_git push parser",
            help="pushes committed changes to remote repo")
    push_parser.add_argument("-u", "--set-upstream", action="store_true", help="set upstream branch")
    push_parser.set_defaults(func=lambda args: git_utils.push(cwd, args.set_upstream, False))

    # lfs-pull
    lfs_pull_parser = subparsers.add_parser(
            "lfs-pull",
            description="wa_git lfs-pull parser",
            help="pulls latest LFS files")

    lfs_pull_parser.add_argument("-I", "--include", type=str, default="", help="directories to include in the lfs pull")
    lfs_pull_parser.add_argument("-X", "--exclude", type=str, default="", help="directories to exclude in the lfs pull")
    lfs_pull_parser.set_defaults(func=lambda args: git_utils.lfs_pull(cwd, args.include, args.exclude, False))

    args = parent_parser.parse_args()
    return args

def main():
    args = parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

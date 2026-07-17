#!/usr/bin/env python3
"""
git_automation.py
------------------------
Commits, pushes, and pulls changes in a Git repository using GitPython —
a Python wrapper around the git command-line tool.

Requires: pip install GitPython
Requires: git installed on your system, and the target directory must
          already be a git repository (or use 'clone' to create one).

Usage:
    python git_automation.py status <repo_path>
    python git_automation.py commit <repo_path> <"commit message"> [--add-all]
    python git_automation.py push <repo_path> [--remote origin] [--branch main]
    python git_automation.py pull <repo_path> [--remote origin] [--branch main]
    python git_automation.py clone <repo_url> <destination_path>
    python git_automation.py log <repo_path> [--count 10]

Example:
    python git_automation.py status ./myproject
    python git_automation.py commit ./myproject "Fix login bug" --add-all
    python git_automation.py push ./myproject
    python git_automation.py pull ./myproject
    python git_automation.py clone https://github.com/user/repo.git ./repo
"""

import argparse
import sys

try:
    import git
    from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
except ImportError:
    print("Error: the 'GitPython' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def open_repo(repo_path: str):
    try:
        return git.Repo(repo_path)
    except InvalidGitRepositoryError:
        print(f"Error: '{repo_path}' is not a valid git repository.")
        sys.exit(1)
    except NoSuchPathError:
        print(f"Error: path '{repo_path}' does not exist.")
        sys.exit(1)


def show_status(repo_path: str) -> None:
    repo = open_repo(repo_path)

    print(f"Repository: {repo_path}")
    try:
        print(f"Current branch: {repo.active_branch.name}")
    except TypeError:
        print("Current branch: (detached HEAD)")
    print(f"Is dirty (uncommitted changes): {repo.is_dirty(untracked_files=True)}\n")

    has_commits = repo.head.is_valid()

    if has_commits and repo.is_dirty():
        print("Modified files:")
        for item in repo.index.diff(None):
            print(f"  M  {item.a_path}")

    if has_commits:
        staged = repo.index.diff("HEAD")
        if staged:
            print("Staged files:")
            for item in staged:
                print(f"  A  {item.a_path}")
    else:
        staged_paths = list(repo.index.entries.keys())
        if staged_paths:
            print("Staged files (initial commit pending):")
            for path, _ in staged_paths:
                print(f"  A  {path}")

    if repo.untracked_files:
        print("Untracked files:")
        for f in repo.untracked_files:
            print(f"  ?  {f}")

    if not repo.is_dirty(untracked_files=True):
        print("Working tree clean.")


def commit_changes(repo_path: str, message: str, add_all: bool) -> None:
    repo = open_repo(repo_path)

    if add_all:
        repo.git.add(A=True)
        print("Staged all changes (git add -A).")

    has_staged_changes = bool(repo.index.entries) if not repo.head.is_valid() else bool(repo.index.diff("HEAD"))

    if not has_staged_changes:
        print("Nothing staged to commit. Use --add-all to stage all changes first.")
        sys.exit(1)

    try:
        commit = repo.index.commit(message)
        print(f"Committed: {commit.hexsha[:8]} - \"{message}\"")
    except GitCommandError as e:
        print(f"Error committing: {e}")
        sys.exit(1)


def push_changes(repo_path: str, remote_name: str, branch: str) -> None:
    repo = open_repo(repo_path)

    try:
        remote = repo.remote(remote_name)
    except ValueError:
        print(f"Error: remote '{remote_name}' not found.")
        sys.exit(1)

    branch_name = branch or repo.active_branch.name

    print(f"Pushing '{branch_name}' to '{remote_name}'...")
    try:
        info_list = remote.push(refspec=f"{branch_name}:{branch_name}")
        for info in info_list:
            print(f"Push result: {info.summary.strip()}")
        print("Push complete.")
    except GitCommandError as e:
        print(f"Error pushing: {e}")
        sys.exit(1)


def pull_changes(repo_path: str, remote_name: str, branch: str) -> None:
    repo = open_repo(repo_path)

    try:
        remote = repo.remote(remote_name)
    except ValueError:
        print(f"Error: remote '{remote_name}' not found.")
        sys.exit(1)

    branch_name = branch or repo.active_branch.name

    print(f"Pulling '{branch_name}' from '{remote_name}'...")
    try:
        info_list = remote.pull(branch_name)
        for info in info_list:
            print(f"Pull result: {info.note or info.ref}")
        print("Pull complete.")
    except GitCommandError as e:
        print(f"Error pulling: {e}")
        sys.exit(1)


def clone_repo(repo_url: str, destination: str) -> None:
    print(f"Cloning '{repo_url}' into '{destination}'...")
    try:
        git.Repo.clone_from(repo_url, destination)
        print("Clone complete.")
    except GitCommandError as e:
        print(f"Error cloning repository: {e}")
        sys.exit(1)


def show_log(repo_path: str, count: int) -> None:
    repo = open_repo(repo_path)

    if not repo.head.is_valid():
        print("No commits found (repository has no commits yet).")
        return

    commits = list(repo.iter_commits(max_count=count))

    if not commits:
        print("No commits found.")
        return

    print(f"Last {len(commits)} commit(s):\n")
    for c in commits:
        print(f"{c.hexsha[:8]}  {c.committed_datetime.strftime('%Y-%m-%d %H:%M')}  {c.author.name:<20} {c.summary}")


def main():
    parser = argparse.ArgumentParser(description="Commit, push, pull, and inspect a git repo via GitPython.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("status", help="Show repository status")
    p.add_argument("repo_path", help="Path to the git repository")

    p = subparsers.add_parser("commit", help="Commit changes")
    p.add_argument("repo_path", help="Path to the git repository")
    p.add_argument("message", help="Commit message")
    p.add_argument("--add-all", action="store_true", help="Stage all changes before committing (git add -A)")

    p = subparsers.add_parser("push", help="Push commits to a remote")
    p.add_argument("repo_path", help="Path to the git repository")
    p.add_argument("--remote", default="origin", help="Remote name (default: origin)")
    p.add_argument("--branch", default=None, help="Branch name (default: current branch)")

    p = subparsers.add_parser("pull", help="Pull changes from a remote")
    p.add_argument("repo_path", help="Path to the git repository")
    p.add_argument("--remote", default="origin", help="Remote name (default: origin)")
    p.add_argument("--branch", default=None, help="Branch name (default: current branch)")

    p = subparsers.add_parser("clone", help="Clone a remote repository")
    p.add_argument("repo_url", help="URL of the repository to clone")
    p.add_argument("destination_path", help="Local destination directory")

    p = subparsers.add_parser("log", help="Show recent commit history")
    p.add_argument("repo_path", help="Path to the git repository")
    p.add_argument("--count", type=int, default=10, help="Number of commits to show (default: 10)")

    args = parser.parse_args()

    if args.action == "status":
        show_status(args.repo_path)
    elif args.action == "commit":
        commit_changes(args.repo_path, args.message, args.add_all)
    elif args.action == "push":
        push_changes(args.repo_path, args.remote, args.branch)
    elif args.action == "pull":
        pull_changes(args.repo_path, args.remote, args.branch)
    elif args.action == "clone":
        clone_repo(args.repo_url, args.destination_path)
    elif args.action == "log":
        show_log(args.repo_path, args.count)


if __name__ == "__main__":
    main()

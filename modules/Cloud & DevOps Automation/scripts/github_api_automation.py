#!/usr/bin/env python3
"""
github_api_automation.py
-------------------------------
Manages GitHub pull requests, releases, and repositories using PyGithub,
a Python wrapper around the GitHub REST API.

Requires: pip install PyGithub
Requires: a GitHub Personal Access Token (create one at
          https://github.com/settings/tokens with 'repo' scope),
          passed via --token or the GITHUB_TOKEN environment variable.

Usage:
    python github_api_automation.py list-prs <owner/repo> [--state open]
    python github_api_automation.py create-pr <owner/repo> <title> <head_branch> <base_branch> [--body "description"]
    python github_api_automation.py merge-pr <owner/repo> <pr_number>
    python github_api_automation.py list-releases <owner/repo>
    python github_api_automation.py create-release <owner/repo> <tag_name> <title> [--body "notes"]
    python github_api_automation.py repo-info <owner/repo>

Example:
    export GITHUB_TOKEN=ghp_yourtokenhere
    python github_api_automation.py list-prs octocat/Hello-World
    python github_api_automation.py create-pr myorg/myrepo "Add feature X" feature-branch main --body "Implements X"
    python github_api_automation.py create-release myorg/myrepo v1.2.0 "Version 1.2.0" --body "Bug fixes"
"""

import argparse
import os
import sys

try:
    from github import Github, Auth
    from github.GithubException import GithubException, BadCredentialsException
except ImportError:
    print("Error: the 'PyGithub' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def get_client(token: str) -> Github:
    token = token or os.environ.get("GITHUB_TOKEN")

    if not token:
        print("Error: no GitHub token provided.")
        print("Pass --token or set the GITHUB_TOKEN environment variable.")
        print("Create a token at: https://github.com/settings/tokens")
        sys.exit(1)

    return Github(auth=Auth.Token(token))


def handle_github_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BadCredentialsException:
            print("Error: invalid GitHub token.")
            sys.exit(1)
        except GithubException as e:
            print(f"GitHub API error ({e.status}): {e.data.get('message', str(e))}")
            sys.exit(1)
    return wrapper


@handle_github_errors
def list_prs(gh: Github, repo_name: str, state: str) -> None:
    repo = gh.get_repo(repo_name)
    prs = repo.get_pulls(state=state)

    pr_list = list(prs)
    if not pr_list:
        print(f"No {state} pull requests found in '{repo_name}'.")
        return

    print(f"{state.capitalize()} pull requests in '{repo_name}' ({len(pr_list)}):\n")
    for pr in pr_list:
        print(f"#{pr.number:<5} {pr.title:<50} by {pr.user.login} ({pr.head.ref} -> {pr.base.ref})")


@handle_github_errors
def create_pr(gh: Github, repo_name: str, title: str, head: str, base: str, body: str) -> None:
    repo = gh.get_repo(repo_name)
    pr = repo.create_pull(title=title, body=body or "", head=head, base=base)
    print(f"Pull request created: #{pr.number} - {pr.title}")
    print(f"URL: {pr.html_url}")


@handle_github_errors
def merge_pr(gh: Github, repo_name: str, pr_number: int) -> None:
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    if pr.merged:
        print(f"PR #{pr_number} is already merged.")
        return

    if not pr.mergeable:
        print(f"Error: PR #{pr_number} is not currently mergeable (conflicts or checks pending).")
        sys.exit(1)

    result = pr.merge()
    if result.merged:
        print(f"PR #{pr_number} merged successfully.")
    else:
        print(f"Error: merge failed - {result.message}")
        sys.exit(1)


@handle_github_errors
def list_releases(gh: Github, repo_name: str) -> None:
    repo = gh.get_repo(repo_name)
    releases = list(repo.get_releases())

    if not releases:
        print(f"No releases found in '{repo_name}'.")
        return

    print(f"Releases in '{repo_name}' ({len(releases)}):\n")
    for r in releases:
        print(f"{r.tag_name:<15} {r.title:<40} published: {r.published_at}")


@handle_github_errors
def create_release(gh: Github, repo_name: str, tag_name: str, title: str, body: str) -> None:
    repo = gh.get_repo(repo_name)
    release = repo.create_git_release(tag=tag_name, name=title, message=body or "")
    print(f"Release created: {release.tag_name} - {release.title}")
    print(f"URL: {release.html_url}")


@handle_github_errors
def repo_info(gh: Github, repo_name: str) -> None:
    repo = gh.get_repo(repo_name)

    print(f"Repository: {repo.full_name}")
    print(f"Description: {repo.description or '(none)'}")
    print(f"Stars: {repo.stargazers_count}")
    print(f"Forks: {repo.forks_count}")
    print(f"Open issues: {repo.open_issues_count}")
    print(f"Default branch: {repo.default_branch}")
    print(f"Language: {repo.language}")
    print(f"URL: {repo.html_url}")


def main():
    parser = argparse.ArgumentParser(description="Manage GitHub PRs, releases, and repos via PyGithub.")
    parser.add_argument("--token", default=None, help="GitHub personal access token (or set GITHUB_TOKEN)")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("list-prs", help="List pull requests")
    p.add_argument("repo_name", help="Repository in owner/repo format")
    p.add_argument("--state", default="open", choices=["open", "closed", "all"], help="PR state filter (default: open)")

    p = subparsers.add_parser("create-pr", help="Create a pull request")
    p.add_argument("repo_name", help="Repository in owner/repo format")
    p.add_argument("title", help="PR title")
    p.add_argument("head_branch", help="Source branch")
    p.add_argument("base_branch", help="Target branch")
    p.add_argument("--body", default="", help="PR description")

    p = subparsers.add_parser("merge-pr", help="Merge a pull request")
    p.add_argument("repo_name", help="Repository in owner/repo format")
    p.add_argument("pr_number", type=int, help="PR number to merge")

    p = subparsers.add_parser("list-releases", help="List releases")
    p.add_argument("repo_name", help="Repository in owner/repo format")

    p = subparsers.add_parser("create-release", help="Create a new release")
    p.add_argument("repo_name", help="Repository in owner/repo format")
    p.add_argument("tag_name", help="Tag name, e.g. v1.2.0")
    p.add_argument("title", help="Release title")
    p.add_argument("--body", default="", help="Release notes")

    p = subparsers.add_parser("repo-info", help="Show repository info")
    p.add_argument("repo_name", help="Repository in owner/repo format")

    args = parser.parse_args()
    gh = get_client(args.token)

    if args.action == "list-prs":
        list_prs(gh, args.repo_name, args.state)
    elif args.action == "create-pr":
        create_pr(gh, args.repo_name, args.title, args.head_branch, args.base_branch, args.body)
    elif args.action == "merge-pr":
        merge_pr(gh, args.repo_name, args.pr_number)
    elif args.action == "list-releases":
        list_releases(gh, args.repo_name)
    elif args.action == "create-release":
        create_release(gh, args.repo_name, args.tag_name, args.title, args.body)
    elif args.action == "repo-info":
        repo_info(gh, args.repo_name)


if __name__ == "__main__":
    main()

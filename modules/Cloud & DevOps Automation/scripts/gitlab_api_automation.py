#!/usr/bin/env python3
"""
gitlab_api_automation.py
-------------------------------
Controls GitLab CI pipelines and merge requests using python-gitlab,
a Python wrapper around the GitLab REST API.

Requires: pip install python-gitlab
Requires: a GitLab Personal Access Token (create one at
          https://gitlab.com/-/user_settings/personal_access_tokens with
          'api' scope), passed via --token or the GITLAB_TOKEN environment
          variable.

Usage:
    python gitlab_api_automation.py list-mrs <project_id> [--state opened]
    python gitlab_api_automation.py create-mr <project_id> <title> <source_branch> <target_branch> [--description "text"]
    python gitlab_api_automation.py merge-mr <project_id> <mr_iid>
    python gitlab_api_automation.py list-pipelines <project_id> [--limit 10]
    python gitlab_api_automation.py trigger-pipeline <project_id> <ref> [--variables "KEY=VALUE,KEY2=VALUE2"]
    python gitlab_api_automation.py pipeline-status <project_id> <pipeline_id>

Example:
    export GITLAB_TOKEN=glpat-yourtokenhere
    python gitlab_api_automation.py list-mrs 12345678
    python gitlab_api_automation.py trigger-pipeline 12345678 main
    python gitlab_api_automation.py pipeline-status 12345678 987654321

Note: <project_id> can be the numeric project ID or the URL-encoded path
      (e.g. 'mygroup%2Fmyproject').
"""

import argparse
import os
import sys

try:
    import gitlab
    from gitlab.exceptions import GitlabAuthenticationError, GitlabError
except ImportError:
    print("Error: the 'python-gitlab' package is required.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)


def get_client(token: str, url: str) -> "gitlab.Gitlab":
    token = token or os.environ.get("GITLAB_TOKEN")

    if not token:
        print("Error: no GitLab token provided.")
        print("Pass --token or set the GITLAB_TOKEN environment variable.")
        print("Create a token at: https://gitlab.com/-/user_settings/personal_access_tokens")
        sys.exit(1)

    gl = gitlab.Gitlab(url, private_token=token)

    try:
        gl.auth()
    except GitlabAuthenticationError:
        print("Error: invalid GitLab token.")
        sys.exit(1)

    return gl


def handle_gitlab_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GitlabError as e:
            print(f"GitLab API error: {e}")
            sys.exit(1)
    return wrapper


@handle_gitlab_errors
def list_mrs(gl, project_id: str, state: str) -> None:
    project = gl.projects.get(project_id)
    mrs = project.mergerequests.list(state=state, all=True)

    if not mrs:
        print(f"No {state} merge requests found in project '{project_id}'.")
        return

    print(f"{state.capitalize()} merge requests in project '{project_id}' ({len(mrs)}):\n")
    for mr in mrs:
        print(f"!{mr.iid:<5} {mr.title:<50} ({mr.source_branch} -> {mr.target_branch})")


@handle_gitlab_errors
def create_mr(gl, project_id: str, title: str, source: str, target: str, description: str) -> None:
    project = gl.projects.get(project_id)
    mr = project.mergerequests.create({
        "source_branch": source,
        "target_branch": target,
        "title": title,
        "description": description or "",
    })
    print(f"Merge request created: !{mr.iid} - {mr.title}")
    print(f"URL: {mr.web_url}")


@handle_gitlab_errors
def merge_mr(gl, project_id: str, mr_iid: int) -> None:
    project = gl.projects.get(project_id)
    mr = project.mergerequests.get(mr_iid)

    if mr.state == "merged":
        print(f"MR !{mr_iid} is already merged.")
        return

    mr.merge()
    print(f"MR !{mr_iid} merged successfully.")


@handle_gitlab_errors
def list_pipelines(gl, project_id: str, limit: int) -> None:
    project = gl.projects.get(project_id)
    pipelines = project.pipelines.list(per_page=limit)

    if not pipelines:
        print(f"No pipelines found in project '{project_id}'.")
        return

    print(f"Recent pipelines in project '{project_id}' ({len(pipelines)}):\n")
    for p in pipelines:
        print(f"ID: {p.id:<12} Status: {p.status:<10} Ref: {p.ref:<20} Created: {p.created_at}")


@handle_gitlab_errors
def trigger_pipeline(gl, project_id: str, ref: str, variables: str) -> None:
    project = gl.projects.get(project_id)

    var_dict = {}
    if variables:
        for pair in variables.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                var_dict[key.strip()] = value.strip()

    pipeline = project.pipelines.create({"ref": ref, "variables": [{"key": k, "value": v} for k, v in var_dict.items()]})
    print(f"Pipeline triggered: ID {pipeline.id} on ref '{ref}'")
    print(f"Status: {pipeline.status}")
    print(f"URL: {pipeline.web_url}")


@handle_gitlab_errors
def pipeline_status(gl, project_id: str, pipeline_id: int) -> None:
    project = gl.projects.get(project_id)
    pipeline = project.pipelines.get(pipeline_id)

    print(f"Pipeline ID:  {pipeline.id}")
    print(f"Status:       {pipeline.status}")
    print(f"Ref:          {pipeline.ref}")
    print(f"SHA:          {pipeline.sha}")
    print(f"Created:      {pipeline.created_at}")
    print(f"Updated:      {pipeline.updated_at}")
    print(f"URL:          {pipeline.web_url}")


def main():
    parser = argparse.ArgumentParser(description="Manage GitLab merge requests and pipelines via python-gitlab.")
    parser.add_argument("--token", default=None, help="GitLab personal access token (or set GITLAB_TOKEN)")
    parser.add_argument("--url", default="https://gitlab.com", help="GitLab instance URL (default: https://gitlab.com)")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p = subparsers.add_parser("list-mrs", help="List merge requests")
    p.add_argument("project_id", help="Numeric project ID or URL-encoded path")
    p.add_argument("--state", default="opened", choices=["opened", "closed", "merged", "all"], help="MR state filter")

    p = subparsers.add_parser("create-mr", help="Create a merge request")
    p.add_argument("project_id", help="Numeric project ID or URL-encoded path")
    p.add_argument("title", help="MR title")
    p.add_argument("source_branch", help="Source branch")
    p.add_argument("target_branch", help="Target branch")
    p.add_argument("--description", default="", help="MR description")

    p = subparsers.add_parser("merge-mr", help="Merge a merge request")
    p.add_argument("project_id", help="Numeric project ID or URL-encoded path")
    p.add_argument("mr_iid", type=int, help="Merge request IID")

    p = subparsers.add_parser("list-pipelines", help="List recent pipelines")
    p.add_argument("project_id", help="Numeric project ID or URL-encoded path")
    p.add_argument("--limit", type=int, default=10, help="Number of pipelines to show (default: 10)")

    p = subparsers.add_parser("trigger-pipeline", help="Trigger a new pipeline")
    p.add_argument("project_id", help="Numeric project ID or URL-encoded path")
    p.add_argument("ref", help="Branch or tag to run the pipeline on")
    p.add_argument("--variables", default=None, help="Comma-separated KEY=VALUE pairs")

    p = subparsers.add_parser("pipeline-status", help="Show status of a specific pipeline")
    p.add_argument("project_id", help="Numeric project ID or URL-encoded path")
    p.add_argument("pipeline_id", type=int, help="Pipeline ID")

    args = parser.parse_args()
    gl = get_client(args.token, args.url)

    if args.action == "list-mrs":
        list_mrs(gl, args.project_id, args.state)
    elif args.action == "create-mr":
        create_mr(gl, args.project_id, args.title, args.source_branch, args.target_branch, args.description)
    elif args.action == "merge-mr":
        merge_mr(gl, args.project_id, args.mr_iid)
    elif args.action == "list-pipelines":
        list_pipelines(gl, args.project_id, args.limit)
    elif args.action == "trigger-pipeline":
        trigger_pipeline(gl, args.project_id, args.ref, args.variables)
    elif args.action == "pipeline-status":
        pipeline_status(gl, args.project_id, args.pipeline_id)


if __name__ == "__main__":
    main()

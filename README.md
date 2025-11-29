# AI Agents for Software Development

This repository contains reusable GitHub Actions workflows that act as AI agents to assist in software development tasks, such as drafting initial solutions and revising pull requests.

## Setup

To use these agents, you will need to set up the following secrets in your GitHub repository or organization:

*   `GITHUB_TOKEN`: A GitHub personal access token with appropriate permissions (e.g., `contents: write`, `issues: write`, `pull_requests: write`) for the agents to create/update files, issues, and PRs.
*   `GEMINI_API_KEY`: Your API key for the Gemini model. This is required for both the Draft and Revise agents to interact with the AI.

## Draft Agent (`draft-agent.yml`)

This agent drafts an initial solution based on a new issue.

### Inputs:

*   `issue_title`: Title of the GitHub issue.
*   `issue_body`: Body of the GitHub issue.

### Secrets:

*   `GITHUB_TOKEN`: Required for interacting with GitHub API.
*   `GEMINI_API_KEY`: Your API key for the Gemini model.

### Example Trigger Workflow (`.github/workflows/trigger-draft.yml`):

```yaml
name: Draft Solution on Command

on:
  issues:
    types: [opened, reopened]

jobs:
  draft_solution:
    permissions:
      contents: write        # Required if the agent creates/updates files
      issues: read           # Required if the agent creates comments/labels on issues
      pull-requests: write   # Required if the agent creates PRs
    steps:
      - name: Draft Solution
        uses: kakonawao/ai-actions/.github/workflows/draft-agent.yml@main
        with:
          issue_title: ${{ github.event.issue.title }}
          issue_body: ${{ github.event.issue.body }}
        secrets:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

## Revise Agent (`revise-agent.yml`)

This agent revises a pull request based on review comments or other triggers.

### Inputs:

*   `pr_number`: The pull request number.

### Secrets:

*   `GITHUB_TOKEN`: Required for interacting with GitHub API.
*   `GEMINI_API_KEY`: Your API key for the Gemini model.

### Example Trigger Workflow (`.github/workflows/trigger-revise.yml`):

```yaml
on:
  pull_request_review:
    types: [submitted]
  issue_comment: # Often revisions are also triggered by comments (e.g., /revise command)
    types: [created]

jobs:
  revise_pr:
    if: |
      github.event_name == 'pull_request_review' && (github.event.review.state == 'commented' || github.event.review.state == 'changes_requested') ||
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '/revise'))
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: Revise Pull Request
        uses: kakonawao/ai-actions/.github/workflows/revise-agent.yml@main
        with:
          pr_number: ${{ github.event.issue.pull_request.number || github.event.pull_request.number }} # Handle both issue_comment (pr_number under issue.pull_request) and pull_request_review (pr_number under pull_request)
        secrets:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

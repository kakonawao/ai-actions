# AI Agents for Software Development

This repository contains reusable GitHub Actions workflows that act as AI agents to assist in software development tasks, such as drafting initial solutions and revising pull requests.

## Setup

To use these agents, you will need to set up the following secrets in your GitHub repository or organization:

*   `GITHUB_TOKEN`: A GitHub personal access token with appropriate permissions (e.g., `contents: write`, `issues: write`, `pull_requests: write`) for the agents to create/update files, issues, and PRs.
*   `GEMINI_API_KEY`: Your API key for the Gemini model. This is required for both the Draft and Revise agents to interact with the AI.

## Draft Agent (`draft-pr.yml`)

This agent drafts an initial solution based on a new issue.

### Inputs:

*   `issue_number`: The number of the issue to draft a solution for.
*   `issue_title`: Title of the GitHub issue.
*   `issue_body`: Body of the GitHub issue.

### Secrets:

*   `GITHUB_TOKEN`: Required for interacting with GitHub API.
*   `GEMINI_API_KEY`: Your API key for the Gemini model.

### Example Trigger Workflow (`.github/workflows/trigger-draft.yml`):

```yaml
name: Trigger Draft PR

on:
  issues:
    types: [opened, reopened]

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  call-draft-pr:
    uses: ./.github/workflows/draft-pr.yml
    with:
      issue_number: ${{ github.event.issue.number }}
      issue_title: ${{ github.event.issue.title }}
      issue_body: ${{ github.event.issue.body }}
    secrets:
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

## Revise Agent (`revise-pr.yml`)

This agent revises a pull request based on review comments or other triggers.

### Inputs:

*   `pr_number`: The pull request number.
*   `branch`: The branch to checkout.

### Secrets:

*   `GITHUB_TOKEN`: Required for interacting with GitHub API.
*   `GEMINI_API_KEY`: Your API key for the Gemini model.

### Example Trigger Workflow (`.github/workflows/trigger-revise.yml`):

```yaml
name: Trigger Revise PR

on:
  pull_request_review:
    types: [submitted]

permissions:
  contents: write
  pull-requests: write

jobs:
  call-revise-pr:
    if: contains(github.event.review.body, '/revise')
    uses: ./.github/workflows/revise-pr.yml
    with:
      pr_number: ${{ github.event.pull_request.number }}
      branch: ${{ github.event.pull_request.head.ref }}
    secrets:
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

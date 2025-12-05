# AI Actions

This repository contains reusable GitHub Actions workflows that act as AI agents to automate various development tasks.

## Summary of Changes

This update includes several improvements and clarifications:

*   **Renamed Repository Title**: Changed from "AI Agents for Software Development" to "AI Actions" for better clarity.
*   **GitHub Token Clarification**: Clarified that `GITHUB_TOKEN` is automatically provided by GitHub Actions, with guidance on using a Personal Access Token (PAT) if different permissions are required.
*   **Simplified Secret Management**: Removed explicit `GITHUB_TOKEN` from individual agent secret lists, as it's generally handled automatically.
*   **Updated Workflow Triggers**: Revised example trigger workflows to use local workflow calls (`uses: ./.github/workflows/`).
*   **Draft Agent Enhancements**: Added `issue_number` as an input for the Draft Agent.
*   **Revise Agent Refinements**: Simplified the Revise Agent trigger to specifically respond to pull request review comments containing `/revise` and introduced a `branch` input for better control.

## Setup

To use these agents, you will need to set up the following secrets in your GitHub repository or organization:

*   `GEMINI_API_KEY`: Your API key for the Gemini model. This is required for both the Draft and Revise agents to interact with the AI.

The `GITHUB_TOKEN` is automatically provided by GitHub Actions with appropriate permissions for the agents to create/update files, issues, and PRs. If you need to use a Personal Access Token (PAT) with different permissions, you can set it as a repository secret (e.g., `MY_GITHUB_TOKEN`) and pass it to the workflows.

## Draft Agent (`draft-agent.yml`)

This agent drafts an initial solution based on a new issue.

### Inputs:

*   `issue_number`: The number of the GitHub issue.
*   `issue_title`: Title of the GitHub issue.
*   `issue_body`: Body of the GitHub issue.

### Secrets:

*   `GEMINI_API_KEY`: Your API key for the Gemini model.

### Example Trigger Workflow (`.github/workflows/trigger-draft.yml`):

```yaml
name: Trigger Draft Agent

on:
  issues:
    types: [opened, reopened]

jobs:
  call-draft-agent:
    uses: ./.github/workflows/draft-agent.yml
    with:
      issue_number: ${{ github.event.issue.number }}
      issue_title: ${{ github.event.issue.title }}
      issue_body: ${{ github.event.issue.body }}
    secrets:
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

## Revise Agent (`revise-agent.yml`)

This agent revises a pull request based on a review comment containing `/revise`.

### Inputs:

*   `pr_number`: The pull request number.
*   `branch`: The branch of the pull request to checkout and revise.

### Secrets:

*   `GEMINI_API_KEY`: Your API key for the Gemini model.

### Example Trigger Workflow (`.github/workflows/trigger-revise.yml`):

```yaml
name: Trigger Revise Agent

on:
  pull_request_review:
    types: [submitted]

jobs:
  call-revise-agent:
    if: contains(github.event.review.body, '/revise')
    uses: ./.github/workflows/revise-agent.yml
    with:
      pr_number: ${{ github.event.pull_request.number }}
      branch: ${{ github.event.pull_request.head.ref }}
    secrets:
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```
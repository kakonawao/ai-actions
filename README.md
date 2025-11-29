# AI Agent Workflows

This repository contains reusable GitHub Actions workflows for AI-powered software development tasks.

## Reusable Workflows

You can integrate the `draft-agent` and `revise-agent` workflows into your own repositories to automate drafting and revising code.

### Using the Workflows

To use a reusable workflow, you create a new workflow file in your repository (e.g., `.github/workflows/call-draft-agent.yml`) and reference the workflow from this repository using the `uses:` keyword.

The general format is:
`uses: owner/repository/.github/workflows/workflow-file.yml@ref`

Replace `owner/repository` with the path to this repository and `ref` with a specific branch, tag, or commit SHA (e.g., `main` or `v1.0.0`).

---

### Draft Agent (`draft-agent.yml`)

This workflow is designed to read a GitHub issue and draft a potential solution based on its content. It will typically create a new branch and open a pull request with the drafted files.

**Inputs:**
*   `issue_number`: (Required) The number of the issue to draft a solution for.
*   `repository_context`: (Required) The `owner/repo` string for the repository containing the issue.

**Secrets:**
*   `token`: (Required) A GitHub token with permissions to read issues, write contents, and create pull requests. `secrets.GITHUB_TOKEN` is usually sufficient if the calling workflow has the necessary permissions.

**Example Trigger Workflow:**

You can trigger this workflow by commenting `/draft` on an issue in your repository. Save the following code in your repository as `.github/workflows/draft-solution.yml`.

yaml
name: Draft Solution on Command

on:
  issue_comment:
    types: [created]

jobs:
  draft_solution_job:
    # Run only for comments on issues (not PRs) that contain '/draft'
    if: github.event.issue.pull_request == null && contains(github.event.comment.body, '/draft')
    runs-on: ubuntu-latest
    # Permissions needed by the calling workflow to pass to the reusable workflow
    permissions:
      contents: write
      pull-requests: write
      issues: read

    steps:
      - name: Call Draft Agent Workflow
        uses: owner/repository/.github/workflows/draft-agent.yml@main
        with:
          issue_number: ${{ github.event.issue.number }}
          repository_context: ${{ github.repository }}
        secrets:
          token: ${{ secrets.GITHUB_TOKEN }}


---

### Revise Agent (`revise-agent.yml`)

This workflow revises an existing pull request based on feedback or instructions provided in a review. It will commit changes directly to the pull request's branch.

**Inputs:**
*   `pull_request_number`: (Required) The number of the pull request to revise.
*   `revision_instructions`: (Required) The text containing the instructions for the revision (e.g., the content of the triggering review comment).

**Secrets:**
*   `token`: (Required) A GitHub token with permissions to read pull requests and write contents.

**Example Trigger Workflow:**

You can trigger this workflow by submitting a pull request review that contains `/revise` followed by your instructions. Save the following code in your repository as `.github/workflows/revise-pr.yml`.

yaml
name: Revise PR on Command

on:
  pull_request_review:
    types: [submitted]

jobs:
  revise_pr_job:
    # Run only for reviews that contain '/revise'
    if: contains(github.event.review.body, '/revise')
    runs-on: ubuntu-latest
    # Permissions needed by the calling workflow to pass to the reusable workflow
    permissions:
      contents: write
      pull-requests: read

    steps:
      - name: Call Revise Agent Workflow
        uses: owner/repository/.github/workflows/revise-agent.yml@main
        with:
          pull_request_number: ${{ github.event.pull_request.number }}
          revision_instructions: ${{ github.event.review.body }}
        secrets:
          token: ${{ secrets.GITHUB_TOKEN }}

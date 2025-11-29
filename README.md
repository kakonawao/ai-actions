# Reusable GitHub Actions Workflows

This repository hosts a collection of reusable workflows for common CI/CD tasks.

## How to Use These Workflows

You can call these workflows from any other repository that has access to this one. To do so, you create a new workflow file (e.g., `.github/workflows/ci.yml`) in your repository and use the `uses` keyword to reference a workflow from this repository.

### Basic Syntax

The core syntax for calling a reusable workflow is as follows:

yaml
jobs:
  call-a-workflow:
    # Replace with the actual owner/repo of these workflows
    # Replace main.yml with the workflow you want to use
    # Replace v1 with a specific tag or branch
    uses: your-org/reusable-workflows-repo/.github/workflows/main.yml@v1
    with:
      # Pass inputs to the reusable workflow
      input-name: 'some-value'
    secrets:
      # Pass secrets to the reusable workflow
      SECRET_NAME: ${{ secrets.CALLER_SECRET_NAME }}


**Key Components:**
-   `uses`: The path to the reusable workflow in the format `{owner}/{repo}/.github/workflows/{filename}@{ref}`.
    -   **{ref}**: It is strongly recommended to use a specific Git tag (e.g., `@v1.2.3`) to pin your workflow to a specific version. You can also use a branch name or a commit SHA.
-   `with`: A map of input parameters to pass to the reusable workflow. The available inputs are defined in the reusable workflow file itself using `on.workflow_call.inputs`.
-   `secrets`: A map of secrets to pass to the reusable workflow. You can also use `secrets: inherit` to pass all of the caller's secrets.

### Required Permissions

The calling workflow must have the necessary permissions for the jobs inside the reusable workflow. If the reusable workflow needs to write to a repository, for example, you must grant `contents: write` permission in the calling workflow.

yaml
# .github/workflows/caller.yml
name: Call a reusable workflow

on:
  push:
    branches: [ main ]

# Grant permissions needed by the reusable workflow
permissions:
  contents: read
  pull-requests: write

jobs:
  do-something:
    uses: your-org/reusable-workflows-repo/.github/workflows/pr-comment.yml@v1


---

## Trigger Code Examples

Here are some complete examples demonstrating how to trigger a reusable workflow on different events.

### Example 1: On Push to `main`

This workflow runs whenever code is pushed to the `main` branch. It calls a hypothetical `reusable-ci.yml` workflow, passing a Node.js version as an input and an NPM token as a secret.

**File:** `.github/workflows/main-ci.yml`
yaml
name: Main Branch CI

on:
  push:
    branches:
      - main

jobs:
  build-and-test:
    uses: your-org/reusable-workflows-repo/.github/workflows/reusable-ci.yml@v1
    with:
      node-version: '20'
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}


### Example 2: On Pull Request

This workflow runs on pull requests opened against the `main` branch. It calls a `reusable-pr-check.yml` workflow to perform checks like linting or running tests.

**File:** `.github/workflows/pr-checks.yml`
yaml
name: Pull Request Checks

on:
  pull_request:
    branches:
      - main

jobs:
  run-pr-checks:
    uses: your-org/reusable-workflows-repo/.github/workflows/reusable-pr-check.yml@v1
    # 'inherit' passes all the calling workflow's secrets to the reusable workflow
    secrets: inherit


### Example 3: On Manual Trigger (`workflow_dispatch`)

This workflow can be triggered manually from the GitHub Actions UI. It prompts the user for an environment name, which is then passed to a `reusable-deploy.yml` workflow.

**File:** `.github/workflows/manual-deploy.yml`
yaml
name: Manual Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

jobs:
  deploy:
    uses: your-org/reusable-workflows-repo/.github/workflows/reusable-deploy.yml@v1.2
    with:
      environment: ${{ github.event.inputs.environment }}
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}


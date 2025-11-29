# Reusable GitHub Actions Workflows

This repository hosts a collection of centralized and reusable GitHub Actions workflows for common CI/CD tasks like building, testing, and deploying applications.

Using these workflows helps ensure consistency, security, and maintainability across all projects in the organization.

## How to Use These Workflows

You can call these reusable workflows from your own repository's GitHub Actions.

### 1. Permissions

Your repository must be configured to allow workflows from this repository to be run.

1.  Navigate to your repository's **Settings > Actions > General**.
2.  Under **Actions permissions**, select a permissive option such as **"Allow all actions and reusable workflows"**. For better security within an organization, choose **"Allow actions from [your-org-name]"**.

### 2. Calling a Workflow

To use a reusable workflow, create a `.yml` file in your repository's `.github/workflows` directory. Inside a job, use the `uses` keyword to reference the workflow you want to run.

The syntax is as follows:

yaml
jobs:
  <your-job-name>:
    uses: <owner>/<repo>/.github/workflows/<workflow-filename.yml>@<ref>


-   **`<owner>/<repo>`**: The path to this repository (e.g., `your-org/reusable-workflows`).
-   **`<workflow-filename.yml>`**: The name of the reusable workflow file you want to execute (e.g., `build-and-test.yml`).
-   **`<ref>`**: A git ref (branch, tag, or commit SHA). **It is strongly recommended to pin this to a specific version tag (e.g., `@v1`)** to prevent unexpected changes.

### 3. Passing Inputs and Secrets

Reusable workflows often require inputs (e.g., a Node.js version) and secrets (e.g., cloud provider credentials).

-   **Inputs**: Use the `with` keyword to pass inputs.
-   **Secrets**: Use the `secrets` keyword. `secrets: inherit` is a convenient way to pass all the calling repository's secrets to the reusable workflow. For more granular control, you can pass secrets individually.

---

### Trigger Code Examples

Here are some common use cases.

#### Example: Run Build and Test on Pull Request

This workflow triggers on every pull request to the `main` branch. It calls a reusable workflow to build the application and run tests.

**File:** `.github/workflows/pull-request-ci.yml`

yaml
name: Pull Request CI

on:
  pull_request:
    branches:
      - main

jobs:
  build-and-test:
    name: Build and Test
    # Replace with your org/repo and desired version tag
    uses: your-org/reusable-workflows/.github/workflows/build-and-test.yml@v1
    with:
      node-version: '18'
    secrets: inherit


#### Example: Deploy to Production on New Tag

This workflow triggers when a new tag following the pattern `v*.*.*` (e.g., `v1.2.3`) is pushed. It calls a reusable deployment workflow.

**File:** `.github/workflows/release.yml`

yaml
name: Release and Deploy

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  release-and-deploy:
    name: Deploy to Production
    # Replace with your org/repo and desired version tag
    uses: your-org/reusable-workflows/.github/workflows/deploy.yml@v1.2
    with:
      environment: 'production'
      # Example: pass the tag name to the deploy workflow
      version: ${{ github.ref_name }}
    secrets:
      # Pass specific secrets required for production deployment
      AWS_ACCESS_KEY_ID: ${{ secrets.PROD_AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.PROD_AWS_SECRET_ACCESS_KEY }}


#### Example: Manual Trigger for Staging Deployment

This workflow can be triggered manually from the GitHub Actions UI using `workflow_dispatch`. It allows for on-demand deployments to a staging environment.

**File:** `.github/workflows/deploy-staging.yml`

yaml
name: Deploy to Staging

on:
  workflow_dispatch:

jobs:
  deploy-to-staging:
    name: Deploy to Staging
    # Replace with your org/repo and desired version tag
    uses: your-org/reusable-workflows/.github/workflows/deploy.yml@v1.2
    with:
      environment: 'staging'
    secrets: inherit


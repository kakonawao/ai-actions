# Reusable GitHub Actions Workflows

This repository contains a collection of reusable GitHub Actions workflows designed to be called from other repositories. This approach promotes consistency, reduces duplication, and simplifies CI/CD pipeline management.

## Usage

To use a workflow from this repository, you need to call it from a workflow file in your own repository using the `uses` keyword. The calling workflow must have the necessary permissions for the jobs it runs.

### General Syntax

The basic syntax points to the workflow file in this repository, including the version (branch, tag, or commit SHA):

yaml
jobs:
  call-reusable-workflow:
    uses: your-org/reusable-workflows/.github/workflows/workflow-file-name.yml@main


- Replace `your-org/reusable-workflows` with the actual path to this repository.
- Replace `workflow-file-name.yml` with the workflow you want to use.
- Replace `@main` with a specific tag (e.g., `@v1.2.3`) for better stability.

### Passing Inputs and Secrets

Reusable workflows can accept inputs and secrets. You pass these using the `with` and `secrets` keywords in the calling job.

yaml
jobs:
  call-reusable-workflow:
    uses: your-org/reusable-workflows/.github/workflows/deploy.yml@main
    with:
      environment: 'staging'
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.STAGING_AWS_ACCESS_KEY_ID }}


For more detailed information, see the official GitHub documentation on [Reusing workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows).

## Available Workflows & Trigger Examples

Below are examples of how to trigger the available workflows.

---

###  lint.yml

This workflow checks the code for linting errors using a standard linter configuration.

**Trigger Example:**

Create a file like `.github/workflows/ci.yml` in your repository with the following content:

yaml
name: Lint Code

on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main ]

jobs:
  lint:
    name: Run Linter
    uses: your-org/reusable-workflows/.github/workflows/lint.yml@main
    # This workflow does not require any specific permissions, inputs, or secrets.


---

### test.yml

This workflow installs dependencies and runs the test suite. It accepts a `node-version` input to specify which version of Node.js to use.

**Trigger Example:**

yaml
name: Run Tests

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    name: Run Unit & Integration Tests
    uses: your-org/reusable-workflows/.github/workflows/test.yml@main
    with:
      node-version: '18'


---

### deploy.yml

This workflow handles deploying the application. It requires an `environment` input (e.g., `staging`, `production`) and several secrets for authentication.

**Trigger Example:**

This example shows a workflow that can be triggered manually to deploy to a staging environment.

yaml
name: Deploy to Staging

on:
  workflow_dispatch:
    inputs:
      ref:
        description: 'The branch, tag, or SHA to deploy.'
        required: true
        default: 'main'

jobs:
  deploy-staging:
    name: Deploy to Staging Environment
    uses: your-org/reusable-workflows/.github/workflows/deploy.yml@main
    with:
      environment: 'staging'
      ref: ${{ github.event.inputs.ref }}
    secrets:
      # Secrets must be created in the calling repository's settings
      AWS_ACCESS_KEY_ID: ${{ secrets.STAGING_AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.STAGING_AWS_SECRET_ACCESS_KEY }}
      AWS_REGION: ${{ secrets.STAGING_AWS_REGION }}


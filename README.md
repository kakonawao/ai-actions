# Reusable GitHub Actions Workflows

This repository contains a collection of reusable GitHub Actions workflows designed to standardize CI/CD processes, reduce code duplication, and improve maintainability across multiple projects.

## Table of Contents

- [Available Workflows](#available-workflows)
- [Usage](#usage)
  - [Prerequisites](#prerequisites)
  - [Calling a Reusable Workflow](#calling-a-reusable-workflow)
- [Examples](#examples)
  - [Example 1: Lint and Test](#example-1-lint-and-test)
  - [Example 2: Build and Publish a Docker Image](#example-2-build-and-publish-a-docker-image)

## Available Workflows

*   `lint-and-test.yml`: A generic workflow to set up Node.js, install dependencies, run linting, and execute tests.
*   `build-and-publish.yml`: A workflow to build a Docker image and publish it to a container registry like Docker Hub or GHCR.

_(More workflows to be added...)_

## Usage

You can use these workflows in your own repository's GitHub Actions by calling them from one of your workflow files.

### Prerequisites

For your repository to use these workflows, it must have permission to access this repository. If this `reusable-workflows` repository is internal, any other internal repository within the same organization can access it by default. For cross-organization usage, you may need to adjust repository settings.

### Calling a Reusable Workflow

To call a reusable workflow, you use the `uses` keyword within a job in your workflow file.

The syntax is:
yaml
jobs:
  <job_id>:
    uses: <owner>/<repo>/.github/workflows/<workflow_filename>@<ref>


-   `<job_id>`: A unique identifier for your job.
-   `<owner>/<repo>`: The owner and repository name where the reusable workflow is located (e.g., `your-org/reusable-workflows`).
-   `<workflow_filename>`: The name of the reusable workflow file (e.g., `lint-and-test.yml`).
-   `<ref>`: The Git ref to use. This can be a branch, tag, or a specific commit SHA. **It is highly recommended to pin to a specific tag or commit SHA for stability.**

You can pass inputs and secrets to the reusable workflow using the `with` and `secrets` keywords, respectively.

## Examples

Here are some practical examples of how to use the workflows from this repository.

### Example 1: Lint and Test

This example shows how to call the `lint-and-test.yml` workflow to run a CI check on every push and pull request to the `main` branch.

#### Caller Workflow (`.github/workflows/ci.yml`)

Create this file in your own repository.

yaml
name: CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  lint-and-test:
    name: Lint and Test
    uses: your-org/reusable-workflows/.github/workflows/lint-and-test.yml@v1
    with:
      node-version: '20'
    # Use 'inherit' to pass all secrets from the caller's context
    # This is useful for secrets like a private NPM token.
    secrets: inherit


#### Reusable Workflow Trigger (`lint-and-test.yml`)

For reference, this is how the `lint-and-test.yml` workflow in *this* repository is configured to be callable. Note the `on: workflow_call` trigger.

yaml
# located in your-org/reusable-workflows/.github/workflows/lint-and-test.yml
name: Reusable Lint and Test

on:
  workflow_call:
    inputs:
      node-version:
        description: 'The Node.js version to use'
        required: false
        type: string
        default: '20'
    secrets:
      NPM_TOKEN:
        description: 'Token for authenticating with a private NPM registry'
        required: false

jobs:
  run-checks:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}

      - name: Install dependencies
        # The NPM_TOKEN secret will be available as an environment variable
        run: npm ci
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test


### Example 2: Build and Publish a Docker Image

This example shows how to use the `build-and-publish.yml` workflow, triggering it when a new version tag (e.g., `v1.2.3`) is pushed.

#### Caller Workflow (`.github/workflows/release.yml`)

Create this file in your own repository. This workflow will pass the required Docker Hub credentials as secrets.

yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  build-and-publish:
    name: Build and Publish Docker Image
    uses: your-org/reusable-workflows/.github/workflows/build-and-publish.yml@v1
    with:
      image-name: ${{ github.repository }}
    secrets:
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}


**Note:** You must define `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` in your repository's secrets settings (`Settings > Secrets and variables > Actions`).

#### Reusable Workflow Trigger (`build-and-publish.yml`)

This is the corresponding `workflow_call` trigger within the `build-and-publish.yml` file. It defines the inputs and secrets it expects to receive.

yaml
# located in your-org/reusable-workflows/.github/workflows/build-and-publish.yml
name: Reusable Build and Publish

on:
  workflow_call:
    inputs:
      image-name:
        description: 'The name of the Docker image (e.g., owner/image-name)'
        required: true
        type: string
    secrets:
      DOCKERHUB_USERNAME:
        description: 'Username for the container registry'
        required: true
      DOCKERHUB_TOKEN:
        description: 'Access token for the container registry'
        required: true

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ inputs.image-name }}:${{ github.ref_name }} # e.g., your-org/my-app:v1.2.3


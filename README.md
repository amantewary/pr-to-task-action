# PR to Task (Agent Prompt) Action

A GitHub Action that automatically turns messy Pull Requests into highly structured, deterministic tasks for autonomous coding agents (like Sweep, Devin, or Claude Code).

Based on the methodology from the paper ["Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"](https://arxiv.org/abs/2601.20404), this action fetches the PR diff and repository tree, feeds them to an LLM (Gemini or OpenAI), and generates a clean GitHub-issue-style prompt that removes ambiguity.

## Usage

Create a workflow file in your repository (e.g., `.github/workflows/pr-to-task.yml`):

```yaml
name: Generate Agent Task

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  generate-task:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - name: Generate Agent Task
        uses: amantewary/pr-to-task-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          llm_provider: 'gemini' # or 'openai'
          llm_api_key: ${{ secrets.GEMINI_API_KEY }} # or secrets.OPENAI_API_KEY
```

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `github_token` | Yes | `${{ github.token }}` | GitHub token to read PR diffs and post comments. |
| `llm_provider` | Yes | `gemini` | The LLM provider to use (`gemini` or `openai`). |
| `llm_api_key` | Yes | | Your API key for the chosen provider. |
| `model` | No | | Model override (defaults to `gemini-2.5-flash` or `gpt-4o-mini`). |

## How it works
1. Triggered on Pull Request events.
2. Uses the GitHub API to fetch the raw diff and the full file tree of the repository.
3. Packages them with a strict system prompt and sends to the configured LLM.
4. Posts the generated structured task directly as a comment on the Pull Request, ready to be picked up by a coding agent.
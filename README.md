# PR to Task (Agent Prompt) Action 🤖

[![Tests](https://github.com/amantewary/pr-to-task-action/actions/workflows/self-test.yml/badge.svg)](https://github.com/amantewary/pr-to-task-action/actions/workflows/self-test.yml)

A GitHub Action that automatically turns messy, ambiguous Pull Requests into highly structured, deterministic tasks for autonomous coding agents (like Devin, OpenClaw, or Claude Code).

## 💡 Why this exists

Coding agents are powerful, but they are often limited by the **quality of context** provided by humans. A raw PR diff is hard for an agent to "reason" about without knowing the project structure and specific constraints. 

Based on research from the paper [*"Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"*](https://arxiv.org/abs/2601.20404), we found that providing agents with a structured "Task Statement" significantly reduces variance and improves task success rates.

## 🎯 What it does

This action intercepts a Pull Request and generates a standardized "Agent Task" that includes:
- **Problem Statement:** Clear summary of the intent.
- **Expected Behavior:** Specific runtime expectations.
- **Constraints:** Files to protect and architectural boundaries.
- **Acceptance Criteria:** Strict conditions for completion.
- **Context Files:** The exact files the agent needs to read first.

## 🚀 Outcome

By using this action, you bridge the gap between "human intent" and "agent execution."
- **Reduced Hallucinations:** The agent is anchored to the actual repository tree.
- **Zero Ambiguity:** Strict acceptance criteria prevent the agent from wandering off-task.
- **Automated Handover:** Seamlessly hand off PR fixes or feature additions to your AI workforce.

---

## 🛠 Usage

Create `.github/workflows/pr-to-task.yml` in your repository:

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
          llm_api_key: ${{ secrets.GEMINI_API_KEY }}
```

## ⚙️ Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `github_token` | Yes | `${{ github.token }}` | Token to read PR diffs and post comments. |
| `llm_provider` | Yes | `gemini` | LLM provider (`gemini` or `openai`). |
| `llm_api_key` | Yes | | API key for the chosen provider. |
| `model` | No | | Model override (e.g., `gpt-4o`). |

## 🏗 How it works
1. **Fetch Context:** Uses GitHub APIs to grab the raw PR diff and the recursive file tree.
2. **LLM Reasoning:** Sends the context to an LLM with a specialized "Technical Lead" system prompt.
3. **Task Injection:** Posts the structured task as a comment directly on the Pull Request.

import os
import sys
import json
import requests

def get_pr_info(event_path):
    with open(event_path, 'r') as f:
        event = json.load(f)
    if 'pull_request' not in event:
        print("Not a pull request event. Skipping.")
        sys.exit(0)
    
    pr_number = event['pull_request']['number']
    repo = event['repository']['full_name']
    return repo, pr_number

def fetch_diff(repo, pr_number, token):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text

def fetch_tree(repo, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    repo_url = f"https://api.github.com/repos/{repo}"
    resp = requests.get(repo_url, headers=headers)
    resp.raise_for_status()
    default_branch = resp.json().get("default_branch", "main")
    
    tree_url = f"https://api.github.com/repos/{repo}/git/trees/{default_branch}?recursive=1"
    resp = requests.get(tree_url, headers=headers)
    resp.raise_for_status()
    tree_data = resp.json().get("tree", [])
    
    paths = []
    for item in tree_data:
        path = item['path']
        if not any(x in path for x in ['.git/', '__pycache__', 'node_modules/', 'venv/']):
            paths.append(path)
    return "\n".join(paths)

def call_gemini(system_prompt, user_prompt, api_key, model):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)
    
    model_name = model if model else 'gemini-2.5-flash'
    
    response = client.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
        )
    )
    return response.text

def call_openai(system_prompt, user_prompt, api_key, model):
    import openai
    client = openai.OpenAI(api_key=api_key)
    
    model_name = model if model else 'gpt-4o-mini'
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

def post_comment(repo, pr_number, token, body):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    resp = requests.post(url, headers=headers, json={"body": body})
    resp.raise_for_status()

def main():
    token = os.environ.get("INPUT_GITHUB_TOKEN")
    provider = os.environ.get("INPUT_LLM_PROVIDER", "gemini").lower()
    llm_key = os.environ.get("INPUT_LLM_API_KEY")
    model = os.environ.get("INPUT_MODEL", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    
    if not token or not llm_key or not event_path:
        print("Missing required environment variables (GITHUB_TOKEN, LLM_API_KEY, GITHUB_EVENT_PATH).")
        sys.exit(1)
        
    repo, pr_number = get_pr_info(event_path)
    print(f"Processing PR {repo}#{pr_number}")
    
    try:
        diff = fetch_diff(repo, pr_number, token)
        tree = fetch_tree(repo, token)
    except Exception as e:
        print(f"Failed to fetch GitHub data: {e}")
        sys.exit(1)
    
    system_prompt = """You are an expert technical lead preparing a task for an autonomous coding agent.
Your job is to read a Pull Request diff and the repository file tree, and generate a highly structured, 
unambiguous task description in the style of a GitHub issue.

Follow this exact structure:

# Problem Statement
(What is this PR trying to achieve? What bug does it fix or feature does it add?)

# Expected Behavior
(What should the system do after the changes?)

# Constraints
(What files must NOT be changed? What performance or architectural boundaries exist based on the repo tree?)

# Acceptance Criteria
(A bulleted list of strict conditions that must be met for this to be considered 'done')

# Context Files
(List the files from the tree that the agent should look at first to understand the context)"""

    diff_trunc = diff[:20000] + ("\n...[truncated]" if len(diff) > 20000 else "")
    tree_trunc = tree[:10000] + ("\n...[truncated]" if len(tree) > 10000 else "")
    
    user_prompt = f"REPOSITORY TREE:\n{tree_trunc}\n\nPR DIFF:\n{diff_trunc}\n"
    
    print(f"Calling LLM ({provider})...")
    try:
        if provider == "gemini":
            task_desc = call_gemini(system_prompt, user_prompt, llm_key, model)
        elif provider == "openai":
            task_desc = call_openai(system_prompt, user_prompt, llm_key, model)
        else:
            print(f"Unsupported provider: {provider}")
            sys.exit(1)
    except Exception as e:
        print(f"LLM call failed: {e}")
        sys.exit(1)
        
    comment_body = f"🤖 **Agent Task Generated**\n\n{task_desc}\n\n---\n*Generated by [PR to Task Action](https://github.com/marketplace/actions/pr-to-task)*"
    
    print("Posting comment to PR...")
    try:
        post_comment(repo, pr_number, token, comment_body)
        print("Done!")
    except Exception as e:
        print(f"Failed to post comment: {e}")
        sys.exit(1)

if __name__ == "__main__":

# Test Change (Fix)
print('This is a clean test change.')

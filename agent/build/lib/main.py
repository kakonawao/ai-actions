import os
import json
import subprocess
import google.generativeai as genai

# Define a constant for the file to store changed paths
CHANGED_FILES_LIST = "ai_changed_files.txt"

def run_draft_mode():
    """Handles the initial code generation from an issue."""
    print("[INFO] Running in 'draft' mode.")
    issue_title = os.getenv("ISSUE_TITLE")
    issue_body = os.getenv("ISSUE_BODY")

    if not all([issue_title, issue_body]):
        print("[ERROR] Incomplete issue information. ISSUE_TITLE and ISSUE_BODY must be set.")
        return

    prompt = f"""
    You are an expert software developer. Your task is to draft a solution for the following issue.
    Issue Title: {issue_title}
    Issue Description: {issue_body}
    Your response must be a JSON object with a "files" key, containing a list of objects, where each object has a "path" and "content" key.
    """
    
    send_prompt_to_ai(prompt)

def run_revise_mode():
    """Handles revising code based on PR review comments."""
    print("[INFO] Running in 'revise' mode.")
    pr_number = os.getenv("PR_NUMBER")
    if not pr_number:
        raise RuntimeError("PR_NUMBER not set.")

    pr_diff = subprocess.check_output(['gh', 'pr', 'diff', pr_number]).decode('utf-8')
    pr_comments = subprocess.check_output(['gh', 'pr', 'view', pr_number, '--comments']).decode('utf-8')

    prompt = f"""
    You are an expert software developer. A pull request has received feedback, and you need to revise it.
    
    Pull Request Diff:
    {pr_diff}
    
    Review Comments:
    {pr_comments}
    
    Based on the comments, provide the necessary code changes. Your response must be a JSON object with a "files" key, containing a list of objects, where each object has a "path" and "content" key.
    Only include files that need to be changed.
    """
    
    send_prompt_to_ai(prompt)

def send_prompt_to_ai(prompt):
    """Sends the generated prompt to the Gemini API and applies the changes."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-pro')

    print("\n[INFO] Sending prompt to Gemini...")
    response = model.generate_content(prompt)

    try:
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        changes = json.loads(cleaned_response)
        
        print(f"\n[DEBUG] AI Response (parsed 'changes' object):\n{json.dumps(changes, indent=2)}")

        if "files" not in changes or not isinstance(changes["files"], list):
            raise ValueError("Invalid AI response: 'files' key is missing or not a list.")

        # Collect paths of changed files
        changed_file_paths = []

        for file_change in changes["files"]:
            path = file_change["path"]
            content = file_change["content"]
            
            # Ensure directory exists before writing the file
            dir_name = os.path.dirname(path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            
            with open(path, "w") as f:
                f.write(content)
            print(f"[INFO] Wrote changes to {path}")
            changed_file_paths.append(path)

        # Write the list of changed files to a temporary file
        with open(CHANGED_FILES_LIST, "w") as f:
            for p in changed_file_paths:
                f.write(f"{p}\n")
        print(f"[INFO] Recorded changed files in {CHANGED_FILES_LIST}")

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"[ERROR] Failed to parse AI response: {e}")
        print(f"Raw response was:\n{response.text}")
        with open("ai_response_error.txt", "w") as f:
            f.write(f"Failed to parse AI response.\n\nError: {e}\n\nRaw Response:\n{response.text}")

def main():
    mode = os.getenv("AGENT_MODE", "draft")
    if mode == "revise":
        run_revise_mode()
    else:
        run_draft_mode()

if __name__ == "__main__":
    main()

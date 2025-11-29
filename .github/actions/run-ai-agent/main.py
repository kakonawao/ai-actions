import os
import json
import subprocess
import google.generativeai as genai

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
    Your entire response must be a JSON object with a "files" key, containing a list of objects, where each object has a "path" and "content" key. Do not include any conversational text or markdown formatting outside of the JSON object itself.
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
    
    Your entire response must be a JSON object with a "files" key, containing a list of objects, where each object has a "path" and "content" key. Only include files that need to be changed. Do not include any conversational text or markdown formatting outside of the JSON object itself.
    """
    
    send_prompt_to_ai(prompt)

def send_prompt_to_ai(prompt):
    """Sends the generated prompt to the Gemini API and applies the changes."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set.")

    genai.configure(api_key=api_key)
    
    gemini_model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
    model = genai.GenerativeModel(gemini_model_name)

    print(f"\n[INFO] Sending prompt to Gemini using model: {gemini_model_name}...")
    response = model.generate_content(prompt)

    try:
        # Expect the model to return only JSON, so strip whitespace and attempt direct load
        cleaned_response = response.text.strip()
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

        print(f"\n[DEBUG] Collected changed_file_paths: {changed_file_paths}")

        # Output the list of changed files as a step output using GITHUB_OUTPUT
        github_output_path = os.getenv("GITHUB_OUTPUT")
        if github_output_path:
            with open(github_output_path, "a") as f:
                f.write("changed_files<<EOF\n")
                for p in changed_file_paths:
                    f.write(f"{p}\n")
                f.write("EOF\n")
            print(f"[INFO] Outputted {len(changed_file_paths)} changed file paths to GITHUB_OUTPUT.")
        else:
            print("[ERROR] GITHUB_OUTPUT environment variable not set. Cannot set step output.")


    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"[ERROR] Failed to parse AI response: {e}")
        print(f"Raw response was:\n{response.text}")

def main():
    mode = os.getenv("AGENT_MODE", "draft")
    if mode == "revise":
        run_revise_mode()
    else:
        run_draft_mode()

if __name__ == "__main__":
    main()

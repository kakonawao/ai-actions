import os
import subprocess
import pprint

from langchain.agents import create_agent
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI

from .tools import list_files, read_file, write_file, _written_files


def _extract_response_text(response: any) -> str:
    # Log the full response object for debugging
    print("[DEBUG] Full agent response object:")
    pprint.pprint(response)

    if isinstance(response, dict):
        if 'messages' in response and isinstance(response['messages'], list) and len(response['messages']) > 0:
            return response['messages'][-1].content
        elif 'output' in response:
            return response['output']
    elif hasattr(response, 'content'):
        return response.content
    
    return str(response) # Fallback to string representation


def _write_outputs_to_github(final_response_text: str, written_files: list):
    github_output_path = os.getenv("GITHUB_OUTPUT")
    if not github_output_path:
        print("[ERROR] GITHUB_OUTPUT environment variable not set. Cannot set step output.")
        return

    with open(github_output_path, "a") as f:
        # List of files
        f.write("changed_files<<EOF\n")
        for p in written_files:
            f.write(f"{p}\n")
        f.write("EOF\n")

        # Summary for pull request
        f.write(f"agent_summary_output<<EOF\n{final_response_text}\nEOF\n")
    
    print(f"[INFO] Outputted {written_files} to changed_files and agent summary.")


def _get_rate_limiter() -> InMemoryRateLimiter | None:
    rate_limit_str = os.getenv("GEMINI_RATE_LIMIT_PER_MINUTE")
    if not rate_limit_str:
        return None
        
    try:
        rate_limit = int(rate_limit_str)
        if rate_limit > 0:
            print(f"[INFO] Setting Gemini API rate limit to {rate_limit} requests/minute.")
            return InMemoryRateLimiter(requests_per_second=rate_limit / 60)
        else:
            print("[INFO] GEMINI_RATE_LIMIT_PER_MINUTE is 0 or less, no rate limit applied.")
            return None
    except ValueError:
        print(f"[WARNING] Invalid GEMINI_RATE_LIMIT_PER_MINUTE value: {rate_limit_str}. Ignoring.")
        return None


def run_agent(user_prompt: str):
    print("[INFO] Initializing LangChain agent...")
    
    gemini_model_name = os.getenv("GEMINI_MODEL")
    rate_limiter = _get_rate_limiter()

    llm = ChatGoogleGenerativeAI(
        model=gemini_model_name, 
        temperature=0,
        rate_limiter=rate_limiter,
    )

    tools = [list_files, read_file, write_file]
    
    # Define the system prompt for the agent
    system_prompt_content = (
        "You are an expert software developer. Your task is to analyze the codebase, "
        "understand the context, and then write the necessary code changes to solve the request. "
        "Use the available tools to explore the codebase, read relevant files, and write new or updated files. "
        "Your final answer should be a summary of the files you wrote or a confirmation that no changes were needed."
    )
    
    # Create the agent directly
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt_content,
    )

    print(f"[INFO] Running agent with prompt:\n{user_prompt}")
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]}
    )

    final_response_text = _extract_response_text(response)
    print(f"[INFO] Agent finished with response:\n{final_response_text}")

    _write_outputs_to_github(final_response_text, _written_files)


def main():
    # Change the current working directory to the target repository's root
    working_directory = os.getenv("AGENT_WORKING_DIRECTORY", ".")
    if os.path.exists(working_directory):
        print(f"[INFO] Changing working directory to: {working_directory}")
        os.chdir(working_directory)
    else:
        print(f"[ERROR] Working directory not found: {working_directory}")
        return

    agent_mode = os.getenv("AGENT_MODE", "draft")

    if agent_mode == "draft":
        issue_title = os.getenv("ISSUE_TITLE")
        issue_body = os.getenv("ISSUE_BODY")
        if not all([issue_title, issue_body]):
            print("[ERROR] Incomplete issue information for draft mode.")
            return
        
        user_prompt = f"""
        Draft a solution for the following issue.
        Issue Title: {issue_title}
        Issue Description: {issue_body}
        
        Start by listing the files in the current directory to understand the project structure.
        Then, read the relevant files to understand the existing code.
        Finally, use the write_file tool to create or update the necessary files with your proposed solution.
        """
        run_agent(user_prompt)

    elif agent_mode == "revise":
        pr_number = os.getenv("PR_NUMBER")
        if not pr_number:
            print("[ERROR] PR_NUMBER not set for revise mode.")
            return
            
        pr_diff = subprocess.check_output(['gh', 'pr', 'diff', pr_number]).decode('utf-8')
        pr_comments = subprocess.check_output(['gh', 'pr', 'view', pr_number, '--comments']).decode('utf-8')

        user_prompt = f"""
        Revise the pull request based on the provided feedback.
        
        Pull Request Diff:
        {pr_diff}
        
        Review Comments:
        {pr_comments}
        
        Start by listing the files in the current directory to understand the project structure.
        Then, read the relevant files to understand the existing code.
        Finally, use the write_file tool to create or update the necessary files with your proposed revisions.
        """
        run_agent(user_prompt)

    else:
        print(f"[ERROR] Unknown agent mode: {agent_mode}")


if __name__ == "__main__":
    main()

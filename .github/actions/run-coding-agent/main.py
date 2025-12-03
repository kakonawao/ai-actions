import os
import subprocess

from langchain.agents import AgentType, initialize_agent
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import list_files, read_file, write_file, _written_files


def run_agent(prompt: str):
    """Initializes and runs the LangChain agent."""
    print("[INFO] Initializing LangChain agent...")
    
    gemini_model_name = os.getenv("GEMINI_MODEL", "models/gemini-pro")
    llm = ChatGoogleGenerativeAI(model=gemini_model_name, temperature=0)

    tools = [list_files, read_file, write_file]
    
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    print(f"[INFO] Running agent with prompt:\n{prompt}")
    response = agent.run(prompt)
    print(f"[INFO] Agent finished with response:\n{response}")

    # After the agent run, output the list of files that were written
    github_output_path = os.getenv("GITHUB_OUTPUT")
    if github_output_path:
        with open(github_output_path, "a") as f:
            f.write("changed_files<<EOF\n")
            for p in _written_files:
                f.write(f"{p}\n")
            f.write("EOF\n")
        print(f"[INFO] Outputted {_written_files} to changed_files.")
    else:
        print("[ERROR] GITHUB_OUTPUT environment variable not set. Cannot set step output.")


def main():
    agent_mode = os.getenv("AGENT_MODE", "draft")

    if agent_mode == "draft":
        issue_title = os.getenv("ISSUE_TITLE")
        issue_body = os.getenv("ISSUE_BODY")
        if not all([issue_title, issue_body]):
            print("[ERROR] Incomplete issue information for draft mode.")
            return
        
        prompt = f"""
        You are an expert software developer. Your task is to draft a solution for the following issue.
        You have access to the following tools: {', '.join([t.name for t in [list_files, read_file, write_file]])}.
        Use these tools to explore the codebase, understand the context, and then write the necessary code changes.
        
        Issue Title: {issue_title}
        Issue Description: {issue_body}
        
        Start by listing the files in the current directory to understand the project structure.
        Then, read the relevant files to understand the existing code.
        Finally, use the write_file tool to create or update the necessary files with your proposed solution.
        Your final answer should be a summary of the files you wrote.
        """
        run_agent(prompt)

    elif agent_mode == "revise":
        pr_number = os.getenv("PR_NUMBER")
        if not pr_number:
            print("[ERROR] PR_NUMBER not set for revise mode.")
            return
            
        pr_diff = subprocess.check_output(['gh', 'pr', 'diff', pr_number]).decode('utf-8')
        pr_comments = subprocess.check_output(['gh', 'pr', 'view', pr_number, '--comments']).decode('utf-8')

        prompt = f"""
        You are an expert software developer. A pull request has received feedback, and you need to revise it.
        You have access to the following tools: {', '.join([t.name for t in [list_files, read_file, write_file]])}.
        Use these tools to explore the codebase, understand the context of the PR, and then write the necessary code changes based on the review comments.
        
        Pull Request Diff:
        {pr_diff}
        
        Review Comments:
        {pr_comments}
        
        Start by listing the files in the current directory to understand the project structure.
        Then, read the relevant files to understand the existing code.
        Finally, use the write_file tool to create or update the necessary files with your proposed revisions.
        Your final answer should be a summary of the files you wrote.
        """
        run_agent(prompt)

    else:
        print(f"[ERROR] Unknown agent mode: {agent_mode}")


if __name__ == "__main__":
    main()

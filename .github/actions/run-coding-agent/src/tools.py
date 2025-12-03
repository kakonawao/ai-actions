import os
from langchain.tools import tool

# A simple in-memory list to track files written by the agent
_written_files = []

@tool
def list_files(directory: str) -> str:
    """Lists files and directories in a given path."""
    try:
        return str(os.listdir(directory))
    except Exception as e:
        return str(e)

@tool
def read_file(file_path: str) -> str:
    """Reads the content of a specific file."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return str(e)

@tool
def write_file(file_path: str, content: str) -> str:
    """Writes content to a file and tracks the file path."""
    try:
        # Create directory if it doesn't exist
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
            
        with open(file_path, "w") as f:
            f.write(content)
        
        # Track the file that was successfully written
        if file_path not in _written_files:
            _written_files.append(file_path)
            
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return str(e)

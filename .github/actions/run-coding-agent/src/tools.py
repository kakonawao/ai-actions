import os
from langchain.tools import tool

# A simple in-memory list to track files written by the agent
_written_files = []

# Get the base working directory for the agent's file operations
_AGENT_WORKING_DIRECTORY = os.getenv("AGENT_WORKING_DIRECTORY", ".")

def _get_full_path(relative_path: str) -> str:
    """Constructs the full path relative to the agent's working directory."""
    return os.path.join(_AGENT_WORKING_DIRECTORY, relative_path)

@tool
def list_files(directory: str = ".") -> str: # Default to current working directory
    """Lists files and directories in a given path relative to the agent's working directory."""
    full_path = _get_full_path(directory)
    try:
        return str(os.listdir(full_path))
    except Exception as e:
        return str(e)

@tool
def read_file(file_path: str) -> str:
    """Reads the content of a specific file relative to the agent's working directory."""
    full_path = _get_full_path(file_path)
    try:
        with open(full_path, "r") as f:
            return f.read()
    except Exception as e:
        return str(e)

@tool
def write_file(file_path: str, content: str) -> str:
    """Writes content to a file and tracks the file path relative to the agent's working directory."""
    full_path = _get_full_path(file_path)
    try:
        # Create directory if it doesn't exist
        dir_name = os.path.dirname(full_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
            
        with open(full_path, "w") as f:
            f.write(content)
        
        # Track the file that was successfully written (store relative path)
        relative_file_path = os.path.relpath(full_path, start=_AGENT_WORKING_DIRECTORY)
        if relative_file_path not in _written_files:
            _written_files.append(relative_file_path)
            
        return f"Successfully wrote to {relative_file_path}"
    except Exception as e:
        return str(e)

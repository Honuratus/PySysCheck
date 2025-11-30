import subprocess

def read_file(file_path):
    """
    reads contents of a file
    raises FileNotFound if file doesn't exists (caller must handle it)
    """
    with open(file_path, "r") as f:
        content = f.read()
    return content

def run_command(command_list):
    """
    runs a shell command using subprocess
    returns stdout string if succesfull, none otherwise
    """
    output = subprocess.run(command_list, capture_output=True, text=True)
    if output.returncode == 0:
        return output.stdout
    return None

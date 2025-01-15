import json
import platform
import os
import subprocess
import shutil

# Load the JSON configuration file
with open('hererocks_config.json', 'r') as file:
    config = json.load(file)

# Define a function to print colored text
def print_colored(text, color):
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'end': '\033[0m'
    }
    print(f"{colors[color]}{text}{colors['end']}")

# Function to recursively print keys
def print_keys(d, prefix=''):
    for key, value in d.items():
        print_colored(f"{prefix}{key}", 'blue')
        if isinstance(value, dict):
            print_keys(value, prefix + '  ')

# Function to move directories
def move_directories(library, os_type):
    print_colored(f"Moving directories for {os_type}/{library}", 'yellow')
    temp_dir = f"{os_type}/{library}_temp"
    lib_src = os.path.join(temp_dir, 'lib', 'lua', '5.1')
    lib_dest = os.path.join(os_type, library)

    share_src = os.path.join(temp_dir, 'share', 'lua', '5.1')
    share_dest = os.path.join(os_type, library, 'lua')

    if os.path.exists(lib_src):
        shutil.move(lib_src, lib_dest)
    if os.path.exists(share_src):
        shutil.move(share_src, share_dest)
    shutil.rmtree(temp_dir)

# Determine the operating system
os_type = platform.system().lower()

# Function to run the preinstall script and check if hererocks folder exists
def run_preinstall_and_check(install_path, preinstall, libraries):
    # Replace $install_path in the preinstall command
    preinstall = preinstall.replace("$install_path", install_path)
    
    # Run the preinstall script
    subprocess.run(preinstall, shell=True, check=True)
    
    # Check if the hererocks folder exists
    if os.path.exists(install_path):
        print_colored(f"hererocks folder exists at {install_path}", 'green')
    else:
        print_colored(f"hererocks folder does not exist at {install_path}", 'red')

    # Activate the hererocks environment and get the Lua version
    if os_type == 'windows':
        activate_script = os.path.join(install_path, 'bin', 'activate.bat')
        print_colored(f"Activating script: {activate_script}", 'yellow')
        command = f'cmd /c "{activate_script} && lua -v"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        
        # Run commands for each library
        for library in libraries:
            build_command = f'cmd /c "{activate_script} && luarocks install {library} --force --keep --no-doc --tree {os_type}/{library}_temp"'
            result = subprocess.run(build_command, shell=True, capture_output=True, text=True)
            print(result.returncode)
            if result.returncode == 0:
                print(f"Successfully installed {library}:\n{result.stdout}")
                move_directories(library, os_type)
            else:
                print(f"Failed to install {library}:\n{result.stderr}")

    elif os_type == 'linux':
        activate_script = os.path.join(install_path, 'bin', 'activate')
        command = f'bash -c "source {activate_script} && luajit -v"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        
        # Run commands for each library
        for library in libraries:
            command = f'bash -c "source {activate_script} && luarocks install {library} --force --keep --no-doc --tree {os_type}/{library}_temp"'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(result.stdout)
            print("Return code:", result.returncode)
            if result.returncode == 0:
                move_directories(library, os_type)
            else:
                print(f"Failed to install {library}:\n{result.stderr}")

# Build command based on the operating system
if os_type == 'windows':
    print_colored("Operating System: Windows", 'blue')
    windows_config = config.get('windows', {})
    print_keys(windows_config)
    run_preinstall_and_check(windows_config['install_path'], windows_config['preinstall'], config['libraries'])
elif os_type == 'linux':
    print_colored("Operating System: Linux", 'blue')
    linux_config = config.get('linux', {})
    print_keys(linux_config)
    run_preinstall_and_check(linux_config['install_path'], linux_config['preinstall'], config['libraries'])
else:
    print_colored(f"Unsupported Operating System: {os_type}", 'red')

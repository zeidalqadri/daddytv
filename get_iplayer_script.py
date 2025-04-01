#!/usr/bin/env python3

import os
import subprocess
import sys
import json
import argparse

# Ensure get_iplayer is in the PATH
get_iplayer_path = os.path.join(os.getcwd(), 'get_iplayer')
if get_iplayer_path not in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + get_iplayer_path

# Function to check and install dependencies
def check_dependencies():
    dependencies = ['ffmpeg', 'rtmpdump']
    for dep in dependencies:
        try:
            subprocess.run([dep, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            print(f"{dep} is not installed. Please install it using `sudo apt-get install {dep}`.")
            sys.exit(1)

# Function to search for BBC programs
def search_program(query):
    try:
        result = subprocess.run(['get_iplayer', '--pid', query], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error searching for program: {result.stderr}")
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Function to display search results
def display_results(results):
    if not results:
        print("No results found.")
        return
    for idx, program in enumerate(results):
        print(f"{idx + 1}. Title: {program['title']}")
        print(f"   Synopsis: {program['synopsis']}")
        print(f"   Duration: {program['duration']}")
        print(f"   Available Versions: {', '.join(program['available_versions'])}")

# Function to download a selected program
def download_program(pid, version, destination):
    try:
        result = subprocess.run(['get_iplayer', '--pid', pid, '--type', version, '--output', destination], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error downloading program: {result.stderr}")
            return False
        print(f"Program downloaded successfully to {destination}")
        return True
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

# Function to manage downloads
def manage_downloads():
    while True:
        print("\nManage Downloads:")
        print("1. Pause")
        print("2. Resume")
        print("3. Delete")
        print("4. Display Progress")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            # Pause logic
            pass
        elif choice == '2':
            # Resume logic
            pass
        elif choice == '3':
            # Delete logic
            pass
        elif choice == '4':
            # Display progress logic
            pass
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

# Function to handle errors
def handle_errors(error_message):
    print(f"Error: {error_message}")
    sys.exit(1)

# Function to check storage space
def check_storage(destination):
    try:
        result = subprocess.run(['df', destination], capture_output=True, text=True)
        if result.returncode != 0:
            handle_errors(f"Error checking storage space: {result.stderr}")
        output = result.stdout.splitlines()
        if len(output) < 2:
            handle_errors("Unexpected output format from df command.")
        available_space = int(output[1].split()[3])
        if available_space < 100 * 1024 * 1024:  # 100 MB threshold
            handle_errors("Insufficient storage space. Please free up some space.")
    except Exception as e:
        handle_errors(f"Exception occurred while checking storage: {e}")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Download BBC iPlayer programs to Sony Bravia TV or USB drive.")
    parser.add_argument('query', type=str, help="Search query for BBC programs.")
    parser.add_argument('--version', type=str, default='sd', help="Version of the program to download (sd, hd).")
    parser.add_argument('--destination', type=str, default='.', help="Destination path for downloaded programs.")

    args = parser.parse_args()

    check_dependencies()
    check_storage(args.destination)

    results = search_program(args.query)
    if not results:
        handle_errors("No results found for the given query.")

    display_results(results)

    if results:
        try:
            program_index = int(input("Enter the number of the program to download: ")) - 1
            if 0 <= program_index < len(results):
                pid = results[program_index]['pid']
                if not download_program(pid, args.version, args.destination):
                    handle_errors("Failed to download the selected program.")
                manage_downloads()
            else:
                handle_errors("Invalid program selection.")
        except ValueError:
            handle_errors("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()

# Installation and usage instructions
# Ensure you have Python 3 installed on your Sony Bravia TV or connected device.
# Install required dependencies:
# - ffmpeg: `sudo apt-get install ffmpeg`
# - rtmpdump: `sudo apt-get install rtmpdump`
# - get_iplayer: `pip install get_iplayer`
# Run the script:
# python get_iplayer_script.py "search query" --version sd --destination /path/to/destination

# Alternatively, use the precompiled executable:
# Run the precompiled executable:
# ./dist/get_iplayer_script "search query" --version sd --destination /path/to/destination
#!/usr/bin/env python3

import os
import subprocess
import sys
import json
import argparse

# Ensure get_iplayer is in the PATH
get_iplayer_path = os.path.join(os.getcwd(), 'get_iplayer')
if get_iplayer_path not in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + get_iplayer_path

# Function to check and install dependencies
def check_dependencies():
    dependencies = ['ffmpeg', 'rtmpdump']
    for dep in dependencies:
        try:
            subprocess.run([dep, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            print(f"{dep} is not installed. Please install it using `sudo apt-get install {dep}`.")
            sys.exit(1)

# Function to search for BBC programs
def search_program(query):
    try:
        result = subprocess.run(['get_iplayer', '--pid', query], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error searching for program: {result.stderr}")
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Function to display search results
def display_results(results):
    if not results:
        print("No results found.")
        return
    for idx, program in enumerate(results):
        print(f"{idx + 1}. Title: {program['title']}")
        print(f"   Synopsis: {program['synopsis']}")
        print(f"   Duration: {program['duration']}")
        print(f"   Available Versions: {', '.join(program['available_versions'])}")

# Function to download a selected program
def download_program(pid, version, destination):
    try:
        result = subprocess.run(['get_iplayer', '--pid', pid, '--type', version, '--output', destination], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error downloading program: {result.stderr}")
            return False
        print(f"Program downloaded successfully to {destination}")
        return True
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

# Function to manage downloads
def manage_downloads():
    while True:
        print("\nManage Downloads:")
        print("1. Pause")
        print("2. Resume")
        print("3. Delete")
        print("4. Display Progress")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            # Pause logic
            pass
        elif choice == '2':
            # Resume logic
            pass
        elif choice == '3':
            # Delete logic
            pass
        elif choice == '4':
            # Display progress logic
            pass
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

# Function to handle errors
def handle_errors(error_message):
    print(f"Error: {error_message}")
    sys.exit(1)

# Function to check storage space
def check_storage(destination):
    try:
        result = subprocess.run(['df', destination], capture_output=True, text=True)
        if result.returncode != 0:
            handle_errors(f"Error checking storage space: {result.stderr}")
        output = result.stdout.splitlines()
        if len(output) < 2:
            handle_errors("Unexpected output format from df command.")
        available_space = int(output[1].split()[3])
        if available_space < 100 * 1024 * 1024:  # 100 MB threshold
            handle_errors("Insufficient storage space. Please free up some space.")
    except Exception as e:
        handle_errors(f"Exception occurred while checking storage: {e}")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Download BBC iPlayer programs to Sony Bravia TV or USB drive.")
    parser.add_argument('query', type=str, help="Search query for BBC programs.")
    parser.add_argument('--version', type=str, default='sd', help="Version of the program to download (sd, hd).")
    parser.add_argument('--destination', type=str, default='.', help="Destination path for downloaded programs.")

    args = parser.parse_args()

    check_dependencies()
    check_storage(args.destination)

    results = search_program(args.query)
    if not results:
        handle_errors("No results found for the given query.")

    display_results(results)

    if results:
        try:
            program_index = int(input("Enter the number of the program to download: ")) - 1
            if 0 <= program_index < len(results):
                pid = results[program_index]['pid']
                if not download_program(pid, args.version, args.destination):
                    handle_errors("Failed to download the selected program.")
                manage_downloads()
            else:
                handle_errors("Invalid program selection.")
        except ValueError:
            handle_errors("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()

# Installation and usage instructions
# Ensure you have Python 3 installed on your Sony Bravia TV or connected device.
# Install required dependencies:
# - ffmpeg: `sudo apt-get install ffmpeg`
# - rtmpdump: `sudo apt-get install rtmpdump`
# - get_iplayer: `pip install get_iplayer`
# Run the script:
# python get_iplayer_script.py "search query" --version sd --destination /path/to/destination
#!/usr/bin/env python3

import os
import subprocess
import sys
import json
import argparse

# Ensure get_iplayer is in the PATH
get_iplayer_path = os.path.join(os.getcwd(), 'get_iplayer')
if get_iplayer_path not in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + get_iplayer_path

# Function to check and install dependencies
def check_dependencies():
    dependencies = ['ffmpeg', 'rtmpdump']
    for dep in dependencies:
        try:
            subprocess.run([dep, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            print(f"{dep} is not installed. Please install it using `sudo apt-get install {dep}`.")
            sys.exit(1)

# Function to search for BBC programs
def search_program(query):
    try:
        result = subprocess.run(['get_iplayer', '--pid', query], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error searching for program: {result.stderr}")
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Function to display search results
def display_results(results):
    if not results:
        print("No results found.")
        return
    for idx, program in enumerate(results):
        print(f"{idx + 1}. Title: {program['title']}")
        print(f"   Synopsis: {program['synopsis']}")
        print(f"   Duration: {program['duration']}")
        print(f"   Available Versions: {', '.join(program['available_versions'])}")

# Function to download a selected program
def download_program(pid, version, destination):
    try:
        result = subprocess.run(['get_iplayer', '--pid', pid, '--type', version, '--output', destination], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error downloading program: {result.stderr}")
            return False
        print(f"Program downloaded successfully to {destination}")
        return True
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

# Function to manage downloads
def manage_downloads():
    while True:
        print("\nManage Downloads:")
        print("1. Pause")
        print("2. Resume")
        print("3. Delete")
        print("4. Display Progress")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            # Pause logic
            pass
        elif choice == '2':
            # Resume logic
            pass
        elif choice == '3':
            # Delete logic
            pass
        elif choice == '4':
            # Display progress logic
            pass
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

# Function to handle errors
def handle_errors(error_message):
    print(f"Error: {error_message}")
    sys.exit(1)

# Main function
def main():
    parser = argparse.ArgumentParser(description="Download BBC iPlayer programs to Sony Bravia TV or USB drive.")
    parser.add_argument('query', type=str, help="Search query for BBC programs.")
    parser.add_argument('--version', type=str, default='sd', help="Version of the program to download (sd, hd).")
    parser.add_argument('--destination', type=str, default='.', help="Destination path for downloaded programs.")

    args = parser.parse_args()

    check_dependencies()

    results = search_program(args.query)
    if not results:
        handle_errors("No results found for the given query.")

    display_results(results)

    if results:
        try:
            program_index = int(input("Enter the number of the program to download: ")) - 1
            if 0 <= program_index < len(results):
                pid = results[program_index]['pid']
                if not download_program(pid, args.version, args.destination):
                    handle_errors("Failed to download the selected program.")
                manage_downloads()
            else:
                handle_errors("Invalid program selection.")
        except ValueError:
            handle_errors("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()

# Installation and usage instructions
# Ensure you have Python 3 installed on your Sony Bravia TV or connected device.
# Install required dependencies:
# - ffmpeg: `sudo apt-get install ffmpeg`
# - rtmpdump: `sudo apt-get install rtmpdump`
# - get_iplayer: `pip install get_iplayer`
# Run the script:
# python get_iplayer_script.py "search query" --version sd --destination /path/to/destination
#!/usr/bin/env python3

import os
import subprocess
import sys
import json
import argparse

# Ensure get_iplayer is in the PATH
get_iplayer_path = os.path.join(os.getcwd(), 'get_iplayer')
if get_iplayer_path not in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + get_iplayer_path

# Function to check and install dependencies
def check_dependencies():
    dependencies = ['ffmpeg', 'rtmpdump']
    for dep in dependencies:
        try:
            subprocess.run([dep, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            print(f"{dep} is not installed. Please install it using `sudo apt-get install {dep}`.")
            sys.exit(1)

# Function to search for BBC programs
def search_program(query):
    try:
        result = subprocess.run(['get_iplayer', '--pid', query], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error searching for program: {result.stderr}")
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Function to display search results
def display_results(results):
    if not results:
        print("No results found.")
        return
    for idx, program in enumerate(results):
        print(f"{idx + 1}. Title: {program['title']}")
        print(f"   Synopsis: {program['synopsis']}")
        print(f"   Duration: {program['duration']}")
        print(f"   Available Versions: {', '.join(program['available_versions'])}")

# Function to download a selected program
def download_program(pid, version, destination):
    try:
        result = subprocess.run(['get_iplayer', '--pid', pid, '--type', version, '--output', destination], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error downloading program: {result.stderr}")
            return False
        print(f"Program downloaded successfully to {destination}")
        return True
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

# Function to manage downloads
def manage_downloads():
    while True:
        print("\nManage Downloads:")
        print("1. Pause")
        print("2. Resume")
        print("3. Delete")
        print("4. Display Progress")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            # Pause logic
            pass
        elif choice == '2':
            # Resume logic
            pass
        elif choice == '3':
            # Delete logic
            pass
        elif choice == '4':
            # Display progress logic
            pass
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Download BBC iPlayer programs to Sony Bravia TV or USB drive.")
    parser.add_argument('query', type=str, help="Search query for BBC programs.")
    parser.add_argument('--version', type=str, default='sd', help="Version of the program to download (sd, hd).")
    parser.add_argument('--destination', type=str, default='.', help="Destination path for downloaded programs.")

    args = parser.parse_args()

    check_dependencies()

    results = search_program(args.query)
    display_results(results)

    if results:
        program_index = int(input("Enter the number of the program to download: ")) - 1
        if 0 <= program_index < len(results):
            pid = results[program_index]['pid']
            download_program(pid, args.version, args.destination)
            manage_downloads()
        else:
            print("Invalid program selection.")

if __name__ == "__main__":
    main()

# Installation and usage instructions
# Ensure you have Python 3 installed on your Sony Bravia TV or connected device.
# Install required dependencies:
# - ffmpeg: `sudo apt-get install ffmpeg`
# - rtmpdump: `sudo apt-get install rtmpdump`
# - get_iplayer: `pip install get_iplayer`
# Run the script:
# python get_iplayer_script.py "search query" --version sd --destination /path/to/destination
#!/usr/bin/env python3

import os
import subprocess
import sys
import json
import argparse

# Ensure get_iplayer is in the PATH
get_iplayer_path = os.path.join(os.getcwd(), 'get_iplayer')
if get_iplayer_path not in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + get_iplayer_path

# Function to search for BBC programs
def search_program(query):
    try:
        result = subprocess.run(['get_iplayer', '--pid', query], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error searching for program: {result.stderr}")
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Function to display search results
def display_results(results):
    if not results:
        print("No results found.")
        return
    for idx, program in enumerate(results):
        print(f"{idx + 1}. Title: {program['title']}")
        print(f"   Synopsis: {program['synopsis']}")
        print(f"   Duration: {program['duration']}")
        print(f"   Available Versions: {', '.join(program['available_versions'])}")

# Function to download a selected program
def download_program(pid, version, destination):
    try:
        result = subprocess.run(['get_iplayer', '--pid', pid, '--type', version, '--output', destination], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error downloading program: {result.stderr}")
            return False
        print(f"Program downloaded successfully to {destination}")
        return True
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

# Function to manage downloads
def manage_downloads():
    while True:
        print("\nManage Downloads:")
        print("1. Pause")
        print("2. Resume")
        print("3. Delete")
        print("4. Display Progress")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            # Pause logic
            pass
        elif choice == '2':
            # Resume logic
            pass
        elif choice == '3':
            # Delete logic
            pass
        elif choice == '4':
            # Display progress logic
            pass
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Download BBC iPlayer programs to Sony Bravia TV or USB drive.")
    parser.add_argument('query', type=str, help="Search query for BBC programs.")
    parser.add_argument('--version', type=str, default='sd', help="Version of the program to download (sd, hd).")
    parser.add_argument('--destination', type=str, default='.', help="Destination path for downloaded programs.")

    args = parser.parse_args()

    results = search_program(args.query)
    display_results(results)

    if results:
        program_index = int(input("Enter the number of the program to download: ")) - 1
        if 0 <= program_index < len(results):
            pid = results[program_index]['pid']
            download_program(pid, args.version, args.destination)
            manage_downloads()
        else:
            print("Invalid program selection.")

if __name__ == "__main__":
    main()

# Installation and usage instructions
# Ensure you have Python 3 installed on your Sony Bravia TV or connected device.
# Install required dependencies:
# - ffmpeg: `sudo apt-get install ffmpeg`
# - rtmpdump: `sudo apt-get install rtmpdump`
# - get_iplayer: `pip install get_iplayer`
# Run the script:
# python get_iplayer_script.py "search query" --version sd --destination /path/to/destination
#!/usr/bin/env python3

import os
import subprocess
import sys
import json
import argparse

# Ensure get_iplayer is in the PATH
get_iplayer_path = os.path.join(os.getcwd(), 'get_iplayer')
if get_iplayer_path not in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + get_iplayer_path

# Function to search for BBC programs
def search_program(query):
    try:
        result = subprocess.run(['get_iplayer', '--pid', query], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error searching for program: {result.stderr}")
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Function to display search results
def display_results(results):
    if not results:
        print("No results found.")
        return
    for idx, program in enumerate(results):
        print(f"{idx + 1}. Title: {program['title']}")
        print(f"   Synopsis: {program['synopsis']}")
        print(f"   Duration: {program['duration']}")
        print(f"   Available Versions: {', '.join(program['available_versions'])}")

# Function to download a selected program
def download_program(pid, version, destination):
    try:
        result = subprocess.run(['get_iplayer', '--pid', pid, '--type', version, '--output', destination], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error downloading program: {result.stderr}")
            return False
        print(f"Program downloaded successfully to {destination}")
        return True
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

# Function to manage downloads
def manage_downloads():
    while True:
        print("\nManage Downloads:")
        print("1. Pause")
        print("2. Resume")
        print("3. Delete")
        print("4. Display Progress")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            # Pause logic
            pass
        elif choice == '2':
            # Resume logic
            pass
        elif choice == '3':
            # Delete logic
            pass
        elif choice == '4':
            # Display progress logic
            pass
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Download BBC iPlayer programs to Sony Bravia TV or USB drive.")
    parser.add_argument('query', type=str, help="Search query for BBC programs.")
    parser.add_argument('--version', type=str, default='sd', help="Version of the program to download (sd, hd).")
    parser.add_argument('--destination', type=str, default='.', help="Destination path for downloaded programs.")

    args = parser.parse_args()

    results = search_program(args.query)
    display_results(results)

    if results:
        program_index = int(input("Enter the number of the program to download: ")) - 1
        if 0 <= program_index < len(results):
            pid = results[program_index]['pid']
            download_program(pid, args.version, args.destination)
            manage_downloads()
        else:
            print("Invalid program selection.")

if __name__ == "__main__":
    main()

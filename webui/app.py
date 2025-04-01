import os
import subprocess
import re
import socket
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your secret key' # Needed for flashing messages

# --- Configuration ---
# Adjust this path if get_iplayer_source is located elsewhere relative to webui/app.py
GET_IPLAYER_SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'get_iplayer_source'))
GET_IPLAYER_SCRIPT = os.path.join(GET_IPLAYER_SOURCE_DIR, 'get_iplayer')
DOWNLOAD_DIR = os.path.expanduser('~/iPlayerDownloads') # Use the user's home directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
THUMBNAIL_DIR = os.path.join(STATIC_DIR, 'thumbnails')

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
# Ensure thumbnail directory exists
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

# --- Routes ---

@app.route('/')
def index():
    """Displays the main search page."""
    return render_template('index.html')

def _run_get_iplayer_command(cmd_args):
    """Helper function to run get_iplayer command and handle common errors."""
    try:
        cmd = [GET_IPLAYER_SCRIPT] + cmd_args
        process = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=GET_IPLAYER_SOURCE_DIR, timeout=120) # Increased timeout

        if process.returncode != 0:
            return None, f"get_iplayer command failed. Error: {process.stderr[:500]}"

        # Check for common warnings that indicate no actual data
        if "WARNING: No programmes are available" in process.stdout or \
           "INFO: 0 matching programmes" in process.stdout:
             return [], None # Return empty list, no error message needed for 'not found'

        return process.stdout, None

    except FileNotFoundError:
         return None, f"Error: Could not find get_iplayer script at {GET_IPLAYER_SCRIPT}. Ensure the path is correct."
    except subprocess.TimeoutExpired:
         return None, f"Error: get_iplayer command timed out after 120 seconds."
    except Exception as e:
        return None, f"An unexpected error occurred running get_iplayer: {str(e)}"

def _parse_get_iplayer_output(output):
    """Parses the text output of get_iplayer list/search."""
    results = []
    """Parses the text output of get_iplayer list/search."""
    results = []
    if not output:
        return results

    # Simpler line-by-line parsing approach
    lines = output.strip().split('\n')
    for line in lines:
        line = line.strip()
        # Check if line starts with digits followed by a colon (potential result line)
        match = re.match(r'^(\d+):\s+(.*)', line)
        if match:
            index = match.group(1)
            details = match.group(2).strip()
            # Try to split the rest by the last comma to get PID
            parts = details.rsplit(',', 1)
            pid = ""
            name_channel = details # Default if no PID found
            if len(parts) == 2 and re.match(r'^[a-zA-Z0-9_]{8}$', parts[1].strip()):
                pid = parts[1].strip()
                name_channel = parts[0].strip() # Everything before the PID

            # Try to split name_channel by the last comma before PID to get channel
            parts2 = name_channel.rsplit(',', 1)
            channel = "N/A"
            name = name_channel # Default if no channel found
            if len(parts2) == 2:
                 # Basic check if the last part looks like a channel name (heuristic)
                 # This is imperfect but better than nothing
                 potential_channel = parts2[1].strip()
                 if "BBC" in potential_channel or "S4C" in potential_channel or "Radio" in potential_channel:
                     channel = potential_channel
                     name = parts2[0].strip()

            results.append({
                'index': index,
                'name': name,
                'channel': channel,
                'pid': pid
            })

    # Add basic logging to see what was parsed
    # print(f"Parsed {len(results)} results.") 
    # if not results and output:
    #     print(f"Failed to parse output:\n{output[:500]}")

    return results


@app.route('/search', methods=['POST'])
def search():
    """Handles the search request."""
    """Handles the search request."""
    query = request.form.get('query')
    if not query:
        flash('Please enter a search query.', 'error')
        return redirect(url_for('index'))

    output, error_message = _run_get_iplayer_command(['--type=tv', query])

    if error_message:
        flash(error_message, 'error')
        return redirect(url_for('index'))

    results = _parse_get_iplayer_output(output)
    
    if not results and not error_message: # If parsing failed or returned empty but no command error
         flash(f"No matching programmes found for '{query}' or could not parse results.", 'warning')
         # Optionally show raw output: flash(f"Raw output:\n{output[:500]}", 'info')
         # return redirect(url_for('index')) # Or show results page with message

    return render_template('results.html', query=query, results=results)

@app.route('/list')
def list_all():
    """Lists all available TV programmes from the cache, with sorting."""
    sort_by = request.args.get('sort_by', 'index') # Default sort by index

    output, error_message = _run_get_iplayer_command(['--type=tv', '.*'])

    if error_message:
        flash(error_message, 'error')
        return redirect(url_for('index'))

    results = _parse_get_iplayer_output(output)

    if not results and not error_message:
        flash("No programmes found in cache. Try refreshing get_iplayer cache manually.", 'warning')
        # Optionally show raw output: flash(f"Raw output:\n{output[:500]}", 'info')
        # return redirect(url_for('index')) # Or show list page with message
    else:
        # Sort results based on query parameter
        try:
            if sort_by == 'name':
                results.sort(key=lambda x: x['name'].lower())
            elif sort_by == 'channel':
                # Sort by channel, then by name within the channel
                results.sort(key=lambda x: (x['channel'].lower(), x['name'].lower()))
            else: # Default to index sort (numeric)
                results.sort(key=lambda x: int(x['index']))
        except ValueError:
             # Fallback if index isn't purely numeric for some reason
             results.sort(key=lambda x: x['index'])
        except Exception as e:
            print(f"Error during sorting: {e}") # Log error but proceed with unsorted/partially sorted list

    # Group results by channel for better display
    grouped_results = {}
    if results:
        # Ensure results are sorted primarily by channel if grouping
        if sort_by != 'channel': # If sorting by index or name, sort by channel first for grouping
             results.sort(key=lambda x: (x['channel'].lower(), x['name'].lower() if sort_by == 'name' else int(x['index'])))
        
        for result in results:
            channel = result['channel']
            if channel not in grouped_results:
                grouped_results[channel] = []
            grouped_results[channel].append(result)

    return render_template('list.html', grouped_results=grouped_results, current_sort=sort_by)


@app.route('/download/<index>')
def download(index):
    """Handles the download request for a specific index."""
    if not index.isdigit():
         flash('Invalid program index.', 'error')
         return redirect(url_for('index'))

    # We need the PID to name the thumbnail
    # Ideally, we'd get this from the list/search results passed via session or cache,
    # but for simplicity now, we run a quick info command first.
    # This adds overhead but avoids complex state management for this example.
    pid = None
    try:
        info_cmd = [GET_IPLAYER_SCRIPT, '--info', '--pid-recursive', index]
        info_process = subprocess.run(info_cmd, capture_output=True, text=True, check=False, cwd=GET_IPLAYER_SOURCE_DIR, timeout=30)
        if info_process.returncode == 0:
             pid_match = re.search(r'pid:\s+([a-zA-Z0-9_]+)', info_process.stdout)
             if pid_match:
                 pid = pid_match.group(1)
                 print(f"Found PID {pid} for index {index}") # Debugging
    except Exception as e:
        print(f"Could not get PID for index {index}: {e}") # Debugging only

    try:
        # Construct download command with subdirectory based on show name
        # Using <nameshort> creates a folder named after the show
        # Using <filename> keeps the original filename structure
        file_prefix_arg = "--file-prefix=<nameshort>/<filename>"
        cmd = [GET_IPLAYER_SCRIPT, '--get', index, '--output', DOWNLOAD_DIR, file_prefix_arg]

        # Run download command in the background
        # Note: Error checking here is limited as we don't wait for completion
        print(f"Running download command: {' '.join(cmd)}") # Debugging
        subprocess.Popen(cmd, cwd=GET_IPLAYER_SOURCE_DIR,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # Hide output

        flash(f'Download started for program index {index}. Files will be saved in a subfolder within {DOWNLOAD_DIR}.', 'success')

        # Attempt to download thumbnail if we found a PID
        if pid:
            try:
                thumb_cmd = [GET_IPLAYER_SCRIPT, '--get', index, '--thumbnail', '--output', THUMBNAIL_DIR, f'--file-prefix={pid}']
                print(f"Running thumbnail command: {' '.join(thumb_cmd)}") # Debugging
                # Run this one and wait briefly, as thumbnails are usually quick
                thumb_proc = subprocess.run(thumb_cmd, cwd=GET_IPLAYER_SOURCE_DIR, timeout=30,
                                            capture_output=True, text=True, check=False)
                if thumb_proc.returncode != 0:
                     print(f"Thumbnail download failed for PID {pid}: {thumb_proc.stderr[:200]}") # Debugging
                else:
                     print(f"Thumbnail downloaded for PID {pid}") # Debugging
            except Exception as te:
                 print(f"Error downloading thumbnail for PID {pid}: {te}") # Debugging

    except FileNotFoundError:
         flash(f"Error: Could not find get_iplayer script at {GET_IPLAYER_SCRIPT}.", 'error')
    except Exception as e:
        flash(f"An error occurred starting the download: {str(e)}", 'error')

    return redirect(url_for('index'))


# --- Function to find an available port ---
def find_available_port(start_port=5000, host='127.0.0.1'):
    """Finds an available TCP port starting from start_port."""
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Try to bind to the port on the specified host
                s.bind((host, port))
                # If bind succeeds, the port is available
                return port
            except OSError:
                # Port is already in use, try the next one
                port += 1
    # If no port is found
    raise IOError("No available port found in the range")

if __name__ == '__main__':
    host_ip = '0.0.0.0' # Makes it accessible on the local network
    try:
        port = find_available_port(start_port=5000, host=host_ip)
        print(f" * Found available port: {port}")
        # Debug=True is helpful during development but should be False in production
        app.run(host=host_ip, port=port, debug=True)
    except IOError as e:
        print(f"Error finding available port: {e}")
    except Exception as e:
        print(f"An error occurred running the app: {e}")

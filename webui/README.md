# get_iplayer Web UI

This is a simple Flask web application that provides a browser-based user interface for searching and downloading BBC iPlayer TV programmes using the `get_iplayer` command-line tool.

## Prerequisites

1.  **Python 3:** Ensure Python 3 (version 3.7 or later recommended, 3.12 used for development) is installed on the machine where you will run this web UI.
2.  **Working `get_iplayer`:** This web UI relies on a functional `get_iplayer` installation. Ensure that:
    *   `get_iplayer` (preferably the latest development version from the `get_iplayer_source` directory in the parent folder) is executable.
    *   Perl and all necessary Perl modules (`LWP::Protocol::https`, `Mojolicious`, `Mozilla::CA`, etc.) are installed.
    *   `ffmpeg` is installed and available in the system's PATH.
    *   You can successfully run `get_iplayer` commands (like searching and downloading) from the terminal in the `get_iplayer_source` directory.

## Setup

1.  **Navigate:** Open a terminal or command prompt and navigate into this `webui` directory.
    ```bash
    cd path/to/daddytv/webui
    ```
2.  **Create Virtual Environment (Recommended):** If you haven't already, create a Python virtual environment. Replace `python3.12` with your Python 3 command if different.
    ```bash
    python3.12 -m venv venv
    ```
3.  **Activate Virtual Environment:**
    *   macOS/Linux: `source venv/bin/activate`
    *   Windows (Command Prompt): `venv\Scripts\activate.bat`
    *   Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
4.  **Install Flask:**
    ```bash
    pip install Flask
    ```

## Running the Web UI

1.  **Ensure Environment is Activated:** Make sure your virtual environment (`venv`) is activated in the terminal.
2.  **Run Flask App:** Execute the `app.py` script.
    ```bash
    python app.py
    ```
3.  **Access UI:** Open a web browser and go to the address shown in the terminal output. It will likely be `http://127.0.0.1:5000` or `http://0.0.0.0:5000`. If accessing from another device on your local network, use your computer's local IP address instead of `127.0.0.1` (e.g., `http://192.168.1.100:5000`).

## Usage

*   Enter a search term for a TV show in the box and click "Search".
*   The results page will show matching programmes found by `get_iplayer`.
*   Click the "Download" button next to a programme to start the download process in the background on the server machine. Downloads will be saved to the `~/iPlayerDownloads` folder (or as configured in `app.py`).
*   A message indicating the download has started will appear on the main page.

## Notes

*   The path to the `get_iplayer` script and the download directory are configured near the top of `app.py`. Adjust these if your setup differs.
*   Download progress is not currently shown in the UI. Downloads run in the background. Check the terminal where `app.py` is running or the download folder for status.
*   Error handling is basic. If `get_iplayer` commands fail, an error message should be displayed.

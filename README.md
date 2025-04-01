# BBC iPlayer Downloader for Sony Bravia TV

## Overview
This project provides a Python script to download BBC iPlayer programs directly to a Sony Bravia TV running Android TV 9 or a connected USB drive for playback on the TV. The script is designed to be user-friendly and executable directly on the Bravia TV.

## Features
- Search for BBC programs by title, keyword, or PID.
- Display search results including title, synopsis, duration, and available versions (e.g., SD, HD).
- Allow selection of specific programs and versions for download.
- Choose the download destination: Bravia's internal storage or a connected USB drive (identified by path/label).
- Manage downloads: pause, resume, delete, and display progress.
- Enable seamless playback of downloaded programs directly on the Bravia TV using a compatible media player.
- Handle `get_iplayer` dependencies (e.g., `ffmpeg`, `rtmpdump`) and potential compatibility issues on Android TV 9.

## Installation and Usage

### Prerequisites
Ensure you have Python 3 installed on your Sony Bravia TV or connected device.

### Steps

1. **Plug in USB**:
   - Plug the USB drive into the Sony Bravia TV.

2. **Run the Executable**:
   - On the Bravia TV, navigate to the USB drive and run the precompiled executable.
   - Use the executable to search for and download BBC iPlayer programs directly to the USB drive.

3. **Playback**:
   - The downloaded programs should be accessible and playable directly on the Bravia TV using a compatible media player.

### Dependencies
The precompiled executable includes all necessary dependencies. However, if you need to install them manually, use the following commands:
- `ffmpeg`: `sudo apt-get install ffmpeg`
- `rtmpdump`: `sudo apt-get install rtmpdump`
- `get_iplayer`: `pip install get_iplayer`

## Precompiled Executable
The precompiled executable is located in the `dist` directory. To use it, follow these steps:
1. Copy the precompiled executable (`dist/get_iplayer_script`) to the USB drive.
2. Ensure the USB drive has enough storage space for the downloaded programs.
3. Include any necessary dependencies (e.g., `ffmpeg`, `rtmpdump`, `get_iplayer`) on the USB drive.

## Script Documentation
For more detailed instructions and script usage, refer to the `get_iplayer_script.py` file.

## License
This project is licensed under the MIT License.

## Contact
For any questions or issues, please contact the project maintainer.

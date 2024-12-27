# Media File Sorter

A desktop application for organizing and managing files with preview support for images and videos.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/file-organizer.git
cd file-organizer
```

2. Install required packages:

```bash
pip install pillow opencv-python python-vlc
```

3. Install VLC media player if you haven't already (required for video preview)

## Running the Application

```bash
python main.py
```

## How to Use

1. Click "Scan Directory" to choose a folder to organize
2. Add output folders using "Add Output Folder"
3. Select files to see their preview and metadata
4. Click on an output folder button to move the selected file there
5. Use the search bar to filter files
6. Use Undo/Redo buttons to reverse or repeat actions

## Features

### File Management

- Scan directories recursively
- Preview images and videos
- View file metadata
- Rename files while organizing
- Move files to output folders
- Search and filter files
- Undo/Redo support

### Preview Support

- Image thumbnails
- Video playback with controls
- Metadata display

### File Operations

- Create multiple output folders
- One-click file organization
- Automatic file renaming for duplicates
- Keep track of file operations history

## Technical Details

- Built with Python and Tkinter
- Uses VLC for video playback
- Supports common image and video formats
- Handles large directories efficiently with threading
- Maintains aspect ratio in previews

## Requirements

- Python 3.6+
- VLC media player
- PIL (Pillow)
- OpenCV
- python-vlc

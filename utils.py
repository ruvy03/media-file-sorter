import os
from pathlib import Path
from PIL import Image
import hashlib
from datetime import datetime
import shutil
from typing import Dict, List, Optional, Tuple
import mimetypes
import logging
import cv2
from PIL import Image
import threading
from tkinter import ttk

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_file_hash(filepath: str) -> str:
    try:
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)  # Read in 64kb chunks
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error generating hash for {filepath}: {e}")
        return "hash_error"

def generate_thumbnail(file_path: str, container_size: Tuple[int, int]) -> Optional[Image.Image]:
    try:
        if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            # Handle video files
            cap = cv2.VideoCapture(file_path)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
            else:
                return None
        else:
            # Handle image files
            img = Image.open(file_path)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Calculate scaling factors for both width and height
        width_ratio = container_size[0] / img.width
        height_ratio = container_size[1] / img.height
        
        # Use the smaller ratio to ensure the image fits entirely within the container
        scale_factor = min(width_ratio, height_ratio) * 0.95  # 95% of the container size for padding
        
        # Calculate new dimensions
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)
        
        # Resize image
        resized_img = img.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )
        
        # Create centered background
        background = Image.new('RGB', container_size, (43, 43, 43))
        x = (container_size[0] - new_width) // 2
        y = (container_size[1] - new_height) // 2
        background.paste(resized_img, (x, y))
        
        return background
        
    except Exception as e:
        logger.error(f"Error generating thumbnail for {file_path}: {e}")
        return None

def get_safe_size(file_stat) -> int:
    try:
        return file_stat.st_size
    except Exception:
        return 0

def get_safe_time(timestamp) -> str:
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Unknown"

def get_file_metadata(filepath: str) -> Dict:
    try:
        file_stat = os.stat(filepath)
        file_type = mimetypes.guess_type(filepath)[0] or "unknown"
        
        metadata = {
            "name": os.path.basename(filepath),
            "size": get_safe_size(file_stat),
            "created": get_safe_time(file_stat.st_ctime),
            "modified": get_safe_time(file_stat.st_mtime),
            "type": file_type,
        }
        
        if metadata["size"] < 100 * 1024 * 1024:
            metadata["hash"] = get_file_hash(filepath)
        else:
            metadata["hash"] = "large_file"
        
        if file_type and file_type.startswith('image'):
            try:
                with Image.open(filepath) as img:
                    metadata.update({
                        "dimensions": img.size,
                        "format": img.format,
                        "mode": img.mode
                    })
            except Exception as e:
                logger.error(f"Error reading image metadata for {filepath}: {e}")
                metadata.update({
                    "dimensions": "unknown",
                    "format": "unknown",
                    "mode": "unknown"
                })
        
        return metadata
    except Exception as e:
        logger.error(f"Error getting metadata for {filepath}: {e}")
        return {
            "name": os.path.basename(filepath),
            "size": 0,
            "created": "Unknown",
            "modified": "Unknown",
            "type": "unknown",
            "hash": "error"
        }

def safe_copy_file(src: str, dest: str) -> bool:
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)
        return True
    except Exception as e:
        logger.error(f"Error copying file {src} to {dest}: {e}")
        return False

def generate_unique_filename(filepath: str) -> str:
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while os.path.exists(filepath):
        filepath = os.path.join(directory, f"{name}_{counter}{ext}")
        counter += 1
    
    return filepath
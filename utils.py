import os
from pathlib import Path
from PIL import Image
import hashlib
from datetime import datetime
import shutil
from typing import Dict, List, Optional, Tuple
import mimetypes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_file_hash(filepath: str) -> str:
    try:
        hasher  = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65546)
            return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error generating has for {filepath}:{e}")
        return "hash_error"
    
def generate_thumbnail(image_path: str, size: Tuple[int,int]= (100, 100)) ->Optional[Image.Image]:
    try:
        with Image.open(image_path) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
                
            img.thumbnail(size)
            return img
    except Exception as e:
        logger.error(f"Error generating thumbnail for {image_path}: {e}")
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
    
def get_file_metadate(filepath: str) -> Dict:
    try:
        file_stat = os.stat(filepath)
        file_type = mimetypes.guess_type(filepath)[0] or "unknown"
        
        metadata = {
            "name": os.path.basename(filepath),
            "size": get_safe_size(file_stat),
            "created": get_safe_time(file_stat.st_time),
            "modified": get_safe_time(file_stat.st_mtime),
            "type": file_type,
        }
        
        if metadata["size"] < 100*1024*1024:
            metadata["hash"] = get_file_hash(filepath)
        else:
            metadata["hash"] = "large_file"
        
        if file_type and file_type.startswith("image"):
            try:
                with Image.open(filepath) as img:
                    metadate.update({
                        "dimensions":img.size,
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
        counter +=1
        
    return filepath
        
    
    

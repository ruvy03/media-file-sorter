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
    

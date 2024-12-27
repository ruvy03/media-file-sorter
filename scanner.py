from pathlib import Path
from typing import List, Dict
from utils import get_file_metadata
import logging

logger = logging.getLogger(__name__)

class FileScanner:
    def __init__(self):
        self.scanned_files: List[Dict] = []
        self.file_history: List[Dict] = []
        
    def scan_directory(self, directory: str, extensions: List[str]= None) -> List[Dict]:
        try:
            self.scanned_files.clear()
            root_path = Path(directory)
            
            if not root_path.exists():
                logger.error(f"Direcotry does not exist: {directory}")
                return []
            
            if not root_path.is_dir():
                logger.error(f"Path is not a directory: {directory}")
                return []
            
            total_files = 0
            errors = 0
            
            
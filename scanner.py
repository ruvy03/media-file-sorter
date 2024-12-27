from pathlib import Path
from typing import List, Dict
from utils import get_file_metadata
import logging

logger = logging.getLogger(__name__)

class FileScanner:
    def __init__(self):
        self.scanned_files: List[Dict] = []
        self.file_history: List[Dict] = []
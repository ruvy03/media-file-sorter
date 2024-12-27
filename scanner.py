from pathlib import Path
from typing import List, Dict
from utils import get_file_metadata
import logging

logger = logging.getLogger(__name__)

class FileScanner:
    def __init__(self):
        self.scanned_files: List[Dict] = []
        self.file_history: List[Dict] = []  # For undo/redo functionality
        
    def scan_directory(self, directory: str, extensions: List[str] = None) -> List[Dict]:
        """
        Recursively scan directory for files.
        Args:
            directory: Root directory to scan
            extensions: List of file extensions to include (e.g., ['.jpg', '.png'])
        Returns:
            List of dictionaries containing file information
        """
        try:
            self.scanned_files.clear()
            root_path = Path(directory)
            
            # Validate directory
            if not root_path.exists():
                logger.error(f"Directory does not exist: {directory}")
                return []
            
            if not root_path.is_dir():
                logger.error(f"Path is not a directory: {directory}")
                return []
            
            # Scan files
            total_files = 0
            errors = 0
            
            for file_path in root_path.rglob('*'):
                try:
                    if file_path.is_file():
                        total_files += 1
                        
                        # Skip files that match extension filter
                        if extensions and file_path.suffix.lower() not in extensions:
                            continue
                        
                        # Skip system files and hidden files
                        if file_path.name.startswith('.') or file_path.name.startswith('~$'):
                            continue
                            
                        try:
                            metadata = get_file_metadata(str(file_path))
                        except Exception as e:
                            logger.error(f"Error getting metadata for {file_path}: {e}")
                            errors += 1
                            continue
                            
                        file_info = {
                            'path': str(file_path),
                            'relative_path': str(file_path.relative_to(root_path)),
                            'metadata': metadata
                        }
                        self.scanned_files.append(file_info)
                        
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    errors += 1
                    continue
                    
            logger.info(f"Scanned {total_files} files, {len(self.scanned_files)} processed, {errors} errors")
            return self.scanned_files
            
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
            return []
    
    def filter_files(self, keyword: str = None, extension: str = None) -> List[Dict]:
        """Filter scanned files based on keyword and/or extension."""
        try:
            filtered_files = self.scanned_files.copy()
            
            if keyword:
                keyword = keyword.lower()
                filtered_files = [
                    f for f in filtered_files
                    if keyword in f['path'].lower() or
                    keyword in str(f['metadata']).lower()
                ]
                
            if extension:
                extension = extension.lower()
                filtered_files = [
                    f for f in filtered_files
                    if Path(f['path']).suffix.lower() == extension
                ]
                
            return filtered_files
        except Exception as e:
            logger.error(f"Error filtering files: {e}")
            return []
    
    def add_to_history(self, action: Dict):
        """Add an action to the history stack."""
        try:
            self.file_history.append(action)
        except Exception as e:
            logger.error(f"Error adding to history: {e}")
"""
PyDiagram - File service module

This module provides services for loading and saving diagram files
using the extended drawpyo functionality.
"""

import os
from typing import Optional

from ..model import DiagramModel
from ..integration import DrawpyoIntegration


class FileService:
    """
    Service for loading and saving diagram files.
    Provides methods to work with drawio files and other formats.
    """
    
    @staticmethod
    def load_drawio_file(file_path: str) -> Optional[DiagramModel]:
        """
        Load a diagram from a drawio file.
        
        Args:
            file_path: Path to the drawio file
            
        Returns:
            A DiagramModel object or None if loading failed
        """
        return DrawpyoIntegration.load_drawio_file(file_path)
    
    @staticmethod
    def save_drawio_file(diagram: DiagramModel, file_path: str) -> bool:
        """
        Save a diagram to a drawio file.
        
        Args:
            diagram: The diagram model to save
            file_path: Path to save the drawio file
            
        Returns:
            True if saving was successful, False otherwise
        """
        return DrawpyoIntegration.save_drawio_file(diagram, file_path)
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        Get the file extension from a file path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            The file extension (lowercase, without the dot)
        """
        _, ext = os.path.splitext(file_path)
        return ext.lower()[1:] if ext else ""

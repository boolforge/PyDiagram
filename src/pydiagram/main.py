"""
PyDiagram - Main application module

This module provides the entry point for the PyDiagram application,
integrating the extended drawpyo functionality with the PyQt5 GUI.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

from .view import MainWindow
from .model import DiagramModel
from .controller import DiagramController


def main():
    """
    Main entry point for the PyDiagram application.
    
    This function initializes the application, creates the main window,
    and starts the event loop.
    """
    # Create application
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

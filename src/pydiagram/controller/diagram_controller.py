"""
PyDiagram - Diagram controller module

This module defines the controller for diagram operations.
It handles the high-level operations on diagrams and coordinates
between the model and view.
"""

from typing import List, Dict, Any, Optional, Tuple, Callable
from ..model import DiagramModel, PageModel, ElementModel, ShapeModel, ConnectorModel, GroupModel
from .commands import Command, CommandManager


class AddShapeCommand(Command):
    """Command for adding a shape to a page."""
    
    def __init__(self, page: PageModel, shape: ShapeModel, description: str = "Add Shape"):
        """
        Initialize a new add shape command.
        
        Args:
            page: The page to add the shape to
            shape: The shape to add
            description: Human-readable description of the command
        """
        super().__init__(description)
        self._page = page
        self._shape = shape
    
    def execute(self) -> None:
        """Execute the command by adding the shape to the page."""
        self._page.add_element(self._shape)
    
    def undo(self) -> None:
        """Undo the command by removing the shape from the page."""
        self._page.remove_element(self._shape)


class RemoveElementCommand(Command):
    """Command for removing an element from a page."""
    
    def __init__(self, page: PageModel, element: ElementModel, description: str = "Remove Element"):
        """
        Initialize a new remove element command.
        
        Args:
            page: The page to remove the element from
            element: The element to remove
            description: Human-readable description of the command
        """
        super().__init__(description)
        self._page = page
        self._element = element
    
    def execute(self) -> None:
        """Execute the command by removing the element from the page."""
        self._page.remove_element(self._element)
    
    def undo(self) -> None:
        """Undo the command by adding the element back to the page."""
        self._page.add_element(self._element)


class MoveElementCommand(Command):
    """Command for moving an element to a new position."""
    
    def __init__(self, element: ElementModel, new_position: Tuple[float, float], 
                 description: str = "Move Element"):
        """
        Initialize a new move element command.
        
        Args:
            element: The element to move
            new_position: The new position (x, y)
            description: Human-readable description of the command
        """
        super().__init__(description)
        self._element = element
        self._new_position = new_position
        self._old_position = element.position
    
    def execute(self) -> None:
        """Execute the command by moving the element to the new position."""
        self._element.position = self._new_position
    
    def undo(self) -> None:
        """Undo the command by moving the element back to the old position."""
        self._element.position = self._old_position


class ResizeShapeCommand(Command):
    """Command for resizing a shape."""
    
    def __init__(self, shape: ShapeModel, new_width: float, new_height: float, 
                 description: str = "Resize Shape"):
        """
        Initialize a new resize shape command.
        
        Args:
            shape: The shape to resize
            new_width: The new width
            new_height: The new height
            description: Human-readable description of the command
        """
        super().__init__(description)
        self._shape = shape
        self._new_width = new_width
        self._new_height = new_height
        self._old_width = shape.width
        self._old_height = shape.height
    
    def execute(self) -> None:
        """Execute the command by resizing the shape."""
        self._shape.set_size(self._new_width, self._new_height)
    
    def undo(self) -> None:
        """Undo the command by restoring the original size."""
        self._shape.set_size(self._old_width, self._old_height)


class DiagramController:
    """
    Controller for diagram operations.
    Handles high-level operations on diagrams and coordinates between model and view.
    """
    
    def __init__(self, diagram: DiagramModel):
        """
        Initialize a new diagram controller.
        
        Args:
            diagram: The diagram model to control
        """
        self._diagram = diagram
        self._command_manager = CommandManager()
        self._selection: List[ElementModel] = []
        self._current_page: Optional[PageModel] = None
        
        # Set the first page as current if available
        if self._diagram.pages:
            self._current_page = self._diagram.pages[0]
    
    @property
    def diagram(self) -> DiagramModel:
        """Get the diagram model."""
        return self._diagram
    
    @property
    def command_manager(self) -> CommandManager:
        """Get the command manager."""
        return self._command_manager
    
    @property
    def current_page(self) -> Optional[PageModel]:
        """Get the current page."""
        return self._current_page
    
    @current_page.setter
    def current_page(self, page: PageModel) -> None:
        """
        Set the current page.
        
        Args:
            page: The page to set as current
        """
        if page in self._diagram.pages:
            self._current_page = page
            self.clear_selection()
    
    @property
    def selection(self) -> List[ElementModel]:
        """Get the currently selected elements."""
        return self._selection.copy()
    
    def select_element(self, element: ElementModel) -> None:
        """
        Select an element.
        
        Args:
            element: The element to select
        """
        if element not in self._selection:
            self._selection.append(element)
    
    def deselect_element(self, element: ElementModel) -> None:
        """
        Deselect an element.
        
        Args:
            element: The element to deselect
        """
        if element in self._selection:
            self._selection.remove(element)
    
    def clear_selection(self) -> None:
        """Clear the current selection."""
        self._selection.clear()
    
    def add_shape(self, shape_type: str, x: float, y: float, width: float = 100, 
                 height: float = 60, text: str = "") -> Optional[ShapeModel]:
        """
        Add a new shape to the current page.
        
        Args:
            shape_type: Type of shape (rectangle, ellipse, etc.)
            x: X coordinate
            y: Y coordinate
            width: Width of the shape
            height: Height of the shape
            text: Text content of the shape
            
        Returns:
            The created shape or None if no current page
        """
        if not self._current_page:
            return None
        
        # Create a unique ID for the shape
        element_id = f"shape_{len(self._current_page.elements) + 1}"
        
        # Create the shape
        shape = ShapeModel(element_id, text, shape_type)
        shape.position = (x, y)
        shape.set_size(width, height)
        
        # Execute the command to add the shape
        command = AddShapeCommand(self._current_page, shape, f"Add {shape_type}")
        self._command_manager.execute_command(command)
        
        return shape
    
    def add_connector(self, source_id: Optional[str], target_id: Optional[str], 
                     waypoints: List[Tuple[float, float]] = None, 
                     text: str = "") -> Optional[ConnectorModel]:
        """
        Add a new connector to the current page.
        
        Args:
            source_id: ID of the source element or None
            target_id: ID of the target element or None
            waypoints: List of waypoints for the connector
            text: Text content of the connector
            
        Returns:
            The created connector or None if no current page
        """
        if not self._current_page:
            return None
        
        # Create a unique ID for the connector
        element_id = f"connector_{len(self._current_page.elements) + 1}"
        
        # Create the connector
        connector = ConnectorModel(element_id, text, source_id, target_id)
        
        # Add waypoints if provided
        if waypoints:
            for x, y in waypoints:
                connector.add_waypoint(x, y)
        
        # Execute the command to add the connector
        command = AddShapeCommand(self._current_page, connector, "Add Connector")
        self._command_manager.execute_command(command)
        
        return connector
    
    def remove_element(self, element: ElementModel) -> bool:
        """
        Remove an element from the current page.
        
        Args:
            element: The element to remove
            
        Returns:
            True if the element was removed, False otherwise
        """
        if not self._current_page:
            return False
        
        # Execute the command to remove the element
        command = RemoveElementCommand(self._current_page, element, "Remove Element")
        self._command_manager.execute_command(command)
        
        # Deselect the element if it was selected
        if element in self._selection:
            self.deselect_element(element)
        
        return True
    
    def move_element(self, element: ElementModel, x: float, y: float) -> bool:
        """
        Move an element to a new position.
        
        Args:
            element: The element to move
            x: New X coordinate
            y: New Y coordinate
            
        Returns:
            True if the element was moved, False otherwise
        """
        # Execute the command to move the element
        command = MoveElementCommand(element, (x, y), "Move Element")
        self._command_manager.execute_command(command)
        
        return True
    
    def resize_shape(self, shape: ShapeModel, width: float, height: float) -> bool:
        """
        Resize a shape.
        
        Args:
            shape: The shape to resize
            width: New width
            height: New height
            
        Returns:
            True if the shape was resized, False otherwise
        """
        if width <= 0 or height <= 0:
            return False
        
        # Execute the command to resize the shape
        command = ResizeShapeCommand(shape, width, height, "Resize Shape")
        self._command_manager.execute_command(command)
        
        return True
    
    def create_new_diagram(self, name: str = "Untitled Diagram") -> None:
        """
        Create a new diagram, replacing the current one.
        
        Args:
            name: Name of the new diagram
        """
        self._diagram = DiagramModel(name)
        self._current_page = None
        self._selection.clear()
        self._command_manager.clear_history()
        
        # Create an initial page
        self.add_page("Page 1")
    
    def add_page(self, name: str = "New Page") -> Optional[PageModel]:
        """
        Add a new page to the diagram.
        
        Args:
            name: Name of the new page
            
        Returns:
            The created page
        """
        page = PageModel(name)
        self._diagram.add_page(page)
        
        # Set as current page if no current page
        if not self._current_page:
            self._current_page = page
        
        return page
    
    def remove_page(self, page: PageModel) -> bool:
        """
        Remove a page from the diagram.
        
        Args:
            page: The page to remove
            
        Returns:
            True if the page was removed, False otherwise
        """
        if page in self._diagram.pages:
            # If removing the current page, set another page as current
            if page == self._current_page:
                pages = self._diagram.pages
                index = pages.index(page)
                
                # Try to set the next page as current, or the previous if at the end
                if index < len(pages) - 1:
                    self._current_page = pages[index + 1]
                elif index > 0:
                    self._current_page = pages[index - 1]
                else:
                    self._current_page = None
            
            self._diagram.remove_page(page)
            self.clear_selection()
            return True
        
        return False

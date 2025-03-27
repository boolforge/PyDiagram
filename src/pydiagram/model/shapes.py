"""
PyDiagram - Shape model module

This module defines the classes for shape elements in a diagram.
"""

from typing import Tuple, Dict, Any, Optional, List
from .base import ElementModel


class ShapeModel(ElementModel):
    """
    Model representing a shape element in a diagram.
    Shapes are visual elements like rectangles, circles, etc.
    """
    
    def __init__(self, element_id: str, value: str = "", shape_type: str = "rectangle"):
        """
        Initialize a new shape.
        
        Args:
            element_id: Unique ID of the element
            value: Text or value of the element
            shape_type: Type of shape (rectangle, ellipse, etc.)
        """
        super().__init__(element_id, value)
        self._shape_type = shape_type
        self._width = 100.0
        self._height = 60.0
        self._rotation = 0.0
        
        # Set default style based on shape type
        self.set_style("shape", shape_type)
        self.set_style("whiteSpace", "wrap")
        self.set_style("html", "1")
        self.set_style("fillColor", "#ffffff")
        self.set_style("strokeColor", "#000000")
        self.set_style("strokeWidth", "1")
    
    @property
    def shape_type(self) -> str:
        """Get the type of shape."""
        return self._shape_type
    
    @shape_type.setter
    def shape_type(self, value: str) -> None:
        """
        Set the type of shape.
        
        Args:
            value: New shape type
        """
        if value != self._shape_type:
            old_type = self._shape_type
            self._shape_type = value
            self.set_style("shape", value)
            self.notify_observers('shape_type_changed', 
                                {'old_type': old_type, 'new_type': value})
    
    @property
    def width(self) -> float:
        """Get the width of the shape."""
        return self._width
    
    @width.setter
    def width(self, value: float) -> None:
        """
        Set the width of the shape.
        
        Args:
            value: New width
        """
        if value != self._width and value > 0:
            old_width = self._width
            self._width = value
            self.notify_observers('size_changed', 
                                {'width': {'old': old_width, 'new': value}, 'height': self._height})
    
    @property
    def height(self) -> float:
        """Get the height of the shape."""
        return self._height
    
    @height.setter
    def height(self, value: float) -> None:
        """
        Set the height of the shape.
        
        Args:
            value: New height
        """
        if value != self._height and value > 0:
            old_height = self._height
            self._height = value
            self.notify_observers('size_changed', 
                                {'height': {'old': old_height, 'new': value}, 'width': self._width})
    
    def set_size(self, width: float, height: float) -> None:
        """
        Set both width and height at once.
        
        Args:
            width: New width
            height: New height
        """
        if (width != self._width or height != self._height) and width > 0 and height > 0:
            old_width = self._width
            old_height = self._height
            self._width = width
            self._height = height
            self.notify_observers('size_changed', 
                                {'width': {'old': old_width, 'new': width}, 
                                 'height': {'old': old_height, 'new': height}})
    
    @property
    def rotation(self) -> float:
        """Get the rotation angle of the shape in degrees."""
        return self._rotation
    
    @rotation.setter
    def rotation(self, value: float) -> None:
        """
        Set the rotation angle of the shape.
        
        Args:
            value: New rotation angle in degrees
        """
        # Normalize to 0-360 range
        value = value % 360
        if value != self._rotation:
            old_rotation = self._rotation
            self._rotation = value
            self.set_style("rotation", str(value))
            self.notify_observers('rotation_changed', 
                                {'old_rotation': old_rotation, 'new_rotation': value})
    
    def clone(self) -> 'ShapeModel':
        """
        Create a copy of the shape.
        
        Returns:
            A new instance with the same properties
        """
        clone = ShapeModel(self.id + "_clone", self.value, self.shape_type)
        clone.position = self.position
        clone.set_size(self.width, self.height)
        clone.rotation = self.rotation
        clone.parent_id = self.parent_id
        
        # Copy all styles
        for key, value in self._style.items():
            clone.set_style(key, value)
        
        return clone


class GroupModel(ElementModel):
    """
    Model representing a group of elements in a diagram.
    Groups can contain shapes, connectors, and other groups.
    """
    
    def __init__(self, element_id: str, value: str = ""):
        """
        Initialize a new group.
        
        Args:
            element_id: Unique ID of the element
            value: Text or value of the element
        """
        super().__init__(element_id, value)
        self._children_ids: List[str] = []
        self._collapsed = False
        
        # Set default style for groups
        self.set_style("group", "1")
        self.set_style("fillColor", "none")
        self.set_style("strokeColor", "#666666")
        self.set_style("dashed", "1")
    
    @property
    def children_ids(self) -> List[str]:
        """Get the list of child element IDs."""
        return self._children_ids.copy()
    
    def add_child(self, child_id: str) -> None:
        """
        Add a child element to the group.
        
        Args:
            child_id: ID of the child element
        """
        if child_id not in self._children_ids:
            self._children_ids.append(child_id)
            self.notify_observers('child_added', {'child_id': child_id})
    
    def remove_child(self, child_id: str) -> None:
        """
        Remove a child element from the group.
        
        Args:
            child_id: ID of the child element
        """
        if child_id in self._children_ids:
            self._children_ids.remove(child_id)
            self.notify_observers('child_removed', {'child_id': child_id})
    
    @property
    def collapsed(self) -> bool:
        """Get whether the group is collapsed."""
        return self._collapsed
    
    @collapsed.setter
    def collapsed(self, value: bool) -> None:
        """
        Set whether the group is collapsed.
        
        Args:
            value: True to collapse, False to expand
        """
        if value != self._collapsed:
            self._collapsed = value
            self.notify_observers('collapsed_changed', {'collapsed': value})
    
    def clone(self) -> 'GroupModel':
        """
        Create a copy of the group.
        
        Returns:
            A new instance with the same properties
        """
        clone = GroupModel(self.id + "_clone", self.value)
        clone.position = self.position
        clone.parent_id = self.parent_id
        clone.collapsed = self.collapsed
        
        # Copy all styles
        for key, value in self._style.items():
            clone.set_style(key, value)
        
        # Copy children IDs
        for child_id in self._children_ids:
            clone.add_child(child_id + "_clone")
        
        return clone

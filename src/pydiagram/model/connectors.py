"""
PyDiagram - Connector model module

This module defines the classes for connector elements in a diagram.
Connectors are used to connect shapes and other elements.
"""

from typing import Tuple, Dict, Any, Optional, List
from .base import ElementModel


class ConnectorModel(ElementModel):
    """
    Model representing a connector element in a diagram.
    Connectors are lines that connect shapes and other elements.
    """
    
    def __init__(self, element_id: str, value: str = "", 
                 source_id: Optional[str] = None, target_id: Optional[str] = None):
        """
        Initialize a new connector.
        
        Args:
            element_id: Unique ID of the element
            value: Text or value of the element
            source_id: ID of the source element
            target_id: ID of the target element
        """
        super().__init__(element_id, value)
        self._source_id = source_id
        self._target_id = target_id
        self._waypoints: List[Tuple[float, float]] = []
        
        # Set default style for connectors
        self.set_style("edgeStyle", "orthogonalEdgeStyle")
        self.set_style("rounded", "0")
        self.set_style("orthogonalLoop", "1")
        self.set_style("jettySize", "auto")
        self.set_style("html", "1")
        self.set_style("strokeColor", "#000000")
        self.set_style("strokeWidth", "1")
    
    @property
    def source_id(self) -> Optional[str]:
        """Get the ID of the source element."""
        return self._source_id
    
    @source_id.setter
    def source_id(self, value: Optional[str]) -> None:
        """
        Set the ID of the source element.
        
        Args:
            value: ID of the source element or None
        """
        if value != self._source_id:
            old_source_id = self._source_id
            self._source_id = value
            self.notify_observers('source_changed', 
                                {'old_source_id': old_source_id, 'new_source_id': value})
    
    @property
    def target_id(self) -> Optional[str]:
        """Get the ID of the target element."""
        return self._target_id
    
    @target_id.setter
    def target_id(self, value: Optional[str]) -> None:
        """
        Set the ID of the target element.
        
        Args:
            value: ID of the target element or None
        """
        if value != self._target_id:
            old_target_id = self._target_id
            self._target_id = value
            self.notify_observers('target_changed', 
                                {'old_target_id': old_target_id, 'new_target_id': value})
    
    @property
    def waypoints(self) -> List[Tuple[float, float]]:
        """Get the list of waypoints for the connector."""
        return self._waypoints.copy()
    
    def add_waypoint(self, x: float, y: float, index: Optional[int] = None) -> None:
        """
        Add a waypoint to the connector.
        
        Args:
            x: X coordinate of the waypoint
            y: Y coordinate of the waypoint
            index: Index to insert the waypoint at, or None to append
        """
        waypoint = (x, y)
        if index is None:
            self._waypoints.append(waypoint)
        else:
            self._waypoints.insert(index, waypoint)
        self.notify_observers('waypoint_added', {'waypoint': waypoint, 'index': index})
    
    def remove_waypoint(self, index: int) -> None:
        """
        Remove a waypoint from the connector.
        
        Args:
            index: Index of the waypoint to remove
        """
        if 0 <= index < len(self._waypoints):
            waypoint = self._waypoints.pop(index)
            self.notify_observers('waypoint_removed', {'waypoint': waypoint, 'index': index})
    
    def clear_waypoints(self) -> None:
        """Remove all waypoints from the connector."""
        if self._waypoints:
            self._waypoints.clear()
            self.notify_observers('waypoints_cleared', {})
    
    def set_edge_style(self, style: str) -> None:
        """
        Set the edge style of the connector.
        
        Args:
            style: Edge style (e.g., 'orthogonalEdgeStyle', 'entityRelationEdgeStyle')
        """
        old_style = self.get_style("edgeStyle")
        self.set_style("edgeStyle", style)
        self.notify_observers('edge_style_changed', 
                            {'old_style': old_style, 'new_style': style})
    
    def set_start_arrow(self, arrow_type: str) -> None:
        """
        Set the start arrow type.
        
        Args:
            arrow_type: Arrow type (e.g., 'none', 'classic', 'diamond')
        """
        old_arrow = self.get_style("startArrow")
        self.set_style("startArrow", arrow_type)
        self.notify_observers('start_arrow_changed', 
                            {'old_arrow': old_arrow, 'new_arrow': arrow_type})
    
    def set_end_arrow(self, arrow_type: str) -> None:
        """
        Set the end arrow type.
        
        Args:
            arrow_type: Arrow type (e.g., 'none', 'classic', 'diamond')
        """
        old_arrow = self.get_style("endArrow")
        self.set_style("endArrow", arrow_type)
        self.notify_observers('end_arrow_changed', 
                            {'old_arrow': old_arrow, 'new_arrow': arrow_type})
    
    def clone(self) -> 'ConnectorModel':
        """
        Create a copy of the connector.
        
        Returns:
            A new instance with the same properties
        """
        clone = ConnectorModel(self.id + "_clone", self.value, 
                              self.source_id + "_clone" if self.source_id else None,
                              self.target_id + "_clone" if self.target_id else None)
        clone.position = self.position
        clone.parent_id = self.parent_id
        
        # Copy all styles
        for key, value in self._style.items():
            clone.set_style(key, value)
        
        # Copy waypoints
        for waypoint in self._waypoints:
            clone.add_waypoint(waypoint[0], waypoint[1])
        
        return clone

"""
PyDiagram - Main view module

This module implements the main application window and UI components
using PyQt5 for the graphical interface.
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QMessageBox,
    QToolBar, QDockWidget, QListWidget, QMenu, QVBoxLayout, QWidget,
    QLabel, QSplitter, QHBoxLayout, QComboBox, QPushButton
)
from PyQt5.QtGui import QIcon, QPainter, QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QRect, QPoint, QSize

from ..model import DiagramModel, PageModel, ShapeModel, ConnectorModel, GroupModel
from ..controller import DiagramController
from ..services import FileService, ExportService


class DiagramView(QWidget):
    """
    Widget for displaying and editing a diagram.
    This is the main canvas where shapes and connectors are drawn and manipulated.
    """
    
    def __init__(self, parent=None):
        """
        Initialize a new diagram view.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        
        # Set white background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)
        
        # Initialize controller and model references
        self._controller = None
        self._diagram = None
        self._current_page = None
        
        # State variables
        self._grid_size = 20
        self._show_grid = True
        self._zoom_level = 1.0
        self._pan_offset = QPoint(0, 0)
        
        # Editing state
        self._is_dragging = False
        self._drag_start = QPoint(0, 0)
        self._selected_elements = []
        self._current_tool = "select"  # select, rectangle, ellipse, connector
        self._creating_shape = False
        self._creation_start = QPoint(0, 0)
        self._temp_shape = None
    
    def set_controller(self, controller):
        """
        Set the diagram controller.
        
        Args:
            controller: The diagram controller
        """
        self._controller = controller
        self._diagram = controller.diagram
        self._current_page = controller.current_page
        self.update()
    
    def set_current_tool(self, tool):
        """
        Set the current editing tool.
        
        Args:
            tool: Tool name (select, rectangle, ellipse, connector)
        """
        self._current_tool = tool
        self.setCursor(Qt.ArrowCursor)
        
        if tool == "select":
            self.setCursor(Qt.ArrowCursor)
        elif tool in ["rectangle", "ellipse"]:
            self.setCursor(Qt.CrossCursor)
        elif tool == "connector":
            self.setCursor(Qt.CrossCursor)
    
    def paintEvent(self, event):
        """
        Paint the diagram view.
        
        Args:
            event: Paint event
        """
        if not self._current_page:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Apply zoom and pan
        painter.translate(self._pan_offset)
        painter.scale(self._zoom_level, self._zoom_level)
        
        # Draw grid if enabled
        if self._show_grid:
            self._draw_grid(painter)
        
        # Draw elements
        for element in self._current_page.elements:
            if isinstance(element, ShapeModel):
                self._draw_shape(painter, element)
            elif isinstance(element, ConnectorModel):
                self._draw_connector(painter, element)
        
        # Draw selection rectangles
        for element in self._selected_elements:
            if isinstance(element, ShapeModel):
                x, y = element.position
                rect = QRect(int(x), int(y), int(element.width), int(element.height))
                painter.setPen(QPen(QColor(0, 120, 215), 1, Qt.DashLine))
                painter.setBrush(QBrush())
                painter.drawRect(rect)
                
                # Draw resize handles
                handle_size = 8
                painter.setBrush(QBrush(QColor(0, 120, 215)))
                
                # Top-left
                painter.drawRect(int(x) - handle_size//2, int(y) - handle_size//2, handle_size, handle_size)
                # Top-right
                painter.drawRect(int(x) + int(element.width) - handle_size//2, int(y) - handle_size//2, handle_size, handle_size)
                # Bottom-left
                painter.drawRect(int(x) - handle_size//2, int(y) + int(element.height) - handle_size//2, handle_size, handle_size)
                # Bottom-right
                painter.drawRect(int(x) + int(element.width) - handle_size//2, int(y) + int(element.height) - handle_size//2, handle_size, handle_size)
        
        # Draw temporary shape during creation
        if self._creating_shape and self._temp_shape:
            self._draw_shape(painter, self._temp_shape)
    
    def _draw_grid(self, painter):
        """
        Draw the grid.
        
        Args:
            painter: QPainter object
        """
        width = self.width()
        height = self.height()
        
        # Adjust for zoom and pan
        width = int(width / self._zoom_level)
        height = int(height / self._zoom_level)
        
        # Calculate grid offset based on pan
        offset_x = -self._pan_offset.x() / self._zoom_level
        offset_y = -self._pan_offset.y() / self._zoom_level
        
        # Calculate grid start and end points
        start_x = int(offset_x - (offset_x % self._grid_size))
        start_y = int(offset_y - (offset_y % self._grid_size))
        end_x = int(offset_x + width)
        end_y = int(offset_y + height)
        
        # Set grid pen
        painter.setPen(QPen(QColor(230, 230, 230), 1))
        
        # Draw vertical lines
        for x in range(start_x, end_x, self._grid_size):
            painter.drawLine(x, start_y, x, end_y)
        
        # Draw horizontal lines
        for y in range(start_y, end_y, self._grid_size):
            painter.drawLine(start_x, y, end_x, y)
    
    def _draw_shape(self, painter, shape):
        """
        Draw a shape.
        
        Args:
            painter: QPainter object
            shape: ShapeModel to draw
        """
        x, y = shape.position
        width = shape.width
        height = shape.height
        
        # Set fill and stroke
        fill_color = QColor(shape.get_style("fillColor", "#ffffff"))
        stroke_color = QColor(shape.get_style("strokeColor", "#000000"))
        stroke_width = int(shape.get_style("strokeWidth", "1"))
        
        painter.setPen(QPen(stroke_color, stroke_width))
        painter.setBrush(QBrush(fill_color))
        
        # Draw based on shape type
        if shape.shape_type == "rectangle":
            if shape.get_style("rounded", "0") == "1":
                painter.drawRoundedRect(int(x), int(y), int(width), int(height), 10, 10)
            else:
                painter.drawRect(int(x), int(y), int(width), int(height))
        
        elif shape.shape_type == "ellipse":
            painter.drawEllipse(int(x), int(y), int(width), int(height))
        
        elif shape.shape_type == "triangle":
            points = [
                QPoint(int(x + width/2), int(y)),
                QPoint(int(x), int(y + height)),
                QPoint(int(x + width), int(y + height))
            ]
            painter.drawPolygon(points)
        
        elif shape.shape_type == "diamond":
            points = [
                QPoint(int(x + width/2), int(y)),
                QPoint(int(x + width), int(y + height/2)),
                QPoint(int(x + width/2), int(y + height)),
                QPoint(int(x), int(y + height/2))
            ]
            painter.drawPolygon(points)
        
        else:
            # Default to rectangle for unknown shapes
            painter.drawRect(int(x), int(y), int(width), int(height))
        
        # Draw text if present
        if shape.value:
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(
                QRect(int(x), int(y), int(width), int(height)),
                Qt.AlignCenter,
                shape.value
            )
    
    def _draw_connector(self, painter, connector):
        """
        Draw a connector.
        
        Args:
            painter: QPainter object
            connector: ConnectorModel to draw
        """
        # Set stroke
        stroke_color = QColor(connector.get_style("strokeColor", "#000000"))
        stroke_width = int(connector.get_style("strokeWidth", "1"))
        
        painter.setPen(QPen(stroke_color, stroke_width))
        painter.setBrush(QBrush())
        
        # Get source and target positions
        source_pos = None
        target_pos = None
        
        if connector.source_id:
            source_element = next((e for e in self._current_page.elements if e.id == connector.source_id), None)
            if source_element and isinstance(source_element, ShapeModel):
                sx, sy = source_element.position
                source_pos = QPoint(
                    int(sx + source_element.width/2),
                    int(sy + source_element.height/2)
                )
        
        if connector.target_id:
            target_element = next((e for e in self._current_page.elements if e.id == connector.target_id), None)
            if target_element and isinstance(target_element, ShapeModel):
                tx, ty = target_element.position
                target_pos = QPoint(
                    int(tx + target_element.width/2),
                    int(ty + target_element.height/2)
                )
        
        # Use element position if source/target not found
        if not source_pos:
            x, y = connector.position
            source_pos = QPoint(int(x), int(y))
        
        if not target_pos:
            x, y = connector.position
            target_pos = QPoint(int(x + 100), int(y))  # Default offset
        
        # Draw the connector
        waypoints = connector.waypoints
        if waypoints:
            # Use waypoints if available
            path = [source_pos]
            for wx, wy in waypoints:
                path.append(QPoint(int(wx), int(wy)))
            path.append(target_pos)
            
            for i in range(len(path) - 1):
                painter.drawLine(path[i], path[i + 1])
        else:
            # Simple straight line
            painter.drawLine(source_pos, target_pos)
        
        # Draw arrowhead if specified
        end_arrow = connector.get_style("endArrow", "none")
        if end_arrow != "none":
            # Calculate arrowhead points
            angle = 0.5  # 30 degrees in radians
            length = 15
            
            # Get the direction vector
            if waypoints:
                last_point = QPoint(int(waypoints[-1][0]), int(waypoints[-1][1]))
                dx = target_pos.x() - last_point.x()
                dy = target_pos.y() - last_point.y()
            else:
                dx = target_pos.x() - source_pos.x()
                dy = target_pos.y() - source_pos.y()
            
            # Normalize
            dist = (dx**2 + dy**2)**0.5
            if dist > 0:
                dx /= dist
                dy /= dist
            
            # Calculate arrowhead points
            p1 = QPoint(
                int(target_pos.x() - length * (dx * 0.866 + dy * 0.5)),
                int(target_pos.y() - length * (dy * 0.866 - dx * 0.5))
            )
            p2 = QPoint(
                int(target_pos.x() - length * (dx * 0.866 - dy * 0.5)),
                int(target_pos.y() - length * (dy * 0.866 + dx * 0.5))
            )
            
            # Draw arrowhead
            points = [target_pos, p1, p2]
            painter.setBrush(QBrush(stroke_color))
            painter.drawPolygon(points)
        
        # Draw text if present
        if connector.value:
            # Calculate midpoint
            if waypoints:
                mid_idx = len(waypoints) // 2
                mid_x, mid_y = waypoints[mid_idx]
            else:
                mid_x = (source_pos.x() + target_pos.x()) / 2
                mid_y = (source_pos.y() + target_pos.y()) / 2
            
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.setFont(QFont("Arial", 10))
            
            # Draw text with white background
            text_rect = painter.fontMetrics().boundingRect(connector.value)
            text_rect.moveCenter(QPoint(int(mid_x), int(mid_y)))
            text_rect.adjust(-5, -2, 5, 2)  # Add padding
            
            painter.fillRect(text_rect, QBrush(QColor(255, 255, 255, 220)))
            painter.drawText(
                QPoint(int(mid_x - text_rect.width()/2 + 5), int(mid_y + painter.fontMetrics().height()/4)),
                connector.value
            )
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Args:
            event: Mouse event
        """
        if not self._current_page:
            return
        
        # Convert to diagram coordinates
        pos = self._screen_to_diagram(event.pos())
        
        if event.button() == Qt.LeftButton:
            if self._current_tool == "select":
                # Check if clicked on an element
                element = self._element_at_position(pos)
                
                if element:
                    # Select the element
                    if not (event.modifiers() & Qt.ControlModifier):
                        self._selected_elements.clear()
                    
                    if element not in self._selected_elements:
                        self._selected_elements.append(element)
                        if self._controller:
                            self._controller.select_element(element)
                    
                    # Start dragging
                    self._is_dragging = True
                    self._drag_start = pos
                else:
                    # Clear selection if clicked on empty space
                    self._selected_elements.clear()
                    if self._controller:
                        self._controller.clear_selection()
            
            elif self._current_tool in ["rectangle", "ellipse"]:
                # Start creating a shape
                self._creating_shape = True
                self._creation_start = pos
                
                # Create temporary shape
                element_id = f"temp_shape"
                shape_type = self._current_tool
                self._temp_shape = ShapeModel(element_id, "", shape_type)
                self._temp_shape.position = (pos.x(), pos.y())
                self._temp_shape.set_size(1, 1)  # Will be updated during mouse move
            
            elif self._current_tool == "connector":
                # Check if clicked on a shape to start connector
                element = self._element_at_position(pos)
                
                if element and isinstance(element, ShapeModel):
                    # Start creating a connector
                    self._creating_shape = True
                    self._creation_start = pos
                    
                    # Create temporary connector
                    element_id = f"temp_connector"
                    self._temp_shape = ConnectorModel(element_id, "", element.id, None)
                    self._temp_shape.position = (pos.x(), pos.y())
        
        elif event.button() == Qt.RightButton:
            # Show context menu
            element = self._element_at_position(pos)
            
            if element:
                menu = QMenu(self)
                
                if isinstance(element, ShapeModel):
                    menu.addAction("Edit Text", lambda: self._edit_element_text(element))
                    menu.addAction("Delete", lambda: self._delete_element(element))
                
                elif isinstance(element, ConnectorModel):
                    menu.addAction("Edit Text", lambda: self._edit_element_text(element))
                    menu.addAction("Delete", lambda: self._delete_element(element))
                
                menu.exec_(event.globalPos())
        
        self.update()
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move events.
        
        Args:
            event: Mouse event
        """
        if not self._current_page:
            return
        
        # Convert to diagram coordinates
        pos = self._screen_to_diagram(event.pos())
        
        if self._is_dragging and self._selected_elements:
            # Calculate the drag delta
            delta_x = pos.x() - self._drag_start.x()
            delta_y = pos.y() - self._drag_start.y()
            
            # Move selected elements
            for element in self._selected_elements:
                if isinstance(element, ShapeModel) or isinstance(element, ConnectorModel):
                    x, y = element.position
                    new_x = x + delta_x
                    new_y = y + delta_y
                    
                    if self._controller:
                        self._controller.move_element(element, new_x, new_y)
            
            # Update drag start for next move
            self._drag_start = pos
            self.update()
        
        elif self._creating_shape and self._temp_shape:
            if isinstance(self._temp_shape, ShapeModel):
                # Update temporary shape size
                width = abs(pos.x() - self._creation_start.x())
                height = abs(pos.y() - self._creation_start.y())
                
                # Ensure minimum size
                width = max(width, 10)
                height = max(height, 10)
                
                # Update position to top-left corner
                x = min(self._creation_start.x(), pos.x())
                y = min(self._creation_start.y(), pos.y())
                
                self._temp_shape.position = (x, y)
                self._temp_shape.set_size(width, height)
            
            elif isinstance(self._temp_shape, ConnectorModel):
                # Update temporary connector endpoint
                element = self._element_at_position(pos)
                
                if element and isinstance(element, ShapeModel):
                    self._temp_shape.target_id = element.id
                else:
                    self._temp_shape.target_id = None
                    # Add waypoint at current position
                    if not self._temp_shape.waypoints:
                        self._temp_shape.add_waypoint(pos.x(), pos.y())
                    else:
                        # Update last waypoint
                        self._temp_shape._waypoints[-1] = (pos.x(), pos.y())
            
            self.update()
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events.
        
        Args:
            event: Mouse event
        """
        if not self._current_page or not self._controller:
            return
        
        # Convert to diagram coordinates
        pos = self._screen_to_diagram(event.pos())
        
        if event.button() == Qt.LeftButton:
            if self._is_dragging:
                self._is_dragging = False
            
            elif self._creating_shape and self._temp_shape:
                if isinstance(self._temp_shape, ShapeModel):
                    # Finalize shape creation
                    shape_type = self._temp_shape.shape_type
                    x, y = self._temp_shape.position
                    width = self._temp_shape.width
                    height = self._temp_shape.height
                    
                    # Create actual shape if size is reasonable
                    if width >= 10 and height >= 10:
                        self._controller.add_shape(
                            shape_type, x, y, width, height, ""
                        )
                
                elif isinstance(self._temp_shape, ConnectorModel):
                    # Finalize connector creation
                    source_id = self._temp_shape.source_id
                    target_id = self._temp_shape.target_id
                    
                    # Create actual connector if both ends are connected
                    if source_id and target_id:
                        self._controller.add_connector(source_id, target_id, [], "")
                
                self._creating_shape = False
                self._temp_shape = None
        
        self.update()
    
    def wheelEvent(self, event):
        """
        Handle mouse wheel events for zooming.
        
        Args:
            event: Wheel event
        """
        # Get the position before zoom
        old_pos = self._screen_to_diagram(event.pos())
        
        # Zoom in/out
        zoom_factor = 1.1
        if event.angleDelta().y() > 0:
            self._zoom_level *= zoom_factor
        else:
            self._zoom_level /= zoom_factor
        
        # Limit zoom level
        self._zoom_level = max(0.1, min(self._zoom_level, 5.0))
        
        # Get the position after zoom
        new_pos = self._screen_to_diagram(event.pos())
        
        # Adjust pan to keep the point under cursor
        self._pan_offset += QPoint(
            int((new_pos.x() - old_pos.x()) * self._zoom_level),
            int((new_pos.y() - old_pos.y()) * self._zoom_level)
        )
        
        self.update()
    
    def _screen_to_diagram(self, pos):
        """
        Convert screen coordinates to diagram coordinates.
        
        Args:
            pos: Screen position
            
        Returns:
            Position in diagram coordinates
        """
        x = (pos.x() - self._pan_offset.x()) / self._zoom_level
        y = (pos.y() - self._pan_offset.y()) / self._zoom_level
        return QPoint(int(x), int(y))
    
    def _diagram_to_screen(self, pos):
        """
        Convert diagram coordinates to screen coordinates.
        
        Args:
            pos: Diagram position
            
        Returns:
            Position in screen coordinates
        """
        x = pos.x() * self._zoom_level + self._pan_offset.x()
        y = pos.y() * self._zoom_level + self._pan_offset.y()
        return QPoint(int(x), int(y))
    
    def _element_at_position(self, pos):
        """
        Find the element at the given position.
        
        Args:
            pos: Position to check
            
        Returns:
            Element at position or None
        """
        if not self._current_page:
            return None
        
        # Check in reverse order (top to bottom)
        for element in reversed(self._current_page.elements):
            if isinstance(element, ShapeModel):
                x, y = element.position
                width = element.width
                height = element.height
                
                if (x <= pos.x() <= x + width and
                    y <= pos.y() <= y + height):
                    return element
            
            elif isinstance(element, ConnectorModel):
                # Check if near the connector line
                source_pos = None
                target_pos = None
                
                if element.source_id:
                    source_element = next((e for e in self._current_page.elements if e.id == element.source_id), None)
                    if source_element and isinstance(source_element, ShapeModel):
                        sx, sy = source_element.position
                        source_pos = QPoint(
                            int(sx + source_element.width/2),
                            int(sy + source_element.height/2)
                        )
                
                if element.target_id:
                    target_element = next((e for e in self._current_page.elements if e.id == element.target_id), None)
                    if target_element and isinstance(target_element, ShapeModel):
                        tx, ty = target_element.position
                        target_pos = QPoint(
                            int(tx + target_element.width/2),
                            int(ty + target_element.height/2)
                        )
                
                # Use element position if source/target not found
                if not source_pos:
                    x, y = element.position
                    source_pos = QPoint(int(x), int(y))
                
                if not target_pos:
                    x, y = element.position
                    target_pos = QPoint(int(x + 100), int(y))
                
                # Check distance to line
                if self._point_to_line_distance(pos, source_pos, target_pos) < 5:
                    return element
        
        return None
    
    def _point_to_line_distance(self, point, line_start, line_end):
        """
        Calculate the distance from a point to a line segment.
        
        Args:
            point: Point to check
            line_start: Start point of line
            line_end: End point of line
            
        Returns:
            Distance from point to line
        """
        # Vector from line_start to line_end
        line_vec = QPoint(line_end.x() - line_start.x(), line_end.y() - line_start.y())
        
        # Vector from line_start to point
        point_vec = QPoint(point.x() - line_start.x(), point.y() - line_start.y())
        
        # Length of line
        line_len = (line_vec.x()**2 + line_vec.y()**2)**0.5
        
        if line_len == 0:
            # Line is a point
            return ((point.x() - line_start.x())**2 + (point.y() - line_start.y())**2)**0.5
        
        # Project point_vec onto line_vec
        proj = (point_vec.x() * line_vec.x() + point_vec.y() * line_vec.y()) / line_len
        
        # Clamp projection to line segment
        proj = max(0, min(line_len, proj))
        
        # Calculate closest point on line
        closest_x = line_start.x() + (proj / line_len) * line_vec.x()
        closest_y = line_start.y() + (proj / line_len) * line_vec.y()
        
        # Calculate distance
        return ((point.x() - closest_x)**2 + (point.y() - closest_y)**2)**0.5
    
    def _edit_element_text(self, element):
        """
        Edit the text of an element.
        
        Args:
            element: Element to edit
        """
        text, ok = QInputDialog.getText(
            self, "Edit Text", "Enter text:", QLineEdit.Normal, element.value
        )
        
        if ok and self._controller:
            # Update element text
            element.value = text
            self.update()
    
    def _delete_element(self, element):
        """
        Delete an element.
        
        Args:
            element: Element to delete
        """
        if self._controller:
            self._controller.remove_element(element)
            
            if element in self._selected_elements:
                self._selected_elements.remove(element)
            
            self.update()


class MainWindow(QMainWindow):
    """
    Main application window for PyDiagram.
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.setWindowTitle("PyDiagram")
        self.setMinimumSize(1024, 768)
        
        # Initialize controller and model
        self._diagram = DiagramModel("Untitled Diagram")
        self._diagram.add_page(PageModel("Page 1"))
        self._controller = DiagramController(self._diagram)
        
        # Create UI components
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_dock_widgets()
        self._create_central_widget()
        
        # Set up status bar
        self.statusBar().showMessage("Ready")
    
    def _create_actions(self):
        """Create actions for menus and toolbars."""
        # File actions
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self._new_diagram)
        
        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self._open_diagram)
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._save_diagram)
        
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self._save_diagram_as)
        
        self.export_svg_action = QAction("Export as &SVG...", self)
        self.export_svg_action.triggered.connect(self._export_svg)
        
        self.export_odp_action = QAction("Export as &ODP...", self)
        self.export_odp_action.triggered.connect(self._export_odp)
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        
        # Edit actions
        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self._undo)
        
        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self._redo)
        
        self.cut_action = QAction("Cu&t", self)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.triggered.connect(self._cut)
        
        self.copy_action = QAction("&Copy", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.triggered.connect(self._copy)
        
        self.paste_action = QAction("&Paste", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self._paste)
        
        self.delete_action = QAction("&Delete", self)
        self.delete_action.setShortcut("Delete")
        self.delete_action.triggered.connect(self._delete)
        
        # View actions
        self.zoom_in_action = QAction("Zoom &In", self)
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.triggered.connect(self._zoom_in)
        
        self.zoom_out_action = QAction("Zoom &Out", self)
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.triggered.connect(self._zoom_out)
        
        self.zoom_reset_action = QAction("&Reset Zoom", self)
        self.zoom_reset_action.setShortcut("Ctrl+0")
        self.zoom_reset_action.triggered.connect(self._zoom_reset)
        
        self.toggle_grid_action = QAction("Show &Grid", self)
        self.toggle_grid_action.setCheckable(True)
        self.toggle_grid_action.setChecked(True)
        self.toggle_grid_action.triggered.connect(self._toggle_grid)
        
        # Tool actions
        self.select_tool_action = QAction("&Select", self)
        self.select_tool_action.setCheckable(True)
        self.select_tool_action.setChecked(True)
        self.select_tool_action.triggered.connect(lambda: self._set_tool("select"))
        
        self.rectangle_tool_action = QAction("&Rectangle", self)
        self.rectangle_tool_action.setCheckable(True)
        self.rectangle_tool_action.triggered.connect(lambda: self._set_tool("rectangle"))
        
        self.ellipse_tool_action = QAction("&Ellipse", self)
        self.ellipse_tool_action.setCheckable(True)
        self.ellipse_tool_action.triggered.connect(lambda: self._set_tool("ellipse"))
        
        self.connector_tool_action = QAction("&Connector", self)
        self.connector_tool_action.setCheckable(True)
        self.connector_tool_action.triggered.connect(lambda: self._set_tool("connector"))
        
        # Create action group for tools
        self.tool_actions = [
            self.select_tool_action,
            self.rectangle_tool_action,
            self.ellipse_tool_action,
            self.connector_tool_action
        ]
    
    def _create_menus(self):
        """Create menus."""
        # File menu
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.export_svg_action)
        self.file_menu.addAction(self.export_odp_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        
        # Edit menu
        self.edit_menu = self.menuBar().addMenu("&Edit")
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.cut_action)
        self.edit_menu.addAction(self.copy_action)
        self.edit_menu.addAction(self.paste_action)
        self.edit_menu.addAction(self.delete_action)
        
        # View menu
        self.view_menu = self.menuBar().addMenu("&View")
        self.view_menu.addAction(self.zoom_in_action)
        self.view_menu.addAction(self.zoom_out_action)
        self.view_menu.addAction(self.zoom_reset_action)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.toggle_grid_action)
    
    def _create_toolbars(self):
        """Create toolbars."""
        # File toolbar
        self.file_toolbar = self.addToolBar("File")
        self.file_toolbar.addAction(self.new_action)
        self.file_toolbar.addAction(self.open_action)
        self.file_toolbar.addAction(self.save_action)
        
        # Edit toolbar
        self.edit_toolbar = self.addToolBar("Edit")
        self.edit_toolbar.addAction(self.undo_action)
        self.edit_toolbar.addAction(self.redo_action)
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addAction(self.cut_action)
        self.edit_toolbar.addAction(self.copy_action)
        self.edit_toolbar.addAction(self.paste_action)
        
        # Tool toolbar
        self.tool_toolbar = self.addToolBar("Tools")
        self.tool_toolbar.addAction(self.select_tool_action)
        self.tool_toolbar.addAction(self.rectangle_tool_action)
        self.tool_toolbar.addAction(self.ellipse_tool_action)
        self.tool_toolbar.addAction(self.connector_tool_action)
    
    def _create_dock_widgets(self):
        """Create dock widgets."""
        # Pages dock
        self.pages_dock = QDockWidget("Pages", self)
        self.pages_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.pages_list = QListWidget()
        self.pages_list.itemClicked.connect(self._page_selected)
        
        pages_widget = QWidget()
        pages_layout = QVBoxLayout(pages_widget)
        pages_layout.addWidget(self.pages_list)
        
        add_page_button = QPushButton("Add Page")
        add_page_button.clicked.connect(self._add_page)
        pages_layout.addWidget(add_page_button)
        
        self.pages_dock.setWidget(pages_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.pages_dock)
        
        # Properties dock
        self.properties_dock = QDockWidget("Properties", self)
        self.properties_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)
        
        self.properties_label = QLabel("No selection")
        self.properties_layout.addWidget(self.properties_label)
        
        self.properties_dock.setWidget(self.properties_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        
        # Update pages list
        self._update_pages_list()
    
    def _create_central_widget(self):
        """Create the central widget."""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create diagram view
        self.diagram_view = DiagramView()
        self.diagram_view.set_controller(self._controller)
        
        layout.addWidget(self.diagram_view)
        
        self.setCentralWidget(central_widget)
    
    def _update_pages_list(self):
        """Update the pages list."""
        self.pages_list.clear()
        
        for page in self._diagram.pages:
            self.pages_list.addItem(page.name)
        
        # Select current page
        if self._controller.current_page:
            index = self._diagram.pages.index(self._controller.current_page)
            self.pages_list.setCurrentRow(index)
    
    def _page_selected(self, item):
        """
        Handle page selection.
        
        Args:
            item: Selected list item
        """
        index = self.pages_list.row(item)
        if 0 <= index < len(self._diagram.pages):
            self._controller.current_page = self._diagram.pages[index]
            self.diagram_view.update()
    
    def _add_page(self):
        """Add a new page to the diagram."""
        page = self._controller.add_page(f"Page {len(self._diagram.pages) + 1}")
        self._controller.current_page = page
        self._update_pages_list()
        self.diagram_view.update()
    
    def _set_tool(self, tool):
        """
        Set the current tool.
        
        Args:
            tool: Tool name
        """
        # Update tool actions
        for action in self.tool_actions:
            action.setChecked(False)
        
        if tool == "select":
            self.select_tool_action.setChecked(True)
        elif tool == "rectangle":
            self.rectangle_tool_action.setChecked(True)
        elif tool == "ellipse":
            self.ellipse_tool_action.setChecked(True)
        elif tool == "connector":
            self.connector_tool_action.setChecked(True)
        
        # Set tool in diagram view
        self.diagram_view.set_current_tool(tool)
    
    def _new_diagram(self):
        """Create a new diagram."""
        # Check for unsaved changes
        # TODO: Implement check for unsaved changes
        
        # Create new diagram
        self._controller.create_new_diagram("Untitled Diagram")
        self.diagram_view.update()
        self._update_pages_list()
        
        self.statusBar().showMessage("New diagram created")
    
    def _open_diagram(self):
        """Open a diagram from file."""
        # Check for unsaved changes
        # TODO: Implement check for unsaved changes
        
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Diagram", "", "Draw.io Files (*.drawio);;All Files (*)"
        )
        
        if file_path:
            # Load diagram
            diagram = FileService.load_drawio_file(file_path)
            
            if diagram:
                self._diagram = diagram
                self._controller = DiagramController(self._diagram)
                self.diagram_view.set_controller(self._controller)
                self._update_pages_list()
                
                self.statusBar().showMessage(f"Opened {file_path}")
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to open diagram file."
                )
    
    def _save_diagram(self):
        """Save the diagram to file."""
        # TODO: Implement save to current file if available, otherwise save as
        self._save_diagram_as()
    
    def _save_diagram_as(self):
        """Save the diagram to a new file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Diagram", "", "Draw.io Files (*.drawio);;All Files (*)"
        )
        
        if file_path:
            # Ensure file has .drawio extension
            if not file_path.lower().endswith('.drawio'):
                file_path += '.drawio'
            
            # Save diagram
            success = FileService.save_drawio_file(self._diagram, file_path)
            
            if success:
                self.statusBar().showMessage(f"Saved to {file_path}")
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to save diagram file."
                )
    
    def _export_svg(self):
        """Export the current page as SVG."""
        if not self._controller.current_page:
            QMessageBox.warning(
                self, "Warning", "No page to export."
            )
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export as SVG", "", "SVG Files (*.svg);;All Files (*)"
        )
        
        if file_path:
            # Ensure file has .svg extension
            if not file_path.lower().endswith('.svg'):
                file_path += '.svg'
            
            # Get current page index
            page_index = self._diagram.pages.index(self._controller.current_page)
            
            # Export to SVG
            success = ExportService.export_to_svg(self._diagram, page_index, file_path) is not None
            
            if success:
                self.statusBar().showMessage(f"Exported to {file_path}")
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to export as SVG."
                )
    
    def _export_odp(self):
        """Export the diagram as ODP."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export as ODP", "", "ODP Files (*.odp);;All Files (*)"
        )
        
        if file_path:
            # Ensure file has .odp extension
            if not file_path.lower().endswith('.odp'):
                file_path += '.odp'
            
            # Export to ODP
            success = ExportService.export_to_odp(self._diagram, file_path)
            
            if success:
                self.statusBar().showMessage(f"Exported to {file_path}")
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to export as ODP."
                )
    
    def _undo(self):
        """Undo the last action."""
        if self._controller.command_manager.undo():
            self.diagram_view.update()
            self.statusBar().showMessage("Undo")
    
    def _redo(self):
        """Redo the last undone action."""
        if self._controller.command_manager.redo():
            self.diagram_view.update()
            self.statusBar().showMessage("Redo")
    
    def _cut(self):
        """Cut the selected elements."""
        # TODO: Implement cut
        self.statusBar().showMessage("Cut not implemented")
    
    def _copy(self):
        """Copy the selected elements."""
        # TODO: Implement copy
        self.statusBar().showMessage("Copy not implemented")
    
    def _paste(self):
        """Paste the copied elements."""
        # TODO: Implement paste
        self.statusBar().showMessage("Paste not implemented")
    
    def _delete(self):
        """Delete the selected elements."""
        if self._controller:
            for element in self.diagram_view._selected_elements.copy():
                self._controller.remove_element(element)
            
            self.diagram_view._selected_elements.clear()
            self.diagram_view.update()
            self.statusBar().showMessage("Deleted selected elements")
    
    def _zoom_in(self):
        """Zoom in the diagram view."""
        self.diagram_view._zoom_level *= 1.2
        self.diagram_view._zoom_level = min(self.diagram_view._zoom_level, 5.0)
        self.diagram_view.update()
        self.statusBar().showMessage(f"Zoom: {int(self.diagram_view._zoom_level * 100)}%")
    
    def _zoom_out(self):
        """Zoom out the diagram view."""
        self.diagram_view._zoom_level /= 1.2
        self.diagram_view._zoom_level = max(self.diagram_view._zoom_level, 0.1)
        self.diagram_view.update()
        self.statusBar().showMessage(f"Zoom: {int(self.diagram_view._zoom_level * 100)}%")
    
    def _zoom_reset(self):
        """Reset zoom to 100%."""
        self.diagram_view._zoom_level = 1.0
        self.diagram_view._pan_offset = QPoint(0, 0)
        self.diagram_view.update()
        self.statusBar().showMessage("Zoom: 100%")
    
    def _toggle_grid(self):
        """Toggle grid visibility."""
        self.diagram_view._show_grid = self.toggle_grid_action.isChecked()
        self.diagram_view.update()
        
        if self.diagram_view._show_grid:
            self.statusBar().showMessage("Grid shown")
        else:
            self.statusBar().showMessage("Grid hidden")


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

"""
PyDiagram - Integration module for drawpyo extended functionality

This module provides the integration between PyDiagram and the extended
drawpyo library, enabling full support for the drawio format.
"""

import sys
import os
import importlib.util
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List, Tuple

# Add the drawpyo fork to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'dependencies', 'drawpyo', 'src'))

# Import drawpyo modules
import drawpyo
from drawpyo.diagram import BaseDiagram, TreeDiagram
from drawpyo.reader import DiagramReader, parse_drawio_file
from drawpyo.writer import DiagramWriter

from ..model import DiagramModel, PageModel, ShapeModel, ConnectorModel, GroupModel


class DrawpyoIntegration:
    """
    Integration class for the extended drawpyo functionality.
    
    This class provides methods to convert between PyDiagram models and
    drawpyo objects, enabling seamless integration with the extended
    drawpyo library.
    """
    
    @staticmethod
    def load_drawio_file(file_path: str) -> Optional[DiagramModel]:
        """
        Load a drawio file using the extended drawpyo library.
        
        Args:
            file_path: Path to the drawio file
            
        Returns:
            A DiagramModel object or None if loading failed
        """
        try:
            # Use the drawpyo reader to parse the file
            drawio_content = parse_drawio_file(file_path)
            
            if not drawio_content:
                return None
            
            # Create a new diagram model
            diagram_name = os.path.basename(file_path)
            if diagram_name.endswith('.drawio'):
                diagram_name = diagram_name[:-7]  # Remove .drawio extension
                
            diagram = DiagramModel(diagram_name)
            
            # Process each page in the drawio file
            for page_idx, page_content in enumerate(drawio_content):
                page_name = page_content.get('name', f"Page {page_idx + 1}")
                page = PageModel(page_name)
                diagram.add_page(page)
                
                # Process the mxGraphModel content
                graph_model = page_content.get('content')
                if not graph_model:
                    continue
                
                # Find the root element
                root_elem = graph_model.find('root')
                if not root_elem:
                    continue
                
                # Process all mxCell elements
                cells = {}
                for cell_elem in root_elem.findall('mxCell'):
                    cell_id = cell_elem.get('id')
                    if not cell_id:
                        continue
                    
                    cells[cell_id] = cell_elem
                
                # First pass: Create all elements
                for cell_id, cell_elem in cells.items():
                    # Skip special cells (0 and 1 are reserved)
                    if cell_id in ['0', '1']:
                        continue
                    
                    # Determine if this is a vertex (shape) or edge (connector)
                    is_vertex = cell_elem.get('vertex') == '1'
                    is_edge = cell_elem.get('edge') == '1'
                    
                    if is_vertex:
                        # Create a shape
                        value = cell_elem.get('value', '')
                        style = cell_elem.get('style', '')
                        
                        # Determine shape type from style
                        shape_type = 'rectangle'  # Default
                        if 'ellipse' in style:
                            shape_type = 'ellipse'
                        elif 'triangle' in style:
                            shape_type = 'triangle'
                        elif 'rhombus' in style:
                            shape_type = 'diamond'
                        
                        # Create the shape
                        shape = ShapeModel(cell_id, value, shape_type)
                        
                        # Set style properties
                        style_props = DrawpyoIntegration._parse_style(style)
                        for key, value in style_props.items():
                            shape.set_style(key, value)
                        
                        # Set geometry
                        geometry_elem = cell_elem.find('mxGeometry')
                        if geometry_elem is not None:
                            x = float(geometry_elem.get('x', '0'))
                            y = float(geometry_elem.get('y', '0'))
                            width = float(geometry_elem.get('width', '100'))
                            height = float(geometry_elem.get('height', '40'))
                            
                            shape.position = (x, y)
                            shape.set_size(width, height)
                        
                        # Add to page
                        page.add_element(shape)
                    
                    elif is_edge:
                        # Create a connector
                        value = cell_elem.get('value', '')
                        style = cell_elem.get('style', '')
                        source = cell_elem.get('source')
                        target = cell_elem.get('target')
                        
                        # Create the connector
                        connector = ConnectorModel(cell_id, value, source, target)
                        
                        # Set style properties
                        style_props = DrawpyoIntegration._parse_style(style)
                        for key, value in style_props.items():
                            connector.set_style(key, value)
                        
                        # Set geometry and waypoints
                        geometry_elem = cell_elem.find('mxGeometry')
                        if geometry_elem is not None:
                            # Set position
                            x = float(geometry_elem.get('x', '0'))
                            y = float(geometry_elem.get('y', '0'))
                            connector.position = (x, y)
                            
                            # Add waypoints
                            for point_elem in geometry_elem.findall('mxPoint'):
                                px = float(point_elem.get('x', '0'))
                                py = float(point_elem.get('y', '0'))
                                connector.add_waypoint(px, py)
                        
                        # Add to page
                        page.add_element(connector)
            
            return diagram
        
        except Exception as e:
            print(f"Error loading drawio file: {e}")
            return None
    
    @staticmethod
    def save_drawio_file(diagram: DiagramModel, file_path: str) -> bool:
        """
        Save a diagram to a drawio file using the extended drawpyo library.
        
        Args:
            diagram: The diagram model to save
            file_path: Path to save the drawio file
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            # Create the mxfile element
            mxfile = ET.Element('mxfile')
            mxfile.set('host', 'PyDiagram')
            mxfile.set('modified', '2025-03-27T07:30:00.000Z')
            mxfile.set('agent', 'PyDiagram/1.0')
            mxfile.set('version', '14.6.13')
            mxfile.set('etag', 'PyDiagram-' + diagram.id)
            mxfile.set('type', 'device')
            
            # Add each page as a diagram element
            for page_idx, page in enumerate(diagram.pages):
                diagram_elem = ET.SubElement(mxfile, 'diagram')
                diagram_elem.set('id', f"page-{page_idx}")
                diagram_elem.set('name', page.name)
                
                # Create the mxGraphModel
                graph_model = ET.Element('mxGraphModel')
                graph_model.set('dx', '1326')
                graph_model.set('dy', '798')
                graph_model.set('grid', '1')
                graph_model.set('gridSize', '10')
                graph_model.set('guides', '1')
                graph_model.set('tooltips', '1')
                graph_model.set('connect', '1')
                graph_model.set('arrows', '1')
                graph_model.set('fold', '1')
                graph_model.set('page', '1')
                graph_model.set('pageScale', '1')
                graph_model.set('pageWidth', '850')
                graph_model.set('pageHeight', '1100')
                graph_model.set('math', '0')
                graph_model.set('shadow', '0')
                
                # Create the root element
                root = ET.SubElement(graph_model, 'root')
                
                # Add default cells (0 and 1)
                cell0 = ET.SubElement(root, 'mxCell')
                cell0.set('id', '0')
                
                cell1 = ET.SubElement(root, 'mxCell')
                cell1.set('id', '1')
                cell1.set('parent', '0')
                
                # Add each element
                for element in page.elements:
                    if isinstance(element, ShapeModel):
                        # Create a shape cell
                        cell = ET.SubElement(root, 'mxCell')
                        cell.set('id', element.id)
                        cell.set('value', element.value)
                        cell.set('style', DrawpyoIntegration._generate_style(element))
                        cell.set('parent', '1')
                        cell.set('vertex', '1')
                        
                        # Add geometry
                        geometry = ET.SubElement(cell, 'mxGeometry')
                        x, y = element.position
                        geometry.set('x', str(x))
                        geometry.set('y', str(y))
                        geometry.set('width', str(element.width))
                        geometry.set('height', str(element.height))
                        geometry.set('as', 'geometry')
                    
                    elif isinstance(element, ConnectorModel):
                        # Create a connector cell
                        cell = ET.SubElement(root, 'mxCell')
                        cell.set('id', element.id)
                        cell.set('value', element.value)
                        cell.set('style', DrawpyoIntegration._generate_style(element))
                        cell.set('parent', '1')
                        cell.set('edge', '1')
                        
                        if element.source_id:
                            cell.set('source', element.source_id)
                        if element.target_id:
                            cell.set('target', element.target_id)
                        
                        # Add geometry with waypoints
                        geometry = ET.SubElement(cell, 'mxGeometry')
                        geometry.set('relative', '1')
                        geometry.set('as', 'geometry')
                        
                        # Add waypoints
                        for wx, wy in element.waypoints:
                            point = ET.SubElement(geometry, 'mxPoint')
                            point.set('x', str(wx))
                            point.set('y', str(wy))
                
                # Convert mxGraphModel to string and add to diagram element
                graph_model_str = ET.tostring(graph_model, encoding='utf-8').decode('utf-8')
                diagram_elem.text = graph_model_str
            
            # Write to file
            tree = ET.ElementTree(mxfile)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            
            return True
        
        except Exception as e:
            print(f"Error saving drawio file: {e}")
            return False
    
    @staticmethod
    def _parse_style(style_str: str) -> Dict[str, str]:
        """
        Parse a drawio style string into a dictionary.
        
        Args:
            style_str: Style string from drawio
            
        Returns:
            Dictionary of style properties
        """
        style_dict = {}
        
        if not style_str:
            return style_dict
        
        # Split by semicolons
        parts = style_str.split(';')
        
        for part in parts:
            if not part:
                continue
            
            # Check if it's a key=value pair
            if '=' in part:
                key, value = part.split('=', 1)
                style_dict[key] = value
            else:
                # Handle flags without values
                style_dict[part] = '1'
        
        return style_dict
    
    @staticmethod
    def _generate_style(element) -> str:
        """
        Generate a drawio style string from an element.
        
        Args:
            element: Element with style properties
            
        Returns:
            Style string for drawio
        """
        style_parts = []
        
        # Add shape-specific style
        if isinstance(element, ShapeModel):
            if element.shape_type == 'rectangle':
                style_parts.append('rounded=0')
                style_parts.append('whiteSpace=wrap')
                style_parts.append('html=1')
            elif element.shape_type == 'ellipse':
                style_parts.append('ellipse')
                style_parts.append('whiteSpace=wrap')
                style_parts.append('html=1')
            elif element.shape_type == 'triangle':
                style_parts.append('triangle')
                style_parts.append('whiteSpace=wrap')
                style_parts.append('html=1')
            elif element.shape_type == 'diamond':
                style_parts.append('rhombus')
                style_parts.append('whiteSpace=wrap')
                style_parts.append('html=1')
        
        elif isinstance(element, ConnectorModel):
            style_parts.append('edgeStyle=orthogonalEdgeStyle')
            style_parts.append('rounded=0')
            style_parts.append('html=1')
            
            # Add arrow style
            if element.get_style('endArrow', 'none') != 'none':
                style_parts.append('endArrow=classic')
            else:
                style_parts.append('endArrow=none')
        
        # Add common style properties
        for key, value in element.style.items():
            # Skip properties already handled
            if key in ['shape', 'endArrow']:
                continue
                
            style_parts.append(f"{key}={value}")
        
        return ';'.join(style_parts)

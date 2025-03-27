"""
PyDiagram - File service module

This module provides services for loading and saving diagram files.
It handles different file formats including the native drawio format.
"""

import os
import base64
import zlib
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List, Tuple

from ..model import DiagramModel, PageModel, ElementModel, ShapeModel, ConnectorModel, GroupModel


class FileService:
    """
    Service for loading and saving diagram files.
    Supports the native drawio format and potentially other formats.
    """
    
    @staticmethod
    def load_drawio_file(file_path: str) -> Optional[DiagramModel]:
        """
        Load a diagram from a drawio file.
        
        Args:
            file_path: Path to the drawio file
            
        Returns:
            The loaded diagram model or None if loading failed
        """
        try:
            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Check if it's a valid drawio file
            if root.tag != 'mxfile':
                raise ValueError("Invalid drawio file: root is not <mxfile>")
            
            # Create a new diagram model
            diagram_name = os.path.basename(file_path)
            if '.' in diagram_name:
                diagram_name = diagram_name.rsplit('.', 1)[0]
            
            diagram = DiagramModel(diagram_name)
            
            # Process each diagram element (page)
            for diagram_elem in root.findall('diagram'):
                page_name = diagram_elem.get('name', 'Page')
                page_id = diagram_elem.get('id', '0')
                
                # Create a new page
                page = PageModel(page_name)
                
                # Get the diagram content
                diagram_content = diagram_elem.text.strip() if diagram_elem.text else ""
                
                # Try to parse as XML directly
                try:
                    xml_root = ET.fromstring(diagram_content)
                    if xml_root.tag != 'mxGraphModel':
                        raise ValueError("Content is not <mxGraphModel>")
                except ET.ParseError:
                    # If parsing fails, try to decompress from base64
                    try:
                        decoded = base64.b64decode(diagram_content)
                        # Try with negative wbits to handle raw deflate data
                        try:
                            xml_content = zlib.decompress(decoded, -zlib.MAX_WBITS).decode('utf-8')
                        except:
                            # Try with default wbits
                            xml_content = zlib.decompress(decoded).decode('utf-8')
                        xml_root = ET.fromstring(xml_content)
                    except Exception as e:
                        raise ValueError(f"Error decompressing diagram content: {e}")
                
                # Process the mxGraphModel
                if xml_root.tag != 'mxGraphModel':
                    raise ValueError("Content is not <mxGraphModel>")
                
                # Process the root element
                root_elem = xml_root.find('root')
                if root_elem is None:
                    raise ValueError("No <root> element found in diagram")
                
                # First pass: create all elements
                elements: Dict[str, ElementModel] = {}
                for cell_elem in root_elem.findall('mxCell'):
                    element_id = cell_elem.get('id', '')
                    if not element_id:
                        continue
                    
                    # Skip the special cells with id 0 and 1
                    if element_id in ('0', '1'):
                        continue
                    
                    parent_id = cell_elem.get('parent', '1')
                    value = cell_elem.get('value', '')
                    style = cell_elem.get('style', '')
                    
                    # Determine the type of element
                    is_vertex = cell_elem.get('vertex', '0') == '1'
                    is_edge = cell_elem.get('edge', '0') == '1'
                    
                    # Get geometry if available
                    geometry_elem = cell_elem.find('mxGeometry')
                    x = float(geometry_elem.get('x', '0')) if geometry_elem is not None else 0.0
                    y = float(geometry_elem.get('y', '0')) if geometry_elem is not None else 0.0
                    width = float(geometry_elem.get('width', '0')) if geometry_elem is not None else 0.0
                    height = float(geometry_elem.get('height', '0')) if geometry_elem is not None else 0.0
                    
                    # Create the appropriate element
                    element = None
                    if is_edge:
                        # Create a connector
                        source_id = cell_elem.get('source', None)
                        target_id = cell_elem.get('target', None)
                        element = ConnectorModel(element_id, value, source_id, target_id)
                    elif is_vertex:
                        # Determine if it's a group
                        is_group = 'group=1' in style
                        
                        if is_group:
                            # Create a group
                            element = GroupModel(element_id, value)
                        else:
                            # Create a shape
                            shape_type = 'rectangle'  # Default
                            if 'shape=' in style:
                                for part in style.split(';'):
                                    if part.startswith('shape='):
                                        shape_type = part.split('=', 1)[1]
                                        break
                            
                            element = ShapeModel(element_id, value, shape_type)
                            if width > 0 and height > 0:
                                element.set_size(width, height)
                    
                    if element:
                        element.position = (x, y)
                        element.parent_id = parent_id
                        element.apply_style_string(style)
                        elements[element_id] = element
                
                # Second pass: add elements to the page
                for element_id, element in elements.items():
                    page.add_element(element)
                
                # Add the page to the diagram
                diagram.add_page(page)
            
            return diagram
        
        except Exception as e:
            print(f"Error loading drawio file: {e}")
            return None
    
    @staticmethod
    def save_drawio_file(diagram: DiagramModel, file_path: str) -> bool:
        """
        Save a diagram to a drawio file.
        
        Args:
            diagram: The diagram model to save
            file_path: Path to save the file to
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            # Create the root element
            root = ET.Element('mxfile')
            root.set('host', 'PyDiagram')
            root.set('modified', '2025-03-27T07:29:00.000Z')
            root.set('agent', 'PyDiagram/1.0')
            root.set('version', '1.0')
            
            # Add each page as a diagram element
            for i, page in enumerate(diagram.pages):
                diagram_elem = ET.SubElement(root, 'diagram')
                diagram_elem.set('id', f'page{i}')
                diagram_elem.set('name', page.name)
                
                # Create the mxGraphModel
                graph_model = ET.Element('mxGraphModel')
                graph_model.set('dx', '1326')
                graph_model.set('dy', '798')
                graph_model.set('grid', '1')
                graph_model.set('gridSize', str(page.grid_size))
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
                
                # Create the root element for cells
                model_root = ET.SubElement(graph_model, 'root')
                
                # Add the special cells with id 0 and 1
                cell0 = ET.SubElement(model_root, 'mxCell')
                cell0.set('id', '0')
                
                cell1 = ET.SubElement(model_root, 'mxCell')
                cell1.set('id', '1')
                cell1.set('parent', '0')
                
                # Add each element
                for element in page.elements:
                    cell = ET.SubElement(model_root, 'mxCell')
                    cell.set('id', element.id)
                    cell.set('value', element.value)
                    cell.set('style', element.get_style_string())
                    
                    # Set parent
                    parent_id = element.parent_id if element.parent_id else '1'
                    cell.set('parent', parent_id)
                    
                    # Set specific attributes based on element type
                    if isinstance(element, ShapeModel):
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
                        cell.set('edge', '1')
                        
                        # Set source and target
                        if element.source_id:
                            cell.set('source', element.source_id)
                        if element.target_id:
                            cell.set('target', element.target_id)
                        
                        # Add geometry
                        geometry = ET.SubElement(cell, 'mxGeometry')
                        geometry.set('relative', '1')
                        geometry.set('as', 'geometry')
                        
                        # Add waypoints if any
                        for i, (wx, wy) in enumerate(element.waypoints):
                            point = ET.SubElement(geometry, 'mxPoint')
                            point.set('x', str(wx))
                            point.set('y', str(wy))
                            point.set('as', f'point{i}')
                    
                    elif isinstance(element, GroupModel):
                        cell.set('vertex', '1')
                        
                        # Add geometry
                        geometry = ET.SubElement(cell, 'mxGeometry')
                        x, y = element.position
                        geometry.set('x', str(x))
                        geometry.set('y', str(y))
                        geometry.set('width', '120')
                        geometry.set('height', '60')
                        geometry.set('as', 'geometry')
                
                # Convert the mxGraphModel to string
                xml_string = ET.tostring(graph_model, encoding='utf-8').decode('utf-8')
                
                # Compress and encode the content
                compressed = zlib.compress(xml_string.encode('utf-8'))
                encoded = base64.b64encode(compressed).decode('utf-8')
                
                # Set the encoded content as the text of the diagram element
                diagram_elem.text = encoded
            
            # Write the XML to file
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            
            return True
        
        except Exception as e:
            print(f"Error saving drawio file: {e}")
            return False

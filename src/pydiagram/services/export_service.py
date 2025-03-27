"""
PyDiagram - Export service module

This module provides services for exporting diagrams to various formats
including ODP (OpenDocument Presentation), Visio, and other common formats.
"""

import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List, Tuple

from ..model import DiagramModel, PageModel, ElementModel, ShapeModel, ConnectorModel, GroupModel


class ExportService:
    """
    Service for exporting diagrams to various formats.
    Supports exporting to ODP, Visio, SVG, PNG, and other formats.
    """
    
    @staticmethod
    def export_to_svg(diagram: DiagramModel, page_index: int = 0, file_path: str = None) -> Optional[str]:
        """
        Export a diagram page to SVG format.
        
        Args:
            diagram: The diagram model to export
            page_index: Index of the page to export
            file_path: Path to save the SVG file, or None to return the SVG content
            
        Returns:
            The SVG content as a string if file_path is None, otherwise None
        """
        try:
            if page_index < 0 or page_index >= len(diagram.pages):
                raise ValueError(f"Invalid page index: {page_index}")
            
            page = diagram.pages[page_index]
            
            # Create the SVG document
            svg = ET.Element('svg')
            svg.set('xmlns', 'http://www.w3.org/2000/svg')
            svg.set('version', '1.1')
            
            # Determine the bounds of the diagram
            min_x, min_y = float('inf'), float('inf')
            max_x, max_y = float('-inf'), float('-inf')
            
            for element in page.elements:
                x, y = element.position
                
                if isinstance(element, ShapeModel):
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x + element.width)
                    max_y = max(max_y, y + element.height)
            
            # Set reasonable defaults if no elements
            if min_x == float('inf'):
                min_x, min_y = 0, 0
                max_x, max_y = 800, 600
            
            # Add some padding
            padding = 20
            min_x -= padding
            min_y -= padding
            max_x += padding
            max_y += padding
            
            # Set the viewBox and size
            width = max_x - min_x
            height = max_y - min_y
            svg.set('viewBox', f"{min_x} {min_y} {width} {height}")
            svg.set('width', f"{width}")
            svg.set('height', f"{height}")
            
            # Add a background rectangle
            background = ET.SubElement(svg, 'rect')
            background.set('x', str(min_x))
            background.set('y', str(min_y))
            background.set('width', str(width))
            background.set('height', str(height))
            background.set('fill', 'white')
            
            # Add each element to the SVG
            for element in page.elements:
                if isinstance(element, ShapeModel):
                    # Create a group for the shape
                    g = ET.SubElement(svg, 'g')
                    g.set('id', element.id)
                    
                    # Create the shape element
                    shape_type = element.shape_type
                    x, y = element.position
                    width = element.width
                    height = element.height
                    
                    if shape_type == 'rectangle':
                        rect = ET.SubElement(g, 'rect')
                        rect.set('x', str(x))
                        rect.set('y', str(y))
                        rect.set('width', str(width))
                        rect.set('height', str(height))
                        rect.set('fill', element.get_style('fillColor', '#ffffff'))
                        rect.set('stroke', element.get_style('strokeColor', '#000000'))
                        rect.set('stroke-width', element.get_style('strokeWidth', '1'))
                        
                        if element.get_style('rounded', '0') == '1':
                            rect.set('rx', '5')
                            rect.set('ry', '5')
                    
                    elif shape_type == 'ellipse':
                        ellipse = ET.SubElement(g, 'ellipse')
                        ellipse.set('cx', str(x + width/2))
                        ellipse.set('cy', str(y + height/2))
                        ellipse.set('rx', str(width/2))
                        ellipse.set('ry', str(height/2))
                        ellipse.set('fill', element.get_style('fillColor', '#ffffff'))
                        ellipse.set('stroke', element.get_style('strokeColor', '#000000'))
                        ellipse.set('stroke-width', element.get_style('strokeWidth', '1'))
                    
                    elif shape_type == 'triangle':
                        # Create a triangle (pointing up)
                        points = f"{x + width/2},{y} {x},{y + height} {x + width},{y + height}"
                        polygon = ET.SubElement(g, 'polygon')
                        polygon.set('points', points)
                        polygon.set('fill', element.get_style('fillColor', '#ffffff'))
                        polygon.set('stroke', element.get_style('strokeColor', '#000000'))
                        polygon.set('stroke-width', element.get_style('strokeWidth', '1'))
                    
                    elif shape_type == 'diamond':
                        # Create a diamond
                        points = f"{x + width/2},{y} {x + width},{y + height/2} {x + width/2},{y + height} {x},{y + height/2}"
                        polygon = ET.SubElement(g, 'polygon')
                        polygon.set('points', points)
                        polygon.set('fill', element.get_style('fillColor', '#ffffff'))
                        polygon.set('stroke', element.get_style('strokeColor', '#000000'))
                        polygon.set('stroke-width', element.get_style('strokeWidth', '1'))
                    
                    else:
                        # Default to rectangle for unknown shapes
                        rect = ET.SubElement(g, 'rect')
                        rect.set('x', str(x))
                        rect.set('y', str(y))
                        rect.set('width', str(width))
                        rect.set('height', str(height))
                        rect.set('fill', element.get_style('fillColor', '#ffffff'))
                        rect.set('stroke', element.get_style('strokeColor', '#000000'))
                        rect.set('stroke-width', element.get_style('strokeWidth', '1'))
                    
                    # Add text if present
                    if element.value:
                        text = ET.SubElement(g, 'text')
                        text.set('x', str(x + width/2))
                        text.set('y', str(y + height/2))
                        text.set('text-anchor', 'middle')
                        text.set('dominant-baseline', 'middle')
                        text.set('font-family', 'Arial')
                        text.set('font-size', '12')
                        text.text = element.value
                
                elif isinstance(element, ConnectorModel):
                    # Create a group for the connector
                    g = ET.SubElement(svg, 'g')
                    g.set('id', element.id)
                    
                    # Get source and target positions
                    source_pos = None
                    target_pos = None
                    
                    if element.source_id:
                        source_element = next((e for e in page.elements if e.id == element.source_id), None)
                        if source_element and isinstance(source_element, ShapeModel):
                            sx, sy = source_element.position
                            source_pos = (sx + source_element.width/2, sy + source_element.height/2)
                    
                    if element.target_id:
                        target_element = next((e for e in page.elements if e.id == element.target_id), None)
                        if target_element and isinstance(target_element, ShapeModel):
                            tx, ty = target_element.position
                            target_pos = (tx + target_element.width/2, ty + target_element.height/2)
                    
                    # Use element position if source/target not found
                    if not source_pos:
                        source_pos = element.position
                    
                    if not target_pos:
                        x, y = element.position
                        target_pos = (x + 100, y)  # Default offset
                    
                    # Create the path for the connector
                    path = ET.SubElement(g, 'path')
                    
                    # Generate the path data
                    waypoints = element.waypoints
                    if waypoints:
                        # Use waypoints if available
                        path_data = f"M {source_pos[0]},{source_pos[1]}"
                        for wx, wy in waypoints:
                            path_data += f" L {wx},{wy}"
                        path_data += f" L {target_pos[0]},{target_pos[1]}"
                    else:
                        # Simple straight line
                        path_data = f"M {source_pos[0]},{source_pos[1]} L {target_pos[0]},{target_pos[1]}"
                    
                    path.set('d', path_data)
                    path.set('fill', 'none')
                    path.set('stroke', element.get_style('strokeColor', '#000000'))
                    path.set('stroke-width', element.get_style('strokeWidth', '1'))
                    
                    # Add arrowheads if specified
                    end_arrow = element.get_style('endArrow', 'none')
                    if end_arrow != 'none':
                        # Simple arrowhead
                        marker = ET.SubElement(svg, 'marker')
                        marker.set('id', f"arrow_{element.id}")
                        marker.set('viewBox', "0 0 10 10")
                        marker.set('refX', "10")
                        marker.set('refY', "5")
                        marker.set('markerWidth', "6")
                        marker.set('markerHeight', "6")
                        marker.set('orient', "auto")
                        
                        arrow = ET.SubElement(marker, 'path')
                        arrow.set('d', "M 0,0 L 10,5 L 0,10 z")
                        arrow.set('fill', element.get_style('strokeColor', '#000000'))
                        
                        path.set('marker-end', f"url(#arrow_{element.id})")
                    
                    # Add text if present
                    if element.value:
                        # Calculate midpoint of the connector
                        if waypoints:
                            # Use middle waypoint
                            mid_idx = len(waypoints) // 2
                            mid_x, mid_y = waypoints[mid_idx]
                        else:
                            # Calculate midpoint of line
                            mid_x = (source_pos[0] + target_pos[0]) / 2
                            mid_y = (source_pos[1] + target_pos[1]) / 2
                        
                        text = ET.SubElement(g, 'text')
                        text.set('x', str(mid_x))
                        text.set('y', str(mid_y))
                        text.set('text-anchor', 'middle')
                        text.set('dominant-baseline', 'middle')
                        text.set('font-family', 'Arial')
                        text.set('font-size', '12')
                        text.set('fill', element.get_style('fontColor', '#000000'))
                        text.set('background', 'white')
                        text.text = element.value
            
            # Convert to string
            svg_string = ET.tostring(svg, encoding='utf-8').decode('utf-8')
            
            # Save to file if path provided
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
                    f.write(svg_string)
                return None
            
            return svg_string
        
        except Exception as e:
            print(f"Error exporting to SVG: {e}")
            return None
    
    @staticmethod
    def export_to_odp(diagram: DiagramModel, file_path: str) -> bool:
        """
        Export a diagram to ODP (OpenDocument Presentation) format.
        
        Args:
            diagram: The diagram model to export
            file_path: Path to save the ODP file
            
        Returns:
            True if exporting was successful, False otherwise
        """
        try:
            # Create a temporary directory for ODP files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create the basic ODP structure
                os.makedirs(os.path.join(temp_dir, 'META-INF'), exist_ok=True)
                
                # Create the manifest file
                manifest_content = """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
 <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.presentation" manifest:full-path="/"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="meta.xml"/>
</manifest:manifest>"""
                
                with open(os.path.join(temp_dir, 'META-INF', 'manifest.xml'), 'w', encoding='utf-8') as f:
                    f.write(manifest_content)
                
                # Create the meta.xml file
                meta_content = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                     xmlns:dc="http://purl.org/dc/elements/1.1/">
 <office:meta>
  <dc:title>""" + diagram.name + """</dc:title>
  <dc:creator>PyDiagram</dc:creator>
  <dc:date>2025-03-27T07:30:00Z</dc:date>
 </office:meta>
</office:document-meta>"""
                
                with open(os.path.join(temp_dir, 'meta.xml'), 'w', encoding='utf-8') as f:
                    f.write(meta_content)
                
                # Create the styles.xml file
                styles_content = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
 <office:styles>
  <!-- Basic styles would go here -->
 </office:styles>
</office:document-styles>"""
                
                with open(os.path.join(temp_dir, 'styles.xml'), 'w', encoding='utf-8') as f:
                    f.write(styles_content)
                
                # Create the content.xml file with slides for each page
                content = ET.Element('office:document-content')
                content.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
                content.set('xmlns:draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')
                content.set('xmlns:text', 'urn:oasis:names:tc:opendocument:xmlns:text:1.0')
                content.set('xmlns:svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0')
                
                # Add automatic styles
                auto_styles = ET.SubElement(content, 'office:automatic-styles')
                
                # Add body
                body = ET.SubElement(content, 'office:body')
                presentation = ET.SubElement(body, 'office:presentation')
                
                # Add a slide for each page
                for i, page in enumerate(diagram.pages):
                    # Create a slide
                    slide = ET.SubElement(presentation, 'draw:page')
                    slide.set('draw:name', page.name)
                    slide.set('draw:style-name', f'dp{i}')
                    
                    # Add each element to the slide
                    for element in page.elements:
                        if isinstance(element, ShapeModel):
                            # Create a shape
                            shape_type = element.shape_type
                            x, y = element.position
                            width = element.width
                            height = element.height
                            
                            if shape_type == 'rectangle':
                                shape = ET.SubElement(slide, 'draw:rect')
                            elif shape_type == 'ellipse':
                                shape = ET.SubElement(slide, 'draw:ellipse')
                            else:
                                # Default to rectangle for other shapes
                                shape = ET.SubElement(slide, 'draw:rect')
                            
                            # Set position and size
                            shape.set('svg:x', f"{x/100}cm")
                            shape.set('svg:y', f"{y/100}cm")
                            shape.set('svg:width', f"{width/100}cm")
                            shape.set('svg:height', f"{height/100}cm")
                            
                            # Set style
                            fill_color = element.get_style('fillColor', '#ffffff')
                            stroke_color = element.get_style('strokeColor', '#000000')
                            
                            shape.set('draw:style-name', f'gr{i}_{element.id}')
                            
                            # Add style for this shape
                            style = ET.SubElement(auto_styles, 'style:style')
                            style.set('style:name', f'gr{i}_{element.id}')
                            style.set('style:family', 'graphic')
                            
                            props = ET.SubElement(style, 'style:graphic-properties')
                            props.set('draw:fill-color', fill_color)
                            props.set('svg:stroke-color', stroke_color)
                            
                            # Add text if present
                            if element.value:
                                text_box = ET.SubElement(shape, 'draw:text-box')
                                p = ET.SubElement(text_box, 'text:p')
                                p.text = element.value
                        
                        elif isinstance(element, ConnectorModel):
                            # Create a connector
                            connector = ET.SubElement(slide, 'draw:connector')
                            connector.set('draw:style-name', f'gr{i}_{element.id}')
                            
                            # Set source and target
                            if element.source_id:
                                connector.set('draw:start-shape', element.source_id)
                            if element.target_id:
                                connector.set('draw:end-shape', element.target_id)
                            
                            # Add style for this connector
                            style = ET.SubElement(auto_styles, 'style:style')
                            style.set('style:name', f'gr{i}_{element.id}')
                            style.set('style:family', 'graphic')
                            
                            props = ET.SubElement(style, 'style:graphic-properties')
                            props.set('svg:stroke-color', element.get_style('strokeColor', '#000000'))
                            
                            # Add text if present
                            if element.value:
                                text_box = ET.SubElement(connector, 'draw:text-box')
                                p = ET.SubElement(text_box, 'text:p')
                                p.text = element.value
                
                # Write the content.xml file
                content_string = ET.tostring(content, encoding='utf-8').decode('utf-8')
                with open(os.path.join(temp_dir, 'content.xml'), 'w', encoding='utf-8') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    f.write(content_string)
                
                # Create the mimetype file
                with open(os.path.join(temp_dir, 'mimetype'), 'w', encoding='utf-8') as f:
                    f.write('application/vnd.oasis.opendocument.presentation')
                
                # Create the ODP file (zip)
                with zipfile.ZipFile(file_path, 'w') as odp_zip:
                    # Add mimetype first (uncompressed)
                    odp_zip.write(os.path.join(temp_dir, 'mimetype'), 'mimetype', compress_type=zipfile.ZIP_STORED)
                    
                    # Add other files
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file != 'mimetype':
                                file_path_in_zip = os.path.relpath(os.path.join(root, file), temp_dir)
                                odp_zip.write(os.path.join(root, file), file_path_in_zip)
            
            return True
        
        except Exception as e:
            print(f"Error exporting to ODP: {e}")
            return False

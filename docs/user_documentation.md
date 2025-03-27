# PyDiagram User Documentation

## Introduction

PyDiagram is a comprehensive Python-based diagram editor that provides a complete alternative to draw.io/diagrams.net. It allows you to create, edit, and export diagrams in various formats, with full support for the drawio file format.

This documentation provides detailed information on how to use PyDiagram, including installation instructions, basic usage, advanced features, and API reference.

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [User Interface](#user-interface)
4. [Creating Diagrams](#creating-diagrams)
5. [Editing Elements](#editing-elements)
6. [Working with Files](#working-with-files)
7. [Exporting Diagrams](#exporting-diagrams)
8. [Advanced Features](#advanced-features)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.7 or higher
- PyQt5
- Required Python packages (automatically installed with pip)

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/boolforge/PyDiagram.git

# Navigate to the project directory
cd PyDiagram

# Install the package and dependencies
pip install -e .
```

## Getting Started

### Launching PyDiagram

After installation, you can launch PyDiagram using the following command:

```bash
python -m pydiagram
```

Alternatively, if you installed PyDiagram using pip, you can simply run:

```bash
pydiagram
```

### Creating Your First Diagram

1. Launch PyDiagram
2. Click on "File" > "New" to create a new diagram
3. Use the shape tools in the toolbar to add elements to your diagram
4. Connect elements using the connector tool
5. Save your diagram using "File" > "Save" or Ctrl+S

## User Interface

The PyDiagram user interface consists of the following components:

### Main Window

The main window provides access to all PyDiagram features through menus, toolbars, and dock widgets.

### Menu Bar

- **File Menu**: Options for creating, opening, saving, and exporting diagrams
- **Edit Menu**: Standard editing operations like undo, redo, cut, copy, paste
- **View Menu**: Options for zooming, showing/hiding grid, and customizing the interface
- **Insert Menu**: Tools for adding various elements to your diagram
- **Format Menu**: Options for formatting diagram elements
- **Arrange Menu**: Tools for aligning, distributing, and ordering elements
- **Help Menu**: Access to documentation and about information

### Toolbars

- **Standard Toolbar**: Common operations like new, open, save
- **Edit Toolbar**: Cut, copy, paste, delete operations
- **View Toolbar**: Zoom controls and view options
- **Insert Toolbar**: Tools for adding shapes, connectors, and text
- **Format Toolbar**: Formatting options for selected elements

### Dock Widgets

- **Shapes Panel**: Library of available shapes organized by categories
- **Properties Panel**: Shows and allows editing of properties for selected elements
- **Layers Panel**: Manages diagram layers
- **Outline Panel**: Shows a hierarchical view of diagram elements

### Diagram Canvas

The central area where you create and edit your diagram. The canvas supports:

- Zooming in/out
- Panning
- Grid display
- Snap to grid
- Rulers

## Creating Diagrams

### Basic Shapes

PyDiagram provides a variety of basic shapes:

- Rectangle
- Ellipse
- Triangle
- Diamond
- Hexagon
- Pentagon
- Star
- Arrow

To add a shape:

1. Select the shape tool from the toolbar or shapes panel
2. Click and drag on the canvas to create the shape
3. Adjust the size and position as needed

### Connectors

Connectors allow you to link elements in your diagram:

1. Select the connector tool from the toolbar
2. Click on the source element
3. Drag to the target element and release
4. The connector will automatically attach to connection points

### Text

To add text:

1. Select the text tool from the toolbar
2. Click on the canvas to create a text box
3. Type your text
4. Format the text using the format toolbar or properties panel

### Groups

You can group multiple elements together:

1. Select multiple elements by holding Shift and clicking on them
2. Right-click and select "Group" or use Ctrl+G
3. The elements will now behave as a single unit

## Editing Elements

### Selection

- Click on an element to select it
- Hold Shift and click to select multiple elements
- Click and drag to create a selection rectangle

### Moving

- Click and drag selected elements to move them
- Use arrow keys for precise positioning

### Resizing

- Click on an element to show resize handles
- Drag the handles to resize the element
- Hold Shift while resizing to maintain aspect ratio

### Formatting

- Use the properties panel to change element properties
- Change fill color, line color, line style, and other attributes
- Apply styles to multiple elements at once

### Alignment

- Select multiple elements
- Use the alignment tools in the Arrange menu or toolbar
- Align left, right, top, bottom, center horizontally, or center vertically

## Working with Files

### Creating a New Diagram

- Click "File" > "New" or press Ctrl+N
- Select a template or start with a blank diagram

### Opening Existing Diagrams

PyDiagram supports opening diagrams in the following formats:

- .drawio (draw.io/diagrams.net format)
- .xml (draw.io XML format)
- .svg (with embedded diagram data)

To open a diagram:

1. Click "File" > "Open" or press Ctrl+O
2. Select the file you want to open
3. Click "Open"

### Saving Diagrams

To save your diagram:

1. Click "File" > "Save" or press Ctrl+S
2. If saving for the first time, enter a filename
3. Select the file format (default is .drawio)
4. Click "Save"

### Autosave and Recovery

PyDiagram automatically saves your work at regular intervals. If the application crashes, you can recover your work:

1. Restart PyDiagram
2. You will be prompted to recover unsaved changes
3. Click "Recover" to restore your diagram

## Exporting Diagrams

PyDiagram supports exporting diagrams to various formats:

### Vector Formats

- **SVG**: Scalable Vector Graphics
  - Click "File" > "Export" > "SVG"
  - Select export options
  - Choose a filename and location
  - Click "Export"

- **PDF**: Portable Document Format
  - Click "File" > "Export" > "PDF"
  - Configure page settings
  - Choose a filename and location
  - Click "Export"

### Raster Formats

- **PNG**: Portable Network Graphics
  - Click "File" > "Export" > "PNG"
  - Set resolution and transparency options
  - Choose a filename and location
  - Click "Export"

### Office Formats

- **ODP**: OpenDocument Presentation
  - Click "File" > "Export" > "ODP"
  - Configure slide options
  - Choose a filename and location
  - Click "Export"

- **Visio**: Microsoft Visio Format
  - Click "File" > "Export" > "Visio"
  - Choose a filename and location
  - Click "Export"

### Web Formats

- **HTML**: Interactive HTML
  - Click "File" > "Export" > "HTML"
  - Configure interactivity options
  - Choose a filename and location
  - Click "Export"

## Advanced Features

### Layers

PyDiagram supports working with layers to organize complex diagrams:

- Create new layers using the Layers panel
- Show/hide layers
- Lock layers to prevent editing
- Reorder layers to change element stacking

### Templates

Save time by using templates:

- Create a diagram that you want to use as a template
- Click "File" > "Save as Template"
- Give your template a name
- Access your templates from "File" > "New from Template"

### Scripting

PyDiagram supports Python scripting for automation:

```python
from pydiagram.model import DiagramModel
from pydiagram.services import FileService

# Create a new diagram
diagram = DiagramModel("My Diagram")

# Add a page
page = diagram.add_page("Page 1")

# Add shapes
shape1 = page.add_rectangle(100, 100, 120, 80, "Process 1")
shape2 = page.add_rectangle(300, 100, 120, 80, "Process 2")

# Add a connector
connector = page.add_connector(shape1, shape2, "Data Flow")

# Save the diagram
FileService.save_drawio_file(diagram, "my_diagram.drawio")
```

## API Reference

### Model Classes

- **DiagramModel**: Represents a complete diagram with multiple pages
- **PageModel**: Represents a single page in a diagram
- **ShapeModel**: Base class for all shape elements
- **ConnectorModel**: Represents connections between elements
- **GroupModel**: Represents a group of elements

### Service Classes

- **FileService**: Handles loading and saving diagram files
- **ExportService**: Provides basic export functionality
- **AdditionalExportFormats**: Extends export capabilities to more formats

### View Classes

- **DiagramView**: Canvas for displaying and editing diagrams
- **MainWindow**: Main application window with menus and toolbars

## Troubleshooting

### Common Issues

#### Application Won't Start

- Ensure Python 3.7+ is installed
- Verify PyQt5 is installed correctly
- Check for error messages in the console

#### Can't Open a File

- Verify the file exists and is not corrupted
- Check if the file format is supported
- Ensure you have read permissions for the file

#### Export Fails

- Ensure required dependencies are installed
- Check if you have write permissions for the destination
- Verify the selected format is supported

### Getting Help

If you encounter issues not covered in this documentation:

- Check the GitHub repository for known issues
- Submit a bug report with detailed information
- Join the community forum for user discussions

---

## License

PyDiagram is released under the MIT License. See the LICENSE file for details.

## Acknowledgments

PyDiagram builds upon the work of several open-source projects:

- drawpyo: Extended to support all drawio format elements
- PyQt5: Used for the graphical user interface
- Various Python libraries for file format support

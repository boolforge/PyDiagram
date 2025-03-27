"""
PyDiagram - Model initialization module

This module initializes the model package and imports key classes.
"""

from .base import (
    ModelObserver,
    BaseModel,
    DiagramModel,
    PageModel,
    ElementModel
)

from .shapes import (
    ShapeModel,
    GroupModel
)

from .connectors import (
    ConnectorModel
)

__all__ = [
    'ModelObserver',
    'BaseModel',
    'DiagramModel',
    'PageModel',
    'ElementModel',
    'ShapeModel',
    'GroupModel',
    'ConnectorModel'
]

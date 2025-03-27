"""
PyDiagram - Módulo de modelo base

Este módulo define las clases base para el modelo de datos de PyDiagram.
Utiliza drawpyo ampliado como base para la representación de diagramas.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple


class ModelObserver:
    """
    Interfaz para el patrón Observer que permite a las vistas
    recibir notificaciones de cambios en el modelo.
    """
    
    def model_changed(self, model: 'BaseModel', change_type: str, data: Any) -> None:
        """
        Método llamado cuando el modelo observado cambia.
        
        Args:
            model: El modelo que ha cambiado
            change_type: Tipo de cambio (ej. 'add', 'remove', 'update')
            data: Datos adicionales sobre el cambio
        """
        pass


class BaseModel(ABC):
    """
    Clase base abstracta para todos los modelos en PyDiagram.
    Implementa el patrón Observer para notificar cambios.
    """
    
    def __init__(self):
        """Inicializa un nuevo modelo base."""
        self._observers: List[ModelObserver] = []
    
    def add_observer(self, observer: ModelObserver) -> None:
        """
        Añade un observador al modelo.
        
        Args:
            observer: El observador a añadir
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: ModelObserver) -> None:
        """
        Elimina un observador del modelo.
        
        Args:
            observer: El observador a eliminar
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, change_type: str, data: Any = None) -> None:
        """
        Notifica a todos los observadores de un cambio en el modelo.
        
        Args:
            change_type: Tipo de cambio
            data: Datos adicionales sobre el cambio
        """
        for observer in self._observers:
            observer.model_changed(self, change_type, data)


class DiagramModel(BaseModel):
    """
    Modelo que representa un diagrama completo.
    Un diagrama puede contener múltiples páginas.
    """
    
    def __init__(self, name: str = "Untitled Diagram"):
        """
        Inicializa un nuevo diagrama.
        
        Args:
            name: Nombre del diagrama
        """
        super().__init__()
        self._name = name
        self._pages: List[PageModel] = []
        self._metadata: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """Obtiene el nombre del diagrama."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """
        Establece el nombre del diagrama.
        
        Args:
            value: Nuevo nombre
        """
        if value != self._name:
            old_name = self._name
            self._name = value
            self.notify_observers('name_changed', {'old_name': old_name, 'new_name': value})
    
    @property
    def pages(self) -> List['PageModel']:
        """Obtiene la lista de páginas del diagrama."""
        return self._pages.copy()
    
    def add_page(self, page: 'PageModel') -> None:
        """
        Añade una página al diagrama.
        
        Args:
            page: Página a añadir
        """
        if page not in self._pages:
            self._pages.append(page)
            self.notify_observers('page_added', {'page': page})
    
    def remove_page(self, page: 'PageModel') -> None:
        """
        Elimina una página del diagrama.
        
        Args:
            page: Página a eliminar
        """
        if page in self._pages:
            self._pages.remove(page)
            self.notify_observers('page_removed', {'page': page})
    
    def get_page_by_index(self, index: int) -> Optional['PageModel']:
        """
        Obtiene una página por su índice.
        
        Args:
            index: Índice de la página
            
        Returns:
            La página en el índice especificado o None si el índice está fuera de rango
        """
        if 0 <= index < len(self._pages):
            return self._pages[index]
        return None
    
    def get_page_by_name(self, name: str) -> Optional['PageModel']:
        """
        Obtiene una página por su nombre.
        
        Args:
            name: Nombre de la página
            
        Returns:
            La primera página con el nombre especificado o None si no se encuentra
        """
        for page in self._pages:
            if page.name == name:
                return page
        return None
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Establece un valor de metadatos.
        
        Args:
            key: Clave de metadatos
            value: Valor de metadatos
        """
        old_value = self._metadata.get(key)
        self._metadata[key] = value
        self.notify_observers('metadata_changed', 
                             {'key': key, 'old_value': old_value, 'new_value': value})
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de metadatos.
        
        Args:
            key: Clave de metadatos
            default: Valor predeterminado si la clave no existe
            
        Returns:
            El valor de metadatos o el valor predeterminado
        """
        return self._metadata.get(key, default)


class PageModel(BaseModel):
    """
    Modelo que representa una página de un diagrama.
    Una página contiene elementos como formas y conectores.
    """
    
    def __init__(self, name: str = "Page 1"):
        """
        Inicializa una nueva página.
        
        Args:
            name: Nombre de la página
        """
        super().__init__()
        self._name = name
        self._elements: List['ElementModel'] = []
        self._properties: Dict[str, Any] = {}
        self._grid_enabled = True
        self._grid_size = 10
    
    @property
    def name(self) -> str:
        """Obtiene el nombre de la página."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """
        Establece el nombre de la página.
        
        Args:
            value: Nuevo nombre
        """
        if value != self._name:
            old_name = self._name
            self._name = value
            self.notify_observers('name_changed', {'old_name': old_name, 'new_name': value})
    
    @property
    def elements(self) -> List['ElementModel']:
        """Obtiene la lista de elementos de la página."""
        return self._elements.copy()
    
    def add_element(self, element: 'ElementModel') -> None:
        """
        Añade un elemento a la página.
        
        Args:
            element: Elemento a añadir
        """
        if element not in self._elements:
            self._elements.append(element)
            self.notify_observers('element_added', {'element': element})
    
    def remove_element(self, element: 'ElementModel') -> None:
        """
        Elimina un elemento de la página.
        
        Args:
            element: Elemento a eliminar
        """
        if element in self._elements:
            self._elements.remove(element)
            self.notify_observers('element_removed', {'element': element})
    
    def get_element_by_id(self, element_id: str) -> Optional['ElementModel']:
        """
        Obtiene un elemento por su ID.
        
        Args:
            element_id: ID del elemento
            
        Returns:
            El elemento con el ID especificado o None si no se encuentra
        """
        for element in self._elements:
            if element.id == element_id:
                return element
        return None
    
    @property
    def grid_enabled(self) -> bool:
        """Obtiene si la cuadrícula está habilitada."""
        return self._grid_enabled
    
    @grid_enabled.setter
    def grid_enabled(self, value: bool) -> None:
        """
        Establece si la cuadrícula está habilitada.
        
        Args:
            value: True para habilitar, False para deshabilitar
        """
        if value != self._grid_enabled:
            self._grid_enabled = value
            self.notify_observers('grid_changed', {'enabled': value})
    
    @property
    def grid_size(self) -> int:
        """Obtiene el tamaño de la cuadrícula."""
        return self._grid_size
    
    @grid_size.setter
    def grid_size(self, value: int) -> None:
        """
        Establece el tamaño de la cuadrícula.
        
        Args:
            value: Nuevo tamaño
        """
        if value != self._grid_size and value > 0:
            old_size = self._grid_size
            self._grid_size = value
            self.notify_observers('grid_changed', 
                                 {'old_size': old_size, 'new_size': value})
    
    def set_property(self, key: str, value: Any) -> None:
        """
        Establece una propiedad de la página.
        
        Args:
            key: Clave de la propiedad
            value: Valor de la propiedad
        """
        old_value = self._properties.get(key)
        self._properties[key] = value
        self.notify_observers('property_changed', 
                             {'key': key, 'old_value': old_value, 'new_value': value})
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """
        Obtiene una propiedad de la página.
        
        Args:
            key: Clave de la propiedad
            default: Valor predeterminado si la clave no existe
            
        Returns:
            El valor de la propiedad o el valor predeterminado
        """
        return self._properties.get(key, default)


class ElementModel(BaseModel, ABC):
    """
    Clase base abstracta para todos los elementos de un diagrama.
    """
    
    def __init__(self, element_id: str, value: str = ""):
        """
        Inicializa un nuevo elemento.
        
        Args:
            element_id: ID único del elemento
            value: Valor o texto del elemento
        """
        super().__init__()
        self._id = element_id
        self._value = value
        self._style: Dict[str, Any] = {}
        self._position: Tuple[float, float] = (0, 0)
        self._parent_id: Optional[str] = None
    
    @property
    def id(self) -> str:
        """Obtiene el ID del elemento."""
        return self._id
    
    @property
    def value(self) -> str:
        """Obtiene el valor o texto del elemento."""
        return self._value
    
    @value.setter
    def value(self, new_value: str) -> None:
        """
        Establece el valor o texto del elemento.
        
        Args:
            new_value: Nuevo valor
        """
        if new_value != self._value:
            old_value = self._value
            self._value = new_value
            self.notify_observers('value_changed', 
                                 {'old_value': old_value, 'new_value': new_value})
    
    @property
    def position(self) -> Tuple[float, float]:
        """Obtiene la posición del elemento (x, y)."""
        return self._position
    
    @position.setter
    def position(self, new_position: Tuple[float, float]) -> None:
        """
        Establece la posición del elemento.
        
        Args:
            new_position: Nueva posición (x, y)
        """
        if new_position != self._position:
            old_position = self._position
            self._position = new_position
            self.notify_observers('position_changed', 
                                 {'old_position': old_position, 'new_position': new_position})
    
    @property
    def parent_id(self) -> Optional[str]:
        """Obtiene el ID del elemento padre."""
        return self._parent_id
    
    @parent_id.setter
    def parent_id(self, parent_id: Optional[str]) -> None:
        """
        Establece el ID del elemento padre.
        
        Args:
            parent_id: ID del elemento padre o None
        """
        if parent_id != self._parent_id:
            old_parent_id = self._parent_id
            self._parent_id = parent_id
            self.notify_observers('parent_changed', 
                                 {'old_parent_id': old_parent_id, 'new_parent_id': parent_id})
    
    def set_style(self, key: str, value: Any) -> None:
        """
        Establece un valor de estilo.
        
        Args:
            key: Clave de estilo
            value: Valor de estilo
        """
        old_value = self._style.get(key)
        self._style[key] = value
        self.notify_observers('style_changed', 
                             {'key': key, 'old_value': old_value, 'new_value': value})
    
    def get_style(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de estilo.
        
        Args:
            key: Clave de estilo
            default: Valor predeterminado si la clave no existe
            
        Returns:
            El valor de estilo o el valor predeterminado
        """
        return self._style.get(key, default)
    
    def apply_style_string(self, style_string: str) -> None:
        """
        Aplica un string de estilo en formato drawio (clave=valor;clave=valor;...).
        
        Args:
            style_string: String de estilo
        """
        if not style_string:
            return
            
        # Parsear el string de estilo
        style_pairs = style_string.split(';')
        for pair in style_pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                self.set_style(key.strip(), value.strip())
    
    def get_style_string(self) -> str:
        """
        Obtiene un string de estilo en formato drawio.
        
        Returns:
            String de estilo (clave=valor;clave=valor;...)
        """
        return ';'.join(f"{key}={value}" for key, value in self._style.items())
    
    @abstractmethod
    def clone(self) -> 'ElementModel':
        """
        Crea una copia del elemento.
        
        Returns:
            Una nueva instancia con las mismas propiedades
        """
        pass

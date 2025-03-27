# Arquitectura del Sistema PyDiagram

Este documento describe la arquitectura completa del sistema PyDiagram, un clon de draw.io implementado en Python.

## Visión General de la Arquitectura

PyDiagram seguirá una arquitectura modular basada en el patrón Modelo-Vista-Controlador (MVC), con capas adicionales para servicios especializados. Esta arquitectura permitirá una clara separación de responsabilidades y facilitará el mantenimiento y la extensión del sistema.

```
+-----------------------------------------------------+
|                    APLICACIÓN                       |
+-----------------------------------------------------+
|  +----------------+  +----------------+  +--------+ |
|  |     VISTA      |  |  CONTROLADOR   |  | MODELO | |
|  | (Interfaz GUI) |  | (Lógica de App)|  |(Datos) | |
|  +----------------+  +----------------+  +--------+ |
+-----------------------------------------------------+
|                     SERVICIOS                       |
| +----------+ +----------+ +----------+ +----------+ |
| |Exportación| |Plantillas| | Plugins  | |Colaboración|
| +----------+ +----------+ +----------+ +----------+ |
+-----------------------------------------------------+
|                   INFRAESTRUCTURA                   |
| +----------+ +----------+ +----------+ +----------+ |
| |  Sistema  | |   I/O    | |Renderizado| | Utilidades|
| +----------+ +----------+ +----------+ +----------+ |
+-----------------------------------------------------+
```

## Componentes Principales

### 1. Capa de Modelo

La capa de modelo se basa en drawpyo ampliado y representa la estructura de datos de los diagramas.

#### Componentes:
- **DiagramModel**: Clase principal que representa un diagrama completo
- **PageModel**: Representa una página individual de un diagrama
- **ElementModel**: Clase base para todos los elementos del diagrama
  - **ShapeModel**: Representa formas (rectángulos, círculos, etc.)
  - **ConnectorModel**: Representa conectores entre formas
  - **GroupModel**: Representa grupos de elementos
- **StyleModel**: Maneja los estilos visuales de los elementos

#### Responsabilidades:
- Mantener el estado del diagrama
- Proporcionar métodos para modificar el diagrama
- Notificar a los observadores sobre cambios en el modelo
- Serializar/deserializar diagramas desde/hacia archivos drawio

### 2. Capa de Vista

La capa de vista implementa la interfaz gráfica de usuario utilizando PyQt5/PySide2.

#### Componentes:
- **MainWindow**: Ventana principal de la aplicación
- **DiagramCanvas**: Área de dibujo donde se visualiza y edita el diagrama
- **Toolbar**: Barra de herramientas con acciones comunes
- **SidePanel**: Panel lateral con biblioteca de formas y propiedades
- **PropertyEditor**: Editor de propiedades para elementos seleccionados
- **ShapeLibrary**: Biblioteca de formas organizadas por categorías

#### Responsabilidades:
- Mostrar el diagrama al usuario
- Capturar eventos de usuario (clics, arrastres, etc.)
- Proporcionar controles para editar el diagrama
- Actualizar la visualización cuando cambia el modelo

### 3. Capa de Controlador

La capa de controlador maneja la lógica de la aplicación y coordina las interacciones entre el modelo y la vista.

#### Componentes:
- **ApplicationController**: Controlador principal de la aplicación
- **DiagramController**: Maneja las operaciones sobre diagramas
- **ElementController**: Maneja las operaciones sobre elementos individuales
- **CommandManager**: Implementa el patrón Command para operaciones deshacer/rehacer
- **SelectionManager**: Gestiona la selección de elementos

#### Responsabilidades:
- Interpretar acciones del usuario
- Actualizar el modelo en respuesta a acciones del usuario
- Coordinar la actualización de la vista
- Gestionar el historial de operaciones (deshacer/rehacer)

### 4. Capa de Servicios

La capa de servicios proporciona funcionalidades especializadas que no forman parte del núcleo MVC.

#### Componentes:
- **ExportService**: Maneja la exportación a diferentes formatos
  - **SVGExporter**: Exporta a SVG
  - **PDFExporter**: Exporta a PDF
  - **ImageExporter**: Exporta a PNG, JPEG
  - **ODPExporter**: Exporta a LibreOffice Impress
  - **VSDXExporter**: Exporta a Visio
- **TemplateService**: Gestiona plantillas predefinidas
- **PluginManager**: Sistema de plugins para extender funcionalidades
- **CollaborationService**: (Opcional) Maneja la colaboración en tiempo real

#### Responsabilidades:
- Proporcionar servicios especializados al resto de la aplicación
- Encapsular lógica compleja que no pertenece al núcleo MVC
- Integrar con bibliotecas externas

### 5. Capa de Infraestructura

La capa de infraestructura proporciona servicios de bajo nivel utilizados por el resto de la aplicación.

#### Componentes:
- **FileSystem**: Maneja operaciones de archivo
- **ConfigManager**: Gestiona la configuración de la aplicación
- **LoggingService**: Sistema de registro
- **RenderEngine**: Motor de renderizado gráfico
- **ResourceManager**: Gestiona recursos como imágenes y fuentes

#### Responsabilidades:
- Proporcionar servicios de bajo nivel
- Abstraer detalles de implementación específicos de la plataforma
- Gestionar recursos del sistema

## Flujos de Trabajo Principales

### 1. Creación de un Nuevo Diagrama

```
Usuario -> MainWindow -> ApplicationController -> DiagramModel (nuevo) -> DiagramCanvas (actualiza)
```

### 2. Edición de un Elemento

```
Usuario -> DiagramCanvas -> ElementController -> CommandManager (registra comando) -> ElementModel (actualiza) -> DiagramCanvas (actualiza)
```

### 3. Exportación de un Diagrama

```
Usuario -> MainWindow -> ApplicationController -> ExportService -> Exportador específico -> Sistema de archivos
```

### 4. Carga de un Diagrama Existente

```
Usuario -> MainWindow -> ApplicationController -> FileSystem -> DiagramModel (carga) -> DiagramCanvas (actualiza)
```

## Interfaces Clave

### 1. Interfaz Modelo-Vista

```python
# Patrón Observer para notificar cambios en el modelo
class ModelObserver:
    def model_changed(self, model, change_type, data): pass

class BaseModel:
    def add_observer(self, observer): pass
    def remove_observer(self, observer): pass
    def notify_observers(self, change_type, data): pass
```

### 2. Interfaz Controlador-Modelo

```python
# Patrón Command para operaciones
class Command:
    def execute(self): pass
    def undo(self): pass
    def redo(self): pass

class CommandManager:
    def execute_command(self, command): pass
    def undo(self): pass
    def redo(self): pass
```

### 3. Interfaz de Plugins

```python
class PluginInterface:
    def initialize(self, app_context): pass
    def shutdown(self): pass
    def get_actions(self): pass
    def get_menu_items(self): pass
```

## Consideraciones de Diseño

### Extensibilidad

- **Sistema de Plugins**: Arquitectura modular que permite añadir nuevas funcionalidades sin modificar el código base
- **Interfaces Bien Definidas**: Interfaces claras entre componentes para facilitar reemplazos o extensiones
- **Patrón Strategy**: Para algoritmos intercambiables (p.ej., diferentes algoritmos de layout)

### Rendimiento

- **Renderizado Eficiente**: Optimización del renderizado para diagramas grandes
- **Carga Perezosa**: Cargar recursos solo cuando sean necesarios
- **Caché**: Cachear resultados de operaciones costosas

### Usabilidad

- **Interfaz Familiar**: Mantener una interfaz similar a draw.io para facilitar la transición
- **Accesibilidad**: Soporte para atajos de teclado y lectores de pantalla
- **Internacionalización**: Soporte para múltiples idiomas

### Compatibilidad

- **Formato de Archivo**: Compatibilidad total con archivos drawio existentes
- **Multiplataforma**: Funcionamiento en Windows, macOS y Linux
- **Estándares Web**: Exportación a formatos estándar como SVG y PNG

## Dependencias Externas

- **PyQt5/PySide2**: Para la interfaz gráfica
- **drawpyo (fork ampliado)**: Como base para el manejo del formato drawio
- **vsdx**: Para exportación a formato Visio
- **pyoo/LibreOffice API**: Para exportación a formato ODP
- **reportlab**: Para exportación a PDF
- **Pillow**: Para manejo de imágenes
- **zlib**: Para compresión/descompresión

## Plan de Implementación

La implementación seguirá un enfoque incremental:

1. **Fase 1**: Implementación del núcleo MVC básico
   - Modelo de datos basado en drawpyo ampliado
   - Interfaz gráfica básica con PyQt5/PySide2
   - Controladores básicos para operaciones fundamentales

2. **Fase 2**: Implementación de funcionalidades esenciales
   - Biblioteca de formas básica
   - Exportación a formatos básicos (SVG, PNG, PDF)
   - Sistema de deshacer/rehacer

3. **Fase 3**: Implementación de funcionalidades avanzadas
   - Exportación a formatos adicionales (ODP, Visio)
   - Sistema de plugins
   - Plantillas avanzadas

4. **Fase 4**: Pulido y optimización
   - Mejoras de rendimiento
   - Mejoras de usabilidad
   - Pruebas exhaustivas

## Conclusión

La arquitectura propuesta para PyDiagram proporciona una base sólida para implementar un clon completo de draw.io en Python. La estructura modular y las interfaces bien definidas facilitarán el desarrollo incremental y la extensión futura del sistema.

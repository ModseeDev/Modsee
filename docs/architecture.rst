Architecture Overview
==================

This document describes the architecture of the Modsee application.

System Architecture
-----------------

Modsee is built on a component-based architecture that promotes modularity, testability, and extensibility.
The architecture follows a modified Model-View-Controller (MVC) pattern with a central application manager
that coordinates interactions between components.

Core Components
-------------

.. list-table::
   :header-rows: 1
   :widths: 20 60

   * - Component
     - Description
   * - ApplicationManager
     - Central manager that coordinates all components and maintains application state
   * - ModelManager
     - Manages model data (nodes, elements, materials, etc.) and selection state
   * - ViewManager
     - Manages UI views, panels, and their interactions
   * - FileService
     - Handles file operations, including loading/saving projects and export

Component Hierarchy
-----------------

The component system is built around a base ``Component`` class with specialized subclasses:

- **Component** - Base class for all components
  - **ModelComponent** - Components that interact with the model
    - **ModelManager** - Central model data manager
    - **[Future] MaterialManager** - Material library manager
  - **ViewComponent** - Components that provide UI views
    - **ViewManager** - Central view manager
    - **[Future] Rendering components**
  - **ServiceComponent** - Components that provide services
    - **FileService** - File operation service
    - **[Future] Analysis service**

Dependency Diagram
----------------

::

    +-------------------+
    | ApplicationManager |
    +--------+----------+
             |
             | coordinates
             v
    +--------+----------+     +--------+----------+     +--------+----------+
    |   ModelManager    |<--->|    ViewManager    |<--->|    FileService    |
    +-------------------+     +-------------------+     +-------------------+
             ^                        ^                         ^
             |                        |                         |
             v                        v                         v
    +-------------------+     +-------------------+     +-------------------+
    |   Model Objects   |     |    UI Components  |     |    I/O Handlers   |
    +-------------------+     +-------------------+     +-------------------+

Component Registration
-------------------

All components are registered with the ApplicationManager, which acts as a service locator:

.. code-block:: python

    # Register a component
    app_manager.register_component('component_name', component_instance)
    
    # Get a component
    component = app_manager.get_component('component_name')

This allows components to interact with each other without direct dependencies,
promoting loose coupling and easier testing.

Data Flow
-------

1. **User Interaction** → ViewManager → ModelManager
2. **File Operations** → FileService → ModelManager
3. **Model Changes** → ModelManager → ViewManager (refresh)
4. **Selection Changes** → ModelManager → ViewManager (refresh)

Integration
---------

The ``Integration`` class handles the setup and wiring of all components:

1. Creates the ApplicationManager
2. Creates and registers core components
3. Sets application references in components
4. Connects signals between components
5. Initializes all components

This centralized setup simplifies the initialization process and ensures proper
component configuration.

Future Extensions
--------------

The architecture is designed to be extended with new components:

1. **Plugin System** - Custom plugins that enhance functionality
2. **Additional Managers** - Specialized managers for specific aspects
3. **UI Components** - Custom views and panels
4. **Service Components** - Additional services like analysis, export, etc.

When adding new components, follow these guidelines:

1. Derive from the appropriate component base class
2. Register with the ApplicationManager
3. Access other components through the ApplicationManager
4. Follow the established component interfaces

System Architecture
==================

Overview
--------

Modsee is an open-source GUI application for Finite Element Modeling (FEM) that enables users to build structural models and export them to OpenSees TCL or OpenSeesPy. The architecture follows a modular design to ensure extensibility, maintainability, and ease of feature additions.

Component Relationships
---------------------

.. mermaid::

   graph TD
      Core[Core System] --> UI[User Interface]
      Core --> ModelEngine[Model Engine]
      Core --> FileSystem[File System]
      ModelEngine --> ModelData[Model Data]
      ModelEngine --> Exporters[Exporters]
      ModelEngine --> Importers[Importers]
      UI --> MainWindow[Main Window]
      UI --> Renderer[3D Renderer]
      Exporters --> OpenSeesExporter[OpenSees Exporter]
      Exporters --> PythonExporter[OpenSeesPy Exporter]
      ModelData --> ResultsManager[Results Manager]
      FileSystem --> ProjectManager[Project Manager]
      FileSystem --> HDF5Manager[HDF5 Manager]
      UI --> UIThemes[UI Themes]
      Renderer --> VTKRenderer[VTK Renderer]
      
System Components
----------------

Core System
~~~~~~~~~~

The central coordination component that initializes the application, manages dependencies between modules, and ensures clean communication between different parts of the system. Provides common utilities and services to all other components.

User Interface (UI)
~~~~~~~~~~

Manages all user interface elements, including the main window layout, dialogs, menus, toolbars, and interaction handling. Ensures consistent look and feel across the application while maintaining separation from business logic.

Model Engine
~~~~~~~~~~

The heart of Modsee, responsible for building, validating, and maintaining the structural model. Handles all model-related operations, implements the domain-specific logic, and manages model state transitions.

File System
~~~~~~~~~~

Manages all file operations, including saving and loading project files (.msee) and handling results data storage (HDF5). Provides a unified interface for all persistence operations.

Exporters
~~~~~~~~~~

Converts the internal model representation to output formats (OpenSees TCL scripts and OpenSeesPy code). Handles all the complexities of generating valid and efficient OpenSees code, including recorders for result capture.

Importers
~~~~~~~~~~

Handles the import of models from various sources, including .msee files and potentially other FEM formats in the future.

3D Renderer
~~~~~~~~~~

Visualization component based on VTK that handles all 3D graphics operations, model display, selection, and interaction. Supports both pre-processing and post-processing visualization modes.

Results Manager
~~~~~~~~~~

Processes and organizes analysis results stored in HDF5 format, providing efficient access to result data for visualization and post-processing operations.

Data Flow
---------

.. mermaid::

   graph LR
      UserInput[User Input] --> MainWindow
      MainWindow --> ModelEngine
      ModelEngine --> ModelData[Model Data Store]
      ModelData --> Renderer[3D Visualization]
      Renderer --> UserView[User View]
      ModelData --> Exporters
      ModelData --> ProjectManager
      Exporters --> OpenSeesCode[OpenSees/Py Code]
      OpenSeesCode --> Analysis[OpenSees Analysis]
      Analysis --> Results[HDF5 Results]
      Results --> ResultsManager
      ResultsManager --> PostProcessor[Post Processor]
      PostProcessor --> Renderer

Architecture Principles
----------------------

Modularity
~~~~~~~~~~

Components are designed with clear responsibilities and minimal dependencies, enabling independent development and testing. New features should be implemented as modules that integrate with the existing architecture.

Extensibility
~~~~~~~~~~

The plugin-based architecture allows for extending functionality without modifying core components. This includes support for new element types, material models, analysis procedures, and post-processing capabilities.

Separation of Concerns
~~~~~~~~~~

The architecture strictly separates model data, processing logic, visualization, and user interface. This ensures that changes in one area have minimal impact on others.

Error Handling
~~~~~~~~~~

A centralized error handling system provides consistent error reporting across the application. All components report errors through this system, which presents issues to users in a unified, user-friendly manner.

Configuration Management
~~~~~~~~~~

Application settings, user preferences, and project configurations are managed through a centralized configuration system that ensures persistence and proper defaults. 
UI Components
===========

This document describes the user interface components of Modsee.

Main Window
----------

The main window is the central component of the Modsee UI. It provides:

- Menu bar with File, Edit, View, and Help menus
- Tool bar with common actions
- Status bar for displaying messages
- Dockable panels for various tools
- Central area for 3D visualization

.. code-block:: text

    +----------------------------------------------------------------------+
    | File  Edit  View  Help                                               |
    +-------------------------------+------------------------------------+
    | Model Explorer               |                                    |
    | +-------------------------+  |                                    |
    | | Nodes                  |  |                                    |
    | |  |- Node 1             |  |                                    |
    | |  |- Node 2             |  |                                    |
    | | Elements               |  |         3D Visualization Area      |
    | |  |- Element 1          |  |                                    |
    | |  |- Element 2          |  |                                    |
    | | Materials              |  |                                    |
    | +-------------------------+  |                                    |
    |                             |                                    |
    +-----------------------------+                                    |
    | Properties                  |                                    |
    | +-------------------------+ |                                    |
    | | Type: Node              | |                                    |
    | | ID: 1                   | |                                    |
    | | X: 0.0                  | |                                    |
    | | Y: 0.0                  | |                                    |
    | | Z: 0.0                  | |                                    |
    | +-------------------------+ |                                    |
    +-----------------------------+------------------------------------+
    | Console                                                          |
    | +--------------------------------------------------------------+ |
    | | > Welcome to Modsee Console                                  | |
    | | > Ready.                                                     | |
    | +--------------------------------------------------------------+ |
    +----------------------------------------------------------------------+

Menu Structure
~~~~~~~~~~~~

File Menu:

- **New** - Create a new model
- **Open** - Open an existing model
- **Save** - Save the current model
- **Save As** - Save the current model with a new name
- **Exit** - Exit the application

Edit Menu:

- **Undo** - Undo the last action (not implemented yet)
- **Redo** - Redo the last undone action (not implemented yet)

View Menu:

- **Model Explorer** - Toggle the Model Explorer panel
- **Properties** - Toggle the Properties panel
- **Console** - Toggle the Console panel

Help Menu:

- **About** - Show information about the application

Dock Panels
---------

Model Explorer
~~~~~~~~~~~~

The Model Explorer panel displays a hierarchical view of all model components:

- Nodes
- Elements
- Materials
- Sections
- Constraints
- Loads

It allows users to:

- Navigate the model structure
- Select objects to view/edit their properties
- Add new objects (not implemented yet)
- Remove objects (not implemented yet)

Properties Panel
~~~~~~~~~~~~~

The Properties panel displays and allows editing of the selected object's properties:

- Shows object type
- Shows object ID
- Shows object name
- Allows editing of object properties (not implemented yet)

When no object is selected, it displays a placeholder message.

Console Panel
~~~~~~~~~~

The Console panel displays log messages and command output:

- Shows welcome message on startup
- Displays application logs and status messages
- Provides a Clear button to clear the console

Implementation Notes
-----------------

The UI components are implemented using PyQt6 and follow these design principles:

1. **Dockable Panels:** All tool panels are implemented as QDockWidget instances, allowing them to be:
   - Positioned on any side of the main window
   - Floated as separate windows
   - Tabbed together
   - Hidden/shown as needed

2. **Component-Based Architecture:** Each panel is a standalone component that interacts with the application through the core architecture:
   - Uses the ModelManager for accessing and modifying model data
   - Uses the ViewManager for registering views and handling view updates
   - Uses the FileService for file operations

3. **MVC Pattern:** The UI follows a Model-View-Controller pattern:
   - Model: Core model components (ModelManager, model objects)
   - View: UI components (MainWindow, dock panels)
   - Controller: Integration between model and view (Application, signal connections)

Future Enhancements
----------------

The following enhancements are planned for the UI:

1. Complete Model Explorer functionality
2. Implement Properties Editor for all object types
3. Add VTK integration for 3D visualization
4. Implement additional panels:
   - Analysis Settings
   - Results Viewer
   - Script Editor
5. Add customizable themes and layouts 
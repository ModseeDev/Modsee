Grid Customization Specification
==============================

Overview
--------

The Grid Customization feature enhances the modeling workflow by providing users with the ability to modify the size, spacing, and appearance of the modeling grid. This document outlines the technical requirements, user interface design, and implementation details for this feature.

Purpose and Goals
----------------

**Primary Goals:**

1. Allow users to customize the grid's overall size and density to match project requirements
2. Provide intuitive controls for grid customization in both the settings dialog and the main interface
3. Support different unit systems and common engineering/architectural scales
4. Implement grid snapping functionality to facilitate precise model creation

User Interface Design
--------------------

Settings Dialog - Grid Settings Group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A new "Grid Settings" group will be added to the Visualization tab of the Settings dialog with the following controls:

.. code-block:: text

    Grid Settings
    ├── Grid Visibility [Checkbox]
    ├── Grid Size [Double Spinner] (Range: 1.0-1000.0)
    ├── Grid Divisions [Integer Spinner] (Range: 2-100)
    ├── Grid Spacing [Double Spinner - Calculated] (Size/Divisions, Read-only)
    ├── Grid Unit [Text Field/Combo] (Default: "m", Options: "mm", "cm", "m", "km", "in", "ft", "yd")
    ├── Show Major Gridlines [Checkbox]
    ├── Major Grid Interval [Integer Spinner] (Every N divisions, Range: 2-20)
    └── Enable Grid Snapping [Checkbox]

Quick Access Controls
~~~~~~~~~~~~~~~~~~~

The main interface will be enhanced with quick access controls for common grid operations:

.. code-block:: text

    Grid Controls
    ├── Grid Size Dropdown [Combo Box]
    │   ├── Presets (1m, 5m, 10m, 20m, 50m, 100m)
    │   ├── Custom...
    │   └── Grid Settings... (Opens settings dialog)
    └── Grid Snapping Toggle [Button]

Data Model Changes
----------------

**RendererManager Class**

The RendererManager class will be extended with the following properties:

.. code-block:: python

    class RendererManager(ViewComponent):
        # Existing properties...
        
        # Grid properties
        self._grid_size = 10.0                # Total size of the grid
        self._grid_divisions = 10             # Number of divisions
        self._grid_spacing = 1.0              # Derived value (size/divisions)
        self._grid_unit = "m"                 # Display unit (for documentation)
        self._show_major_gridlines = True     # Show emphasized major gridlines
        self._major_grid_interval = 5         # Interval for major gridlines
        self._enable_grid_snapping = False    # Grid snapping enabled
        self._grid_snap_precision = 0.1       # Snapping precision

**Settings Class**

The application settings data model will be extended to store grid preferences:

.. code-block:: python

    # In _load_settings() method
    settings = {
        # Existing settings...
        
        # Grid settings
        'grid_size': 10.0,
        'grid_divisions': 10,
        'grid_unit': "m",
        'show_major_gridlines': True,
        'major_grid_interval': 5,
        'enable_grid_snapping': False,
    }

Implementation Details
--------------------

Grid Actor Creation
~~~~~~~~~~~~~~~~~

The ``create_grid_actor`` function in ``ui/vtk_helpers.py`` will be enhanced to support major gridlines:

.. code-block:: python

    def create_grid_actor(size: float = 10.0, divisions: int = 10,
                          color: Tuple[float, float, float] = (0.7, 0.7, 0.7),
                          plane: str = 'xy',
                          show_major_gridlines: bool = True,
                          major_interval: int = 5,
                          major_color: Tuple[float, float, float] = (0.5, 0.5, 0.5)) -> Dict[str, vtk.vtkActor]:
        """
        Create VTK actors representing a customizable grid with major and minor gridlines.
        
        Args:
            size: Size of the grid.
            divisions: Number of divisions.
            color: RGB color tuple for minor gridlines (values 0.0-1.0).
            plane: Plane for the grid ('xy', 'xz', or 'yz').
            show_major_gridlines: Whether to show emphasized major gridlines.
            major_interval: Interval for major gridlines (every N divisions).
            major_color: RGB color tuple for major gridlines (values 0.0-1.0).
            
        Returns:
            Dictionary of VTK actors for the grid.
        """
        # Implementation details...

Grid Size Setter Methods
~~~~~~~~~~~~~~~~~~~~~~

New methods will be added to the RendererManager to update grid properties:

.. code-block:: python

    def set_grid_size(self, size: float) -> None:
        """
        Set the size of the grid and update visualization.
        
        Args:
            size: Size of the grid.
        """
        self._grid_size = size
        self._grid_spacing = self._grid_size / self._grid_divisions
        
        # Update grid visualization
        self.set_grid_visibility(self._grid_enabled)
    
    def set_grid_divisions(self, divisions: int) -> None:
        """
        Set the number of grid divisions and update visualization.
        
        Args:
            divisions: Number of grid divisions.
        """
        self._grid_divisions = divisions
        self._grid_spacing = self._grid_size / self._grid_divisions
        
        # Update grid visualization
        self.set_grid_visibility(self._grid_enabled)
    
    def set_major_gridlines(self, show: bool, interval: int = 5) -> None:
        """
        Set major gridline visibility and interval.
        
        Args:
            show: Whether to show major gridlines.
            interval: Interval for major gridlines.
        """
        self._show_major_gridlines = show
        self._major_grid_interval = interval
        
        # Update grid visualization
        self.set_grid_visibility(self._grid_enabled)

Grid Snapping Functionality
~~~~~~~~~~~~~~~~~~~~~~~~~

The SelectionInteractorStyle class will be extended to support grid snapping:

.. code-block:: python

    class SelectionInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
        # Existing methods...
        
        def snap_to_grid(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
            """
            Snap a point to the nearest grid intersection if snapping is enabled.
            
            Args:
                x: X coordinate.
                y: Y coordinate.
                z: Z coordinate.
                
            Returns:
                Tuple of snapped coordinates.
            """
            if not self._model_manager or not self._model_manager.grid_snapping_enabled:
                return (x, y, z)
                
            spacing = self._model_manager.grid_spacing
            
            # Snap to nearest grid point
            snapped_x = round(x / spacing) * spacing
            snapped_y = round(y / spacing) * spacing
            snapped_z = round(z / spacing) * spacing
            
            return (snapped_x, snapped_y, snapped_z)

Settings Dialog Updates
~~~~~~~~~~~~~~~~~~~~~

The SettingsDialog class will be extended to include grid settings in the visualization tab:

.. code-block:: python

    def _create_visualization_tab(self):
        # Existing code...
        
        # Grid Settings Group
        grid_group = QGroupBox("Grid Settings")
        grid_layout = QFormLayout(grid_group)
        
        # Show grid
        self.show_grid_check = QCheckBox()
        self.show_grid_check.setChecked(self.settings['show_grid'])
        grid_layout.addRow("Show grid:", self.show_grid_check)
        
        # Grid size
        self.grid_size_spin = QDoubleSpinBox()
        self.grid_size_spin.setRange(1.0, 1000.0)
        self.grid_size_spin.setSingleStep(1.0)
        self.grid_size_spin.setValue(self.settings['grid_size'])
        self.grid_size_spin.setSuffix(" units")
        grid_layout.addRow("Grid size:", self.grid_size_spin)
        
        # Grid divisions
        self.grid_divisions_spin = QSpinBox()
        self.grid_divisions_spin.setRange(2, 100)
        self.grid_divisions_spin.setValue(self.settings['grid_divisions'])
        grid_layout.addRow("Grid divisions:", self.grid_divisions_spin)
        
        # Grid spacing (calculated, read-only)
        self.grid_spacing_label = QLabel(f"{self.settings['grid_size'] / self.settings['grid_divisions']:.2f} units")
        grid_layout.addRow("Grid spacing:", self.grid_spacing_label)
        
        # Update spacing when size or divisions change
        def update_spacing():
            size = self.grid_size_spin.value()
            divisions = self.grid_divisions_spin.value()
            spacing = size / divisions
            self.grid_spacing_label.setText(f"{spacing:.2f} {self.grid_unit_combo.currentText()}")
            
        self.grid_size_spin.valueChanged.connect(update_spacing)
        self.grid_divisions_spin.valueChanged.connect(update_spacing)
        
        # Grid unit
        self.grid_unit_combo = QComboBox()
        self.grid_unit_combo.addItems(["mm", "cm", "m", "km", "in", "ft", "yd"])
        self.grid_unit_combo.setCurrentText(self.settings.get('grid_unit', "m"))
        self.grid_unit_combo.currentTextChanged.connect(update_spacing)
        grid_layout.addRow("Grid unit:", self.grid_unit_combo)
        
        # Show major gridlines
        self.major_grid_check = QCheckBox()
        self.major_grid_check.setChecked(self.settings.get('show_major_gridlines', True))
        grid_layout.addRow("Show major gridlines:", self.major_grid_check)
        
        # Major grid interval
        self.major_interval_spin = QSpinBox()
        self.major_interval_spin.setRange(2, 20)
        self.major_interval_spin.setValue(self.settings.get('major_grid_interval', 5))
        grid_layout.addRow("Major grid interval:", self.major_interval_spin)
        
        # Enable grid snapping
        self.grid_snap_check = QCheckBox()
        self.grid_snap_check.setChecked(self.settings.get('enable_grid_snapping', False))
        grid_layout.addRow("Enable grid snapping:", self.grid_snap_check)
        
        layout.addWidget(grid_group)

Main Window Toolbar Updates
~~~~~~~~~~~~~~~~~~~~~~~~~

The MainWindow class will be extended with quick access controls for grid settings:

.. code-block:: python

    def _create_toolbars(self):
        # Existing toolbar code...
        
        # Create Grid Control Toolbar
        self.grid_toolbar = QToolBar("Grid Controls")
        self.grid_toolbar.setObjectName("grid_toolbar")
        
        # Grid Size Dropdown
        self.grid_size_combo = QComboBox()
        self.grid_size_combo.addItems(["1m", "5m", "10m", "20m", "50m", "100m", "Custom...", "Grid Settings..."])
        self.grid_size_combo.setCurrentIndex(2)  # Default 10m
        self.grid_size_combo.currentIndexChanged.connect(self._on_grid_size_changed)
        
        self.grid_toolbar.addWidget(QLabel("Grid Size: "))
        self.grid_toolbar.addWidget(self.grid_size_combo)
        self.grid_toolbar.addSeparator()
        
        # Grid Snap Toggle
        self.grid_snap_action = QAction("Snap to Grid", self)
        self.grid_snap_action.setCheckable(True)
        self.grid_snap_action.setChecked(False)
        self.grid_snap_action.toggled.connect(self._on_grid_snap_toggled)
        self.grid_toolbar.addAction(self.grid_snap_action)
        
        self.addToolBar(self.grid_toolbar)

Testing Plan
-----------

Unit Tests
~~~~~~~~~

1. Test grid size and division setter methods
2. Verify grid spacing calculation
3. Test grid actor creation with different parameters
4. Test grid snapping functionality with various inputs

Integration Tests
~~~~~~~~~~~~~~~

1. Verify grid appearance updates when settings are changed
2. Test interaction between grid settings dialog and main interface controls
3. Test grid snapping with node creation and movement
4. Verify persistence of grid settings between application sessions

User Acceptance Criteria
----------------------

1. Users can modify grid size and density to match their modeling needs
2. Grid appearance updates immediately when settings are changed
3. Common size presets are available for quick access
4. Grid snapping works predictably and enhances precision for node placement
5. Grid settings are correctly saved and restored between sessions 
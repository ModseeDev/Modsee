#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Main window UI
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QFrame,
    QMenuBar, QStatusBar, QAction, QMenu, QToolBar,
    QDockWidget, QTreeView, QListWidget, QTabWidget,
    QLabel, QPushButton, QToolButton, QMessageBox, QFileDialog, QDialog,
    QFormLayout, QGroupBox
)
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QIcon, QColor, QPalette

# Import ModseeScene for 3D visualization
from ..visualization.scene import ModseeScene

# Import the ModelExplorer at the top of the file with other imports
from src.ui.model_explorer import ModelExplorer

# Try to import get_icon, but provide a fallback if it fails
try:
    from ..utils.resources import get_icon
except ImportError:
    # Simple fallback if the resources module isn't available
    def get_icon(icon_name):
        return QIcon()


class MainWindow(QWidget):
    """Main window widget containing the application UI"""

    def __init__(self, parent=None):
        """Initialize the main window"""
        super().__init__(parent)
        self.parent = parent
        
        # Initialize settings
        self.settings = QSettings("Modsee", "Modsee")
        self.current_theme = self.settings.value("theme", "Light")
        
        # Initialize the UI
        self.init_ui()
        self.apply_styles()
        self.apply_theme(self.current_theme)
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create the menu bar
        self.create_menu_bar()
        
        # Create the toolbar
        self.create_toolbar()
        
        # Create the main content area with splitters
        self.create_main_content()
        
        # Set up status bar
        self.create_status_bar()
        
        # Adjust layout to minimize empty space
        self.main_layout.setStretch(2, 1)  # Give the main_splitter more stretch priority
        
    def create_menu_bar(self):
        """Create the menu bar at the top of the application"""
        self.menu_bar = QMenuBar()
        self.menu_bar.setObjectName("mainMenuBar")
        
        # File menu
        self.file_menu = QMenu("&File", self.menu_bar)
        self.menu_bar.addMenu(self.file_menu)
        
        # File actions
        self.act_new = QAction("&New", self)
        self.act_new.setIcon(get_icon("new"))
        self.act_new.setShortcut("Ctrl+N")
        self.file_menu.addAction(self.act_new)
        
        self.act_open = QAction("&Open...", self)
        self.act_open.setIcon(get_icon("open"))
        self.act_open.setShortcut("Ctrl+O")
        self.file_menu.addAction(self.act_open)
        
        self.act_save = QAction("&Save", self)
        self.act_save.setIcon(get_icon("save"))
        self.act_save.setShortcut("Ctrl+S")
        self.file_menu.addAction(self.act_save)
        
        self.act_save_as = QAction("Save &As...", self)
        self.act_save_as.setShortcut("Ctrl+Shift+S")
        self.file_menu.addAction(self.act_save_as)
        
        self.file_menu.addSeparator()
        
        self.act_export = QAction("&Export...", self)
        self.act_export.setIcon(get_icon("export"))
        self.act_export.setShortcut("Ctrl+E")
        self.file_menu.addAction(self.act_export)
        
        self.file_menu.addSeparator()
        
        self.act_exit = QAction("E&xit", self)
        self.act_exit.setShortcut("Alt+F4")
        self.file_menu.addAction(self.act_exit)
        
        # Edit menu
        self.edit_menu = QMenu("&Edit", self.menu_bar)
        self.menu_bar.addMenu(self.edit_menu)
        
        # Edit menu actions
        self.act_project_properties = QAction("Project &Properties...", self)
        self.act_project_properties.setIcon(get_icon("properties"))
        self.act_project_properties.setShortcut("Ctrl+P")
        self.edit_menu.addAction(self.act_project_properties)
        
        # View menu
        self.view_menu = QMenu("&View", self.menu_bar)
        self.menu_bar.addMenu(self.view_menu)
        
        # View menu actions - panels
        self.view_menu.addSection("Panels")
        
        self.act_view_model_explorer = QAction("Model Explorer", self)
        self.act_view_model_explorer.setCheckable(True)
        self.act_view_model_explorer.setChecked(True)
        self.view_menu.addAction(self.act_view_model_explorer)
        
        self.act_view_properties = QAction("Properties Panel", self)
        self.act_view_properties.setCheckable(True)
        self.act_view_properties.setChecked(True)
        self.view_menu.addAction(self.act_view_properties)
        
        self.act_view_console = QAction("Console", self)
        self.act_view_console.setCheckable(True)
        self.act_view_console.setChecked(True)
        self.view_menu.addAction(self.act_view_console)
        
        self.view_menu.addSeparator()
        
        # View menu actions - tabs
        self.view_menu.addSection("Views")
        
        self.act_view_3d = QAction("3D View", self)
        self.act_view_3d.setCheckable(True)
        self.act_view_3d.setChecked(True)
        self.view_menu.addAction(self.act_view_3d)
        
        # Add Visualization submenu
        self.view_menu.addSeparator()
        self.view_menu.addSection("Visualization")
        
        self.visualization_menu = QMenu("Visualization", self)
        self.view_menu.addMenu(self.visualization_menu)
        
        # Color settings actions
        self.act_node_color = QAction("Node Color...", self)
        self.act_element_color = QAction("Element Color...", self)
        self.act_load_color = QAction("Load Color...", self)
        self.act_bc_color = QAction("Boundary Condition Color...", self)
        self.act_label_color = QAction("Label Color...", self)
        self.act_selection_color = QAction("Selection Highlight Color...", self)
        
        self.visualization_menu.addAction(self.act_node_color)
        self.visualization_menu.addAction(self.act_element_color)
        self.visualization_menu.addAction(self.act_load_color)
        self.visualization_menu.addAction(self.act_bc_color)
        self.visualization_menu.addAction(self.act_label_color)
        self.visualization_menu.addSeparator()
        self.visualization_menu.addAction(self.act_selection_color)
        
        # Connect view menu actions
        self.act_view_model_explorer.triggered.connect(self.toggle_model_explorer)
        self.act_view_properties.triggered.connect(self.toggle_properties_panel)
        self.act_view_console.triggered.connect(self.toggle_console)
        self.act_view_3d.triggered.connect(self.toggle_3d_view_tab)
        
        # Connect color setting actions
        self.act_node_color.triggered.connect(lambda: self.change_visualization_color("node"))
        self.act_element_color.triggered.connect(lambda: self.change_visualization_color("element"))
        self.act_load_color.triggered.connect(lambda: self.change_visualization_color("load"))
        self.act_bc_color.triggered.connect(lambda: self.change_visualization_color("bc"))
        self.act_label_color.triggered.connect(lambda: self.change_visualization_color("label"))
        self.act_selection_color.triggered.connect(lambda: self.change_visualization_color("selection"))
        
        # Help menu
        self.help_menu = QMenu("&Help", self.menu_bar)
        self.menu_bar.addMenu(self.help_menu)
        
        # Help actions
        self.act_documentation = QAction("&Documentation", self)
        self.act_documentation.setIcon(get_icon("help"))
        self.act_documentation.setShortcut("F1")
        self.help_menu.addAction(self.act_documentation)
        
        self.act_check_updates = QAction("Check for &Updates", self)
        self.act_check_updates.setIcon(get_icon("info"))
        self.help_menu.addAction(self.act_check_updates)
        
        self.help_menu.addSeparator()
        
        self.act_about = QAction("&About Modsee", self)
        self.act_about.setIcon(get_icon("info"))
        self.help_menu.addAction(self.act_about)
        
        # Settings menu
        self.settings_menu = QMenu("&Settings", self.menu_bar)
        self.menu_bar.addMenu(self.settings_menu)
        
        # Settings actions
        self.act_preferences = QAction("&Preferences...", self)
        self.act_preferences.setIcon(get_icon("settings"))
        self.act_preferences.setShortcut("Ctrl+,")
        self.settings_menu.addAction(self.act_preferences)
        
        # Connect help menu actions
        self.act_documentation.triggered.connect(self.open_documentation)
        self.act_check_updates.triggered.connect(self.check_updates)
        self.act_about.triggered.connect(self.show_about_dialog)
        self.act_preferences.triggered.connect(self.show_preferences)
        
        # Connect edit menu actions
        self.act_project_properties.triggered.connect(self.show_project_properties)
        
        # Add the menu bar to the main layout
        self.main_layout.addWidget(self.menu_bar)
        
    def create_toolbar(self):
        """Create the main toolbar"""
        # Create toolbar container
        self.toolbar_frame = QFrame()
        self.toolbar_frame.setObjectName("toolbarFrame")
        self.toolbar_frame.setStyleSheet("#toolbarFrame { border-bottom: 1px solid #CCCCCC; background-color: #F5F5F5; }")
        self.toolbar_frame.setFixedHeight(40)
        
        self.toolbar_layout = QHBoxLayout(self.toolbar_frame)
        self.toolbar_layout.setContentsMargins(8, 2, 8, 2)
        self.toolbar_layout.setSpacing(2)
        
        # Quick access buttons (File operations)
        self.btn_new = QToolButton()
        self.btn_new.setIcon(get_icon("new"))
        self.btn_new.setToolTip("New (Ctrl+N)")
        self.btn_new.setIconSize(QSize(20, 20))
        
        self.btn_open = QToolButton()
        self.btn_open.setIcon(get_icon("open"))
        self.btn_open.setToolTip("Open (Ctrl+O)")
        self.btn_open.setIconSize(QSize(20, 20))
        
        self.btn_save = QToolButton()
        self.btn_save.setIcon(get_icon("save"))
        self.btn_save.setToolTip("Save (Ctrl+S)")
        self.btn_save.setIconSize(QSize(20, 20))
        
        # Add quick access buttons to toolbar
        self.toolbar_layout.addWidget(self.btn_new)
        self.toolbar_layout.addWidget(self.btn_open)
        self.toolbar_layout.addWidget(self.btn_save)
        
        # Add a separator
        self.separator1 = QFrame()
        self.separator1.setFrameShape(QFrame.VLine)
        self.separator1.setFrameShadow(QFrame.Sunken)
        self.toolbar_layout.addWidget(self.separator1)
        self.toolbar_layout.addSpacing(4)
        
        # Add label for model section
        self.model_label = QLabel("Model:")
        self.toolbar_layout.addWidget(self.model_label)
        self.toolbar_layout.addSpacing(4)
        
        # Add model buttons
        self.btn_model_view = QToolButton()
        self.btn_model_view.setText("View")
        self.btn_model_view.setToolTip("View Model")
        self.btn_model_view.setIcon(get_icon("view"))
        self.btn_model_view.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_model_view.setIconSize(QSize(16, 16))
        
        self.btn_model_analyze = QToolButton()
        self.btn_model_analyze.setText("Analyze")
        self.btn_model_analyze.setToolTip("Analyze Model")
        self.btn_model_analyze.setIcon(get_icon("analyze"))
        self.btn_model_analyze.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_model_analyze.setIconSize(QSize(16, 16))
        
        self.toolbar_layout.addWidget(self.btn_model_view)
        self.toolbar_layout.addWidget(self.btn_model_analyze)
        
        # Add a separator
        self.separator2 = QFrame()
        self.separator2.setFrameShape(QFrame.VLine)
        self.separator2.setFrameShadow(QFrame.Sunken)
        self.toolbar_layout.addWidget(self.separator2)
        self.toolbar_layout.addSpacing(4)
        
        # Add label for tool section
        self.tool_label = QLabel("Tools:")
        self.toolbar_layout.addWidget(self.tool_label)
        self.toolbar_layout.addSpacing(4)
        
        # Tool actions
        self.btn_select = self.create_tool_button("select", "Select", True)
        self.btn_node = self.create_tool_button("node", "Node", True)
        self.btn_element = self.create_tool_button("element", "Element", True)
        self.btn_material = self.create_tool_button("material", "Material", True)
        
        # Add tool buttons to toolbar
        self.toolbar_layout.addWidget(self.btn_select)
        self.toolbar_layout.addWidget(self.btn_node)
        self.toolbar_layout.addWidget(self.btn_element)
        self.toolbar_layout.addWidget(self.btn_material)
        self.toolbar_layout.addStretch()
        
        # Add toolbar to main layout
        self.main_layout.addWidget(self.toolbar_frame)
    
    def create_tool_button(self, icon_name, text, checkable=False):
        """Create a tool button with icon and text"""
        button = QToolButton()
        button.setText(text)
        button.setIcon(get_icon(icon_name))
        button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        button.setCheckable(checkable)
        button.setIconSize(QSize(18, 18))
        button.setMinimumWidth(70)
        button.setMaximumHeight(28)
        return button
        
    def create_main_content(self):
        """Create the main content area with splitters"""
        # Create main horizontal splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setObjectName("mainSplitter")
        self.main_splitter.setHandleWidth(1)
        self.main_layout.addWidget(self.main_splitter, 1)  # Add stretch factor of 1 to expand this widget
        
        # Create left panel (model explorer)
        self.create_left_panel()
        
        # Create center area with tabs panel and terminal
        self.create_center_area()
        
        # Create right panel (properties panel)
        self.create_right_panel()
        
        # Set splitter sizes - give more width to the model explorer
        self.main_splitter.setSizes([400, 550, 250])
    
    def create_center_area(self):
        """Create the center area with tabs panel and terminal"""
        # Create a container for the center area
        self.center_container = QFrame()
        self.center_container.setObjectName("centerContainer")
        
        # Create a vertical layout for the center container
        self.center_container_layout = QVBoxLayout(self.center_container)
        self.center_container_layout.setContentsMargins(0, 0, 0, 0)
        self.center_container_layout.setSpacing(0)
        
        # Create the center panel (main view area)
        self.create_center_panel()
        
        # Create terminal/console panel
        self.create_terminal_panel()
        
        # Create a splitter for the center panel and terminal
        self.center_splitter = QSplitter(Qt.Vertical)
        self.center_splitter.setHandleWidth(1)
        self.center_splitter.addWidget(self.center_panel)
        self.center_splitter.addWidget(self.terminal_panel)
        self.center_splitter.setSizes([600, 200])
        
        # Add the splitter to the center container
        self.center_container_layout.addWidget(self.center_splitter)
        
        # Add the center container to the main splitter
        self.main_splitter.addWidget(self.center_container)
        
    def create_terminal_panel(self):
        """Create the terminal/console panel"""
        self.terminal_panel = QFrame()
        self.terminal_panel.setObjectName("terminalPanel")
        self.terminal_panel.setFrameShape(QFrame.StyledPanel)
        
        self.terminal_layout = QVBoxLayout(self.terminal_panel)
        self.terminal_layout.setContentsMargins(0, 0, 0, 0)
        self.terminal_layout.setSpacing(0)
        
        # Terminal header
        self.terminal_header = QFrame()
        self.terminal_header.setObjectName("panelHeader")
        self.terminal_header.setStyleSheet("#panelHeader { background-color: #E0E0E0; border-bottom: 1px solid #CCCCCC; }")
        self.terminal_header.setMinimumHeight(30)
        self.terminal_header.setMaximumHeight(30)
        
        self.terminal_header_layout = QHBoxLayout(self.terminal_header)
        self.terminal_header_layout.setContentsMargins(8, 0, 8, 0)
        
        # Terminal title
        self.terminal_title = QLabel("Console Output")
        self.terminal_title.setStyleSheet("font-weight: bold; color: #333333;")
        self.terminal_header_layout.addWidget(self.terminal_title)
        
        # Add header to terminal layout
        self.terminal_layout.addWidget(self.terminal_header)
        
        # Terminal output (placeholder)
        self.terminal_output = QListWidget()
        self.terminal_output.setStyleSheet("""
            background-color: #1E1E1E;
            color: #CCCCCC;
            font-family: Consolas, 'Courier New', monospace;
            padding: 5px;
            border: none;
        """)
        
        # Enable vertical scrollbar
        self.terminal_output.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.terminal_output.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.terminal_layout.addWidget(self.terminal_output)
        
        # Add some example output
        self.terminal_output.addItem("Welcome to Modsee - OpenSees Finite Element Modeling Interface")
        self.terminal_output.addItem("> Ready to start modeling")
        
        # Scroll to bottom
        self.terminal_output.scrollToBottom()
        
        # Connect itemAdded signal to auto-scroll
        self.terminal_output.model().rowsInserted.connect(self.terminal_output.scrollToBottom)
        
    def create_left_panel(self):
        """Create the left panel (model explorer)"""
        self.left_panel = QFrame()
        self.left_panel.setObjectName("leftPanel")
        self.left_panel.setFrameShape(QFrame.StyledPanel)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)
        
        # Project explorer header
        self.left_header = QFrame()
        self.left_header.setObjectName("panelHeader")
        self.left_header.setStyleSheet("#panelHeader { background-color: #E0E0E0; border-bottom: 1px solid #CCCCCC; }")
        self.left_header.setMinimumHeight(30)
        self.left_header.setMaximumHeight(30)
        
        self.left_header_layout = QHBoxLayout(self.left_header)
        self.left_header_layout.setContentsMargins(8, 0, 8, 0)
        
        # Project explorer title
        self.left_title = QLabel("Model Explorer")
        self.left_title.setStyleSheet("font-weight: bold; color: #333333;")
        self.left_header_layout.addWidget(self.left_title)
        
        # Add header to left layout
        self.left_layout.addWidget(self.left_header)
        
        # Create a tree view for the model
        self.model_tree = QTreeView()
        self.model_tree.setAlternatingRowColors(True)
        self.model_tree.setHeaderHidden(True)
        self.model_tree.setSelectionMode(QTreeView.SingleSelection)
        
        # Configure column widths - make sure the text isn't truncated
        self.model_tree.setUniformRowHeights(True)
        self.model_tree.setColumnWidth(0, 300)  # Main column wider
        self.model_tree.setTextElideMode(Qt.ElideNone)  # Prevent text truncation
        self.model_tree.setWordWrap(True)  # Allow word wrap for long text
        self.model_tree.setIndentation(20)  # Increase indentation for better readability
        
        self.left_layout.addWidget(self.model_tree)
        
        # Initialize the model explorer
        self.model_explorer = ModelExplorer(self.model_tree)
        
        # Set callback to select items in scene when clicked in the tree
        self.model_explorer.set_scene_selection_callback(self.select_in_scene)
        
        # Add to splitter
        self.main_splitter.addWidget(self.left_panel)
        
    def create_center_panel(self):
        """Create the center panel (main view area)"""
        self.center_panel = QFrame()
        self.center_panel.setObjectName("centerPanel")
        self.center_panel.setFrameShape(QFrame.StyledPanel)
        
        self.center_layout = QVBoxLayout(self.center_panel)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(0)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #CCCCCC;
                background: white;
            }
            QTabBar::tab {
                background: #E6E6E6;
                border: 1px solid #CCCCCC;
                border-bottom: none;
                padding: 5px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover:!selected {
                background: #F0F0F0;
            }
            QTabBar::close-button {
                image: url(:/icons/close.png);
                subcontrol-position: right;
            }
            QTabBar::close-button:hover {
                background: rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Connect tab signals
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Create welcome widget (initially hidden)
        self.welcome_widget = self.create_welcome_widget()
        self.center_layout.addWidget(self.welcome_widget)
        
        # Add tabs to center layout
        self.center_layout.addWidget(self.tabs)
        
        # Create a 3D scene as the default tab
        self.create_3d_scene_tab()
        
    def create_welcome_widget(self):
        """Create a welcome widget with helpful information"""
        welcome_widget = QFrame()
        welcome_widget.setStyleSheet("background-color: white;")
        welcome_layout = QVBoxLayout(welcome_widget)
        
        # Welcome message
        welcome_label = QLabel("<h1>Welcome to Modsee</h1><p>OpenSees Finite Element Modeling Interface</p>")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_label)
        
        return welcome_widget
        
    def on_tab_changed(self, index):
        """Handle tab changes"""
        # Show welcome widget when no tabs are open
        if self.tabs.count() == 0:
            self.welcome_widget.setVisible(True)
            self.tabs.setVisible(False)
        else:
            self.welcome_widget.setVisible(False)
            self.tabs.setVisible(True)
        
    def close_tab(self, index):
        """Close a tab at the given index"""
        tab_name = self.tabs.tabText(index)
        
        # Update corresponding menu action if applicable
        if tab_name == "3D View":
            self.act_view_3d.setChecked(False)
        
        # Remove the tab
        self.tabs.removeTab(index)
        
        # Show welcome widget if no tabs are left
        if self.tabs.count() == 0:
            self.welcome_widget.setVisible(True)
            self.tabs.setVisible(False)

    def create_3d_scene_tab(self):
        """Create a 3D scene for model visualization"""
        from ..visualization.scene import ModseeScene
        
        # Create a 3D scene
        self.scene = ModseeScene(self)
        
        # Connect hover and selection callbacks
        self.scene.set_hover_callback(self.update_hover_coordinates)
        self.scene.set_selection_callback(self.handle_scene_selection)
        
        # Add to tabs
        self.tabs.addTab(self.scene, "3D View")
    
    def create_right_panel(self):
        """Create the right panel (properties panel)"""
        self.right_panel = QFrame()
        self.right_panel.setObjectName("rightPanel")
        self.right_panel.setFrameShape(QFrame.StyledPanel)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        
        # Properties header
        self.right_header = QFrame()
        self.right_header.setObjectName("panelHeader")
        self.right_header.setStyleSheet("#panelHeader { background-color: #E0E0E0; border-bottom: 1px solid #CCCCCC; }")
        self.right_header.setMinimumHeight(30)
        self.right_header.setMaximumHeight(30)
        
        self.right_header_layout = QHBoxLayout(self.right_header)
        self.right_header_layout.setContentsMargins(8, 0, 8, 0)
        
        # Properties title
        self.right_title = QLabel("Properties")
        self.right_title.setStyleSheet("font-weight: bold; color: #333333;")
        self.right_header_layout.addWidget(self.right_title)
        
        # Add header to right layout
        self.right_layout.addWidget(self.right_header)
        
        # Properties placeholder container
        self.properties_container = QFrame()
        self.properties_container.setStyleSheet("background-color: white;")
        self.properties_container_layout = QVBoxLayout(self.properties_container)
        self.properties_container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Properties placeholder
        self.properties_placeholder = QLabel("Properties Panel\n(   Select an object to view properties)")
        self.properties_placeholder.setAlignment(Qt.AlignCenter)
        self.properties_placeholder.setStyleSheet("color: #757575; font-size: 12px; padding: 20px; border: 1px dashed #CCCCCC; border-radius: 4px;")
        self.properties_container_layout.addWidget(self.properties_placeholder)
        self.properties_container_layout.addStretch()
        
        self.right_layout.addWidget(self.properties_container)
        
        # Add to splitter
        self.main_splitter.addWidget(self.right_panel)
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_frame = QFrame()
        self.status_frame.setObjectName("statusFrame")
        self.status_frame.setMinimumHeight(25)
        self.status_frame.setMaximumHeight(25)
        self.status_frame.setStyleSheet("#statusFrame { border-top: 1px solid #CCCCCC; background-color: #F5F5F5; }")
        
        self.status_layout = QHBoxLayout(self.status_frame)
        self.status_layout.setContentsMargins(8, 0, 8, 0)
        
        # Status message
        self.status_message = QLabel("Ready")
        
        # Coordinates type indicator
        self.coord_type_label = QLabel("")
        self.coord_type_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.coord_type_label.setStyleSheet("color: #666666;")
        
        # Coordinates display
        self.coordinates_display = QLabel("X: 0.00  Y: 0.00  Z: 0.00")
        self.coordinates_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Add to layout
        self.status_layout.addWidget(self.status_message, 1)
        self.status_layout.addWidget(self.coord_type_label)
        self.status_layout.addWidget(self.coordinates_display)
        
        # Add to main layout
        self.main_layout.addWidget(self.status_frame)
        
    def update_hover_coordinates(self, x, y, z):
        """Update coordinates in status bar for mouse hover"""
        self.coord_type_label.setText("Hover:")
        self.coordinates_display.setText(f"X: {x:.2f}  Y: {y:.2f}  Z: {z:.2f}")
    
    def update_selection_coordinates(self, x, y, z):
        """Update coordinates in status bar for selection"""
        self.coord_type_label.setText("Selection:")
        self.coordinates_display.setText(f"X: {x:.2f}  Y: {y:.2f}  Z: {z:.2f}")
        
    def apply_styles(self):
        """Apply additional styles to the UI components"""
        # Set main splitter style
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #CCCCCC;
                width: 1px;
            }
        """)
        
        # Set center splitter style
        self.center_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #CCCCCC;
                height: 1px;
            }
        """)
        
        # Set tab widget style
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                background: #EEEEEE;
                border: 1px solid #CCCCCC;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #2979FF;
            }
        """)
        
        # Set menu bar style
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #F5F5F5;
                border-bottom: 1px solid #CCCCCC;
                min-height: 25px;
                padding: 2px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 4px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: rgba(0, 0, 0, 0.1);
            }
            QMenuBar::item:pressed {
                background: rgba(0, 0, 0, 0.15);
            }
            QMenu {
                background-color: white;
                border: 1px solid #CCCCCC;
                padding: 2px;
            }
            QMenu::item {
                padding: 5px 25px 5px 30px;
                border-radius: 0px;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
                color: black;
            }
            QMenu::separator {
                height: 1px;
                background-color: #CCCCCC;
                margin: 4px 0px;
            }
        """)
        
        # Set toolbar style
        self.toolbar_frame.setStyleSheet("""
            #toolbarFrame {
                background-color: #F5F5F5;
                border-bottom: 1px solid #CCCCCC;
            }
            QToolButton {
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 3px;
                margin: 1px;
            }
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
                border: 1px solid #CCCCCC;
            }
            QToolButton:pressed {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QToolButton:checked {
                background-color: #E3F2FD;
                border: 1px solid #BBDEFB;
            }
            QFrame[frameShape="5"] { /* VLine */
                color: #CCCCCC;
                width: 1px;
            }
        """)
        
    def apply_theme(self, theme_name):
        """Apply the selected theme to the application"""
        from .style.theme import set_dark_theme
        
        if theme_name == "Dark":
            set_dark_theme(self)
        else:
            # Reset to default light theme
            self.setStyleSheet("")
            
        # Update specific UI elements based on theme
        self.update_theme_specific_elements(theme_name)
        
    def update_theme_specific_elements(self, theme_name):
        """Update theme-specific UI elements"""
        is_dark = theme_name == "Dark"
        
        # Update terminal panel colors
        if is_dark:
            self.terminal_output.setStyleSheet("""
                background-color: #1E1E1E;
                color: #CCCCCC;
                font-family: Consolas, 'Courier New', monospace;
                padding: 5px;
                border: none;
            """)
        else:
            self.terminal_output.setStyleSheet("""
                background-color: white;
                color: #333333;
                font-family: Consolas, 'Courier New', monospace;
                padding: 5px;
                border: 1px solid #CCCCCC;
            """)
            
        # Update other theme-specific elements here
        
    # Help menu action handlers
    def open_documentation(self):
        """Open the documentation website"""
        import webbrowser
        webbrowser.open("https://docs.modsee.net")
    
    def check_updates(self):
        """Check for updates"""
        from PyQt5.QtWidgets import QMessageBox
        # This would normally connect to a server to check for updates
        QMessageBox.information(self, "Check for Updates", 
                               "Checking for updates...\n\nYou are using the latest version of Modsee.")
    
    def show_about_dialog(self):
        """Show the about dialog"""
        from PyQt5.QtWidgets import QMessageBox
        
        # Version information
        version = "0.1.0"  # This would normally be imported from a version file
        
        about_text = f"""
        <h2>Modsee</h2>
        <p>OpenSees Finite Element Modeling Interface</p>
        <p>Version: {version}</p>
        <p>© 2023-2024 Modsee Team</p>
        <p><a href="https://docs.modsee.net">https://docs.modsee.net</a></p>
        """
        
        QMessageBox.about(self, "About Modsee", about_text)

    def show_preferences(self):
        """Show the preferences dialog"""
        from src.ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        if dialog.exec_():
            # Handle any changes that need to be reflected in the UI
            print("Preferences dialog accepted - applying settings changes")
            self.settings_changed()
        else:
            print("Preferences dialog cancelled - no settings changes applied")
        
    def show_project_properties(self):
        """Show the project properties dialog"""
        # Find the ModseeApp instance
        # In a proper implementation, you would get this from a parent or pass it in
        # We're using a simple parent chain traversal here
        parent = self.parent
        while parent:
            if hasattr(parent, 'show_project_properties'):
                parent.show_project_properties()
                return
            parent = parent.parent
            
        # If we can't find the app, show a simple message
        QMessageBox.information(self, "Project Properties", 
                               "Cannot show project properties dialog - app instance not found")
        
    def settings_changed(self):
        """Handle settings changes"""
        # Add debug output to verify method is being called
        print("MainWindow.settings_changed() called - applying settings changes")
        
        # Reload settings and update the UI accordingly
        settings = QSettings("Modsee", "Modsee")
        settings.sync()  # Force sync to make sure we get the latest settings
        
        # Update theme if changed
        theme = settings.value("theme", "Light")
        if theme != self.current_theme:
            print(f"Theme changed from {self.current_theme} to {theme} - applying theme")
            self.current_theme = theme
            self.apply_theme(theme)
        
        # Update scene visualization settings - direct approach
        # Get the scene reference
        scene = None
        if hasattr(self, 'scene') and self.scene is not None:
            scene = self.scene
        
        # If we have a scene, refresh it
        if scene is not None:
            print("Found scene - forcing visualization refresh")
            scene.force_refresh()
        else:
            print("Warning: scene not found or is None - visualization settings won't apply")

    # Add a method to update the model explorer with a project
    def update_model_explorer(self, project):
        """Update the model explorer with project data"""
        self.model_explorer.update_model(project)

    # Add new method to handle selected objects and update properties panel
    def handle_scene_selection(self, object_type, object_id):
        """Handle selection of objects in the 3D scene and update properties panel"""
        # Clear the properties container first
        # Remove all widgets from the properties container layout
        while self.properties_container_layout.count():
            item = self.properties_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create a new form for properties
        if object_type and object_id:
            # Update the properties panel based on selected object
            if object_type == "node":
                self.show_node_properties(object_id)
            elif object_type == "element":
                self.show_element_properties(object_id)
            elif object_type == "material":
                self.show_material_properties(object_id)
            elif object_type == "section":
                self.show_section_properties(object_id)
            elif object_type == "constraint":
                self.show_constraint_properties(object_id)
            elif object_type == "boundary_condition":
                self.show_boundary_condition_properties(object_id)
            elif object_type == "load":
                self.show_load_properties(object_id)
            elif object_type == "recorder":
                self.show_recorder_properties(object_id)
            elif object_type == "transformation":
                self.show_transformation_properties(object_id)
            elif object_type == "timeseries":
                self.show_timeseries_properties(object_id)
            elif object_type == "pattern":
                self.show_pattern_properties(object_id)
            # We can add more types here in the future
        else:
            # Nothing is selected, show placeholder
            self.properties_placeholder = QLabel("Properties Panel\n(will show properties of selected objects)")
            self.properties_placeholder.setAlignment(Qt.AlignCenter)
            self.properties_placeholder.setStyleSheet("color: #757575; font-size: 12px; padding: 20px; border: 1px dashed #CCCCCC; border-radius: 4px;")
            self.properties_container_layout.addWidget(self.properties_placeholder)
            self.properties_container_layout.addStretch()
            
    def show_node_properties(self, node_id):
        """Show properties of the selected node"""
        # Check if we have a project with nodes
        project = None
        if hasattr(self, 'project'):
            project = self.project
        elif hasattr(self.parent, 'project'):
            project = self.parent.project
            
        # Create label showing the node ID
        id_label = QLabel(f"<b>Node {node_id}</b>")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full node properties
        if project and node_id in project.nodes:
            node = project.nodes[node_id]
            
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add node properties
            coords = node.get("coordinates", [0, 0, 0])
            form_layout.addRow("X:", QLabel(f"{coords[0]:.4f}"))
            form_layout.addRow("Y:", QLabel(f"{coords[1]:.4f}"))
            form_layout.addRow("Z:", QLabel(f"{coords[2]:.4f}"))
            
            # Add constraints if available
            if "constraints" in node:
                form_layout.addRow("Constraints:", QLabel(str(node["constraints"])))
                
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Node ID: {node_id}\n\nCoordinates not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
        
    def show_element_properties(self, element_id):
        """Show properties of the selected element"""
        # Check if we have a project with elements
        project = None
        if hasattr(self, 'project'):
            project = self.project
        elif hasattr(self.parent, 'project'):
            project = self.parent.project
            
        # Create label showing the element ID
        id_label = QLabel(f"<b>Element {element_id}</b>")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full element properties
        if project and element_id in project.elements:
            element = project.elements[element_id]
            
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add element properties
            # Element type
            if "type" in element:
                form_layout.addRow("Type:", QLabel(element["type"]))
                
            # Connected nodes
            if "nodes" in element:
                nodes_text = ", ".join(str(n) for n in element["nodes"])
                form_layout.addRow("Nodes:", QLabel(nodes_text))
                
            # Material info
            if "material" in element:
                form_layout.addRow("Material:", QLabel(str(element["material"])))
                
            # Section info
            if "section" in element:
                form_layout.addRow("Section:", QLabel(str(element["section"])))
                
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Element ID: {element_id}\n\nProperties not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
        
    def show_material_properties(self, material_id):
        """Show properties of the selected material"""
        # Check if we have a project with materials
        project = None
        if hasattr(self, 'project'):
            project = self.project
        elif hasattr(self.parent, 'project'):
            project = self.parent.project
            
        # Create label showing the material ID
        id_label = QLabel(f"<b>Material {material_id}</b>")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full material properties
        if project and int(material_id) in project.materials:
            material = project.materials[int(material_id)]
            
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add material properties
            # Material type
            if "type" in material:
                form_layout.addRow("Type:", QLabel(material["type"]))
                
            # Properties dictionary
            if "properties" in material and material["properties"]:
                properties_group = QGroupBox("Material Properties")
                properties_layout = QFormLayout(properties_group)
                
                for prop_name, prop_value in material["properties"].items():
                    if isinstance(prop_value, (int, float)):
                        # Format numbers with 4 decimal places
                        properties_layout.addRow(f"{prop_name}:", QLabel(f"{prop_value:.4f}"))
                    else:
                        properties_layout.addRow(f"{prop_name}:", QLabel(str(prop_value)))
                
                # Add properties group to form
                form_layout.addRow(properties_group)
                
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Material ID: {material_id}\n\nProperties not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
    
    def show_boundary_condition_properties(self, bc_id):
        """Show properties of the selected boundary condition"""
        # Check if we have a project with boundary conditions
        project = None
        if hasattr(self, 'project'):
            project = self.project
        elif hasattr(self.parent, 'project'):
            project = self.parent.project
            
        # Create label showing the boundary condition ID
        id_label = QLabel(f"<b>Boundary Condition {bc_id}</b>")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full boundary condition properties
        if project and int(bc_id) in project.boundary_conditions:
            bc = project.boundary_conditions[int(bc_id)]
            
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add node ID
            if "node" in bc:
                node_id = bc["node"]
                form_layout.addRow("Applied to Node:", QLabel(str(node_id)))
                
                # Show node coordinates if available
                if node_id in project.nodes:
                    coords = project.nodes[node_id].get("coordinates", [0, 0, 0])
                    coords_text = f"({coords[0]:.2f}, {coords[1]:.2f}, {coords[2]:.2f})"
                    form_layout.addRow("Node Location:", QLabel(coords_text))
            
            # Add DOFs and values in a table
            if "dofs" in bc and "values" in bc:
                dofs = bc["dofs"]
                values = bc["values"]
                
                if dofs and values and len(dofs) == len(values):
                    dof_group = QGroupBox("Constrained DOFs")
                    dof_layout = QFormLayout(dof_group)
                    
                    # DOF meanings for reference
                    dof_meanings = {
                        1: "X Translation",
                        2: "Y Translation",
                        3: "Z Translation",
                        4: "X Rotation",
                        5: "Y Rotation",
                        6: "Z Rotation"
                    }
                    
                    for i, (dof, value) in enumerate(zip(dofs, values)):
                        dof_text = f"DOF {dof}"
                        if dof in dof_meanings:
                            dof_text += f" ({dof_meanings[dof]})"
                        
                        # 0 typically means fixed, 1 means free
                        value_text = "Fixed" if value == 0 else f"Value: {value}"
                        dof_layout.addRow(dof_text + ":", QLabel(value_text))
                    
                    # Add DOF group to form
                    form_layout.addRow(dof_group)
            
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Boundary Condition ID: {bc_id}\n\nProperties not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
    
    def show_load_properties(self, load_id):
        """Show properties of the selected load"""
        # Check if we have a project with loads
        project = None
        if hasattr(self, 'project'):
            project = self.project
        elif hasattr(self.parent, 'project'):
            project = self.parent.project
            
        # Create label showing the load ID
        id_label = QLabel(f"<b>Load {load_id}</b>")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full load properties
        if project and int(load_id) in project.loads:
            load = project.loads[int(load_id)]
            
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add load type
            if "type" in load:
                form_layout.addRow("Type:", QLabel(load["type"]))
            
            # Add target (node) ID
            if "target" in load:
                target_id = load["target"]
                form_layout.addRow("Applied to Node:", QLabel(str(target_id)))
                
                # Show node coordinates if available
                if target_id in project.nodes:
                    coords = project.nodes[target_id].get("coordinates", [0, 0, 0])
                    coords_text = f"({coords[0]:.2f}, {coords[1]:.2f}, {coords[2]:.2f})"
                    form_layout.addRow("Node Location:", QLabel(coords_text))
            
            # Add DOFs and values in a table
            if "dofs" in load and "values" in load:
                dofs = load["dofs"]
                values = load["values"]
                
                if dofs and values and len(dofs) == len(values):
                    load_group = QGroupBox("Load Values")
                    load_layout = QFormLayout(load_group)
                    
                    # DOF meanings for reference
                    dof_meanings = {
                        1: "X Direction",
                        2: "Y Direction",
                        3: "Z Direction",
                        4: "Moment X",
                        5: "Moment Y",
                        6: "Moment Z"
                    }
                    
                    for i, (dof, value) in enumerate(zip(dofs, values)):
                        dof_text = f"DOF {dof}"
                        if dof in dof_meanings:
                            dof_text += f" ({dof_meanings[dof]})"
                        
                        load_layout.addRow(dof_text + ":", QLabel(f"{value:.4f}"))
                    
                    # Add load group to form
                    form_layout.addRow(load_group)
            
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Load ID: {load_id}\n\nProperties not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
        
    def show_section_properties(self, section_id):
        """Show properties of the selected section"""
        # Check if we have a project with sections
        project = None
        if hasattr(self, 'project'):
            project = self.project
        elif hasattr(self.parent, 'project'):
            project = self.parent.project
            
        # Create label showing the section ID
        id_label = QLabel(f"<b>Section {section_id}</b>")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full section properties
        if project and int(section_id) in project.sections:
            section = project.sections[int(section_id)]
            
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add section properties
            # Section type
            if "type" in section:
                form_layout.addRow("Type:", QLabel(section["type"]))
                
            # Properties dictionary
            if "properties" in section and section["properties"]:
                properties_group = QGroupBox("Section Properties")
                properties_layout = QFormLayout(properties_group)
                
                for prop_name, prop_value in section["properties"].items():
                    if isinstance(prop_value, (int, float)):
                        # Format numbers with 4 decimal places
                        properties_layout.addRow(f"{prop_name}:", QLabel(f"{prop_value:.4f}"))
                    else:
                        properties_layout.addRow(f"{prop_name}:", QLabel(str(prop_value)))
                
                # Add properties group to form
                form_layout.addRow(properties_group)
                
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Section ID: {section_id}\n\nProperties not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
        
    def show_constraint_properties(self, constraint_id):
        """Show properties of the selected constraint"""
        # Check if we have a project with constraints
        project = None
        if hasattr(self, 'project'):
            project = self.project
        elif hasattr(self.parent, 'project'):
            project = self.parent.project
            
        # Create label showing the constraint ID
        id_label = QLabel(f"<b>Constraint {constraint_id}</b>")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full constraint properties
        if project and int(constraint_id) in project.constraints:
            constraint = project.constraints[int(constraint_id)]
            
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add constraint type
            if "type" in constraint:
                form_layout.addRow("Type:", QLabel(constraint["type"]))
                
            # Properties dictionary
            if "properties" in constraint and constraint["properties"]:
                properties_group = QGroupBox("Constraint Properties")
                properties_layout = QFormLayout(properties_group)
                
                for prop_name, prop_value in constraint["properties"].items():
                    if isinstance(prop_value, (int, float)):
                        # Format numbers with 4 decimal places
                        properties_layout.addRow(f"{prop_name}:", QLabel(f"{prop_value:.4f}"))
                    elif isinstance(prop_value, (list, tuple)):
                        # Format lists with commas
                        value_str = ", ".join(str(v) for v in prop_value)
                        properties_layout.addRow(f"{prop_name}:", QLabel(value_str))
                    else:
                        properties_layout.addRow(f"{prop_name}:", QLabel(str(prop_value)))
                
                # Add properties group to form
                form_layout.addRow(properties_group)
                
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Constraint ID: {constraint_id}\n\nProperties not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
        
    def show_recorder_properties(self, recorder_id):
        """Show properties of the selected recorder"""
        # Check if we have a project with recorders
        project = None
        if hasattr(self, 'project'):
            project = self.project
        elif hasattr(self.parent, 'project'):
            project = self.parent.project
            
        # Create label showing the recorder ID
        id_label = QLabel(f"<b>Recorder {recorder_id}</b>")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full recorder properties
        if project and int(recorder_id) in project.recorders:
            recorder = project.recorders[int(recorder_id)]
            
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add recorder properties
            if "type" in recorder:
                form_layout.addRow("Type:", QLabel(recorder["type"]))
                
            if "target" in recorder:
                form_layout.addRow("Target:", QLabel(str(recorder["target"])))
                
            if "file_name" in recorder:
                form_layout.addRow("Output File:", QLabel(recorder["file_name"]))
                
            if "time_interval" in recorder:
                form_layout.addRow("Time Interval:", QLabel(f"{recorder['time_interval']:.4f}"))
                
            if "dofs" in recorder and recorder["dofs"]:
                dof_str = ", ".join(str(d) for d in recorder["dofs"])
                form_layout.addRow("DOFs:", QLabel(dof_str))
                
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Recorder ID: {recorder_id}\n\nProperties not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
        
    def show_transformation_properties(self, transformation_id):
        """Show properties of the selected transformation"""
        # Check if we have a project with transformations
        project = None
        if hasattr(self, 'project'):
            project = self.project
        elif hasattr(self.parent, 'project'):
            project = self.parent.project
            
        # Create label showing the transformation ID
        id_label = QLabel(f"<b>Transformation {transformation_id}</b>")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full transformation properties
        if project and int(transformation_id) in project.transformations:
            transformation = project.transformations[int(transformation_id)]
            
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add transformation type
            if "type" in transformation:
                form_layout.addRow("Type:", QLabel(transformation["type"]))
                
            # Properties dictionary
            if "properties" in transformation and transformation["properties"]:
                properties_group = QGroupBox("Transformation Properties")
                properties_layout = QFormLayout(properties_group)
                
                for prop_name, prop_value in transformation["properties"].items():
                    if isinstance(prop_value, (int, float)):
                        # Format numbers with 4 decimal places
                        properties_layout.addRow(f"{prop_name}:", QLabel(f"{prop_value:.4f}"))
                    elif isinstance(prop_value, (list, tuple)):
                        # Format vectors
                        value_str = ", ".join(f"{v:.4f}" if isinstance(v, (int, float)) else str(v) for v in prop_value)
                        properties_layout.addRow(f"{prop_name}:", QLabel(value_str))
                    else:
                        properties_layout.addRow(f"{prop_name}:", QLabel(str(prop_value)))
                
                # Add properties group to form
                form_layout.addRow(properties_group)
                
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Transformation ID: {transformation_id}\n\nProperties not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
        
    def show_timeseries_properties(self, timeseries_id):
        """Show properties of the selected timeseries"""
        # Check if we have a project with timeseries
        project = None
        if hasattr(self, 'project'):
            project = self.project
        elif hasattr(self.parent, 'project'):
            project = self.parent.project
            
        # Create label showing the timeseries ID
        id_label = QLabel(f"<b>Timeseries {timeseries_id}</b>")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full timeseries properties
        if project and int(timeseries_id) in project.timeseries:
            timeseries = project.timeseries[int(timeseries_id)]
            
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add timeseries type
            if "type" in timeseries:
                form_layout.addRow("Type:", QLabel(timeseries["type"]))
                
            # Properties dictionary
            if "properties" in timeseries and timeseries["properties"]:
                properties_group = QGroupBox("Timeseries Properties")
                properties_layout = QFormLayout(properties_group)
                
                for prop_name, prop_value in timeseries["properties"].items():
                    if isinstance(prop_value, (int, float)):
                        # Format numbers with 4 decimal places
                        properties_layout.addRow(f"{prop_name}:", QLabel(f"{prop_value:.4f}"))
                    elif isinstance(prop_value, (list, tuple)):
                        # For long lists, show a summary
                        if len(prop_value) > 10:
                            value_str = f"List with {len(prop_value)} values: [{prop_value[0]:.4f}, {prop_value[1]:.4f}, ...]"
                        else:
                            value_str = ", ".join(f"{v:.4f}" if isinstance(v, (int, float)) else str(v) for v in prop_value)
                        properties_layout.addRow(f"{prop_name}:", QLabel(value_str))
                    else:
                        properties_layout.addRow(f"{prop_name}:", QLabel(str(prop_value)))
                
                # Add properties group to form
                form_layout.addRow(properties_group)
                
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Timeseries ID: {timeseries_id}\n\nProperties not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
        
    def show_pattern_properties(self, pattern_id):
        """Show properties of the selected pattern"""
        # Check if we have a project with patterns
        project = None
        if hasattr(self, 'project'):
            project = self.project
        elif hasattr(self.parent, 'project'):
            project = self.parent.project
            
        # Create label showing the pattern ID
        id_label = QLabel(f"<b>Pattern {pattern_id}</b>")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full pattern properties
        if project and int(pattern_id) in project.patterns:
            pattern = project.patterns[int(pattern_id)]
            
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add pattern type
            if "type" in pattern:
                form_layout.addRow("Type:", QLabel(pattern["type"]))
                
            # Add timeseries reference
            if "timeseries" in pattern and pattern["timeseries"]:
                form_layout.addRow("Timeseries:", QLabel(str(pattern["timeseries"])))
                
            # Properties dictionary
            if "properties" in pattern and pattern["properties"]:
                properties_group = QGroupBox("Pattern Properties")
                properties_layout = QFormLayout(properties_group)
                
                for prop_name, prop_value in pattern["properties"].items():
                    if isinstance(prop_value, (int, float)):
                        # Format numbers with 4 decimal places
                        properties_layout.addRow(f"{prop_name}:", QLabel(f"{prop_value:.4f}"))
                    elif isinstance(prop_value, (list, tuple)):
                        # Format lists with commas
                        value_str = ", ".join(f"{v:.4f}" if isinstance(v, (int, float)) else str(v) for v in prop_value)
                        properties_layout.addRow(f"{prop_name}:", QLabel(value_str))
                    else:
                        properties_layout.addRow(f"{prop_name}:", QLabel(str(prop_value)))
                
                # Add properties group to form
                form_layout.addRow(properties_group)
                
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Pattern ID: {pattern_id}\n\nProperties not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
        
    def toggle_model_explorer(self, visible):
        """Toggle the visibility of the model explorer panel"""
        self.left_panel.setVisible(visible)
        
    def toggle_properties_panel(self, visible):
        """Toggle the visibility of the properties panel"""
        self.right_panel.setVisible(visible)
        
    def toggle_console(self, visible):
        """Toggle the visibility of the console panel"""
        self.terminal_panel.setVisible(visible)
        
    def toggle_3d_view_tab(self, visible):
        """Toggle the visibility of the 3D view tab"""
        tab_index = self.find_tab_by_name("3D View")
        
        if visible and tab_index == -1:
            # 3D View tab doesn't exist and should be shown, create it
            self.create_3d_scene_tab()
            # Hide welcome if it was showing
            self.welcome_widget.setVisible(False)
            self.tabs.setVisible(True)
        elif not visible and tab_index != -1:
            # Tab exists and should be hidden, remove it
            self.tabs.removeTab(tab_index)
            
            # Show welcome widget if no tabs are left
            if self.tabs.count() == 0:
                self.welcome_widget.setVisible(True)
                self.tabs.setVisible(False)
            
    def find_tab_by_name(self, tab_name):
        """Find a tab by its name, return -1 if not found"""
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_name:
                return i
        return -1

    def change_visualization_color(self, component_type):
        """Change the color of various visualization components
        
        Args:
            component_type (str): Type of component - "node", "element", "load", "label", "bc", or "selection"
        """
        from PyQt5.QtWidgets import QColorDialog
        from PyQt5.QtGui import QColor
        
        # Get current color from settings
        settings = QSettings("Modsee", "Modsee")
        current_color_str = settings.value(f"visualization/{component_type}_color", None)
        
        # Default colors if not set
        default_colors = {
            "node": QColor(255, 0, 0),        # Red for nodes
            "element": QColor(0, 0, 255),     # Blue for elements
            "load": QColor(255, 0, 0),        # Red for loads
            "label": QColor(255, 255, 255),   # White for labels
            "bc": QColor(0, 255, 0),          # Green for boundary conditions
            "selection": QColor(255, 255, 0)  # Yellow for selection highlight
        }
        
        # Convert string to QColor or use default
        if current_color_str:
            parts = current_color_str.split(',')
            if len(parts) >= 3:
                current_color = QColor(int(parts[0]), int(parts[1]), int(parts[2]))
            else:
                current_color = default_colors[component_type]
        else:
            current_color = default_colors[component_type]
            
        # Show color dialog
        title = "Select Selection Highlight Color" if component_type == "selection" else f"Select {component_type.capitalize()} Color"
        color = QColorDialog.getColor(current_color, self, title)
        
        # If a valid color was selected, save it
        if color.isValid():
            # Save color to settings
            color_str = f"{color.red()},{color.green()},{color.blue()}"
            settings.setValue(f"visualization/{component_type}_color", color_str)
            settings.sync()
            
            # Log color change
            component_name = "Selection highlight" if component_type == "selection" else component_type
            self.terminal_output.addItem(f"> Changed {component_name} color to RGB({color.red()}, {color.green()}, {color.blue()})")
            
            # Apply the color change to the visualization
            self.apply_visualization_color(component_type, color)
    
    def apply_visualization_color(self, component_type, color):
        """Apply the selected color to the visualization
        
        Args:
            component_type (str): Type of component - "node", "element", "load", "label", "bc", or "selection"
            color (QColor): The color to apply
        """
        # First convert QColor to VTK format (0-1 range)
        r, g, b = color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0
        
        # Find the scene instance
        scene = None
        if hasattr(self, 'scene') and self.scene is not None:
            scene = self.scene
        
        if scene is not None:
            # Apply based on component type
            if component_type == "node":
                # Update node color in scene
                for node_id, node_info in scene.nodes.items():
                    if "actor" in node_info:
                        node_info["actor"].GetProperty().SetColor(r, g, b)
                
                # Store for future nodes
                scene.node_color = (r, g, b)
                
            elif component_type == "element":
                # Update element color in scene
                for element_id, element_info in scene.elements.items():
                    if "actor" in element_info:
                        element_info["actor"].GetProperty().SetColor(r, g, b)
                
                # Store for future elements
                scene.element_color = (r, g, b)
                
            elif component_type == "load":
                # Update load color in scene
                for load_id, load_info in scene.loads.items():
                    if "actor" in load_info:
                        load_info["actor"].GetProperty().SetColor(r, g, b)
                
                # Store for future loads
                scene.load_color = (r, g, b)
                
            elif component_type == "bc":
                # Update boundary condition color in scene
                for bc_id, bc_info in scene.boundary_conditions.items():
                    if "actor" in bc_info:
                        # Update the color of the actor
                        bc_info["actor"].GetProperty().SetColor(r, g, b)
                        
                        # We might need to redraw certain types of complex boundary conditions
                        # For now we just update the color, but in the future we might need
                        # to recreate the symbol with the new color
                
                # Store for future boundary conditions
                scene.bc_color = (r, g, b)
                
                # Log that we've updated the boundary condition colors
                self.terminal_output.addItem(f"> Updated boundary condition colors - refreshed {len(scene.boundary_conditions)} symbols")
                
            elif component_type == "label":
                # Update label colors
                # For load labels
                for load_id, load_info in scene.loads.items():
                    if "label" in load_info and load_info["label"]:
                        load_info["label"].GetProperty().SetColor(r, g, b)
                
                # For boundary condition labels
                for bc_id, bc_info in scene.boundary_conditions.items():
                    if "label" in bc_info and bc_info["label"]:
                        bc_info["label"].GetProperty().SetColor(r, g, b)
                
                # Store for future labels
                scene.label_color = (r, g, b)
            
            elif component_type == "selection":
                # Store the selection highlight color
                scene.selection_color = (r, g, b)
                
                # If there's currently something selected, update its color
                if hasattr(scene, 'selected_actor') and scene.selected_actor:
                    scene.selected_actor.GetProperty().SetColor(r, g, b)
                
                # Log success
                self.terminal_output.addItem(f"> Updated selection highlight color - will be used for future selections")
            
            # Force a render update
            scene.vtk_widget.GetRenderWindow().Render()
            
            # Log success
            if component_type != "selection":  # Already logged for selection
                self.terminal_output.addItem(f"> Updated {component_type} colors in visualization")
        else:
            # Log that the scene couldn't be found
            self.terminal_output.addItem(f"> Warning: Could not find 3D scene to update {component_type} color")

    def select_in_scene(self, object_type, object_id):
        """Select an object in the scene based on its type and ID
        
        Args:
            object_type (str): Type of object ('node', 'element', 'material', 'section', 'constraint', 
                              'boundary_condition', 'load', 'recorder', 'transformation', 'timeseries', 'pattern')
            object_id (str or int): ID of the object to select
        """
        # Ensure the scene exists
        if not hasattr(self, 'scene'):
            return
            
        # Clear the current selection first
        self.scene.clear_selection()
        
        # Convert ID to the appropriate type (often integer)
        try:
            object_id = int(object_id)
        except (ValueError, TypeError):
            # If conversion fails, keep as is
            pass
            
        # Components that don't have 3D representation
        non_3d_types = ["material", "section", "constraint", "recorder", 
                        "transformation", "timeseries", "pattern"]
                        
        if object_type in non_3d_types:
            # Just display properties in the properties panel
            self.handle_scene_selection(object_type, object_id)
            return
            
        # Find and select the actor based on the object type and ID
        if object_type == "node" and hasattr(self.scene, 'node_actors'):
            if object_id in self.scene.node_actors:
                actor = self.scene.node_actors[object_id]
                self.scene.handle_selection(actor)
                
        elif object_type == "element" and hasattr(self.scene, 'element_actors'):
            if object_id in self.scene.element_actors:
                actor = self.scene.element_actors[object_id]
                self.scene.handle_selection(actor)
                
        elif object_type == "boundary_condition" and hasattr(self.scene, 'bc_actors'):
            if object_id in self.scene.bc_actors:
                actor = self.scene.bc_actors[object_id]
                self.scene.handle_selection(actor)
                
        elif object_type == "load" and hasattr(self.scene, 'load_actors'):
            if object_id in self.scene.load_actors:
                actor = self.scene.load_actors[object_id]
                self.scene.handle_selection(actor)
        
        # Update the properties panel
        self.handle_scene_selection(object_type, object_id)
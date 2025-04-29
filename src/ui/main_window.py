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
    QLabel, QPushButton, QToolButton, QMessageBox, QFileDialog, QDialog
)
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QIcon, QColor, QPalette

# Import ModseeScene for 3D visualization
from ..visualization.scene import ModseeScene

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
        
        # View menu
        self.view_menu = QMenu("&View", self.menu_bar)
        self.menu_bar.addMenu(self.view_menu)
        
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
        
        # Set splitter sizes
        self.main_splitter.setSizes([250, 700, 250])
    
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
        self.terminal_layout.addWidget(self.terminal_output)
        
        # Add some example output
        self.terminal_output.addItem("Welcome to Modsee - OpenSees Finite Element Modeling Interface")
        self.terminal_output.addItem("> Ready to start modeling")
        
    def create_left_panel(self):
        """Create the left panel (model explorer)"""
        self.left_panel = QFrame()
        self.left_panel.setObjectName("leftPanel")
        self.left_panel.setFrameShape(QFrame.StyledPanel)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)
        
        # Model explorer header
        self.left_header = QFrame()
        self.left_header.setObjectName("panelHeader")
        self.left_header.setStyleSheet("#panelHeader { background-color: #E0E0E0; border-bottom: 1px solid #CCCCCC; }")
        self.left_header.setMinimumHeight(30)
        self.left_header.setMaximumHeight(30)
        
        self.left_header_layout = QHBoxLayout(self.left_header)
        self.left_header_layout.setContentsMargins(8, 0, 8, 0)
        
        # Model explorer title
        self.left_title = QLabel("Model Explorer")
        self.left_title.setStyleSheet("font-weight: bold; color: #333333;")
        self.left_header_layout.addWidget(self.left_title)
        
        # Add header to left layout
        self.left_layout.addWidget(self.left_header)
        
        # Model tree view
        self.model_tree = QTreeView()
        self.model_tree.setAlternatingRowColors(True)
        self.model_tree.setHeaderHidden(True)
        self.model_tree.setStyleSheet("border: none;")
        self.left_layout.addWidget(self.model_tree)
        
        # Add to splitter
        self.main_splitter.addWidget(self.left_panel)
        
    def create_center_panel(self):
        """Create the center panel (main view area)"""
        self.center_panel = QFrame()
        self.center_panel.setObjectName("centerPanel")
        self.center_panel.setStyleSheet("#centerPanel { background-color: white; }")
        self.center_layout = QVBoxLayout(self.center_panel)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(0)
        
        # View tabs
        self.view_tabs = QTabWidget()
        self.view_tabs.setTabPosition(QTabWidget.North)
        self.view_tabs.setDocumentMode(True)
        
        # 3D view with actual ModseeScene implementation
        self.view_3d = QWidget()
        self.view_3d.setStyleSheet("background-color: #FAFAFA;")
        self.view_3d_layout = QVBoxLayout(self.view_3d)
        self.view_3d_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the 3D scene widget
        self.scene_3d = ModseeScene(self)
        self.view_3d_layout.addWidget(self.scene_3d)
        
        # Analysis view placeholder
        self.view_analysis = QWidget()
        self.view_analysis.setStyleSheet("background-color: #FAFAFA;")
        self.view_analysis_layout = QVBoxLayout(self.view_analysis)
        self.view_analysis_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a styled container for the analysis view placeholder
        self.view_analysis_container = QFrame()
        self.view_analysis_container.setStyleSheet("background-color: white; border: 1px dashed #CCCCCC; border-radius: 4px; margin: 20px;")
        self.view_analysis_container_layout = QVBoxLayout(self.view_analysis_container)
        
        self.view_analysis_placeholder = QLabel("Analysis Results View\n(will be implemented)")
        self.view_analysis_placeholder.setAlignment(Qt.AlignCenter)
        self.view_analysis_placeholder.setStyleSheet("color: #757575; font-size: 14px; border: none;")
        self.view_analysis_container_layout.addWidget(self.view_analysis_placeholder)
        
        self.view_analysis_layout.addWidget(self.view_analysis_container)
        
        # Add tabs
        self.view_tabs.addTab(self.view_3d, "3D Model")
        self.view_tabs.addTab(self.view_analysis, "Analysis Results")
        
        # Add to layout
        self.center_layout.addWidget(self.view_tabs)
        
        # Add to splitter
        self.main_splitter.addWidget(self.center_panel)
        
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
        self.properties_placeholder = QLabel("Properties Panel\n(will show properties of selected objects)")
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
        
        # Coordinates display
        self.coordinates_display = QLabel("X: 0.00  Y: 0.00  Z: 0.00")
        self.coordinates_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Add to layout
        self.status_layout.addWidget(self.status_message, 1)
        self.status_layout.addWidget(self.coordinates_display)
        
        # Add to main layout
        self.main_layout.addWidget(self.status_frame)
        
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
        self.view_tabs.setStyleSheet("""
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
        from .settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.settings_changed()
            
    def settings_changed(self):
        """Handle settings changes"""
        # Reload settings and update the UI accordingly
        settings = QSettings("Modsee", "Modsee")
        
        # Update theme if changed
        theme = settings.value("theme", "Light")
        if theme != self.current_theme:
            self.current_theme = theme
            self.apply_theme(theme)
            
        # Update other UI elements based on settings
        # This is where you would update other UI elements based on settings changes 
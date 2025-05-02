"""
Theme Dialog for Modsee application.

This module provides a dialog for selecting and customizing themes.
"""

import logging
from typing import Dict, Optional, List, Tuple, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTabWidget, QWidget, QFormLayout, QColorDialog,
    QGroupBox, QGridLayout, QScrollArea, QSpinBox, QLineEdit,
    QFrame, QMessageBox
)
from PyQt6.QtGui import QColor, QFont, QPalette, QFontDatabase
from PyQt6.QtCore import Qt, pyqtSlot

from ui.theme_manager import ThemeManager, Theme, ThemeType, ColorSet, VTKColors

logger = logging.getLogger('modsee.ui.theme_dialog')


class ColorButton(QPushButton):
    """Button that shows a color and opens a color dialog when clicked."""
    
    def __init__(self, color: Tuple[float, float, float], parent=None):
        """
        Initialize the color button.
        
        Args:
            color: RGB color tuple (values 0.0-1.0).
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setMinimumSize(30, 30)
        self.setMaximumSize(30, 30)
        self._color = color
        self._update_style()
        self.clicked.connect(self._on_click)
    
    def _update_style(self):
        """Update the button style based on the current color."""
        r, g, b = [int(c * 255) for c in self._color]
        self.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid #888888;")
    
    def _on_click(self):
        """Handle button click to show color dialog."""
        r, g, b = [int(c * 255) for c in self._color]
        color = QColorDialog.getColor(QColor(r, g, b), self.parent())
        
        if color.isValid():
            self._color = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
            self._update_style()
    
    def get_color(self) -> Tuple[float, float, float]:
        """Get the current RGB color tuple."""
        return self._color
    
    def set_color(self, color: Tuple[float, float, float]):
        """Set the current RGB color tuple."""
        self._color = color
        self._update_style()


class ThemePreviewWidget(QFrame):
    """Widget that shows a preview of what a theme looks like."""
    
    def __init__(self, theme: Theme, parent=None):
        """
        Initialize the theme preview widget.
        
        Args:
            theme: The theme to preview.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.theme = theme
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumHeight(120)
        
        # Convert colors
        background = self._rgb_to_qcolor(theme.ui_colors.background)
        primary = self._rgb_to_qcolor(theme.ui_colors.primary)
        secondary = self._rgb_to_qcolor(theme.ui_colors.secondary)
        highlight = self._rgb_to_qcolor(theme.ui_colors.highlight)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Title bar to simulate a window
        title_bar = QFrame()
        title_bar.setStyleSheet(f"background-color: {self._qcolor_to_css(secondary)};")
        title_bar.setMaximumHeight(25)
        title_bar.setMinimumHeight(25)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(8, 0, 8, 0)
        
        title_label = QLabel("Theme Preview")
        if theme.type == ThemeType.DARK or theme.type == ThemeType.HIGH_CONTRAST:
            title_label.setStyleSheet("color: white;")
        else:
            title_label.setStyleSheet("color: black;")
        title_layout.addWidget(title_label)
        
        layout.addWidget(title_bar)
        
        # Content area
        content = QFrame()
        content.setStyleSheet(f"background-color: {self._qcolor_to_css(background)};")
        content_layout = QVBoxLayout(content)
        
        # Add some sample UI elements
        button = QPushButton("Sample Button")
        button.setStyleSheet(f"background-color: {self._qcolor_to_css(primary)}; color: white;")
        content_layout.addWidget(button)
        
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        combo.setStyleSheet(f"border: 1px solid {self._qcolor_to_css(secondary)};")
        content_layout.addWidget(combo)
        
        # Sample text with appropriate color
        text_label = QLabel("Sample text in theme colors")
        if theme.type == ThemeType.DARK or theme.type == ThemeType.HIGH_CONTRAST:
            text_label.setStyleSheet("color: white;")
        else:
            text_label.setStyleSheet("color: black;")
        content_layout.addWidget(text_label)
        
        # Add highlight example
        highlight_frame = QFrame()
        highlight_frame.setStyleSheet(f"background-color: {self._qcolor_to_css(highlight)}; border-radius: 3px;")
        highlight_frame.setMinimumHeight(20)
        content_layout.addWidget(highlight_frame)
        
        layout.addWidget(content)
    
    @staticmethod
    def _rgb_to_qcolor(rgb: Tuple[float, float, float]) -> QColor:
        """Convert RGB tuple to QColor."""
        return QColor(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    
    @staticmethod
    def _qcolor_to_css(color: QColor) -> str:
        """Convert QColor to CSS color string."""
        return f"rgb({color.red()}, {color.green()}, {color.blue()})"


class ThemeDialog(QDialog):
    """Dialog for selecting and customizing themes."""
    
    def __init__(self, theme_manager: ThemeManager, parent=None):
        """
        Initialize the theme dialog.
        
        Args:
            theme_manager: The theme manager instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.current_theme = theme_manager.current_theme
        self.custom_theme = None
        
        self.setWindowTitle("Theme Settings")
        self.resize(600, 500)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Theme selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Theme:"))
        
        self.theme_combo = QComboBox()
        self._populate_theme_combo()
        selector_layout.addWidget(self.theme_combo)
        
        layout.addLayout(selector_layout)
        
        # Preview area
        self.preview_widget = ThemePreviewWidget(self.current_theme)
        layout.addWidget(self.preview_widget)
        
        # Tabs for different customization options
        self.tab_widget = QTabWidget()
        
        # UI Colors Tab
        self.ui_colors_tab = QWidget()
        self._setup_ui_colors_tab()
        self.tab_widget.addTab(self.ui_colors_tab, "UI Colors")
        
        # VTK Colors Tab
        self.vtk_colors_tab = QWidget()
        self._setup_vtk_colors_tab()
        self.tab_widget.addTab(self.vtk_colors_tab, "3D View Colors")
        
        # Font & Style Tab
        self.style_tab = QWidget()
        self._setup_style_tab()
        self.tab_widget.addTab(self.style_tab, "Font & Style")
        
        layout.addWidget(self.tab_widget)
        
        # Save custom theme section
        save_layout = QHBoxLayout()
        self.custom_name_edit = QLineEdit()
        self.custom_name_edit.setPlaceholderText("Custom Theme Name")
        save_layout.addWidget(self.custom_name_edit)
        
        self.save_button = QPushButton("Save as Custom Theme")
        save_layout.addWidget(self.save_button)
        
        layout.addLayout(save_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.theme_combo.currentIndexChanged.connect(self._on_theme_selected)
        self.apply_button.clicked.connect(self._on_apply)
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self._on_save_custom)
        
        # Disable custom theme fields initially
        self._update_edit_state()
    
    def _populate_theme_combo(self):
        """Populate the theme combo box with available themes."""
        self.theme_combo.clear()
        
        # Add built-in themes
        for theme_type, theme in ThemeManager.THEMES.items():
            self.theme_combo.addItem(theme.name, theme_type)
        
        # Add custom themes
        custom_themes = self.theme_manager.get_custom_themes()
        for name, theme in custom_themes.items():
            self.theme_combo.addItem(name, (ThemeType.CUSTOM, name))
        
        # Set current theme
        current_theme = self.current_theme
        if current_theme.type == ThemeType.CUSTOM:
            for i in range(self.theme_combo.count()):
                data = self.theme_combo.itemData(i)
                if isinstance(data, tuple) and data[0] == ThemeType.CUSTOM and data[1] == current_theme.name:
                    self.theme_combo.setCurrentIndex(i)
                    break
        else:
            for i in range(self.theme_combo.count()):
                data = self.theme_combo.itemData(i)
                if data == current_theme.type:
                    self.theme_combo.setCurrentIndex(i)
                    break
    
    def _setup_ui_colors_tab(self):
        """Set up the UI colors tab."""
        layout = QVBoxLayout(self.ui_colors_tab)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QFormLayout(scroll_content)
        
        # UI Colors
        colors_group = QGroupBox("Application UI Colors")
        colors_layout = QFormLayout(colors_group)
        
        self.ui_color_buttons = {}
        
        # Create color buttons for each UI color
        self.ui_color_buttons['primary'] = ColorButton(self.current_theme.ui_colors.primary)
        colors_layout.addRow("Primary:", self.ui_color_buttons['primary'])
        
        self.ui_color_buttons['secondary'] = ColorButton(self.current_theme.ui_colors.secondary)
        colors_layout.addRow("Secondary:", self.ui_color_buttons['secondary'])
        
        self.ui_color_buttons['background'] = ColorButton(self.current_theme.ui_colors.background)
        colors_layout.addRow("Background:", self.ui_color_buttons['background'])
        
        self.ui_color_buttons['highlight'] = ColorButton(self.current_theme.ui_colors.highlight)
        colors_layout.addRow("Highlight:", self.ui_color_buttons['highlight'])
        
        self.ui_color_buttons['selected'] = ColorButton(self.current_theme.ui_colors.selected)
        colors_layout.addRow("Selected:", self.ui_color_buttons['selected'])
        
        self.ui_color_buttons['error'] = ColorButton(self.current_theme.ui_colors.error)
        colors_layout.addRow("Error:", self.ui_color_buttons['error'])
        
        self.ui_color_buttons['warning'] = ColorButton(self.current_theme.ui_colors.warning)
        colors_layout.addRow("Warning:", self.ui_color_buttons['warning'])
        
        self.ui_color_buttons['success'] = ColorButton(self.current_theme.ui_colors.success)
        colors_layout.addRow("Success:", self.ui_color_buttons['success'])
        
        scroll_layout.addWidget(colors_group)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
    
    def _setup_vtk_colors_tab(self):
        """Set up the VTK colors tab."""
        layout = QVBoxLayout(self.vtk_colors_tab)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QFormLayout(scroll_content)
        
        # 3D View Colors
        vtk_group = QGroupBox("3D View Colors")
        vtk_layout = QFormLayout(vtk_group)
        
        self.vtk_color_buttons = {}
        
        # Create color buttons for each VTK color
        self.vtk_color_buttons['background'] = ColorButton(self.current_theme.vtk_colors.background)
        vtk_layout.addRow("Background:", self.vtk_color_buttons['background'])
        
        self.vtk_color_buttons['node'] = ColorButton(self.current_theme.vtk_colors.node)
        vtk_layout.addRow("Node:", self.vtk_color_buttons['node'])
        
        self.vtk_color_buttons['element'] = ColorButton(self.current_theme.vtk_colors.element)
        vtk_layout.addRow("Element:", self.vtk_color_buttons['element'])
        
        self.vtk_color_buttons['selected_node'] = ColorButton(self.current_theme.vtk_colors.selected_node)
        vtk_layout.addRow("Selected Node:", self.vtk_color_buttons['selected_node'])
        
        self.vtk_color_buttons['selected_element'] = ColorButton(self.current_theme.vtk_colors.selected_element)
        vtk_layout.addRow("Selected Element:", self.vtk_color_buttons['selected_element'])
        
        self.vtk_color_buttons['grid'] = ColorButton(self.current_theme.vtk_colors.grid)
        vtk_layout.addRow("Grid:", self.vtk_color_buttons['grid'])
        
        self.vtk_color_buttons['axis_x'] = ColorButton(self.current_theme.vtk_colors.axis_x)
        vtk_layout.addRow("X Axis:", self.vtk_color_buttons['axis_x'])
        
        self.vtk_color_buttons['axis_y'] = ColorButton(self.current_theme.vtk_colors.axis_y)
        vtk_layout.addRow("Y Axis:", self.vtk_color_buttons['axis_y'])
        
        self.vtk_color_buttons['axis_z'] = ColorButton(self.current_theme.vtk_colors.axis_z)
        vtk_layout.addRow("Z Axis:", self.vtk_color_buttons['axis_z'])
        
        self.vtk_color_buttons['boundary_condition'] = ColorButton(self.current_theme.vtk_colors.boundary_condition)
        vtk_layout.addRow("Boundary Condition:", self.vtk_color_buttons['boundary_condition'])
        
        self.vtk_color_buttons['load'] = ColorButton(self.current_theme.vtk_colors.load)
        vtk_layout.addRow("Load:", self.vtk_color_buttons['load'])
        
        self.vtk_color_buttons['text'] = ColorButton(self.current_theme.vtk_colors.text)
        vtk_layout.addRow("Text:", self.vtk_color_buttons['text'])
        
        scroll_layout.addWidget(vtk_group)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
    
    def _setup_style_tab(self):
        """Set up the font and style tab."""
        layout = QVBoxLayout(self.style_tab)
        
        # Font settings
        font_group = QGroupBox("Font Settings")
        font_layout = QFormLayout(font_group)
        
        self.font_family_combo = QComboBox()
        # Use QFontDatabase static method to get font families
        for family in QFontDatabase.families():
            self.font_family_combo.addItem(family)
        
        # Try to set the current font family
        index = self.font_family_combo.findText(self.current_theme.font_family)
        if index >= 0:
            self.font_family_combo.setCurrentIndex(index)
        
        font_layout.addRow("Font Family:", self.font_family_combo)
        
        # Font sizes
        self.font_size_normal = QSpinBox()
        self.font_size_normal.setRange(6, 24)
        self.font_size_normal.setValue(self.current_theme.font_size_normal)
        font_layout.addRow("Normal Font Size:", self.font_size_normal)
        
        self.font_size_small = QSpinBox()
        self.font_size_small.setRange(6, 20)
        self.font_size_small.setValue(self.current_theme.font_size_small)
        font_layout.addRow("Small Font Size:", self.font_size_small)
        
        self.font_size_large = QSpinBox()
        self.font_size_large.setRange(8, 28)
        self.font_size_large.setValue(self.current_theme.font_size_large)
        font_layout.addRow("Large Font Size:", self.font_size_large)
        
        self.font_size_title = QSpinBox()
        self.font_size_title.setRange(10, 36)
        self.font_size_title.setValue(self.current_theme.font_size_title)
        font_layout.addRow("Title Font Size:", self.font_size_title)
        
        layout.addWidget(font_group)
        
        # UI style settings
        style_group = QGroupBox("UI Style")
        style_layout = QFormLayout(style_group)
        
        self.corner_radius = QSpinBox()
        self.corner_radius.setRange(0, 12)
        self.corner_radius.setValue(self.current_theme.ui_corner_radius)
        style_layout.addRow("Corner Radius:", self.corner_radius)
        
        self.border_width = QSpinBox()
        self.border_width.setRange(0, 5)
        self.border_width.setValue(self.current_theme.ui_border_width)
        style_layout.addRow("Border Width:", self.border_width)
        
        layout.addWidget(style_group)
        layout.addStretch()
    
    def _on_theme_selected(self, index: int):
        """
        Handle theme selection from the combo box.
        
        Args:
            index: Selected index in the combo box.
        """
        data = self.theme_combo.itemData(index)
        
        if isinstance(data, tuple) and data[0] == ThemeType.CUSTOM:
            # Custom theme
            custom_name = data[1]
            custom_themes = self.theme_manager.get_custom_themes()
            if custom_name in custom_themes:
                self.custom_theme = custom_themes[custom_name]
                self._update_ui_from_theme(self.custom_theme)
        elif data is not None:
            # Built-in theme
            theme_type = data
            if theme_type in ThemeManager.THEMES:
                theme = ThemeManager.THEMES[theme_type]
                self.custom_theme = None
                self._update_ui_from_theme(theme)
            else:
                logger.warning(f"Unknown theme type: {theme_type}")
        else:
            logger.warning("Theme selection has no associated data")
        
        self._update_edit_state()
    
    def _update_ui_from_theme(self, theme: Theme):
        """
        Update the UI elements to reflect the selected theme.
        
        Args:
            theme: The theme to display.
        """
        # Update preview
        self.preview_widget.theme = theme
        self.preview_widget.update()
        
        # Update UI color buttons
        for key, button in self.ui_color_buttons.items():
            button.set_color(getattr(theme.ui_colors, key))
        
        # Update VTK color buttons
        for key, button in self.vtk_color_buttons.items():
            button.set_color(getattr(theme.vtk_colors, key))
        
        # Update font and style settings
        index = self.font_family_combo.findText(theme.font_family)
        if index >= 0:
            self.font_family_combo.setCurrentIndex(index)
        
        self.font_size_normal.setValue(theme.font_size_normal)
        self.font_size_small.setValue(theme.font_size_small)
        self.font_size_large.setValue(theme.font_size_large)
        self.font_size_title.setValue(theme.font_size_title)
        
        self.corner_radius.setValue(theme.ui_corner_radius)
        self.border_width.setValue(theme.ui_border_width)
    
    def _update_edit_state(self):
        """Update the enabled state of the edit controls."""
        is_custom = self.custom_theme is not None or self.theme_combo.currentText() not in [t.name for t in ThemeManager.THEMES.values()]
        
        # Enable custom theme editing
        self._set_controls_enabled(is_custom)
        
        # Set custom name field if we're working with a custom theme
        if self.custom_theme:
            self.custom_name_edit.setText(self.custom_theme.name)
    
    def _set_controls_enabled(self, enabled: bool):
        """
        Set the enabled state of all color and style controls.
        
        Args:
            enabled: Whether the controls should be enabled.
        """
        # UI color buttons
        for button in self.ui_color_buttons.values():
            button.setEnabled(enabled)
        
        # VTK color buttons
        for button in self.vtk_color_buttons.values():
            button.setEnabled(enabled)
        
        # Font and style settings
        self.font_family_combo.setEnabled(enabled)
        self.font_size_normal.setEnabled(enabled)
        self.font_size_small.setEnabled(enabled)
        self.font_size_large.setEnabled(enabled)
        self.font_size_title.setEnabled(enabled)
        self.corner_radius.setEnabled(enabled)
        self.border_width.setEnabled(enabled)
    
    def _create_theme_from_current_settings(self, name: str) -> Theme:
        """
        Create a theme object from the current UI settings.
        
        Args:
            name: The name for the theme.
            
        Returns:
            A Theme object with the current settings.
        """
        # Create UI colors
        ui_colors = ColorSet(
            primary=self.ui_color_buttons['primary'].get_color(),
            secondary=self.ui_color_buttons['secondary'].get_color(),
            background=self.ui_color_buttons['background'].get_color(),
            highlight=self.ui_color_buttons['highlight'].get_color(),
            selected=self.ui_color_buttons['selected'].get_color(),
            error=self.ui_color_buttons['error'].get_color(),
            warning=self.ui_color_buttons['warning'].get_color(),
            success=self.ui_color_buttons['success'].get_color()
        )
        
        # Create VTK colors
        vtk_colors = VTKColors(
            background=self.vtk_color_buttons['background'].get_color(),
            node=self.vtk_color_buttons['node'].get_color(),
            element=self.vtk_color_buttons['element'].get_color(),
            selected_node=self.vtk_color_buttons['selected_node'].get_color(),
            selected_element=self.vtk_color_buttons['selected_element'].get_color(),
            grid=self.vtk_color_buttons['grid'].get_color(),
            axis_x=self.vtk_color_buttons['axis_x'].get_color(),
            axis_y=self.vtk_color_buttons['axis_y'].get_color(),
            axis_z=self.vtk_color_buttons['axis_z'].get_color(),
            boundary_condition=self.vtk_color_buttons['boundary_condition'].get_color(),
            load=self.vtk_color_buttons['load'].get_color(),
            text=self.vtk_color_buttons['text'].get_color()
        )
        
        # Create theme
        return Theme(
            name=name,
            type=ThemeType.CUSTOM,
            ui_colors=ui_colors,
            vtk_colors=vtk_colors,
            font_family=self.font_family_combo.currentText(),
            font_size_normal=self.font_size_normal.value(),
            font_size_small=self.font_size_small.value(),
            font_size_large=self.font_size_large.value(),
            font_size_title=self.font_size_title.value(),
            ui_corner_radius=self.corner_radius.value(),
            ui_border_width=self.border_width.value()
        )
    
    def _on_save_custom(self):
        """Handle saving a custom theme."""
        name = self.custom_name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a name for your custom theme.")
            return
        
        # Check if name exists
        if name in self.theme_manager.get_custom_themes() and (
                not self.custom_theme or name != self.custom_theme.name):
            confirm = QMessageBox.question(
                self,
                "Confirm Overwrite",
                f"A custom theme named '{name}' already exists. Do you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if confirm != QMessageBox.StandardButton.Yes:
                return
        
        # Create and save the custom theme
        theme = self._create_theme_from_current_settings(name)
        self.theme_manager.add_custom_theme(theme)
        
        # Update the combo box
        current_text = self.theme_combo.currentText()
        self._populate_theme_combo()
        
        # Find and select the custom theme in the combo box
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemText(i) == name:
                self.theme_combo.setCurrentIndex(i)
                break
        
        QMessageBox.information(self, "Theme Saved", f"Custom theme '{name}' has been saved.")
    
    def _on_apply(self):
        """Handle applying the current theme."""
        if self.custom_theme:
            # Apply custom theme
            self.theme_manager.set_theme(ThemeType.CUSTOM, self.custom_theme.name)
        else:
            # Apply built-in theme
            theme_type = self.theme_combo.currentData()
            self.theme_manager.set_theme(theme_type)
    
    def _on_ok(self):
        """Handle OK button click."""
        self._on_apply()
        self.accept()


def show_theme_dialog(theme_manager: ThemeManager, parent=None) -> bool:
    """
    Show the theme selection dialog.
    
    Args:
        theme_manager: The theme manager instance.
        parent: The parent widget.
        
    Returns:
        True if the dialog was accepted, False otherwise.
    """
    dialog = ThemeDialog(theme_manager, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted 
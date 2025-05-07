"""
Theme Manager for Modsee application.

This module manages color themes and visual styling for the Modsee application.
It provides a centralized way to control the appearance of the application.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger('modsee.ui.theme_manager')


class ThemeType(Enum):
    """Enumeration of available theme types."""
    LIGHT = "light"
    DARK = "dark"
    BLUE = "blue"
    HIGH_CONTRAST = "high_contrast"
    CUSTOM = "custom"


@dataclass
class ColorSet:
    """Class to hold a set of colors for a specific component."""
    primary: Tuple[float, float, float]
    secondary: Tuple[float, float, float]
    background: Tuple[float, float, float]
    highlight: Tuple[float, float, float]
    selected: Tuple[float, float, float]
    error: Tuple[float, float, float]
    warning: Tuple[float, float, float]
    success: Tuple[float, float, float]


@dataclass
class VTKColors:
    """Class to hold VTK-specific colors."""
    background: Tuple[float, float, float]
    node: Tuple[float, float, float]
    element: Tuple[float, float, float]
    selected_node: Tuple[float, float, float]
    selected_element: Tuple[float, float, float]
    grid: Tuple[float, float, float]
    axis_x: Tuple[float, float, float]
    axis_y: Tuple[float, float, float]
    axis_z: Tuple[float, float, float]
    boundary_condition: Tuple[float, float, float]
    load: Tuple[float, float, float]
    text: Tuple[float, float, float]


@dataclass
class Theme:
    """Class to represent a complete application theme."""
    name: str
    type: ThemeType
    ui_colors: ColorSet
    vtk_colors: VTKColors
    font_family: str = "Segoe UI"
    font_size_normal: int = 9
    font_size_small: int = 8
    font_size_large: int = 12
    font_size_title: int = 14
    ui_corner_radius: int = 4
    ui_border_width: int = 1


class ThemeManager(QObject):
    """
    Manager for application-wide color themes and visual styling.
    """
    
    # Signal emitted when the theme changes
    theme_changed = pyqtSignal(Theme)
    
    # Predefined themes
    THEMES = {
        # Light theme (default)
        ThemeType.LIGHT: Theme(
            name="Light",
            type=ThemeType.LIGHT,
            ui_colors=ColorSet(
                primary=(0.0, 120/255, 215/255),  # Blue
                secondary=(100/255, 100/255, 100/255),  # Dark gray
                background=(240/255, 240/255, 240/255),  # Light gray
                highlight=(0.0, 150/255, 215/255),  # Light blue
                selected=(220/255, 240/255, 255/255),  # Very light blue
                error=(200/255, 0.0, 0.0),  # Red
                warning=(200/255, 150/255, 0.0),  # Orange
                success=(0.0, 150/255, 0.0)  # Green
            ),
            vtk_colors=VTKColors(
                background=(0.9, 0.9, 0.9),  # Light gray
                node=(1.0, 0.0, 0.0),  # Red
                element=(0.0, 0.0, 1.0),  # Blue
                selected_node=(1.0, 0.7, 0.0),  # Orange
                selected_element=(1.0, 0.7, 0.0),  # Orange
                grid=(0.8, 0.8, 0.8),  # Gray
                axis_x=(1.0, 0.0, 0.0),  # Red
                axis_y=(0.0, 0.7, 0.0),  # Green
                axis_z=(0.0, 0.0, 1.0),  # Blue
                boundary_condition=(0.0, 0.6, 0.0),  # Green
                load=(0.8, 0.0, 0.8),  # Purple
                text=(0.0, 0.0, 0.0)  # Black
            )
        ),
        
        # Dark theme
        ThemeType.DARK: Theme(
            name="Dark",
            type=ThemeType.DARK,
            ui_colors=ColorSet(
                primary=(0.0, 120/255, 215/255),  # Blue
                secondary=(200/255, 200/255, 200/255),  # Light gray
                background=(45/255, 45/255, 48/255),  # Dark gray
                highlight=(0.0, 150/255, 215/255),  # Light blue
                selected=(40/255, 62/255, 80/255),  # Deep blue
                error=(220/255, 50/255, 50/255),  # Red
                warning=(220/255, 170/255, 50/255),  # Orange
                success=(40/255, 180/255, 40/255)  # Green
            ),
            vtk_colors=VTKColors(
                background=(0.2, 0.2, 0.2),  # Dark gray
                node=(1.0, 0.4, 0.4),  # Light red
                element=(0.4, 0.6, 1.0),  # Light blue
                selected_node=(1.0, 0.8, 0.0),  # Yellow
                selected_element=(1.0, 0.8, 0.0),  # Yellow
                grid=(0.3, 0.3, 0.3),  # Dark gray
                axis_x=(1.0, 0.4, 0.4),  # Light red
                axis_y=(0.4, 0.9, 0.4),  # Light green
                axis_z=(0.4, 0.6, 1.0),  # Light blue
                boundary_condition=(0.4, 0.9, 0.4),  # Light green
                load=(1.0, 0.6, 1.0),  # Light purple
                text=(0.9, 0.9, 0.9)  # Light gray
            )
        ),
        
        # Blue theme
        ThemeType.BLUE: Theme(
            name="Blue",
            type=ThemeType.BLUE,
            ui_colors=ColorSet(
                primary=(25/255, 121/255, 202/255),  # Medium blue
                secondary=(80/255, 80/255, 80/255),  # Gray
                background=(225/255, 235/255, 245/255),  # Very light blue
                highlight=(41/255, 128/255, 185/255),  # Lighter blue
                selected=(213/255, 233/255, 249/255),  # Very light blue
                error=(192/255, 57/255, 43/255),  # Red
                warning=(211/255, 84/255, 0.0),  # Orange
                success=(39/255, 174/255, 96/255)  # Green
            ),
            vtk_colors=VTKColors(
                background=(0.9, 0.95, 1.0),  # Very light blue
                node=(0.8, 0.2, 0.2),  # Dark red
                element=(0.2, 0.4, 0.8),  # Dark blue
                selected_node=(1.0, 0.7, 0.0),  # Orange
                selected_element=(1.0, 0.7, 0.0),  # Orange
                grid=(0.7, 0.8, 0.9),  # Light blue-gray
                axis_x=(0.8, 0.2, 0.2),  # Dark red
                axis_y=(0.2, 0.6, 0.2),  # Dark green
                axis_z=(0.2, 0.4, 0.8),  # Dark blue
                boundary_condition=(0.2, 0.6, 0.2),  # Dark green
                load=(0.7, 0.2, 0.7),  # Dark purple
                text=(0.1, 0.1, 0.1)  # Near black
            )
        ),
        
        # High Contrast theme
        ThemeType.HIGH_CONTRAST: Theme(
            name="High Contrast",
            type=ThemeType.HIGH_CONTRAST,
            ui_colors=ColorSet(
                primary=(0.0, 0.0, 1.0),  # Blue
                secondary=(0.9, 0.9, 0.9),  # Very light gray
                background=(0.0, 0.0, 0.0),  # Black
                highlight=(1.0, 1.0, 0.0),  # Yellow
                selected=(0.0, 0.7, 0.0),  # Green
                error=(1.0, 0.0, 0.0),  # Red
                warning=(1.0, 0.5, 0.0),  # Orange
                success=(0.0, 1.0, 0.0)  # Bright green
            ),
            vtk_colors=VTKColors(
                background=(0.0, 0.0, 0.0),  # Black
                node=(1.0, 0.0, 0.0),  # Red
                element=(0.0, 1.0, 0.0),  # Green
                selected_node=(1.0, 1.0, 0.0),  # Yellow
                selected_element=(1.0, 1.0, 0.0),  # Yellow
                grid=(1.0, 1.0, 1.0),  # White
                axis_x=(1.0, 0.0, 0.0),  # Red
                axis_y=(0.0, 1.0, 0.0),  # Green
                axis_z=(0.0, 0.0, 1.0),  # Blue
                boundary_condition=(0.0, 1.0, 1.0),  # Cyan
                load=(1.0, 0.0, 1.0),  # Magenta
                text=(1.0, 1.0, 1.0)  # White
            ),
            font_size_normal=10,  # Slightly larger text for readability
            font_size_small=9
        )
    }
    
    def __init__(self):
        """Initialize the theme manager with default theme."""
        super().__init__()
        
        # Start with the default light theme
        self._current_theme = self.THEMES[ThemeType.LIGHT]
        
        # Store custom themes
        self._custom_themes: Dict[str, Theme] = {}
        
        logger.info("ThemeManager initialized with default light theme")
    
    @property
    def current_theme(self) -> Theme:
        """Get the current theme."""
        return self._current_theme
    
    def set_theme(self, theme_type: ThemeType, custom_name: Optional[str] = None) -> None:
        """
        Set the current theme.
        
        Args:
            theme_type: The type of theme to set.
            custom_name: For custom themes, the name of the theme.
        """
        if theme_type == ThemeType.CUSTOM and custom_name:
            if custom_name in self._custom_themes:
                self._current_theme = self._custom_themes[custom_name]
                logger.info(f"Applied custom theme: {custom_name}")
            else:
                logger.error(f"Custom theme not found: {custom_name}")
                return
        elif theme_type in self.THEMES:
            self._current_theme = self.THEMES[theme_type]
            logger.info(f"Applied theme: {theme_type.value}")
        else:
            logger.error(f"Unknown theme type: {theme_type}")
            return
        
        # Apply theme to the application
        self._apply_theme_to_application()
        
        # Emit signal to inform components of theme change
        self.theme_changed.emit(self._current_theme)
    
    def add_custom_theme(self, theme: Theme) -> None:
        """
        Add a custom theme.
        
        Args:
            theme: The custom theme to add.
        """
        if theme.type != ThemeType.CUSTOM:
            theme.type = ThemeType.CUSTOM
        
        self._custom_themes[theme.name] = theme
        logger.info(f"Added custom theme: {theme.name}")
    
    def remove_custom_theme(self, name: str) -> bool:
        """
        Remove a custom theme.
        
        Args:
            name: The name of the custom theme to remove.
            
        Returns:
            True if the theme was removed, False otherwise.
        """
        if name in self._custom_themes:
            if self._current_theme == self._custom_themes[name]:
                logger.warning("Cannot remove the currently active theme")
                return False
            
            del self._custom_themes[name]
            logger.info(f"Removed custom theme: {name}")
            return True
        else:
            logger.warning(f"Custom theme not found: {name}")
            return False
    
    def get_custom_themes(self) -> Dict[str, Theme]:
        """
        Get all custom themes.
        
        Returns:
            A dictionary of custom themes.
        """
        return self._custom_themes
    
    def get_available_themes(self) -> List[Theme]:
        """
        Get a list of all available themes (built-in and custom).
        
        Returns:
            A list of all available themes.
        """
        themes = list(self.THEMES.values())
        themes.extend(self._custom_themes.values())
        return themes
    
    def _apply_theme_to_application(self) -> None:
        """Apply the current theme to the application's palette."""
        app = QApplication.instance()
        if not app:
            logger.warning("QApplication instance not found, cannot apply theme")
            return
        
        palette = QPalette()
        theme = self._current_theme
        
        # Convert theme colors to QColors
        primary_color = self._rgb_float_to_qcolor(theme.ui_colors.primary)
        secondary_color = self._rgb_float_to_qcolor(theme.ui_colors.secondary)
        background_color = self._rgb_float_to_qcolor(theme.ui_colors.background)
        highlight_color = self._rgb_float_to_qcolor(theme.ui_colors.highlight)
        selected_color = self._rgb_float_to_qcolor(theme.ui_colors.selected)
        
        # Set application palette colors
        if theme.type == ThemeType.DARK or theme.type == ThemeType.HIGH_CONTRAST:
            # Dark theme specific palette
            text_color = QColor(240, 240, 240)  # Light text for dark backgrounds
            palette.setColor(QPalette.ColorRole.Window, background_color)
            palette.setColor(QPalette.ColorRole.WindowText, text_color)
            palette.setColor(QPalette.ColorRole.Base, QColor(60, 60, 60))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
            palette.setColor(QPalette.ColorRole.Text, text_color)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, text_color)
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Link, primary_color)
            palette.setColor(QPalette.ColorRole.Highlight, highlight_color)
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        else:
            # Light theme specific palette
            text_color = QColor(0, 0, 0)  # Dark text for light backgrounds
            palette.setColor(QPalette.ColorRole.Window, background_color)
            palette.setColor(QPalette.ColorRole.WindowText, text_color)
            palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
            palette.setColor(QPalette.ColorRole.Text, text_color)
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ButtonText, text_color)
            palette.setColor(QPalette.ColorRole.BrightText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Link, primary_color)
            palette.setColor(QPalette.ColorRole.Highlight, highlight_color)
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Apply palette to application
        app.setPalette(palette)
        
        # Set up global application stylesheet
        self._apply_stylesheet(app)
        
        logger.info("Applied theme to application palette and stylesheet")
    
    def _apply_stylesheet(self, app: QApplication) -> None:
        """
        Apply a stylesheet based on the current theme.
        
        Args:
            app: The QApplication instance.
        """
        theme = self._current_theme
        
        # Convert theme colors to stylable format
        primary = self._rgb_float_to_css(theme.ui_colors.primary)
        secondary = self._rgb_float_to_css(theme.ui_colors.secondary)
        background = self._rgb_float_to_css(theme.ui_colors.background)
        highlight = self._rgb_float_to_css(theme.ui_colors.highlight)
        selected = self._rgb_float_to_css(theme.ui_colors.selected)
        error = self._rgb_float_to_css(theme.ui_colors.error)
        warning = self._rgb_float_to_css(theme.ui_colors.warning)
        success = self._rgb_float_to_css(theme.ui_colors.success)
        
        # Set up a stylesheet with theme-specific styling
        stylesheet = f"""
        /* Global Styles */
        QWidget {{
            font-family: "{theme.font_family}";
            font-size: {theme.font_size_normal}pt;
        }}
        
        QMainWindow {{
            background-color: {background};
        }}
        
        QFrame {{
            border-radius: {theme.ui_corner_radius}px;
        }}
        
        /* Dock Widget Styling */
        QDockWidget {{
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }}
        
        QDockWidget::title {{
            background: {secondary};
            color: {primary};
            padding-left: 5px;
            padding-top: 2px;
        }}
        
        /* Menu and Toolbar Styling */
        QMenuBar {{
            background-color: {background};
            border-bottom: 1px solid {secondary};
        }}
        
        QMenuBar::item:selected {{
            background-color: {highlight};
        }}
        
        QMenu {{
            background-color: {background};
            border: 1px solid {secondary};
        }}
        
        QMenu::item:selected {{
            background-color: {selected};
        }}
        
        QToolBar {{
            background-color: {background};
            border: none;
            spacing: 3px;
        }}
        
        QToolButton {{
            border-radius: {theme.ui_corner_radius}px;
            padding: 3px;
        }}
        
        QToolButton:hover {{
            background-color: {selected};
        }}
        
        QToolButton:checked {{
            background-color: {highlight};
        }}
        
        /* Status Bar Styling */
        QStatusBar {{
            background-color: {background};
            border-top: 1px solid {secondary};
        }}
        
        /* Tab Widget Styling */
        QTabWidget::pane {{
            border: 1px solid {secondary};
            border-radius: {theme.ui_corner_radius}px;
        }}
        
        QTabBar::tab {{
            background-color: {background};
            border: 1px solid {secondary};
            border-bottom-color: {background};
            border-top-left-radius: {theme.ui_corner_radius}px;
            border-top-right-radius: {theme.ui_corner_radius}px;
            padding: 5px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {selected};
        }}
        
        /* Form Controls */
        QPushButton {{
            background-color: {primary};
            color: white;
            border-radius: {theme.ui_corner_radius}px;
            padding: 5px 10px;
        }}
        
        QPushButton:hover {{
            background-color: {highlight};
        }}
        
        QPushButton:disabled {{
            background-color: {secondary};
            color: #888888;
        }}
        
        QLineEdit, QTextEdit, QComboBox {{
            border: 1px solid {secondary};
            border-radius: {theme.ui_corner_radius}px;
            padding: 3px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 1px solid {primary};
        }}
        
        /* ScrollBar Styling */
        QScrollBar:vertical {{
            border: none;
            background-color: {background};
            width: 14px;
            margin: 15px 0 15px 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {secondary};
            min-height: 30px;
            border-radius: 7px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {primary};
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background-color: {background};
            height: 14px;
            margin: 0 15px 0 15px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {secondary};
            min-width: 30px;
            border-radius: 7px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {primary};
        }}
        """
        
        # Apply stylesheet to application
        app.setStyleSheet(stylesheet)
    
    @staticmethod
    def _rgb_float_to_qcolor(rgb: Tuple[float, float, float]) -> QColor:
        """
        Convert RGB floats (0.0-1.0) to QColor.
        
        Args:
            rgb: Tuple of RGB values (0.0-1.0).
            
        Returns:
            QColor object with the specified RGB values.
        """
        return QColor(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
    
    @staticmethod
    def _rgb_float_to_css(rgb: Tuple[float, float, float]) -> str:
        """
        Convert RGB floats (0.0-1.0) to CSS color string.
        
        Args:
            rgb: Tuple of RGB values (0.0-1.0).
            
        Returns:
            CSS color string in the format 'rgb(R, G, B)'.
        """
        return f"rgb({int(rgb[0] * 255)}, {int(rgb[1] * 255)}, {int(rgb[2] * 255)})" 
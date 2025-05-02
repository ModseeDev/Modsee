"""
Tests for the ThemeManager component.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication

from ui.theme_manager import ThemeManager, ThemeType, Theme, ColorSet, VTKColors


class TestThemeManager(unittest.TestCase):
    """Test cases for the ThemeManager class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up a QApplication for testing."""
        # QApplication is required for some theme operations
        cls.app = QApplication.instance() or QApplication(sys.argv)
    
    def setUp(self):
        """Create a ThemeManager instance for testing."""
        self.theme_manager = ThemeManager()
    
    def test_default_theme(self):
        """Test the default theme is set to Light."""
        self.assertEqual(self.theme_manager.current_theme.type, ThemeType.LIGHT)
        self.assertEqual(self.theme_manager.current_theme.name, "Light")
    
    def test_set_theme(self):
        """Test setting a different theme."""
        # Change to dark theme
        self.theme_manager.set_theme(ThemeType.DARK)
        self.assertEqual(self.theme_manager.current_theme.type, ThemeType.DARK)
        self.assertEqual(self.theme_manager.current_theme.name, "Dark")
        
        # Change to blue theme
        self.theme_manager.set_theme(ThemeType.BLUE)
        self.assertEqual(self.theme_manager.current_theme.type, ThemeType.BLUE)
        self.assertEqual(self.theme_manager.current_theme.name, "Blue")
        
        # Change to high contrast theme
        self.theme_manager.set_theme(ThemeType.HIGH_CONTRAST)
        self.assertEqual(self.theme_manager.current_theme.type, ThemeType.HIGH_CONTRAST)
        self.assertEqual(self.theme_manager.current_theme.name, "High Contrast")
        
        # Change back to light theme
        self.theme_manager.set_theme(ThemeType.LIGHT)
        self.assertEqual(self.theme_manager.current_theme.type, ThemeType.LIGHT)
        self.assertEqual(self.theme_manager.current_theme.name, "Light")
    
    def test_custom_theme(self):
        """Test adding and using a custom theme."""
        # Create a custom theme
        ui_colors = ColorSet(
            primary=(0.5, 0.0, 0.5),  # Purple
            secondary=(0.3, 0.3, 0.3),  # Dark gray
            background=(0.95, 0.9, 0.95),  # Very light purple
            highlight=(0.7, 0.3, 0.7),  # Medium purple
            selected=(0.9, 0.8, 0.9),  # Light purple
            error=(0.8, 0.2, 0.2),  # Red
            warning=(0.8, 0.6, 0.0),  # Orange
            success=(0.2, 0.8, 0.2)   # Green
        )
        
        vtk_colors = VTKColors(
            background=(0.95, 0.9, 0.95),  # Very light purple
            node=(0.5, 0.0, 0.5),  # Purple
            element=(0.3, 0.3, 0.3),  # Dark gray
            selected_node=(0.7, 0.3, 0.7),  # Medium purple
            selected_element=(0.7, 0.3, 0.7),  # Medium purple
            grid=(0.8, 0.8, 0.8),  # Light gray
            axis_x=(0.8, 0.2, 0.2),  # Red
            axis_y=(0.2, 0.8, 0.2),  # Green
            axis_z=(0.2, 0.2, 0.8),  # Blue
            boundary_condition=(0.2, 0.6, 0.2),  # Dark green
            load=(0.6, 0.2, 0.6),  # Dark purple
            text=(0.1, 0.1, 0.1)  # Near black
        )
        
        custom_theme = Theme(
            name="Custom Purple",
            type=ThemeType.CUSTOM,
            ui_colors=ui_colors,
            vtk_colors=vtk_colors,
            font_family="Arial",
            font_size_normal=10,
            font_size_small=8,
            font_size_large=12,
            font_size_title=16,
            ui_corner_radius=6,
            ui_border_width=1
        )
        
        # Add custom theme
        self.theme_manager.add_custom_theme(custom_theme)
        
        # Verify it was added
        custom_themes = self.theme_manager.get_custom_themes()
        self.assertIn("Custom Purple", custom_themes)
        
        # Apply custom theme
        self.theme_manager.set_theme(ThemeType.CUSTOM, "Custom Purple")
        
        # Verify it's the current theme
        self.assertEqual(self.theme_manager.current_theme.type, ThemeType.CUSTOM)
        self.assertEqual(self.theme_manager.current_theme.name, "Custom Purple")
        
        # Test removing custom theme
        # Try to remove the active theme (should fail)
        result = self.theme_manager.remove_custom_theme("Custom Purple")
        self.assertFalse(result)
        self.assertIn("Custom Purple", self.theme_manager.get_custom_themes())
        
        # Change to a different theme first, then remove
        self.theme_manager.set_theme(ThemeType.LIGHT)
        result = self.theme_manager.remove_custom_theme("Custom Purple")
        self.assertTrue(result)
        self.assertNotIn("Custom Purple", self.theme_manager.get_custom_themes())
    
    def test_get_available_themes(self):
        """Test getting all available themes."""
        # By default, only built-in themes are available
        themes = self.theme_manager.get_available_themes()
        self.assertEqual(len(themes), 4)  # Light, Dark, Blue, High Contrast
        
        # Add a custom theme
        custom_theme = Theme(
            name="Test Theme",
            type=ThemeType.CUSTOM,
            ui_colors=self.theme_manager.current_theme.ui_colors,
            vtk_colors=self.theme_manager.current_theme.vtk_colors
        )
        self.theme_manager.add_custom_theme(custom_theme)
        
        # Check again, should have one more
        themes = self.theme_manager.get_available_themes()
        self.assertEqual(len(themes), 5)  # 4 built-in + 1 custom
        
        # Clean up
        self.theme_manager.set_theme(ThemeType.LIGHT)
        self.theme_manager.remove_custom_theme("Test Theme")


if __name__ == "__main__":
    unittest.main() 
"""
Splash screen and dependency checker for Modsee.
"""

import sys
import os
import logging
import importlib
import pkg_resources
import time
from pathlib import Path

from PyQt6 import QtCore, QtWidgets, QtGui, QtSvg

logger = logging.getLogger('modsee.splash')

class DependencyChecker:
    """Checks for required and optional dependencies."""
    
    def __init__(self):
        self.required_deps = {
            'PyQt6': {'min_version': '6.5.0', 'import_name': 'PyQt6'},
            'vtk': {'min_version': '9.2.0', 'import_name': 'vtk'},
            'numpy': {'min_version': '1.22.0', 'import_name': 'numpy'},
            'h5py': {'min_version': '3.7.0', 'import_name': 'h5py'}
        }
        
        self.optional_deps = {
            'openseespy': {'min_version': '3.4.0', 'import_name': 'openseespy'},
            'pytest': {'min_version': '7.3.1', 'import_name': 'pytest'},
            'sphinx': {'min_version': '7.1.0', 'import_name': 'sphinx'}
        }
        
        self.missing_required = []
        self.missing_optional = []
        self.version_issues = []
    
    def check_dependency(self, name, details, is_required=True):
        """Check if a dependency is installed and meets the minimum version."""
        try:
            # Check if module can be imported
            module = importlib.import_module(details['import_name'])
            
            # Try to get version and compare with minimum
            try:
                version = None
                
                # Different packages expose version in different ways
                if hasattr(module, '__version__'):
                    version = module.__version__
                elif hasattr(module, 'VERSION'):
                    version = module.VERSION
                elif name == 'PyQt6':
                    # PyQt6 specific version check
                    version = QtCore.QT_VERSION_STR
                elif hasattr(module, 'VTK_VERSION'):
                    # VTK specific version check
                    version = module.VTK_VERSION
                
                if version:
                    if pkg_resources.parse_version(version) < pkg_resources.parse_version(details['min_version']):
                        self.version_issues.append((name, version, details['min_version']))
                        return False
            except (AttributeError, ValueError):
                # If we can't determine version, assume it's okay if the import worked
                pass
                
            return True
            
        except ImportError:
            if is_required:
                self.missing_required.append(name)
            else:
                self.missing_optional.append(name)
            return False
    
    def check_all_dependencies(self):
        """Check all required and optional dependencies."""
        # Check required dependencies
        for name, details in self.required_deps.items():
            self.check_dependency(name, details, is_required=True)
            
        # Check optional dependencies
        for name, details in self.optional_deps.items():
            self.check_dependency(name, details, is_required=False)
        
        return {
            'missing_required': self.missing_required,
            'missing_optional': self.missing_optional,
            'version_issues': self.version_issues,
            'all_required_met': len(self.missing_required) == 0 and len(self.version_issues) == 0
        }


class ModseeSplashScreen(QtWidgets.QSplashScreen):
    """Modsee splash screen with styled appearance and dependency check."""
    
    def __init__(self, parent=None):
        # Create a pixmap for the splash screen
        splash_width, splash_height = 600, 350
        
        # Create the base pixmap
        pixmap = QtGui.QPixmap(splash_width, splash_height)
        
        # Fill with solid color background
        pixmap.fill(QtGui.QColor(40, 40, 45))
        
        # Create painter for the pixmap
        painter = QtGui.QPainter(pixmap)
        
        # Draw blue top border
        painter.fillRect(0, 0, splash_width, 4, QtGui.QColor(0, 120, 215))
        
        # Load and draw the logo
        logo_path = os.path.join(os.path.dirname(__file__), "resources", "images", "Modsee_light.svg")
        logo_renderer = QtSvg.QSvgRenderer(logo_path)
        
        # Calculate logo position for centering (logo is 681x306)
        logo_width, logo_height = 300, 135  # Scaled down to fit nicely
        logo_x = (splash_width - logo_width) // 2
        logo_y = 40
        
        # Draw the logo
        logo_renderer.render(painter, QtCore.QRectF(logo_x, logo_y, logo_width, logo_height))
        
        # Draw subtitle
        subtitle_font = QtGui.QFont("Segoe UI", 14)
        painter.setFont(subtitle_font)
        painter.setPen(QtGui.QColor(200, 200, 200))
        painter.drawText(42, 210, "Finite Element Modeling GUI")
        
        # Import version info from version checker
        from utils.version_checker import CURRENT_VERSION, UpdateChannel
        
        # Get the current channel from settings
        settings = QtCore.QSettings()
        channel_value = settings.value('updates/channel', UpdateChannel.STABLE.value, str)
        
        # Get user-friendly channel name
        channel_name = "Stable"
        if channel_value == UpdateChannel.BETA.value:
            channel_name = "Beta"
        elif channel_value == UpdateChannel.DEV.value:
            channel_name = "Development"
        
        # Draw version with channel type - make it more prominent
        version_font = QtGui.QFont("Segoe UI", 12)
        version_font.setBold(True)
        painter.setFont(version_font)
        painter.setPen(QtGui.QColor(180, 180, 180))
        
        # Position version info below the subtitle with proper spacing
        version_text = f"Version {CURRENT_VERSION} ({channel_name})"
        painter.drawText(42, 240, version_text)
        
        # Add design element - left side accent
        painter.fillRect(0, 4, 8, splash_height-4, QtGui.QColor(0, 120, 215, 100))
        
        # Create progress area background
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(30, 30, 35))
        painter.drawRect(0, splash_height-60, splash_width, 60)
        
        # Finalize painter
        painter.end()
        
        # Initialize splash screen
        super().__init__(pixmap)
        
        # Center on screen
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # Initialize state
        self.progress = 0
        self.status_message = "Initializing..."
        self.version_check_message = ""
        
        # Dependency checker
        self.dependency_checker = DependencyChecker()
        self.check_results = None
        
        # Version checker
        self.version_check_status = None
        
        # Timer for progress animation
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_progress)
    
    def update_progress(self):
        """Update progress bar animation."""
        self.progress = (self.progress + 1) % 100
        self.repaint()
        
        # If dependencies have been checked, finish up
        if self.check_results and self.progress >= 90:
            self.timer.stop()
            
            if self.check_results['all_required_met']:
                self.status_message = "Starting application..."
            else:
                self.status_message = "Dependency issues detected. See log."
                # Keep splash screen visible longer to show error
                QtCore.QTimer.singleShot(2000, self.close)
            
            self.repaint()
    
    def drawContents(self, painter):
        """Override to draw custom splash screen contents."""
        # Draw message text
        message_font = QtGui.QFont("Segoe UI", 10)
        painter.setFont(message_font)
        painter.setPen(QtGui.QColor(200, 200, 200))
        painter.drawText(20, self.height() - 30, self.status_message)
        
        # Draw version check message if available
        if self.version_check_message:
            version_font = QtGui.QFont("Segoe UI", 9)
            painter.setFont(version_font)
            painter.setPen(QtGui.QColor(150, 150, 200))
            painter.drawText(self.width() - 180, self.height() - 30, self.version_check_message)
        
        # Draw progress bar background
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(60, 60, 65))
        painter.drawRect(20, self.height() - 20, self.width() - 40, 6)
        
        # Draw progress bar
        width = int((self.width() - 40) * (self.progress / 100))
        painter.setBrush(QtGui.QColor(0, 120, 215))
        painter.drawRect(20, self.height() - 20, width, 6)
    
    def start_dependency_check(self):
        """Start the dependency checking process."""
        self.status_message = "Checking dependencies..."
        self.repaint()
        
        # Start progress animation
        self.timer.start(25)
        
        # Run dependency check with short processing times to ensure visibility
        QtCore.QTimer.singleShot(200, self._check_dependencies)
    
    def _check_dependencies(self):
        """Run the actual dependency check."""
        # Perform checks
        try:
            self.check_results = self.dependency_checker.check_all_dependencies()
            
            # Show some intermediate steps to make the splash screen visible
            checks = ["Checking core libraries...", 
                     "Verifying PyQt6...",
                     "Checking VTK installation...",
                     "Checking numpy and h5py...",
                     "Verifying optional packages..."]
            
            for check in checks:
                self.status_message = check
                self.repaint()
                # Process GUI events to ensure splash is visible
                QtWidgets.QApplication.processEvents()
                time.sleep(0.2)
            
            # Log issues
            for name in self.check_results['missing_required']:
                logger.error(f"Required dependency {name} is missing")
                
            for name in self.check_results['missing_optional']:
                logger.warning(f"Optional dependency {name} is not installed")
                
            for name, version, min_version in self.check_results['version_issues']:
                logger.error(f"Dependency {name} version {version} is lower than required {min_version}")
            
            if self.check_results['all_required_met']:
                logger.debug("All required dependencies are satisfied")
                self.status_message = "All dependencies verified"
                
                # Start version check
                QtCore.QTimer.singleShot(100, self._start_version_check)
            else:
                self.status_message = "Dependency issues detected"
            
            self.repaint()
        except Exception as e:
            logger.error(f"Error during dependency check: {str(e)}")
    
    def _start_version_check(self):
        """Start checking for updates."""
        try:
            from utils.version_checker import CURRENT_VERSION
            
            self.status_message = "Checking for updates..."
            self.version_check_message = f"Version {CURRENT_VERSION}"
            self.repaint()
            
            # Process events to keep UI responsive
            QtWidgets.QApplication.processEvents()
            
            # We're not actually checking for updates here - just showing the status
            # The actual check will be done by the VersionChecker in the background
            # after the main window is loaded
            
            # Wait a moment to show the message
            time.sleep(0.3)
            
            self.status_message = "Starting application..."
            self.repaint()
        except Exception as e:
            logger.error(f"Error during version check initialization: {str(e)}")
    
    def show_dependency_errors(self):
        """Show dependency errors in a dialog."""
        if not self.check_results:
            return
        
        if self.check_results['all_required_met']:
            return
        
        # Create message for errors
        message = "The following dependency issues were detected:\n\n"
        
        for name in self.check_results['missing_required']:
            message += f"• Missing required dependency: {name}\n"
            
        for name, version, min_version in self.check_results['version_issues']:
            message += f"• {name} version {version} is too old (minimum: {min_version})\n"
        
        message += "\nPlease install the missing dependencies and try again."
        
        # Show error dialog
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Dependency Error")
        error_dialog.setText("Missing Dependencies")
        error_dialog.setInformativeText(message)
        error_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        error_dialog.exec()


def show_splash_and_check_dependencies():
    """
    Show the splash screen and check dependencies.
    
    Returns:
        True if all required dependencies are met, False otherwise.
    """
    # Create QApplication instance if it doesn't exist
    if QtWidgets.QApplication.instance() is None:
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    
    # Create splash screen
    splash = ModseeSplashScreen()
    splash.show()
    
    # Make sure the splash screen is displayed
    app.processEvents()
    
    # Start dependency check
    splash.start_dependency_check()
    
    # Process events to ensure splash is shown
    QtWidgets.QApplication.processEvents()
    
    # Wait until dependency check is complete
    while splash.check_results is None:
        QtWidgets.QApplication.processEvents()
        time.sleep(0.05)
    
    # If there are dependency issues, show error dialog
    if not splash.check_results['all_required_met']:
        splash.show_dependency_errors()
        splash.close()
        return False
    
    return True 
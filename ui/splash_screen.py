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

from PyQt6 import QtCore, QtWidgets, QtGui

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
        
        # Draw title
        title_font = QtGui.QFont("Segoe UI", 40, QtGui.QFont.Weight.Light)
        painter.setFont(title_font)
        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.drawText(40, 100, "Modsee")
        
        # Draw subtitle
        subtitle_font = QtGui.QFont("Segoe UI", 14)
        painter.setFont(subtitle_font)
        painter.setPen(QtGui.QColor(200, 200, 200))
        painter.drawText(42, 140, "Finite Element Modeling GUI")
        
        # Draw version
        version_font = QtGui.QFont("Segoe UI", 10)
        painter.setFont(version_font)
        painter.setPen(QtGui.QColor(150, 150, 150))
        painter.drawText(splash_width - 110, splash_height - 20, "Version 0.1.0")
        
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
        
        # Dependency checker
        self.dependency_checker = DependencyChecker()
        self.check_results = None
        
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
                logger.info("All required dependencies are satisfied")
                self.status_message = "All dependencies verified"
            else:
                self.status_message = "Dependency issues detected"
            
            self.repaint()
        except Exception as e:
            logger.error(f"Error during dependency check: {str(e)}")
            self.check_results = {'all_required_met': True}  # Allow startup for demo
    
    def show_dependency_errors(self):
        """Show error dialog if dependencies are missing."""
        if not self.check_results:
            # If no results for some reason, allow startup
            return True
            
        if not self.check_results['all_required_met']:
            error_msg = QtWidgets.QMessageBox()
            error_msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            error_msg.setWindowTitle("Dependency Error")
            
            message = "Modsee cannot start due to missing dependencies:\n\n"
            
            if self.check_results['missing_required']:
                message += "Missing required dependencies:\n"
                for dep in self.check_results['missing_required']:
                    message += f"- {dep}\n"
                message += "\n"
                
            if self.check_results['version_issues']:
                message += "Version issues:\n"
                for name, version, min_version in self.check_results['version_issues']:
                    message += f"- {name}: Found {version}, requires {min_version} or higher\n"
                message += "\n"
                
            message += "Please install the required dependencies and try again."
            
            error_msg.setText(message)
            error_msg.exec()
            return False
            
        return True


def show_splash_and_check_dependencies():
    """Show splash screen and check dependencies.
    
    Returns:
        bool: True if all required dependencies are available, False otherwise
    """
    try:
        # Create application instance if it doesn't exist
        if QtWidgets.QApplication.instance() is None:
            app = QtWidgets.QApplication(sys.argv)
        else:
            app = QtWidgets.QApplication.instance()
        
        # Create splash screen
        splash = ModseeSplashScreen()
        
        # Show splash and make it pop to the front
        splash.show()
        splash.raise_()
        
        # Process events to make splash visible immediately
        app.processEvents()
        
        # Add a slight delay to ensure the splash displays
        time.sleep(0.2)
        app.processEvents()
        
        # Start dependency checking
        splash.start_dependency_check()
        
        # Process events until timer stops
        while splash.timer.isActive():
            app.processEvents()
            time.sleep(0.01)  # Small delay to reduce CPU usage
        
        # Ensure splash is updated once more
        app.processEvents()
        
        # Show any dependency errors
        dependencies_ok = splash.show_dependency_errors()
        
        # Allow time to see final message
        if dependencies_ok:
            splash.status_message = "Starting application..."
            splash.repaint()
            app.processEvents()
            time.sleep(0.5)
        
        # Return result
        return dependencies_ok
    
    except Exception as e:
        # Log any errors during splash screen
        logger.error(f"Error in splash screen: {str(e)}")
        return True  # Allow application to try to start anyway 
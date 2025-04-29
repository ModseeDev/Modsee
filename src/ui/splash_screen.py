#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Splash screen with dependency check
"""

import sys
import os
import importlib
import threading
import re
from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QApplication, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QPoint, QRect
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor, QLinearGradient, QPen, QFontDatabase

# Import version check
from ..utils.version_check import VERSION, get_latest_version

# Define which dependencies are required vs optional
REQUIRED_MODULES = [
    "PyQt5",
    "numpy",
    "scipy", 
    "vtk",
    "matplotlib",
    "pyqtgraph"
]

# These won't trigger an error if missing
OPTIONAL_MODULES = [
    "openseespy"
]

def get_dependencies_from_requirements():
    """Read dependencies from requirements.txt file"""
    req_file_paths = [
        # Try relative to this file first
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "requirements.txt"),
        # Also try from the root directory if run as a module
        os.path.join(os.getcwd(), "requirements.txt")
    ]
    
    dependencies = []
    
    for req_path in req_file_paths:
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                for line in f:
                    # Skip empty lines or comments
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Extract package name and remove version info
                    # Example: "numpy>=1.20.0" becomes "numpy"
                    match = re.match(r'^([a-zA-Z0-9_\-]+).*$', line)
                    if match:
                        dependencies.append(match.group(1))
            
            # Return on first found requirements file
            break
    
    return dependencies

# Get all dependencies from requirements.txt
ALL_DEPENDENCIES = get_dependencies_from_requirements()

# Create tuples of (module_name, display_name) for all dependencies
REQUIRED_DEPENDENCIES = [(module, module) for module in REQUIRED_MODULES if module in ALL_DEPENDENCIES]
OPTIONAL_DEPENDENCIES = [(module, module) for module in OPTIONAL_MODULES if module in ALL_DEPENDENCIES]

# Add any dependencies from requirements.txt that aren't explicitly categorized
for dep in ALL_DEPENDENCIES:
    if dep not in REQUIRED_MODULES and dep not in OPTIONAL_MODULES:
        # Default to optional for any dependency not explicitly required
        OPTIONAL_DEPENDENCIES.append((dep, dep))


class VersionCheckSignals(QObject):
    """Signals for version check thread"""
    finished = pyqtSignal(object)


class VersionCheckThread(threading.Thread):
    """Thread for checking version updates"""
    
    def __init__(self):
        super().__init__(daemon=True)
        self.signals = VersionCheckSignals()
        
    def run(self):
        """Run the version check"""
        try:
            # Don't force check - use cached version if available
            result = get_latest_version(force_check=False)
            self.signals.finished.emit(result)
        except Exception as e:
            # Signal with error
            self.signals.finished.emit((VERSION, False, {"error": str(e)}))


class DependencyCheckThread(threading.Thread):
    """Thread for checking dependencies"""
    
    def __init__(self, required_deps, optional_deps):
        super().__init__(daemon=True)
        self.required_deps = required_deps
        self.optional_deps = optional_deps
        self.signals = DependencyCheckSignals()
        
    def run(self):
        """Run the dependency check"""
        missing_required = []
        missing_optional = []
        
        # Check required dependencies
        for module_name, display_name in self.required_deps:
            self.signals.status.emit(f"Checking {display_name}...")
            
            try:
                importlib.import_module(module_name)
                self.signals.progress.emit(1)
                self.signals.status.emit(f"{display_name} found")
            except ImportError:
                missing_required.append(display_name)
                self.signals.progress.emit(1)
                self.signals.status.emit(f"{display_name} NOT found")
        
        # Check optional dependencies
        for module_name, display_name in self.optional_deps:
            self.signals.status.emit(f"Checking {display_name} (optional)...")
            
            try:
                importlib.import_module(module_name)
                self.signals.progress.emit(1)
                self.signals.status.emit(f"{display_name} found")
            except ImportError:
                missing_optional.append(display_name)
                self.signals.progress.emit(1)
                self.signals.status.emit(f"{display_name} not found (optional)")
        
        # Signal completion - only pass the required missing dependencies
        self.signals.finished.emit((missing_required, missing_optional))


class DependencyCheckSignals(QObject):
    """Signals for dependency check thread"""
    status = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal(tuple)  # (missing_required, missing_optional)


class ModseeSplashScreen(QSplashScreen):
    """Custom splash screen with progress bar for dependency checking"""
    
    def __init__(self):
        """Initialize the splash screen"""
        # Create a modern looking splash screen
        # Load Roboto font for a more modern look if available
        QFontDatabase.addApplicationFont(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "resources", "fonts", "Roboto-Regular.ttf"))
        
        # Modern dimensions with 16:9 aspect ratio
        width, height = 640, 360
        
        # Try to find splash image
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                "resources", "icons", "splash_logo.png")
        
        if os.path.exists(logo_path):
            # Use the actual logo
            pixmap = QPixmap(logo_path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            # Create a placeholder with a modern gradient background
            pixmap = QPixmap(width, height)
            self._create_modern_logo(pixmap)
        
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        
        # Create progress bar with modern styling
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(width//2 - 150, height - 60, 300, 8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, len(REQUIRED_DEPENDENCIES) + len(OPTIONAL_DEPENDENCIES) + 2)  # +2 for file system and version check
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: rgba(255, 255, 255, 100);
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #4d94ff;
                border-radius: 4px;
            }
        """)
        
        # Status label with smaller font for a cleaner look
        self.status_label = QLabel(self)
        self.status_label.setGeometry(width//2 - 150, height - 40, 300, 20)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: rgba(255, 255, 255, 220);
            background: transparent;
            font-size: 9pt;
        """)
        
        # Set flags for tracking
        self.dependency_check_done = False
        self.all_dependencies_ok = True
        self.missing_required_deps = []
        self.missing_optional_deps = []
        
        # Version check result
        self.version_info = None
        self.update_available = False
        
        # Set window to be in center of screen and make it always on top
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    
    def _create_modern_logo(self, pixmap):
        """Create a modern-looking logo with gradient background"""
        # Create a dark gradient background for a more professional look
        gradient = QLinearGradient(0, 0, 0, pixmap.height())
        gradient.setColorAt(0.0, QColor(25, 35, 45))   # Dark blue-gray at top
        gradient.setColorAt(1.0, QColor(40, 50, 65))   # Slightly lighter at bottom
        
        # Paint the background
        painter = QPainter(pixmap)
        painter.fillRect(0, 0, pixmap.width(), pixmap.height(), gradient)
        
        # Use a more modern font set
        title_font = QFont("Roboto", 32, QFont.Bold)
        subtitle_font = QFont("Roboto", 12)
        version_font = QFont("Roboto", 8)
        
        # Draw a stylized "M" logo in the center
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw a modern geometric logo
        logo_size = pixmap.height() // 3
        logo_rect = QRect(
            pixmap.width()//2 - logo_size//2,
            pixmap.height()//3 - logo_size//2, 
            logo_size, 
            logo_size
        )
        
        # Draw a hexagon with gradient
        hex_gradient = QLinearGradient(
            logo_rect.left(), logo_rect.top(),
            logo_rect.right(), logo_rect.bottom()
        )
        hex_gradient.setColorAt(0.0, QColor(65, 105, 225))  # Royal blue
        hex_gradient.setColorAt(1.0, QColor(30, 144, 255))  # Dodger blue
        
        painter.setBrush(hex_gradient)
        painter.setPen(Qt.NoPen)
        
        # Calculate hexagon points
        center_x = logo_rect.center().x()
        center_y = logo_rect.center().y()
        radius = logo_size // 2
        
        points = []
        for i in range(6):
            angle = i * 60
            x = center_x + radius * 0.9 * (0.5 if i % 2 else 1.0) * 0.95 * \
                (1.0 if angle == 0 or angle == 180 else 0.866) * \
                (-1.0 if angle > 180 else 1.0)
                
            y = center_y + radius * 0.9 * (0.5 if i % 2 else 1.0) * \
                (0.0 if angle == 0 or angle == 180 else 0.5) * \
                (-1.0 if angle < 90 or angle > 270 else 1.0)
                
            points.append(QPoint(int(x), int(y)))
        
        painter.drawPolygon(points)
        
        # Draw an "M" in the center of the hexagon
        painter.setPen(QPen(QColor(255, 255, 255, 220), 4))
        m_points = [
            QPoint(center_x - radius//2, center_y + radius//3),
            QPoint(center_x - radius//4, center_y - radius//3),
            QPoint(center_x, center_y + radius//4),
            QPoint(center_x + radius//4, center_y - radius//3),
            QPoint(center_x + radius//2, center_y + radius//3)
        ]
        
        # Connect the points to form the "M"
        for i in range(len(m_points) - 1):
            painter.drawLine(m_points[i], m_points[i+1])
        
        # Draw text elements
        painter.setPen(QColor(255, 255, 255, 220))
        painter.setFont(title_font)
        painter.drawText(
            QRect(0, logo_rect.bottom() + 20, pixmap.width(), 50), 
            Qt.AlignCenter, 
            "Modsee"
        )
        
        painter.setPen(QColor(200, 200, 200, 180))
        painter.setFont(subtitle_font)
        painter.drawText(
            QRect(0, logo_rect.bottom() + 70, pixmap.width(), 30), 
            Qt.AlignCenter, 
            "OpenSees Finite Element Modeling Interface"
        )
        
        # Version in bottom right
        painter.setPen(QColor(180, 180, 180, 160))
        painter.setFont(version_font)
        painter.drawText(
            pixmap.rect().adjusted(0, 0, -15, -10), 
            Qt.AlignRight | Qt.AlignBottom, 
            f"Version {VERSION}"
        )
        
        painter.end()
    
    def _on_version_check_complete(self, result):
        """Handle version check completion"""
        latest_version, is_update_available, version_info = result
        self.version_info = version_info
        self.update_available = is_update_available
        
        if is_update_available:
            self.status_label.setText(f"Update available: v{latest_version}")
        
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        QApplication.processEvents()
    
    def _on_dependency_status(self, status):
        """Handle dependency check status updates"""
        self.status_label.setText(status)
        QApplication.processEvents()
    
    def _on_dependency_progress(self, steps):
        """Handle dependency check progress updates"""
        self.progress_bar.setValue(self.progress_bar.value() + steps)
        QApplication.processEvents()
    
    def _on_dependency_check_complete(self, result):
        """Handle dependency check completion"""
        missing_required, missing_optional = result
        self.missing_required_deps = missing_required
        self.missing_optional_deps = missing_optional
        self.all_dependencies_ok = len(missing_required) == 0
        
        # Final status
        if self.all_dependencies_ok:
            self.status_label.setText("All required dependencies found. Starting application...")
        else:
            missing = ", ".join(self.missing_required_deps)
            self.status_label.setText(f"Missing dependencies: {missing}")
        
        self.dependency_check_done = True
        
        # Ensure progress bar is complete
        self.progress_bar.setValue(self.progress_bar.maximum())
        QApplication.processEvents()
    
    def check_dependencies(self):
        """Check all required and optional dependencies"""
        # Initialize progress
        self.progress_bar.setValue(0)
        
        # Start version check in background thread
        self.status_label.setText("Checking for updates...")
        version_check_thread = VersionCheckThread()
        version_check_thread.signals.finished.connect(self._on_version_check_complete)
        version_check_thread.start()
        
        # Check file system access
        self.status_label.setText("Checking file system access...")
        QApplication.processEvents()
        
        try:
            temp_dir = os.path.join(os.path.expanduser("~"), ".modsee")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)
            
            # Test write access
            test_file = os.path.join(temp_dir, "test_write.tmp")
            with open(test_file, "w") as f:
                f.write("Test")
            if os.path.exists(test_file):
                os.remove(test_file)
        except Exception as e:
            self.all_dependencies_ok = False
            self.missing_required_deps.append("File system access")
        
        # Update progress for file system check
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        QApplication.processEvents()
        
        # Start dependency check in background thread
        dependency_thread = DependencyCheckThread(REQUIRED_DEPENDENCIES, OPTIONAL_DEPENDENCIES)
        dependency_thread.signals.status.connect(self._on_dependency_status)
        dependency_thread.signals.progress.connect(self._on_dependency_progress)
        dependency_thread.signals.finished.connect(self._on_dependency_check_complete)
        dependency_thread.start()
        
        # Wait for dependency check to complete
        while not self.dependency_check_done:
            QApplication.processEvents()
        
        # Return the status
        return self.all_dependencies_ok
        
    def show_missing_dependencies_message(self):
        """Display detailed information about missing dependencies"""
        # Lower the splash screen temporarily to ensure dialog is visible
        self.hide()
        
        # Create message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Missing Dependencies")
        
        missing = "\n- ".join(self.missing_required_deps)
        message = (
            f"The following required dependencies are missing:\n- {missing}\n\n"
            "Please install these dependencies using pip:\n"
            "pip install -r requirements.txt"
        )
        
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Add info about optional missing dependencies if any
        if self.missing_optional_deps:
            missing_opt = "\n- ".join(self.missing_optional_deps)
            msg_box.setInformativeText(
                f"The following optional dependencies are also missing:\n- {missing_opt}\n\n"
                "You can still use most features without these, but some functionality may be limited."
            )
        
        # Make sure the dialog has focus and is in front
        msg_box.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # Show the dialog
        msg_box.exec_()
        
        # Show splash again
        self.show()


def run_splash_screen():
    """Run the splash screen and return True if all dependencies are met"""
    splash = ModseeSplashScreen()
    splash.show()
    QApplication.processEvents()
    
    # Check dependencies (runs in background threads)
    dependencies_ok = splash.check_dependencies()
    
    # Show error message if dependencies are missing
    if not dependencies_ok:
        splash.show_missing_dependencies_message()
    
    # Keep the splash visible for a short time before closing
    QTimer.singleShot(500, splash.close)
    
    # Return the version check results along with dependencies status
    return dependencies_ok, splash.update_available, splash.version_info 
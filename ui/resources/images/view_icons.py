"""
Icons for view directions in the Modsee application.
This module generates simple programmatic icons for different view directions.
"""

from typing import Tuple

from PyQt6.QtCore import Qt, QSize, QRect, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QBrush, QPolygon, QLinearGradient

def create_xy_view_icon(size: int = 32) -> QIcon:
    """
    Create an icon for the XY (Plan) view.
    
    Args:
        size: The size of the icon in pixels.
    
    Returns:
        QIcon representing the XY view.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    
    # Draw a top-down rectangle with X and Y axes
    rect = QRect(2, 2, size - 4, size - 4)
    painter.setPen(QPen(QColor(60, 60, 60), 2))
    painter.setBrush(QBrush(QColor(230, 230, 230, 150)))
    painter.drawRect(rect)
    
    # Draw X axis (horizontal)
    painter.setPen(QPen(QColor(200, 0, 0), 2))
    painter.drawLine(2, size // 2, size - 2, size // 2)
    
    # Draw Y axis (vertical)
    painter.setPen(QPen(QColor(0, 150, 0), 2))
    painter.drawLine(size // 2, 2, size // 2, size - 2)
    
    # X label
    painter.setPen(QColor(200, 0, 0))
    painter.drawText(size - 12, size // 2 - 4, "X")
    
    # Y label
    painter.setPen(QColor(0, 150, 0))
    painter.drawText(size // 2 + 4, 10, "Y")
    
    painter.end()
    
    return QIcon(pixmap)

def create_xz_view_icon(size: int = 32) -> QIcon:
    """
    Create an icon for the XZ (Front) view.
    
    Args:
        size: The size of the icon in pixels.
    
    Returns:
        QIcon representing the XZ view.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    
    # Draw a front view rectangle with X and Z axes
    rect = QRect(2, 2, size - 4, size - 4)
    painter.setPen(QPen(QColor(60, 60, 60), 2))
    painter.setBrush(QBrush(QColor(230, 230, 230, 150)))
    painter.drawRect(rect)
    
    # Draw X axis (horizontal)
    painter.setPen(QPen(QColor(200, 0, 0), 2))
    painter.drawLine(2, size // 2, size - 2, size // 2)
    
    # Draw Z axis (vertical)
    painter.setPen(QPen(QColor(0, 0, 200), 2))
    painter.drawLine(size // 2, 2, size // 2, size - 2)
    
    # X label
    painter.setPen(QColor(200, 0, 0))
    painter.drawText(size - 12, size // 2 - 4, "X")
    
    # Z label
    painter.setPen(QColor(0, 0, 200))
    painter.drawText(size // 2 + 4, 10, "Z")
    
    painter.end()
    
    return QIcon(pixmap)

def create_yz_view_icon(size: int = 32) -> QIcon:
    """
    Create an icon for the YZ (Side) view.
    
    Args:
        size: The size of the icon in pixels.
    
    Returns:
        QIcon representing the YZ view.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    
    # Draw a side view rectangle with Y and Z axes
    rect = QRect(2, 2, size - 4, size - 4)
    painter.setPen(QPen(QColor(60, 60, 60), 2))
    painter.setBrush(QBrush(QColor(230, 230, 230, 150)))
    painter.drawRect(rect)
    
    # Draw Y axis (horizontal)
    painter.setPen(QPen(QColor(0, 150, 0), 2))
    painter.drawLine(2, size // 2, size - 2, size // 2)
    
    # Draw Z axis (vertical)
    painter.setPen(QPen(QColor(0, 0, 200), 2))
    painter.drawLine(size // 2, 2, size // 2, size - 2)
    
    # Y label
    painter.setPen(QColor(0, 150, 0))
    painter.drawText(size - 12, size // 2 - 4, "Y")
    
    # Z label
    painter.setPen(QColor(0, 0, 200))
    painter.drawText(size // 2 + 4, 10, "Z")
    
    painter.end()
    
    return QIcon(pixmap)

def create_iso_view_icon(size: int = 32) -> QIcon:
    """
    Create an icon for the Isometric view.
    
    Args:
        size: The size of the icon in pixels.
    
    Returns:
        QIcon representing the Isometric view.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    
    # Draw a 3D cube to represent isometric view
    # Face points
    center_x = size // 2
    center_y = size // 2
    cube_size = size - 12
    
    # Top face
    top_face = QPolygon([
        QPoint(center_x, center_y - cube_size//3),
        QPoint(center_x + cube_size//3, center_y - cube_size//6),
        QPoint(center_x, center_y),
        QPoint(center_x - cube_size//3, center_y - cube_size//6)
    ])
    
    # Front face
    front_face = QPolygon([
        QPoint(center_x - cube_size//3, center_y - cube_size//6),
        QPoint(center_x, center_y),
        QPoint(center_x, center_y + cube_size//3),
        QPoint(center_x - cube_size//3, center_y + cube_size//6)
    ])
    
    # Right face
    right_face = QPolygon([
        QPoint(center_x, center_y),
        QPoint(center_x + cube_size//3, center_y - cube_size//6),
        QPoint(center_x + cube_size//3, center_y + cube_size//6),
        QPoint(center_x, center_y + cube_size//3)
    ])
    
    # Draw the faces with different shades
    painter.setPen(QPen(QColor(60, 60, 60), 1))
    
    # Top face (lighter)
    gradient1 = QLinearGradient(center_x - cube_size//3, center_y - cube_size//6, 
                               center_x + cube_size//3, center_y - cube_size//6)
    gradient1.setColorAt(0, QColor(180, 180, 180, 220))
    gradient1.setColorAt(1, QColor(220, 220, 220, 220))
    painter.setBrush(QBrush(gradient1))
    painter.drawPolygon(top_face)
    
    # Right face (medium)
    gradient2 = QLinearGradient(center_x, center_y, 
                               center_x + cube_size//3, center_y - cube_size//6)
    gradient2.setColorAt(0, QColor(120, 120, 120, 220))
    gradient2.setColorAt(1, QColor(160, 160, 160, 220))
    painter.setBrush(QBrush(gradient2))
    painter.drawPolygon(right_face)
    
    # Front face (darkest)
    gradient3 = QLinearGradient(center_x - cube_size//3, center_y - cube_size//6,
                               center_x, center_y)
    gradient3.setColorAt(0, QColor(80, 80, 80, 220))
    gradient3.setColorAt(1, QColor(140, 140, 140, 220))
    painter.setBrush(QBrush(gradient3))
    painter.drawPolygon(front_face)
    
    # Draw coordinate axes
    # X-axis (red)
    painter.setPen(QPen(QColor(200, 0, 0), 2))
    painter.drawLine(center_x, center_y, center_x + cube_size//2, center_y - cube_size//4)
    painter.drawText(center_x + cube_size//2 + 1, center_y - cube_size//4, "X")
    
    # Y-axis (green)
    painter.setPen(QPen(QColor(0, 150, 0), 2))
    painter.drawLine(center_x, center_y, center_x - cube_size//2, center_y - cube_size//4)
    painter.drawText(center_x - cube_size//2 - 8, center_y - cube_size//4, "Y")
    
    # Z-axis (blue)
    painter.setPen(QPen(QColor(0, 0, 200), 2))
    painter.drawLine(center_x, center_y, center_x, center_y + cube_size//2)
    painter.drawText(center_x + 2, center_y + cube_size//2 + 8, "Z")
    
    painter.end()
    
    return QIcon(pixmap)

# Function to get an icon by view direction
def get_view_icon(direction: str, size: int = 32) -> QIcon:
    """
    Get an icon for the specified view direction.
    
    Args:
        direction: The view direction ('xy', 'xz', 'yz', 'iso').
        size: The size of the icon in pixels.
    
    Returns:
        QIcon for the view direction.
    """
    if direction.lower() == 'xy':
        return create_xy_view_icon(size)
    elif direction.lower() == 'xz':
        return create_xz_view_icon(size)
    elif direction.lower() == 'yz':
        return create_yz_view_icon(size)
    elif direction.lower() == 'iso':
        return create_iso_view_icon(size)
    else:
        # Return a default icon
        return create_iso_view_icon(size) 
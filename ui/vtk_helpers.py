"""
VTK Helper functions for Modsee.
"""

import logging
from typing import Tuple, List, Dict, Any, Optional

import vtk
import numpy as np

logger = logging.getLogger('modsee.ui.vtk_helpers')


def create_node_actor(x: float, y: float, z: float, radius: float = 0.05, 
                      color: Tuple[float, float, float] = (1.0, 0.0, 0.0)) -> vtk.vtkActor:
    """
    Create a VTK actor representing a node.
    
    Args:
        x: X coordinate.
        y: Y coordinate.
        z: Z coordinate.
        radius: Sphere radius.
        color: RGB color tuple (values 0.0-1.0).
        
    Returns:
        VTK actor representing the node.
    """
    # Create a sphere
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(x, y, z)
    sphere.SetRadius(radius)
    sphere.SetPhiResolution(12)
    sphere.SetThetaResolution(12)
    
    # Create a mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphere.GetOutputPort())
    
    # Create an actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    
    return actor


def create_line_actor(points: List[Tuple[float, float, float]], 
                      color: Tuple[float, float, float] = (0.0, 0.0, 1.0),
                      line_width: float = 2.0) -> vtk.vtkActor:
    """
    Create a VTK actor representing a line.
    
    Args:
        points: List of (x, y, z) coordinate tuples.
        color: RGB color tuple (values 0.0-1.0).
        line_width: Width of the line.
        
    Returns:
        VTK actor representing the line.
    """
    # Create points
    vtk_points = vtk.vtkPoints()
    for i, (x, y, z) in enumerate(points):
        vtk_points.InsertPoint(i, x, y, z)
    
    # Create a line
    line = vtk.vtkLineSource()
    if len(points) == 2:
        # Simple line between two points
        line.SetPoint1(points[0])
        line.SetPoint2(points[1])
    else:
        # Line strip through multiple points
        cells = vtk.vtkCellArray()
        polyline = vtk.vtkPolyLine()
        polyline.GetPointIds().SetNumberOfIds(len(points))
        
        for i in range(len(points)):
            polyline.GetPointIds().SetId(i, i)
        
        cells.InsertNextCell(polyline)
        
        # Create polydata
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_points)
        polydata.SetLines(cells)
        
        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        
        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(line_width)
        
        return actor
    
    # Map the line to graphics primitives
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(line.GetOutputPort())
    
    # Create an actor for the line
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetLineWidth(line_width)
    
    return actor


def create_axis_actor(origin: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                      length: float = 5.0,
                      x_color: Tuple[float, float, float] = (1.0, 0.0, 0.0),
                      y_color: Tuple[float, float, float] = (0.0, 1.0, 0.0),
                      z_color: Tuple[float, float, float] = (0.0, 0.0, 1.0),
                      line_width: float = 2.0,
                      show_labels: bool = True) -> vtk.vtkAssembly:
    """
    Create a VTK actor representing coordinate axes at the specified origin.
    
    Args:
        origin: (x, y, z) origin point for the axes.
        length: Length of each axis.
        x_color: RGB color tuple for X axis (values 0.0-1.0).
        y_color: RGB color tuple for Y axis (values 0.0-1.0).
        z_color: RGB color tuple for Z axis (values 0.0-1.0).
        line_width: Width of the axis lines.
        show_labels: Whether to show axis labels.
        
    Returns:
        VTK assembly containing the axis actors.
    """
    # Create an assembly to hold all the axis actors
    assembly = vtk.vtkAssembly()
    
    # Create X axis
    x_axis_points = [origin, (origin[0] + length, origin[1], origin[2])]
    x_axis_actor = create_line_actor(x_axis_points, color=x_color, line_width=line_width)
    assembly.AddPart(x_axis_actor)
    
    # Create Y axis
    y_axis_points = [origin, (origin[0], origin[1] + length, origin[2])]
    y_axis_actor = create_line_actor(y_axis_points, color=y_color, line_width=line_width)
    assembly.AddPart(y_axis_actor)
    
    # Create Z axis
    z_axis_points = [origin, (origin[0], origin[1], origin[2] + length)]
    z_axis_actor = create_line_actor(z_axis_points, color=z_color, line_width=line_width)
    assembly.AddPart(z_axis_actor)
    
    # Add labels if requested
    if show_labels:
        # Create X label
        x_label = vtk.vtkVectorText()
        x_label.SetText("X")
        x_mapper = vtk.vtkPolyDataMapper()
        x_mapper.SetInputConnection(x_label.GetOutputPort())
        x_label_actor = vtk.vtkActor()
        x_label_actor.SetMapper(x_mapper)
        x_label_actor.GetProperty().SetColor(x_color)
        x_label_actor.SetPosition(origin[0] + length + 0.2, origin[1], origin[2])
        x_label_actor.SetScale(0.3, 0.3, 0.3)
        assembly.AddPart(x_label_actor)
        
        # Create Y label
        y_label = vtk.vtkVectorText()
        y_label.SetText("Y")
        y_mapper = vtk.vtkPolyDataMapper()
        y_mapper.SetInputConnection(y_label.GetOutputPort())
        y_label_actor = vtk.vtkActor()
        y_label_actor.SetMapper(y_mapper)
        y_label_actor.GetProperty().SetColor(y_color)
        y_label_actor.SetPosition(origin[0], origin[1] + length + 0.2, origin[2])
        y_label_actor.SetScale(0.3, 0.3, 0.3)
        assembly.AddPart(y_label_actor)
        
        # Create Z label
        z_label = vtk.vtkVectorText()
        z_label.SetText("Z")
        z_mapper = vtk.vtkPolyDataMapper()
        z_mapper.SetInputConnection(z_label.GetOutputPort())
        z_label_actor = vtk.vtkActor()
        z_label_actor.SetMapper(z_mapper)
        z_label_actor.GetProperty().SetColor(z_color)
        z_label_actor.SetPosition(origin[0], origin[1], origin[2] + length + 0.2)
        z_label_actor.SetScale(0.3, 0.3, 0.3)
        assembly.AddPart(z_label_actor)
    
    return assembly


def create_grid_actor(size: float = 10.0, divisions: int = 10, 
                      color: Tuple[float, float, float] = (0.7, 0.7, 0.7),
                      plane: str = 'xy') -> vtk.vtkActor:
    """
    Create a VTK actor representing a grid.
    
    Args:
        size: Size of the grid.
        divisions: Number of divisions.
        color: RGB color tuple (values 0.0-1.0).
        plane: Plane for the grid ('xy', 'xz', or 'yz').
        
    Returns:
        VTK actor representing the grid.
    """
    # Create a grid
    grid = vtk.vtkRectilinearGrid()
    
    # Set grid dimensions (one more than divisions)
    grid.SetDimensions(divisions + 1, divisions + 1, 1)
    
    # Create coordinates
    x_coords = vtk.vtkDoubleArray()
    y_coords = vtk.vtkDoubleArray()
    z_coords = vtk.vtkDoubleArray()
    
    # Calculate spacing
    spacing = size / divisions
    
    # Create coordinate arrays based on the selected plane
    for i in range(divisions + 1):
        coord = -size / 2 + i * spacing
        if plane == 'xy':
            x_coords.InsertNextValue(coord)
            y_coords.InsertNextValue(coord)
            z_coords.InsertNextValue(0)
        elif plane == 'xz':
            x_coords.InsertNextValue(coord)
            y_coords.InsertNextValue(0)
            z_coords.InsertNextValue(coord)
        elif plane == 'yz':
            x_coords.InsertNextValue(0)
            y_coords.InsertNextValue(coord)
            z_coords.InsertNextValue(coord)
    
    # Set the grid coordinates
    grid.SetXCoordinates(x_coords)
    grid.SetYCoordinates(y_coords)
    grid.SetZCoordinates(z_coords)
    
    # Extract the grid edges
    edges = vtk.vtkExtractEdges()
    edges.SetInputData(grid)
    
    # Create a tube filter to make the grid lines
    tubes = vtk.vtkTubeFilter()
    tubes.SetInputConnection(edges.GetOutputPort())
    tubes.SetRadius(size / 600)
    tubes.SetNumberOfSides(6)
    tubes.UseDefaultNormalOn()
    
    # Create a mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tubes.GetOutputPort())
    
    # Create an actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    
    return actor


def create_sample_model() -> Dict[str, vtk.vtkActor]:
    """
    Create a sample structural model with nodes and elements.
    
    Returns:
        Dictionary of VTK actors.
    """
    actors = {}
    
    # Create a grid
    actors['grid_xy'] = create_grid_actor(size=10.0, divisions=10, color=(0.5, 0.5, 0.5), plane='xy')
    
    # Create some nodes
    node_coords = [
        (0, 0, 0),
        (5, 0, 0),
        (5, 5, 0),
        (0, 5, 0),
        (0, 0, 5),
        (5, 0, 5),
        (5, 5, 5),
        (0, 5, 5)
    ]
    
    for i, (x, y, z) in enumerate(node_coords):
        actors[f'node_{i+1}'] = create_node_actor(x, y, z, radius=0.2, color=(1.0, 0.0, 0.0))
    
    # Create column elements (vertical)
    for i in range(4):
        start = node_coords[i]
        end = node_coords[i+4]
        actors[f'column_{i+1}'] = create_line_actor([start, end], color=(0.0, 0.0, 1.0), line_width=3.0)
    
    # Create beam elements at base and top
    for i in range(4):
        start = node_coords[i]
        end = node_coords[(i+1) % 4]
        actors[f'base_beam_{i+1}'] = create_line_actor([start, end], color=(0.0, 0.7, 0.0), line_width=3.0)
        
        start = node_coords[i+4]
        end = node_coords[((i+1) % 4) + 4]
        actors[f'top_beam_{i+1}'] = create_line_actor([start, end], color=(0.0, 0.7, 0.0), line_width=3.0)
    
    # Create diagonal braces
    actors['brace_1'] = create_line_actor([node_coords[0], node_coords[2]], color=(0.7, 0.0, 0.7), line_width=2.0)
    actors['brace_2'] = create_line_actor([node_coords[1], node_coords[3]], color=(0.7, 0.0, 0.7), line_width=2.0)
    actors['brace_3'] = create_line_actor([node_coords[4], node_coords[6]], color=(0.7, 0.0, 0.7), line_width=2.0)
    actors['brace_4'] = create_line_actor([node_coords[5], node_coords[7]], color=(0.7, 0.0, 0.7), line_width=2.0)
    
    return actors 
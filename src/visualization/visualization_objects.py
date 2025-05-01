#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Visualization objects for 3D scene
"""

import vtk
import math


def create_node(coords, radius, color):
    """Create a node (sphere) visualization
    
    Args:
        coords (tuple): (x, y, z) coordinates
        radius (float): Radius of the sphere
        color (tuple): RGB color values (0-1 range)
        
    Returns:
        vtk.vtkActor: Actor representing the node
    """
    # Create a sphere source for the node
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(coords)
    sphere.SetRadius(radius)
    sphere.SetPhiResolution(16)
    sphere.SetThetaResolution(16)
    
    # Create a mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphere.GetOutputPort())
    
    # Create an actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    
    return actor


def create_element(node1_coords, node2_coords, radius, color):
    """Create an element (tube) visualization
    
    Args:
        node1_coords (tuple): (x, y, z) coordinates of first node
        node2_coords (tuple): (x, y, z) coordinates of second node
        radius (float): Radius of the tube
        color (tuple): RGB color values (0-1 range)
        
    Returns:
        vtk.vtkActor: Actor representing the element
    """
    # Create line source
    line = vtk.vtkLineSource()
    line.SetPoint1(node1_coords)
    line.SetPoint2(node2_coords)
    
    # Create tube filter for 3D visualization
    tube = vtk.vtkTubeFilter()
    tube.SetInputConnection(line.GetOutputPort())
    tube.SetRadius(radius)
    tube.SetNumberOfSides(10)
    
    # Create a mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tube.GetOutputPort())
    
    # Create an actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    
    return actor


def create_text_label(position, text, color, font_size, camera=None):
    """Add a text label at the specified position
    
    Args:
        position (tuple): (x, y, z) coordinates
        text (str): Text to display
        color (tuple): RGB color values (0-1 range)
        font_size (int): Font size
        camera (vtkCamera, optional): Camera for the follower
        
    Returns:
        vtk.vtkFollower: Follower actor representing the label
    """
    # Create a vtkVectorText for 3D text
    text_source = vtk.vtkVectorText()
    text_source.SetText(text)
    
    # Create mapper for the text
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(text_source.GetOutputPort())
    
    # Create a follower actor (always faces the camera)
    follower = vtk.vtkFollower()
    follower.SetMapper(mapper)
    follower.SetPosition(position[0], position[1], position[2])
    
    # Apply offset - move labels above the nodes/elements
    offset_factor = max(0.5, 0.2 * 2)  # Offset proportional to typical node size
    follower.AddPosition(0, offset_factor, 0)  # Only offset in Y direction
    
    # Set appearance properties
    follower.GetProperty().SetColor(color)
    follower.GetProperty().SetAmbient(1.0)
    follower.GetProperty().SetDiffuse(0.0)  # No lighting effect on text
    
    # Scale the text to an appropriate size
    scale_factor = 0.015 * font_size
    follower.SetScale(scale_factor, scale_factor, scale_factor)
    
    # Set the camera for the follower if provided
    if camera:
        follower.SetCamera(camera)
    
    return follower


def create_load_arrow(coords, force_values, scale_factor, color, node_size):
    """Create a load arrow visualization
    
    Args:
        coords (tuple): (x, y, z) coordinates of the node
        force_values (list): [fx, fy, fz] force components
        scale_factor (float): Scale factor for the arrow size
        color (tuple): RGB color values (0-1 range)
        node_size (float): Size of the node to adjust arrow scale
        
    Returns:
        vtk.vtkActor: Actor representing the load arrow
    """
    # Ensure values has at least 3 elements (for forces)
    if len(force_values) < 3:
        # Convert DOF indices to proper force vector
        # DOF mapping: 1=x, 2=y, 3=z, 4=rx, 5=ry, 6=rz
        full_force = [0.0, 0.0, 0.0]
        
        # Handle moment (rotational) loads differently
        if len(force_values) == 1 and len(force_values[0]) >= 2:
            dof = force_values[0][0]  # Get DOF index
            value = force_values[0][1]  # Get value
            
            # Map DOF index to proper direction
            if dof <= 3:  # Translational DOFs
                full_force[dof-1] = value
            else:  # Rotational DOFs - create a smaller vertical arrow for visualization
                full_force[1] = value * 0.5  # Use half scale for rotational loads
        else:
            # Handle regular force values
            for i, val in enumerate(force_values):
                if i < 3:  # Only use first 3 components
                    full_force[i] = val
                    
        force_values = full_force
        
    # Determine the length and direction of the arrow based on the load values
    force = force_values[:3]  # First 3 values are forces
    length = sum(v*v for v in force) ** 0.5  # Magnitude of force
    
    if length < 0.0001:
        # If no force, create a tiny invisible sphere
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(coords)
        sphere.SetRadius(0.001)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(0.0)
        return actor
        
    # Create a line source for the arrow shaft
    line = vtk.vtkLineSource()
    
    # Calculate direction from the force vector
    direction = [f/length for f in force]
    
    # Calculate the arrow length based on scale settings
    base_size = node_size * 2
    max_size = node_size * 10
    arrow_length = min(max_size, base_size + (scale_factor * abs(length)))
    
    # Ensure exact node coordinates are used for start point
    start_point = [float(coords[0]), float(coords[1]), float(coords[2])]
    
    # Calculate end point precisely
    end_point = [
        start_point[0] + direction[0] * arrow_length,
        start_point[1] + direction[1] * arrow_length,
        start_point[2] + direction[2] * arrow_length
    ]
    
    # Set exact line endpoints
    line.SetPoint1(start_point)
    line.SetPoint2(end_point)
    
    # Create arrow head (triangle)
    head_size = arrow_length * 0.25  # Head size proportional to arrow length
    
    # Calculate perpendicular vectors for arrow head using cross product with up vector
    perp1 = [
        -direction[1],
        direction[0],
        0
    ]
    
    # If perp1 is too small, try cross product with right vector
    perp1_length = sum(v*v for v in perp1) ** 0.5
    if perp1_length < 0.0001:
        perp1 = [
            0,
            -direction[2],
            direction[1]
        ]
        perp1_length = sum(v*v for v in perp1) ** 0.5
    
    # Normalize perp1
    if perp1_length > 0:
        perp1 = [v/perp1_length * head_size for v in perp1]
    
    # Create points for arrow head triangle
    points = vtk.vtkPoints()
    points.InsertNextPoint(end_point)  # Tip
    
    # Calculate base points of the arrow head
    base_point = [
        end_point[0] - direction[0] * head_size,
        end_point[1] - direction[1] * head_size,
        end_point[2] - direction[2] * head_size
    ]
    
    left_point = [
        base_point[0] + perp1[0],
        base_point[1] + perp1[1],
        base_point[2] + perp1[2]
    ]
    
    right_point = [
        base_point[0] - perp1[0],
        base_point[1] - perp1[1],
        base_point[2] - perp1[2]
    ]
    
    points.InsertNextPoint(left_point)
    points.InsertNextPoint(right_point)
    
    # Create triangle for arrow head
    triangle = vtk.vtkTriangle()
    triangle.GetPointIds().SetId(0, 0)
    triangle.GetPointIds().SetId(1, 1)
    triangle.GetPointIds().SetId(2, 2)
    
    # Create cell array and add triangle
    triangles = vtk.vtkCellArray()
    triangles.InsertNextCell(triangle)
    
    # Create polydata for arrow head
    head = vtk.vtkPolyData()
    head.SetPoints(points)
    head.SetPolys(triangles)
    
    # Combine shaft and head
    append = vtk.vtkAppendPolyData()
    
    # Convert line to polydata
    line_poly = vtk.vtkPolyData()
    line.Update()
    line_poly.ShallowCopy(line.GetOutput())
    
    append.AddInputData(line_poly)
    append.AddInputData(head)
    append.Update()
    
    # Create mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(append.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    
    # Make sure the arrow is always visible
    actor.GetProperty().SetAmbient(1.0)
    actor.GetProperty().SetDiffuse(0.0)
    
    return actor


def create_grid(grid_size, divisions, origin_position):
    """Create a reference grid
    
    Args:
        grid_size (float): Size of the grid
        divisions (int): Number of divisions
        origin_position (tuple): (x, y, z) position of the grid origin
        
    Returns:
        vtk.vtkActor: Actor representing the grid
    """
    # Origin is offset by the grid position
    origin_x = -grid_size/2 + origin_position[0]
    origin_y = -grid_size/2 + origin_position[1]
    origin_z = origin_position[2]  # Z position directly from settings
    
    # Create a grid source
    grid = vtk.vtkPlaneSource()
    grid.SetXResolution(divisions)
    grid.SetYResolution(divisions)
    grid.SetOrigin(origin_x, origin_y, origin_z)
    grid.SetPoint1(origin_x + grid_size, origin_y, origin_z)
    grid.SetPoint2(origin_x, origin_y + grid_size, origin_z)
    
    # Create a mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(grid.GetOutputPort())
    
    # Create the grid actor
    grid_actor = vtk.vtkActor()
    grid_actor.SetMapper(mapper)
    
    # Use a wireframe representation
    grid_actor.GetProperty().SetRepresentationToWireframe()
    grid_actor.GetProperty().SetColor(0.7, 0.7, 0.7)  # Light gray
    grid_actor.GetProperty().SetLineWidth(1)
    
    return grid_actor


def create_axes(axes_length):
    """Create coordinate axes
    
    Args:
        axes_length (float): Length of the axes
        
    Returns:
        vtk.vtkAxesActor: Actor representing the axes
    """
    axes = vtk.vtkAxesActor()
    
    axes.SetTotalLength(axes_length, axes_length, axes_length)
    axes.SetShaftType(0)  # Make the axes a cylinder
    axes.SetCylinderRadius(0.01)  # Adjust thickness
    
    # Adjust the labels
    axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
    
    return axes 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Boundary condition symbols for 3D visualization
"""

import vtk
import math

def create_bc_symbol(coords, dofs, size, color):
    """Create a boundary condition visualization symbol based on which DOFs are fixed
    
    Args:
        coords (tuple): (x, y, z) coordinates where to place the symbol
        dofs (list): List of booleans indicating which DOFs are fixed
                     [x_fixed, y_fixed, z_fixed]
        size (float): Size of the symbol
        color (tuple): (r, g, b) color values (0-1 range)
        
    Returns:
        vtk.vtkActor: Actor representing the boundary condition symbol
    """
    # Ensure dofs has at least 3 values
    dofs_padded = dofs + [False] * (3 - len(dofs)) if len(dofs) < 3 else dofs[:3]
    
    # Count how many directions are fixed
    fixed_count = sum(dofs_padded)
    
    # Choose the appropriate visualization based on fixed DOFs
    if fixed_count == 0:
        # No fixed DOFs - return an empty actor
        return create_empty_symbol(coords)
    elif fixed_count == 3:
        # All DOFs fixed - show fixed symbol
        return create_fixed_symbol(coords, size, color)
    else:
        # Some DOFs fixed - show specialized symbol
        return create_partial_constraint_symbol(coords, dofs_padded, size, color)

def create_empty_symbol(coords):
    """Create an empty/invisible symbol for boundary conditions with no constraints"""
    # Create a small invisible point
    point = vtk.vtkSphereSource()
    point.SetCenter(coords)
    point.SetRadius(0.001)  # Very small radius
    point.SetPhiResolution(4)
    point.SetThetaResolution(4)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(point.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetOpacity(0.0)  # Make it invisible
    
    return actor

def create_fixed_symbol(coords, size, color):
    """Create a fixed boundary condition symbol (all DOFs constrained)"""
    # Create a cube to represent a fully fixed boundary condition
    cube = vtk.vtkCubeSource()
    cube.SetCenter(coords)
    cube.SetXLength(size)
    cube.SetYLength(size)
    cube.SetZLength(size)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cube.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetOpacity(0.9)
    
    return actor

def create_partial_constraint_symbol(coords, dofs, size, color):
    """Create a boundary condition symbol for partial constraints
    
    Args:
        coords (tuple): (x, y, z) coordinates
        dofs (list): List of 3 booleans [x_fixed, y_fixed, z_fixed]
        size (float): Size of the symbol
        color (tuple): (r, g, b) color values
        
    Returns:
        vtk.vtkActor: A combined actor for the boundary condition symbol
    """
    # Create a multiblock dataset to hold all the parts
    append = vtk.vtkAppendPolyData()
    
    x_fixed, y_fixed, z_fixed = dofs
    
    # For X direction constraint
    if x_fixed:
        x_plane = create_direction_plane(coords, size, color, 'x')
        append.AddInputConnection(x_plane.GetOutputPort())
    
    # For Y direction constraint
    if y_fixed:
        y_plane = create_direction_plane(coords, size, color, 'y')
        append.AddInputConnection(y_plane.GetOutputPort())
    
    # For Z direction constraint
    if z_fixed:
        z_plane = create_direction_plane(coords, size, color, 'z')
        append.AddInputConnection(z_plane.GetOutputPort())
    
    # Create mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(append.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetOpacity(0.9)
    
    return actor

def create_direction_plane(coords, size, color, direction):
    """Create a thin plane perpendicular to the given direction"""
    plane = vtk.vtkPlaneSource()
    
    # Set the size
    half_size = size / 2
    thickness = size / 10  # Make the plane thin
    
    if direction == 'x':
        # YZ plane
        plane.SetOrigin(coords[0] - thickness/2, coords[1] - half_size, coords[2] - half_size)
        plane.SetPoint1(coords[0] - thickness/2, coords[1] + half_size, coords[2] - half_size)
        plane.SetPoint2(coords[0] - thickness/2, coords[1] - half_size, coords[2] + half_size)
    elif direction == 'y':
        # XZ plane
        plane.SetOrigin(coords[0] - half_size, coords[1] - thickness/2, coords[2] - half_size)
        plane.SetPoint1(coords[0] + half_size, coords[1] - thickness/2, coords[2] - half_size)
        plane.SetPoint2(coords[0] - half_size, coords[1] - thickness/2, coords[2] + half_size)
    else:  # z
        # XY plane
        plane.SetOrigin(coords[0] - half_size, coords[1] - half_size, coords[2] - thickness/2)
        plane.SetPoint1(coords[0] + half_size, coords[1] - half_size, coords[2] - thickness/2)
        plane.SetPoint2(coords[0] - half_size, coords[1] + half_size, coords[2] - thickness/2)
    
    # Create an extrusion to make the plane have some thickness
    extrude = vtk.vtkLinearExtrusionFilter()
    extrude.SetInputConnection(plane.GetOutputPort())
    
    if direction == 'x':
        extrude.SetVector(thickness, 0, 0)
    elif direction == 'y':
        extrude.SetVector(0, thickness, 0)
    else:  # z
        extrude.SetVector(0, 0, thickness)
    
    return extrude

def create_arrow_constraint(coords, size, color, direction):
    """Create an arrow pointing in the constraint direction"""
    # Create an arrow source
    arrow = vtk.vtkArrowSource()
    arrow.SetTipResolution(12)
    arrow.SetShaftResolution(12)
    arrow.SetTipLength(0.3)
    arrow.SetTipRadius(0.1)
    arrow.SetShaftRadius(0.03)
    
    # Transform to position and orient the arrow
    transform = vtk.vtkTransform()
    transform.Translate(coords[0], coords[1], coords[2])
    
    # Scale the arrow based on the size
    transform.Scale(size, size, size)
    
    # Orient the arrow based on the direction
    if direction == 'x':
        transform.RotateY(0)  # Arrow already points in X
    elif direction == 'y':
        transform.RotateZ(90)  # Rotate 90 around Z to point in Y
    else:  # z
        transform.RotateY(-90)  # Rotate -90 around Y to point in Z
    
    # Apply the transform
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputConnection(arrow.GetOutputPort())
    transform_filter.SetTransform(transform)
    
    return transform_filter 
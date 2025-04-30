#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Example script for creating a fixed beam model with advanced components
"""

import os
import sys
import numpy as np
import datetime
import uuid

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.project import Project
from src.io.hdf5_storage import HDF5Storage

def create_fixed_beam_model():
    """Create a sample fixed beam structural model with advanced components"""
    project = Project("Fixed Beam Example")
    project.description = "A fixed beam model with sections, constraints, and recorders"
    
    # Add nodes along the beam
    for i in range(5):
        x = i * 2.0  # 2m spacing
        project.add_node(i+1, x, 0.0, 0.0)  # Nodes 1-5 along X axis
    
    # Add material
    project.add_material(1, "Steel", {
        "E": 200e9,    # Young's modulus (Pa)
        "nu": 0.3,     # Poisson's ratio
        "rho": 7850.0  # Density (kg/m³)
    })
    
    # Add section
    project.add_section(1, "WideFlange", {
        "d": 0.4,      # Depth (m)
        "bf": 0.2,     # Flange width (m)
        "tf": 0.02,    # Flange thickness (m)
        "tw": 0.015,   # Web thickness (m)
        "A": 0.0134,   # Cross-sectional area (m²)
        "Ix": 0.000467, # Moment of inertia about x-axis (m⁴)
        "Iy": 0.000156, # Moment of inertia about y-axis (m⁴)
        "J": 0.00002    # Torsional constant (m⁴)
    })
    
    # Add beam elements connecting the nodes
    for i in range(4):
        project.add_element(i+1, "elasticBeamColumn", [i+1, i+2], material_id=1, section_id=1)
    
    # Add boundary conditions (fixed at both ends)
    # Fix all DOFs at node 1 (left end)
    project.add_boundary_condition(1, 1, [1, 2, 3, 4, 5, 6], [0, 0, 0, 0, 0, 0])
    # Fix all DOFs at node 5 (right end)
    project.add_boundary_condition(2, 5, [1, 2, 3, 4, 5, 6], [0, 0, 0, 0, 0, 0])
    
    # Add a vertical load at the middle node (node 3)
    project.add_load(1, "point", 3, [2], [-10000.0])  # 10kN downward at node 3
    
    # Add a transformation for geometric nonlinearity
    project.add_transformation(1, "PDelta", {
        "vecxz": [0.0, 0.0, 1.0]  # Vector defining the x-z plane
    })
    
    # Add a constraint for equal DOFs between nodes 2 and 4
    project.add_constraint(1, "equalDOF", {
        "retained_node": 2,
        "constrained_node": 4,
        "dofs": [4, 5]  # Equal rotations about X and Y
    })
    
    # Add a recorder for node displacements
    project.add_recorder(1, "Node", 
                         target="all", 
                         dofs=[1, 2, 3], 
                         file_name="node_disp.out", 
                         time_interval=0.01)
    
    # Add a recorder for element forces
    project.add_recorder(2, "Element", 
                         target="all", 
                         file_name="element_forces.out", 
                         time_interval=0.01)
    
    # Add a timeseries for dynamic analysis
    project.add_timeseries(1, "Linear", {
        "factor": 1.0
    })
    
    # Add a load pattern with the timeseries
    project.add_pattern(1, "Plain", 
                        timeseries_id=1, 
                        properties={"loadCase": "static"})
    
    # Configure analysis settings
    project.analysis_settings = {
        "type": "static",
        "solver": "newton",
        "tolerance": 1e-6,
        "max_iterations": 100,
        "time_step": 0.01,
        "num_steps": 10
    }
    
    return project

def simulate_analysis_results(project):
    """Simulate analysis results for demonstration purposes"""
    # Create a dictionary to hold the analysis results
    analysis_id = str(uuid.uuid4())
    results = {
        'analysis_info': {
            'type': 'static',
            'solver': 'newton',
            'timestamp': datetime.datetime.now().isoformat()
        },
        'time_steps': np.linspace(0, 1.0, 10).tolist(),
        'node_displacements': {},
        'element_forces': {}
    }
    
    # Generate dummy displacement data for each node
    max_displacement = 0.01  # 1cm at the middle node
    for node_id in project.nodes:
        # Create displacements that form a parabola (maximum at center)
        x = project.nodes[node_id]["coordinates"][0]
        # Parabolic shape with zero at x=0 and x=8
        shape_factor = -(x**2) / 16 + x / 2
        
        # Create time series data
        displacements = np.zeros((10, 3))  # 10 time steps, 3 DOFs (x, y, z)
        # No x displacement
        displacements[:, 0] = np.zeros(10)
        # Y displacement increases with time
        displacements[:, 1] = np.linspace(0, max_displacement * shape_factor, 10)
        # No z displacement
        displacements[:, 2] = np.zeros(10)
        
        results['node_displacements'][node_id] = displacements.tolist()
    
    # Generate dummy force data for each element
    for element_id in project.elements:
        # Create some random forces that increase over time steps
        moments = np.random.uniform(-10000, 10000, size=(10, 6))
        # Make forces increase with time steps
        for i in range(10):
            moments[i, :] = moments[i, :] * (i+1) / 10
            
        results['element_forces'][element_id] = moments.tolist()
    
    return analysis_id, results

def main():
    """Main function"""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a sample project
    print("Creating fixed beam model...")
    project = create_fixed_beam_model()
    
    # Save to HDF5
    hdf5_path = os.path.join(output_dir, 'fixed_beam.h5')
    print(f"Saving project to HDF5: {hdf5_path}")
    project.save(hdf5_path)
    
    # Simulate analysis results
    print("Simulating analysis results...")
    analysis_id, results = simulate_analysis_results(project)
    
    # Add analysis results to the project
    print(f"Adding analysis results with ID: {analysis_id}")
    project.add_analysis_results(analysis_id, results)
    
    # Read back the project to verify
    print("\nReading project from HDF5...")
    loaded_project = Project.load(hdf5_path)
    print(f"Loaded project: {loaded_project.name}")
    print(f"Description: {loaded_project.description}")
    print(f"Nodes: {len(loaded_project.nodes)}")
    print(f"Elements: {len(loaded_project.elements)}")
    print(f"Materials: {len(loaded_project.materials)}")
    print(f"Sections: {len(loaded_project.sections)}")
    print(f"Constraints: {len(loaded_project.constraints)}")
    print(f"Recorders: {len(loaded_project.recorders)}")
    print(f"Transformations: {len(loaded_project.transformations)}")
    print(f"Timeseries: {len(loaded_project.timeseries)}")
    print(f"Patterns: {len(loaded_project.patterns)}")
    
    # Get analysis results
    print("\nRetrieving analysis results...")
    analyses = loaded_project.get_analysis_results()
    print(f"Available analyses: {len(analyses)}")
    
    if analyses:
        # Get node displacements from the most recent analysis
        analysis_id = analyses[0]['id']
        results = loaded_project.get_analysis_results(analysis_id)
        print(f"Analysis has {len(results['time_steps'])} time steps")
        
        # Show displacement at the middle node
        middle_node = 3
        if middle_node in results['node_displacements']:
            max_disp = results['node_displacements'][middle_node][-1]
            print(f"Maximum vertical displacement at middle node: {max_disp[1]:.6f} m")
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Example script for creating and using HDF5 model storage
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

def create_sample_model():
    """Create a sample structural model"""
    project = Project("Sample Truss Bridge")
    project.description = "A sample 2D truss bridge model for demonstration"
    
    # Add nodes
    project.add_node(1, 0.0, 0.0)
    project.add_node(2, 4.0, 0.0)
    project.add_node(3, 8.0, 0.0)
    project.add_node(4, 12.0, 0.0)
    project.add_node(5, 2.0, 3.0)
    project.add_node(6, 6.0, 3.0)
    project.add_node(7, 10.0, 3.0)
    
    # Add material
    project.add_material(1, "Steel01", {
        "Fy": 345e6,  # Yield stress
        "E0": 200e9,  # Young's modulus
        "b": 0.01     # Strain hardening ratio
    })
    
    # Add truss elements
    # Bottom chord
    project.add_element(1, "truss", [1, 2], 1, 0.01)
    project.add_element(2, "truss", [2, 3], 1, 0.01)
    project.add_element(3, "truss", [3, 4], 1, 0.01)
    
    # Top chord
    project.add_element(4, "truss", [5, 6], 1, 0.01)
    project.add_element(5, "truss", [6, 7], 1, 0.01)
    
    # Diagonal members
    project.add_element(6, "truss", [1, 5], 1, 0.008)
    project.add_element(7, "truss", [5, 2], 1, 0.008)
    project.add_element(8, "truss", [2, 6], 1, 0.008)
    project.add_element(9, "truss", [6, 3], 1, 0.008)
    project.add_element(10, "truss", [3, 7], 1, 0.008)
    project.add_element(11, "truss", [7, 4], 1, 0.008)
    
    # Add boundary conditions
    project.add_boundary_condition(1, 1, [1, 2], [1, 1])  # Fix node 1 in x and y
    project.add_boundary_condition(2, 4, [1, 2], [0, 1])  # Fix node 4 in y, allow x
    
    # Add a load
    project.add_load(1, "point", 6, [2], [-10000.0])  # Downward 10kN load at top middle
    
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
    for node_id in project.nodes:
        # Create some random displacements that increase over time steps
        displacements = np.zeros((10, 3))  # 10 time steps, 3 DOFs (x, y, z)
        displacements[:, 0] = np.linspace(0, np.random.uniform(-0.01, 0.01), 10)  # x displacement
        displacements[:, 1] = np.linspace(0, np.random.uniform(-0.02, 0.02), 10)  # y displacement
        
        results['node_displacements'][node_id] = displacements.tolist()
    
    # Generate dummy force data for each element
    for element_id in project.elements:
        # Create some random forces that increase over time steps
        forces = np.zeros((10, 6))  # 10 time steps, 6 force components
        forces[:, 0] = np.linspace(0, np.random.uniform(-50000, 50000), 10)  # axial force
        
        results['element_forces'][element_id] = forces.tolist()
    
    return analysis_id, results

def main():
    """Main function"""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a sample project
    print("Creating sample project...")
    project = create_sample_model()
    
    # Save to HDF5
    hdf5_path = os.path.join(output_dir, 'sample_bridge.h5')
    print(f"Saving project to HDF5: {hdf5_path}")
    project.save(hdf5_path)
    
    # Simulate analysis results
    print("Simulating analysis results...")
    analysis_id, results = simulate_analysis_results(project)
    
    # Add analysis results to the project
    print(f"Adding analysis results with ID: {analysis_id}")
    project.add_analysis_results(analysis_id, results)
    
    # Read back the project
    print("\nReading project from HDF5...")
    loaded_project = Project.load(hdf5_path)
    print(f"Loaded project: {loaded_project.name}")
    print(f"Description: {loaded_project.description}")
    print(f"Nodes: {len(loaded_project.nodes)}")
    print(f"Elements: {len(loaded_project.elements)}")
    print(f"Materials: {len(loaded_project.materials)}")
    
    # Get analysis results
    print("\nRetrieving analysis results...")
    analyses = loaded_project.get_analysis_results()
    print(f"Available analyses: {len(analyses)}")
    
    for analysis in analyses:
        print(f"Analysis ID: {analysis['id']}")
        print(f"Timestamp: {analysis.get('timestamp', 'N/A')}")
        
        # Get full results for this analysis
        analysis_results = loaded_project.get_analysis_results(analysis['id'])
        
        if 'time_steps' in analysis_results:
            print(f"Time steps: {len(analysis_results['time_steps'])}")
        
        if 'node_displacements' in analysis_results:
            print(f"Node results: {len(analysis_results['node_displacements'])} nodes")
            
            # Show sample node result
            node_id = next(iter(analysis_results['node_displacements'].keys()))
            node_disp = analysis_results['node_displacements'][node_id]
            print(f"  Node {node_id} final displacement: {node_disp[-1]}")
            
        if 'element_forces' in analysis_results:
            print(f"Element results: {len(analysis_results['element_forces'])} elements")
            
            # Show sample element result
            element_id = next(iter(analysis_results['element_forces'].keys()))
            element_force = analysis_results['element_forces'][element_id]
            print(f"  Element {element_id} final force: {element_force[-1][0]:.2f} N")
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main() 
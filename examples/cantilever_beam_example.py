#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Example script for creating a cantilever beam model with staged analysis
"""

import os
import sys
import numpy as np
import datetime
import uuid
import h5py

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.project import Project
from src.io.hdf5_storage import HDF5Storage

def create_cantilever_beam_model():
    """Create a cantilever beam model with multiple analysis stages"""
    
    # Create a new project
    project = Project("Cantilever Beam Analysis")
    project.description = "A multi-stage analysis of a cantilever beam with different loading conditions"
    
    # Update model builder parameters for this specific model
    project.update_model_builder_params(ndm=3, ndf=6, model_type="basic")
    
    # Stage 1: Model Definition (Beam structure with fixed end)
    project.create_stage(1, "Model Definition")
    
    # Material: Steel
    project.add_material(1, "Elastic", {
        "E": 200e9,    # Young's modulus (Pa)
        "nu": 0.3,     # Poisson's ratio
        "rho": 7850.0  # Density (kg/m³)
    }, stage_id=1)
    
    # Section properties: I-beam
    project.add_section(1, "WideFlange", {
        "d": 0.3,      # Depth (m) 
        "bf": 0.2,     # Flange width (m)
        "tf": 0.015,   # Flange thickness (m)
        "tw": 0.01     # Web thickness (m)
    }, stage_id=1)
    
    # Define nodes for a 6m cantilever beam with 7 nodes
    for i in range(7):
        x = i * 1.0  # 1m spacing
        project.add_node(i+1, x, 0.0, 0.0, stage_id=1)
    
    # Add elements connecting the nodes (beam elements)
    for i in range(6):
        project.add_element(
            i+1, 
            "elasticBeamColumn", 
            [i+1, i+2],  # Connect adjacent nodes 
            material_id=1, 
            section_id=1, 
            stage_id=1
        )
    
    # Add fixed boundary condition at the left end (node 1)
    project.add_boundary_condition(
        1, 
        1,  # Node 1 
        [1, 1, 1, 1, 1, 1],  # Fix all 6 DOFs (x, y, z, rx, ry, rz)
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # Zero values
        stage_id=1
    )
    
    # Define transformation for the beam elements
    project.add_transformation(
        1, 
        "Linear", 
        {"vector": [0.0, 0.0, 1.0]},  # Vector defining the local z-axis
        stage_id=1
    )
    
    # Stage 2: Vertical Point Load at End
    project.create_stage(2, "Vertical Point Load")
    
    # Copy all elements from stage 1
    project.propagate_stage(1, 2)
    
    # Add vertical load at the free end (node 7)
    project.add_load(
        1, 
        "point", 
        7,  # Node 7 (end of beam)
        [2],  # DOF 2 (vertical direction)
        [-10000.0],  # 10 kN downward force
        stage_id=2
    )
    
    # Define a recorder to capture displacements at all nodes
    project.add_recorder(
        1,
        "Node",
        "all",
        dofs=[1, 2, 3],  # Record x, y, z displacements
        file_name="cantilever_displacements.out",
        time_interval=0.1,
        stage_id=2
    )
    
    # Define a recorder to capture element forces
    project.add_recorder(
        2,
        "Element",
        "all",
        file_name="cantilever_forces.out",
        time_interval=0.1,
        stage_id=2
    )
    
    # Stage 3: Distributed Load
    project.create_stage(3, "Distributed Load")
    
    # Copy all elements from stage 1, but not the loads from stage 2
    project.propagate_stage(1, 3)
    
    # Add uniformly distributed load along the beam
    for i in range(6):
        project.add_load(
            i+1, 
            "element",
            i+1,  # Element ID
            [2],  # DOF 2 (vertical direction)
            [-2000.0],  # 2 kN/m downward distributed load
            stage_id=3
        )
    
    # Define recorders for this stage
    project.add_recorder(
        3,
        "Node",
        "all",
        dofs=[1, 2, 3],  # Record x, y, z displacements
        file_name="cantilever_distributed_displacements.out",
        time_interval=0.1,
        stage_id=3
    )
    
    project.add_recorder(
        4,
        "Element",
        "all",
        file_name="cantilever_distributed_forces.out",
        time_interval=0.1,
        stage_id=3
    )
    
    # Stage 4: Combined Loading
    project.create_stage(4, "Combined Loading")
    
    # Copy the base model from stage 1
    project.propagate_stage(1, 4)
    
    # Add both types of loads
    # Point load
    project.add_load(
        1, 
        "point", 
        7,  # Node 7 (end of beam)
        [2],  # DOF 2 (vertical direction)
        [-5000.0],  # 5 kN downward force
        stage_id=4
    )
    
    # Distributed load
    for i in range(6):
        project.add_load(
            i+2, 
            "element",
            i+1,  # Element ID
            [2],  # DOF 2 (vertical direction)
            [-1000.0],  # 1 kN/m downward distributed load
            stage_id=4
        )
    
    # Add moment at the middle of the beam (node 4)
    project.add_load(
        8,
        "point",
        4,  # Node 4 (middle)
        [6],  # DOF 6 (rotation about z)
        [2000.0],  # 2 kN·m moment
        stage_id=4
    )
    
    # Define recorders for this stage
    project.add_recorder(
        5,
        "Node",
        "all",
        dofs=[1, 2, 3, 4, 5, 6],  # Record all DOFs
        file_name="cantilever_combined_displacements.out",
        time_interval=0.1,
        stage_id=4
    )
    
    project.add_recorder(
        6,
        "Element",
        "all",
        file_name="cantilever_combined_forces.out",
        time_interval=0.1,
        stage_id=4
    )
    
    return project

def generate_simulated_results(project):
    """Generate simulated analysis results for demonstration purposes"""
    
    # Create a new HDF5 storage object with matching name to MSEE file
    # This enables automatic results file association in post-processing mode
    filename = os.path.join(os.path.dirname(__file__), "cantilever_beam.h5")
    storage = HDF5Storage(filename)
    
    # Save the project structure to HDF5
    storage.save_project(project)
    
    # Generate simulated results for each stage
    stages = [2, 3, 4]  # We only have loads and analysis in stages 2, 3, and 4
    
    for stage_id in stages:
        # Generate analysis ID
        analysis_id = f"analysis_{stage_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create simulated displacement results
        node_ids = list(project.stages[stage_id]['nodes'].keys())
        num_nodes = len(node_ids)
        
        # Create time steps
        time_steps = np.linspace(0, 1.0, 11)  # 11 time steps from 0 to 1.0
        
        # Simulated displacements
        # For stage 2 (point load), displacement increases from support to tip
        if stage_id == 2:
            # For a cantilever beam with point load at end, displacement varies with x²(3L-x)
            displacements = {}
            beam_length = 6.0  # 6m
            for node_id in node_ids:
                x = project.stages[stage_id]['nodes'][node_id]['coordinates'][0]
                scale_factor = -0.001  # Scale for reasonable displacement values
                
                # Only vertical displacement for point load at end
                node_disps = []
                for t in time_steps:
                    # Analytical formula for cantilever with end load: y = Px²(3L-x)/(6EI)
                    # We simplify and just scale by time for demonstration
                    vert_disp = scale_factor * t * x**2 * (3*beam_length - x)
                    node_disps.append([0.0, vert_disp, 0.0, 0.0, 0.0, 0.0])
                
                displacements[node_id] = node_disps
        
        # For stage 3 (distributed load), displacement has a different pattern
        elif stage_id == 3:
            # For a cantilever beam with UDL, displacement varies with x²(6L²-4Lx+x²)/24
            displacements = {}
            beam_length = 6.0  # 6m
            for node_id in node_ids:
                x = project.stages[stage_id]['nodes'][node_id]['coordinates'][0]
                scale_factor = -0.0005  # Scale for reasonable displacement values
                
                # Only vertical displacement for distributed load
                node_disps = []
                for t in time_steps:
                    # Simplified formula for demonstration
                    vert_disp = scale_factor * t * x**2 * (6*beam_length**2 - 4*beam_length*x + x**2)
                    node_disps.append([0.0, vert_disp, 0.0, 0.0, 0.0, 0.0])
                
                displacements[node_id] = node_disps
        
        # For stage 4 (combined loading), sum the effects
        elif stage_id == 4:
            # Combine effects of point load, distributed load, and moment
            displacements = {}
            beam_length = 6.0  # 6m
            for node_id in node_ids:
                x = project.stages[stage_id]['nodes'][node_id]['coordinates'][0]
                point_scale = -0.0005  # Scale for point load effect
                dist_scale = -0.00025  # Scale for distributed load effect
                moment_scale = 0.0002  # Scale for moment effect
                
                node_disps = []
                for t in time_steps:
                    # Point load effect
                    point_disp = point_scale * t * x**2 * (3*beam_length - x)
                    
                    # Distributed load effect
                    dist_disp = dist_scale * t * x**2 * (6*beam_length**2 - 4*beam_length*x + x**2)
                    
                    # Moment effect (simplified)
                    moment_disp = moment_scale * t * x**2 if x >= 3 else 0
                    
                    # Combined effect
                    vert_disp = point_disp + dist_disp + moment_disp
                    
                    node_disps.append([0.0, vert_disp, 0.0, 0.0, 0.0, 0.0])
                
                displacements[node_id] = node_disps
        
        # Create simulated element forces
        element_ids = list(project.stages[stage_id]['elements'].keys())
        num_elements = len(element_ids)
        
        # Element forces (simplified for demonstration)
        element_forces = {}
        for element_id in element_ids:
            # Get element nodes
            element_data = project.stages[stage_id]['elements'][element_id]
            node_ids = element_data['nodes']
            
            # Get node coordinates
            start_node = project.stages[stage_id]['nodes'][node_ids[0]]['coordinates']
            end_node = project.stages[stage_id]['nodes'][node_ids[1]]['coordinates']
            
            # Element position along beam (use start position for simplicity)
            x = start_node[0]
            
            # Simulated forces depend on position and stage
            element_force_data = []
            for t in time_steps:
                if stage_id == 2:  # Point load - shear constant, moment varies linearly
                    shear = -10000 * t if x < 6.0 else 0  # 10kN point load
                    moment = -10000 * (6.0 - x) * t  # Moment = Force * distance
                elif stage_id == 3:  # Distributed load - shear varies linearly, moment varies quadratically
                    shear = -2000 * (6.0 - x) * t  # 2kN/m distributed load
                    moment = -1000 * (6.0 - x)**2 * t  # Approximation
                else:  # Combined loading - sum of effects
                    shear = -5000 * t if x < 6.0 else 0  # Point load
                    shear += -1000 * (6.0 - x) * t  # Distributed load
                    moment = -5000 * (6.0 - x) * t  # Point load moment
                    moment += -500 * (6.0 - x)**2 * t  # Distributed load moment
                    if x < 3.0:  # Moment effect
                        moment += 2000 * t
                
                # Basic forces format for beam elements
                element_force_data.append([shear, 0.0, 0.0, moment, 0.0, 0.0])
            
            element_forces[element_id] = element_force_data
        
        # Create results dictionary
        results = {
            'name': f"Stage {stage_id} Analysis",
            'time': time_steps.tolist(),
            'displacements': displacements,
            'element_forces': element_forces
        }
        
        # Save to HDF5
        storage.save_analysis_results(project.project_id, analysis_id, results)
    
    # Close HDF5 file
    storage.close()
    
    # Return the filename where results were saved
    return filename

def save_msee_file(project):
    """Save the project to a msee file format"""
    filename = os.path.join(os.path.dirname(__file__), "cantilever_beam.msee")
    project.save(filename)
    return filename

def main():
    """Main function to run the example"""
    print("Creating cantilever beam model...")
    project = create_cantilever_beam_model()
    
    print("Saving model to MSEE file...")
    msee_file = save_msee_file(project)
    print(f"Model saved to: {msee_file}")
    
    print("Generating simulated results...")
    results_file = generate_simulated_results(project)
    print(f"Results saved to: {results_file}")
    
    print("Example complete.")

if __name__ == "__main__":
    main() 
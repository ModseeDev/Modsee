"""
Example of using the Stage management system for multi-stage analysis.

This example demonstrates how to create and manage stages for sequential analysis,
such as applying different loads in stages or modeling construction sequences.
"""

import os
import sys

# Add parent directory to path to allow importing from model directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.base.core import ModelMetadata
from model.base.manager import ModelManager
from model.stages import StageType
from model.loads import LoadDirection


def create_simple_model():
    """Create a simple model with nodes only (for demonstration)."""
    manager = ModelManager()
    
    # Create a few nodes
    node1 = manager.create_node(
        metadata=ModelMetadata(name="Node 1"),
        coordinates=[0.0, 0.0, 0.0]
    )
    node2 = manager.create_node(
        metadata=ModelMetadata(name="Node 2"),
        coordinates=[5.0, 0.0, 0.0]
    )
    node3 = manager.create_node(
        metadata=ModelMetadata(name="Node 3"),
        coordinates=[5.0, 5.0, 0.0]
    )
    node4 = manager.create_node(
        metadata=ModelMetadata(name="Node 4"),
        coordinates=[0.0, 5.0, 0.0]
    )
    
    return manager


def setup_stages(manager):
    """Set up a multi-stage analysis using the Stage management system."""
    # Create an initial stage for basic geometry and boundary conditions
    initial_stage = manager.stage_manager.create_stage(
        stage_type=StageType.STATIC,
        name="Initial Configuration",
        description="Base geometry and boundary conditions",
        is_initial=True
    )
    
    # Add all nodes to the initial stage
    for node in manager.nodes.all():
        initial_stage.add_node(node.id)
    
    # Create a second stage for the first load case
    stage_load1 = manager.stage_manager.create_stage(
        stage_type=StageType.STATIC,
        name="First Load Case",
        description="Apply first set of loads",
        order=1,
        parent_stage_id=initial_stage.id
    )
    
    # Create a third stage for the second load case
    stage_load2 = manager.stage_manager.create_stage(
        stage_type=StageType.STATIC,
        name="Second Load Case",
        description="Apply second set of loads",
        order=2,
        parent_stage_id=stage_load1.id
    )
    
    # Configure analysis parameters for each stage
    initial_stage.set_analysis_parameter("load_increment", 0.1)
    initial_stage.set_analysis_parameter("num_steps", 10)
    
    stage_load1.set_analysis_parameter("load_increment", 0.05)
    stage_load1.set_analysis_parameter("num_steps", 20)
    stage_load1.set_analysis_parameter("load_pattern", "uniform")
    
    stage_load2.set_analysis_parameter("load_increment", 0.05)
    stage_load2.set_analysis_parameter("num_steps", 20)
    stage_load2.set_analysis_parameter("load_pattern", "triangular")
    
    return manager


def generate_opensees_code(manager):
    """Generate OpenSeesPy code for the multi-stage analysis."""
    code_lines = [
        "# OpenSeesPy code for multi-stage analysis",
        "import openseespy.opensees as ops",
        "",
        "# Initialize model",
        "ops.wipe()",
        "ops.model('basic', '-ndm', 3, '-ndf', 6)",
        ""
    ]
    
    # Get stages in sequence
    stages = manager.stage_manager.get_stage_sequence()
    
    # For each stage, generate code
    for stage in stages:
        code_lines.append(f"# {'-'*50}")
        code_lines.append(f"# Stage: {stage.metadata.name}")
        code_lines.append(f"# Description: {stage.description}")
        code_lines.append(f"# {'-'*50}")
        code_lines.append("")
        
        # For initial stage, create nodes
        if stage.is_initial:
            # Create nodes
            code_lines.append("# Create nodes")
            for node_id in stage.active_nodes:
                node = manager.nodes.get(node_id)
                if node:
                    # Use the coordinates list
                    coords = node.coordinates
                    if len(coords) >= 3:
                        code_lines.append(f"ops.node({node.id}, {coords[0]}, {coords[1]}, {coords[2]})")
                    elif len(coords) >= 2:
                        code_lines.append(f"ops.node({node.id}, {coords[0]}, {coords[1]})")
                    else:
                        code_lines.append(f"ops.node({node.id}, {coords[0]})")
            
            code_lines.append("")
            
            # Define boundary conditions
            code_lines.append("# Define boundary conditions")
            code_lines.append("ops.fix(1, 1, 1, 1, 1, 1, 1)  # Fix node 1 in all DOFs")
            code_lines.append("")
        
        # Add stage-specific analysis setup from the stage's to_opensees_py() method
        code_lines.append("# Set up analysis for this stage")
        code_lines.append(stage.to_opensees_py())
        code_lines.append("")
        
        # Add loads based on analysis parameters
        code_lines.append("# Apply loads for this stage")
        load_pattern = stage.get_analysis_parameter("load_pattern")
        if load_pattern:
            code_lines.append(f"# Using load pattern: {load_pattern}")
            if load_pattern == "uniform":
                code_lines.append("# Applying uniform loads to all nodes")
                code_lines.append("ops.timeSeries('Linear', 1)")
                code_lines.append("ops.pattern('Plain', 1, 1)")
                for node_id in stage.active_nodes:
                    if node_id != 1:  # Skip fixed node
                        code_lines.append(f"ops.load({node_id}, 0.0, -10.0, 0.0, 0.0, 0.0, 0.0)")
            elif load_pattern == "triangular":
                code_lines.append("# Applying triangular distribution of loads")
                code_lines.append("ops.timeSeries('Linear', 2)")
                code_lines.append("ops.pattern('Plain', 2, 2)")
                for node_id in stage.active_nodes:
                    if node_id != 1:  # Skip fixed node
                        # Vary load based on node ID for demonstration
                        magnitude = -5.0 * node_id
                        code_lines.append(f"ops.load({node_id}, 0.0, {magnitude}, 0.0, 0.0, 0.0, 0.0)")
        
        code_lines.append("")
        
        # Add analysis execution
        code_lines.append("# Run analysis for this stage")
        num_steps = stage.get_analysis_parameter("num_steps", 10)
        code_lines.append(f"print('Running analysis for stage: {stage.metadata.name}')")
        code_lines.append(f"for i in range({num_steps}):")
        code_lines.append("    ops.analyze(1)")
        code_lines.append("    print(f'  Step {i+1}/{num_steps} completed')")
        code_lines.append("")
        
        # If this is not the final stage, we need to maintain the state for the next stage
        if stage != stages[-1]:
            code_lines.append("# Commit state before moving to next stage")
            code_lines.append("ops.reactions()")
            code_lines.append("")
    
    return "\n".join(code_lines)


def main():
    """Main function to demonstrate the Stage management system."""
    print("Creating model...")
    manager = create_simple_model()
    
    print("\nSetting up stages...")
    manager = setup_stages(manager)
    
    print("\nStages in execution order:")
    for i, stage in enumerate(manager.stage_manager.get_stage_sequence()):
        print(f"{i+1}. {stage.metadata.name} ({stage.stage_type.name})")
    
    print("\nGenerating OpenSeesPy code for multi-stage analysis...")
    code = generate_opensees_code(manager)
    
    # Write code to file
    with open("multi_stage_analysis.py", "w") as f:
        f.write(code)
    
    print("\nCode generated and saved to 'multi_stage_analysis.py'")
    print("Stage management system demonstration complete.")


if __name__ == "__main__":
    main() 
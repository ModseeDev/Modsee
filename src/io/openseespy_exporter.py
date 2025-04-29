#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
OpenSeesPy export utilities
"""

import os
import datetime


class OpenSeesPyExporter:
    """Class for exporting models to OpenSeesPy script format"""
    
    def __init__(self, project):
        """Initialize with a project"""
        self.project = project
        
    def export(self, file_path):
        """Export the project to an OpenSeesPy script"""
        with open(file_path, 'w') as f:
            # Write file header
            self._write_header(f)
            
            # Write imports
            self._write_imports(f)
            
            # Write model initialization
            self._write_model_init(f)
            
            # Write materials
            self._write_materials(f)
            
            # Write nodes
            self._write_nodes(f)
            
            # Write elements
            self._write_elements(f)
            
            # Write boundary conditions
            self._write_boundary_conditions(f)
            
            # Write loads
            self._write_loads(f)
            
            # Write analysis settings
            self._write_analysis(f)
            
            # Write recorder commands
            self._write_recorders(f)
            
            # Write footer
            self._write_footer(f)
            
        return file_path
        
    def _write_header(self, file):
        """Write the file header"""
        file.write("# OpenSeesPy Model exported from Modsee\n")
        file.write("# Project: {}\n".format(self.project.name))
        file.write("# Description: {}\n".format(self.project.description))
        file.write("# Date: {}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        file.write("# Modsee Version: 0.1.0\n\n")
        
    def _write_imports(self, file):
        """Write import statements"""
        file.write("# Import the OpenSeesPy module\n")
        file.write("import openseespy.opensees as ops\n")
        file.write("import numpy as np\n\n")
        
    def _write_model_init(self, file):
        """Write model initialization commands"""
        file.write("# Model initialization\n")
        file.write("ops.wipe()\n")
        
        # Determine model dimensions based on nodes
        dimensions = 2  # Default to 2D
        for node in self.project.nodes.values():
            if abs(node["coordinates"][2]) > 1e-6:
                dimensions = 3
                break
                
        file.write("ops.model('BasicBuilder', '-ndm', {}, '-ndf', {})\n\n".format(
            dimensions, 3 if dimensions == 2 else 6))
        
    def _write_materials(self, file):
        """Write material definitions"""
        if not self.project.materials:
            return
            
        file.write("# Material definitions\n")
        
        for material_id, material in self.project.materials.items():
            material_type = material["type"]
            props = material["properties"]
            
            if material_type == "Steel01":
                # Steel01 material
                file.write("ops.uniaxialMaterial('Steel01', {}, {}, {}, {})\n".format(
                    material_id, props.get("Fy", 0), props.get("E0", 0), props.get("b", 0)))
                    
            elif material_type == "Concrete01":
                # Concrete01 material
                file.write("ops.uniaxialMaterial('Concrete01', {}, {}, {}, {}, {})\n".format(
                    material_id, props.get("fpc", 0), props.get("epsc0", 0), 
                    props.get("fpcu", 0), props.get("epscu", 0)))
                    
            elif material_type == "Elastic":
                # Elastic material
                file.write("ops.uniaxialMaterial('Elastic', {}, {})\n".format(
                    material_id, props.get("E", 0)))
                    
            # Add more material types as needed
            
        file.write("\n")
        
    def _write_nodes(self, file):
        """Write node definitions"""
        if not self.project.nodes:
            return
            
        file.write("# Node definitions\n")
        
        for node_id, node in self.project.nodes.items():
            coords = node["coordinates"]
            file.write("ops.node({}, {}, {}, {})\n".format(node_id, coords[0], coords[1], coords[2]))
            
            # Add mass if defined
            mass = node["mass"]
            if mass and (mass[0] > 0 or mass[1] > 0 or mass[2] > 0):
                file.write("ops.mass({}, {}, {}, {})\n".format(node_id, mass[0], mass[1], mass[2]))
                
        file.write("\n")
        
    def _write_elements(self, file):
        """Write element definitions"""
        if not self.project.elements:
            return
            
        file.write("# Element definitions\n")
        
        for element_id, element in self.project.elements.items():
            element_type = element["type"]
            nodes = element["nodes"]
            material_id = element["material"]
            section_id = element["section"]
            
            if element_type == "truss":
                # Truss element
                file.write("ops.element('truss', {}, {}, {}, {}, {})\n".format(
                    element_id, nodes[0], nodes[1], section_id, material_id))
                    
            elif element_type == "elasticBeamColumn":
                # Elastic beam-column element
                file.write("ops.element('elasticBeamColumn', {}, {}, {}, {}, {}, {}, {})\n".format(
                    element_id, nodes[0], nodes[1], section_id, material_id, 
                    1, 1))  # Assuming transformation ID 1 and integration points 1
                    
            # Add more element types as needed
            
        file.write("\n")
        
    def _write_boundary_conditions(self, file):
        """Write boundary condition definitions"""
        if not self.project.boundary_conditions:
            return
            
        file.write("# Boundary conditions\n")
        
        for bc_id, bc in self.project.boundary_conditions.items():
            node_id = bc["node"]
            dofs = bc["dofs"]
            values = bc["values"]
            
            dof_str = ", ".join([str(d) for d in dofs])
            value_str = ", ".join([str(v) for v in values])
            
            file.write("ops.fix({}, [{}], [{}])\n".format(node_id, dof_str, value_str))
            
        file.write("\n")
        
    def _write_loads(self, file):
        """Write load definitions"""
        if not self.project.loads:
            return
            
        file.write("# Loads\n")
        file.write("ops.pattern('Plain', 1, 'Linear')\n")
        
        for load_id, load in self.project.loads.items():
            load_type = load["type"]
            target_id = load["target"]
            dofs = load["dofs"]
            values = load["values"]
            
            if load_type == "nodeLoad":
                # Node load
                for i, dof in enumerate(dofs):
                    file.write("ops.load({}, {}, {})\n".format(
                        target_id, dof, values[i]))
                        
            # Add more load types as needed
            
        file.write("\n")
        
    def _write_analysis(self, file):
        """Write analysis settings"""
        analysis_settings = self.project.analysis_settings
        
        file.write("# Analysis settings\n")
        
        # Analysis type
        analysis_type = analysis_settings.get("type", "static")
        
        # Solver
        solver = analysis_settings.get("solver", "newton")
        file.write("ops.algorithm('{}')\n".format(solver))
        
        # Create the numberer
        file.write("ops.numberer('RCM')\n")
        
        # Create the system of equations
        file.write("ops.system('BandSPD')\n")
        
        # Create the constraint handler
        file.write("ops.constraints('Plain')\n")
        
        # Create the integrator
        file.write("ops.integrator('LoadControl', 1.0)\n")
        
        # Create the analysis object
        file.write("ops.analysis('Static')\n\n")
        
        # Perform the analysis
        file.write("# Perform the analysis\n")
        file.write("ops.analyze(1)\n\n")
        
    def _write_recorders(self, file):
        """Write recorder commands"""
        file.write("# Recorders\n")
        file.write("ops.recorder('Node', '-file', 'node_disp.out', '-time', '-node', 'all', '-dof', 1, 2, 3, 'disp')\n")
        file.write("ops.recorder('Element', '-file', 'element_forces.out', '-time', '-ele', 'all', 'forces')\n\n")
        
    def _write_footer(self, file):
        """Write the file footer"""
        file.write("# Print to screen that analysis is complete\n")
        file.write("print('Analysis complete.')\n")
        file.write("ops.wipe()\n") 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
HDF5 database storage utilities
"""

import os
import h5py
import numpy as np
import json
import datetime
from uuid import uuid4


class HDF5Storage:
    """Class for storing and retrieving model data using HDF5 format"""
    
    def __init__(self, file_path=None):
        """Initialize with an optional file path"""
        self.file_path = file_path
        self.h5file = None
        
    def open(self, file_path=None, mode='a'):
        """Open the HDF5 file for reading/writing"""
        if file_path:
            self.file_path = file_path
        
        if not self.file_path:
            raise ValueError("No file path specified")
            
        self.h5file = h5py.File(self.file_path, mode)
        return self.h5file
        
    def close(self):
        """Close the HDF5 file"""
        if self.h5file:
            self.h5file.close()
            self.h5file = None
            
    def __enter__(self):
        """Context manager entry"""
        if not self.h5file:
            self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        
    def save_project(self, project):
        """Save a project to HDF5 format"""
        with self.open(mode='a'):
            # Create or clear project group
            if 'Project' in self.h5file:
                del self.h5file['Project']
                
            project_group = self.h5file.create_group('Project')
            
            # Save project metadata
            project_group.attrs['project_id'] = project.project_id
            project_group.attrs['name'] = project.name
            project_group.attrs['description'] = project.description
            project_group.attrs['created_at'] = project.created_at
            project_group.attrs['modified_at'] = project.modified_at
            
            # Create model definition group
            model_group = project_group.create_group('ModelDefinition')
            
            # Save nodes
            if project.nodes:
                nodes_group = model_group.create_group('Nodes')
                for node_id, node in project.nodes.items():
                    node_group = nodes_group.create_group(str(node_id))
                    node_group.attrs['id'] = node_id
                    node_group.create_dataset('coordinates', data=node['coordinates'])
                    node_group.create_dataset('mass', data=node['mass'])
            
            # Save elements
            if project.elements:
                elements_group = model_group.create_group('Elements')
                for element_id, element in project.elements.items():
                    element_group = elements_group.create_group(str(element_id))
                    element_group.attrs['id'] = element_id
                    element_group.attrs['type'] = element['type']
                    element_group.attrs['material'] = element.get('material', 0)
                    element_group.attrs['section'] = element.get('section', 0)
                    element_group.create_dataset('nodes', data=element['nodes'])
            
            # Save materials
            if project.materials:
                materials_group = model_group.create_group('Materials')
                for material_id, material in project.materials.items():
                    material_group = materials_group.create_group(str(material_id))
                    material_group.attrs['id'] = material_id
                    material_group.attrs['type'] = material['type']
                    
                    # Store properties as dataset
                    for prop_name, prop_value in material['properties'].items():
                        material_group.attrs[prop_name] = prop_value
            
            # Save boundary conditions
            if project.boundary_conditions:
                bcs_group = model_group.create_group('BoundaryConditions')
                for bc_id, bc in project.boundary_conditions.items():
                    bc_group = bcs_group.create_group(str(bc_id))
                    bc_group.attrs['id'] = bc_id
                    bc_group.attrs['node'] = bc['node']
                    bc_group.create_dataset('dofs', data=bc['dofs'])
                    bc_group.create_dataset('values', data=bc['values'])
            
            # Save loads
            if project.loads:
                loads_group = model_group.create_group('Loads')
                for load_id, load in project.loads.items():
                    load_group = loads_group.create_group(str(load_id))
                    load_group.attrs['id'] = load_id
                    load_group.attrs['type'] = load['type']
                    load_group.attrs['target'] = load['target']
                    load_group.create_dataset('dofs', data=load['dofs'])
                    load_group.create_dataset('values', data=load['values'])
            
            # Save analysis settings as attributes
            settings_group = model_group.create_group('AnalysisSettings')
            for key, value in project.analysis_settings.items():
                settings_group.attrs[key] = value
                
        return self.file_path
    
    def load_project(self):
        """Load a project from HDF5 format"""
        from src.models.project import Project
        
        project = Project()
        
        with self.open(mode='r'):
            if 'Project' not in self.h5file:
                raise ValueError("No project data found in HDF5 file")
                
            project_group = self.h5file['Project']
            
            # Load project metadata
            project.project_id = project_group.attrs['project_id']
            project.name = project_group.attrs['name']
            project.description = project_group.attrs['description']
            project.created_at = project_group.attrs['created_at']
            project.modified_at = project_group.attrs['modified_at']
            project.file_path = self.file_path
            
            model_group = project_group['ModelDefinition']
            
            # Load nodes
            if 'Nodes' in model_group:
                nodes_group = model_group['Nodes']
                for node_id in nodes_group:
                    node_group = nodes_group[node_id]
                    node_data = {
                        'id': node_group.attrs['id'],
                        'coordinates': node_group['coordinates'][()].tolist(),
                        'mass': node_group['mass'][()].tolist()
                    }
                    project.nodes[int(node_id)] = node_data
            
            # Load elements
            if 'Elements' in model_group:
                elements_group = model_group['Elements']
                for element_id in elements_group:
                    element_group = elements_group[element_id]
                    element_data = {
                        'id': element_group.attrs['id'],
                        'type': element_group.attrs['type'],
                        'material': element_group.attrs['material'],
                        'section': element_group.attrs['section'],
                        'nodes': element_group['nodes'][()].tolist()
                    }
                    project.elements[int(element_id)] = element_data
            
            # Load materials
            if 'Materials' in model_group:
                materials_group = model_group['Materials']
                for material_id in materials_group:
                    material_group = materials_group[material_id]
                    
                    # Get properties from attributes
                    properties = {}
                    for key in material_group.attrs:
                        if key not in ['id', 'type']:
                            properties[key] = material_group.attrs[key]
                    
                    material_data = {
                        'id': material_group.attrs['id'],
                        'type': material_group.attrs['type'],
                        'properties': properties
                    }
                    project.materials[int(material_id)] = material_data
            
            # Load boundary conditions
            if 'BoundaryConditions' in model_group:
                bcs_group = model_group['BoundaryConditions']
                for bc_id in bcs_group:
                    bc_group = bcs_group[bc_id]
                    bc_data = {
                        'id': bc_group.attrs['id'],
                        'node': bc_group.attrs['node'],
                        'dofs': bc_group['dofs'][()].tolist(),
                        'values': bc_group['values'][()].tolist()
                    }
                    project.boundary_conditions[int(bc_id)] = bc_data
            
            # Load loads
            if 'Loads' in model_group:
                loads_group = model_group['Loads']
                for load_id in loads_group:
                    load_group = loads_group[load_id]
                    load_data = {
                        'id': load_group.attrs['id'],
                        'type': load_group.attrs['type'],
                        'target': load_group.attrs['target'],
                        'dofs': load_group['dofs'][()].tolist(),
                        'values': load_group['values'][()].tolist()
                    }
                    project.loads[int(load_id)] = load_data
            
            # Load analysis settings
            if 'AnalysisSettings' in model_group:
                settings_group = model_group['AnalysisSettings']
                for key in settings_group.attrs:
                    project.analysis_settings[key] = settings_group.attrs[key]
                    
        return project
        
    def save_analysis_results(self, project_id, analysis_id, results):
        """Save analysis results to the HDF5 file
        
        Args:
            project_id: The project ID
            analysis_id: A unique identifier for this analysis run
            results: Dictionary containing analysis results with keys:
                - node_displacements: Dictionary mapping node_id to displacement array
                - element_forces: Dictionary mapping element_id to forces array
                - time_steps: Array of time steps
                - analysis_info: Dictionary with analysis parameters
        """
        with self.open(mode='a'):
            # Create or get project group
            if 'Project' not in self.h5file:
                raise ValueError("No project found in HDF5 file")
                
            project_group = self.h5file['Project']
            
            # Create analysis results group if not exists
            if 'AnalysisResults' not in project_group:
                results_group = project_group.create_group('AnalysisResults')
            else:
                results_group = project_group['AnalysisResults']
                
            # Create group for this analysis
            analysis_id_str = str(analysis_id)
            if analysis_id_str in results_group:
                del results_group[analysis_id_str]
                
            analysis_group = results_group.create_group(analysis_id_str)
            
            # Save timestamp
            analysis_group.attrs['timestamp'] = datetime.datetime.now().isoformat()
            
            # Save analysis info
            for key, value in results.get('analysis_info', {}).items():
                analysis_group.attrs[key] = value
                
            # Save time steps
            if 'time_steps' in results:
                analysis_group.create_dataset('time_steps', data=results['time_steps'])
                
            # Save node displacements
            if 'node_displacements' in results:
                node_group = analysis_group.create_group('NodeResults')
                for node_id, displacements in results['node_displacements'].items():
                    node_group.create_dataset(str(node_id), data=displacements)
                    
            # Save element forces
            if 'element_forces' in results:
                element_group = analysis_group.create_group('ElementResults')
                for element_id, forces in results['element_forces'].items():
                    element_group.create_dataset(str(element_id), data=forces)
                    
        return True
        
    def get_analysis_list(self, project_id=None):
        """Get a list of available analyses in the file
        
        Returns:
            List of dictionaries with analysis information
        """
        analyses = []
        
        with self.open(mode='r'):
            if 'Project' not in self.h5file:
                return analyses
                
            project_group = self.h5file['Project']
            
            if 'AnalysisResults' not in project_group:
                return analyses
                
            results_group = project_group['AnalysisResults']
            
            for analysis_id in results_group:
                analysis_group = results_group[analysis_id]
                
                analysis_info = {
                    'id': analysis_id,
                    'timestamp': analysis_group.attrs.get('timestamp', '')
                }
                
                # Add any other attributes from the analysis
                for key in analysis_group.attrs:
                    if key != 'timestamp':
                        analysis_info[key] = analysis_group.attrs[key]
                        
                analyses.append(analysis_info)
                
        return analyses
        
    def get_analysis_results(self, analysis_id, result_type=None, ids=None):
        """Get analysis results from the file
        
        Args:
            analysis_id: The analysis ID to retrieve
            result_type: Optional type of results to retrieve ('node' or 'element')
            ids: Optional list of specific node or element IDs to retrieve
            
        Returns:
            Dictionary containing requested results
        """
        results = {}
        
        with self.open(mode='r'):
            if 'Project' not in self.h5file:
                return results
                
            project_group = self.h5file['Project']
            
            if 'AnalysisResults' not in project_group:
                return results
                
            results_group = project_group['AnalysisResults']
            
            if str(analysis_id) not in results_group:
                return results
                
            analysis_group = results_group[str(analysis_id)]
            
            # Get analysis info
            results['analysis_info'] = {}
            for key in analysis_group.attrs:
                results['analysis_info'][key] = analysis_group.attrs[key]
                
            # Get time steps if available
            if 'time_steps' in analysis_group:
                results['time_steps'] = analysis_group['time_steps'][()].tolist()
                
            # Get node results if requested
            if result_type is None or result_type == 'node':
                if 'NodeResults' in analysis_group:
                    results['node_displacements'] = {}
                    node_group = analysis_group['NodeResults']
                    
                    # Get all nodes or just requested ones
                    if ids is None:
                        for node_id in node_group:
                            results['node_displacements'][int(node_id)] = node_group[node_id][()].tolist()
                    else:
                        for node_id in ids:
                            if str(node_id) in node_group:
                                results['node_displacements'][int(node_id)] = node_group[str(node_id)][()].tolist()
                            
            # Get element results if requested
            if result_type is None or result_type == 'element':
                if 'ElementResults' in analysis_group:
                    results['element_forces'] = {}
                    element_group = analysis_group['ElementResults']
                    
                    # Get all elements or just requested ones
                    if ids is None:
                        for element_id in element_group:
                            results['element_forces'][int(element_id)] = element_group[element_id][()].tolist()
                    else:
                        for element_id in ids:
                            if str(element_id) in element_group:
                                results['element_forces'][int(element_id)] = element_group[str(element_id)][()].tolist()
                                
        return results 
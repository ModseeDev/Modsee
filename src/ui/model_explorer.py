#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Model Explorer UI components
"""

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QVariant, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QFont
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QToolButton, QButtonGroup, QLabel, QMenu, QAction


class ProjectTreeItem:
    """Tree item for the model explorer"""
    
    def __init__(self, data, parent=None):
        """Initialize with item data and parent"""
        self.parent_item = parent
        self.item_data = data
        self.child_items = []
        
    def appendChild(self, item):
        """Add a child item"""
        self.child_items.append(item)
        
    def child(self, row):
        """Get child item at row"""
        if row < 0 or row >= len(self.child_items):
            return None
        return self.child_items[row]
        
    def childCount(self):
        """Get number of child items"""
        return len(self.child_items)
        
    def columnCount(self):
        """Get number of columns"""
        return len(self.item_data)
        
    def data(self, column):
        """Get data for column"""
        if column < 0 or column >= len(self.item_data):
            return None
        return self.item_data[column]
        
    def parent(self):
        """Get parent item"""
        return self.parent_item
        
    def row(self):
        """Get row of this item in parent"""
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0


class ModelExplorerTreeModel(QAbstractItemModel):
    """Tree model for the model explorer"""
    
    def __init__(self, parent=None):
        """Initialize with parent"""
        super().__init__(parent)
        
        # Create root item
        self.root_item = ProjectTreeItem(["Name", "Value"])
        
        # Add placeholder
        self.setupModelData(None)
        
        # Keep track of the currently selected item
        self.selected_item_text = ""
        
    def columnCount(self, parent=QModelIndex()):
        """Get number of columns"""
        if parent.isValid():
            return parent.internalPointer().columnCount()
        return self.root_item.columnCount()
        
    def data(self, index, role=Qt.DisplayRole):
        """Get data for index and role"""
        if not index.isValid():
            return QVariant()
            
        item = index.internalPointer()
        
        if role == Qt.DisplayRole:
            return item.data(index.column())
        elif role == Qt.FontRole:
            if index.column() == 0:
                # Make the selected item bold
                if item.data(0) == self.selected_item_text:
                    font = QFont()
                    font.setBold(True)
                    return font
                # Bold font for top-level items
                elif index.parent() == QModelIndex():
                    font = QFont()
                    font.setBold(True)
                    return font
                
        return QVariant()
        
    def flags(self, index):
        """Get flags for index"""
        if not index.isValid():
            return Qt.NoItemFlags
            
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Get header data"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.root_item.data(section)
            
        return QVariant()
        
    def index(self, row, column, parent=QModelIndex()):
        """Get index for row, column and parent"""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
            
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
            
        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()
            
    def parent(self, index):
        """Get parent index"""
        if not index.isValid():
            return QModelIndex()
            
        child_item = index.internalPointer()
        parent_item = child_item.parent()
        
        if parent_item == self.root_item:
            return QModelIndex()
            
        return self.createIndex(parent_item.row(), 0, parent_item)
        
    def rowCount(self, parent=QModelIndex()):
        """Get number of rows"""
        if parent.column() > 0:
            return 0
            
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
            
        return parent_item.childCount()
        
    def setupModelData(self, project):
        """Setup model data from project"""
        # Clear existing items
        self.beginResetModel()
        self.root_item.child_items.clear()
        
        if project is None:
            # Add placeholder item
            placeholder = ProjectTreeItem(["No Project Loaded", ""], self.root_item)
            self.root_item.appendChild(placeholder)
            self.endResetModel()
            return
            
        # Create project root
        project_root = ProjectTreeItem([project.name, ""], self.root_item)
        self.root_item.appendChild(project_root)
        
        # Add model components categories
        model_root = ProjectTreeItem(["Model", ""], project_root)
        project_root.appendChild(model_root)
        
        # Add stages category
        stages_root = ProjectTreeItem(["Stages", str(len(project.stages))], model_root)
        model_root.appendChild(stages_root)
        
        # Sort stages by ID (numeric)
        sorted_stages = sorted(project.stages.items(), key=lambda x: x[0])
        
        # Add each stage
        for stage_id, stage_data in sorted_stages:
            stage_text = f"Stage {stage_id}: {stage_data['name']}"
            stage_item = ProjectTreeItem([stage_text, ""], stages_root)
            stages_root.appendChild(stage_item)
            
            # Add nodes category for this stage
            nodes_text = f"Nodes"
            nodes_count = len(stage_data['nodes'])
            nodes_root = ProjectTreeItem([nodes_text, str(nodes_count)], stage_item)
            stage_item.appendChild(nodes_root)
            
            # Add node items
            for node_id, node in stage_data['nodes'].items():
                coords = node["coordinates"]
                node_text = f"Node {node_id}: ({coords[0]:.2f}, {coords[1]:.2f}, {coords[2]:.2f})"
                node_item = ProjectTreeItem([node_text, ""], nodes_root)
                nodes_root.appendChild(node_item)
            
            # Add elements category for this stage
            elements_text = f"Elements"
            elements_count = len(stage_data['elements'])
            elements_root = ProjectTreeItem([elements_text, str(elements_count)], stage_item)
            stage_item.appendChild(elements_root)
            
            # Add element items
            for element_id, element in stage_data['elements'].items():
                element_text = f"Element {element_id}: {element['type']}"
                element_item = ProjectTreeItem([element_text, ""], elements_root)
                elements_root.appendChild(element_item)
            
            # Add materials category for this stage
            materials_text = f"Materials"
            materials_count = len(stage_data['materials'])
            materials_root = ProjectTreeItem([materials_text, str(materials_count)], stage_item)
            stage_item.appendChild(materials_root)
            
            # Add material items
            for material_id, material in stage_data['materials'].items():
                material_text = f"Material {material_id}: {material['type']}"
                material_item = ProjectTreeItem([material_text, ""], materials_root)
                materials_root.appendChild(material_item)
            
            # Add sections category for this stage
            sections_text = f"Sections"
            sections_count = len(stage_data['sections'])
            sections_root = ProjectTreeItem([sections_text, str(sections_count)], stage_item)
            stage_item.appendChild(sections_root)
            
            # Add section items
            for section_id, section in stage_data['sections'].items():
                section_text = f"Section {section_id}: {section['type']}"
                section_item = ProjectTreeItem([section_text, ""], sections_root)
                sections_root.appendChild(section_item)
            
            # Add constraints category for this stage
            constraints_text = f"Constraints"
            constraints_count = len(stage_data['constraints'])
            constraints_root = ProjectTreeItem([constraints_text, str(constraints_count)], stage_item)
            stage_item.appendChild(constraints_root)
            
            # Add constraint items
            for constraint_id, constraint in stage_data['constraints'].items():
                constraint_text = f"Constraint {constraint_id}: {constraint['type']}"
                constraint_item = ProjectTreeItem([constraint_text, ""], constraints_root)
                constraints_root.appendChild(constraint_item)
            
            # Add transformations category for this stage
            transformations_text = f"Transformations"
            transformations_count = len(stage_data['transformations'])
            transformations_root = ProjectTreeItem([transformations_text, str(transformations_count)], stage_item)
            stage_item.appendChild(transformations_root)
            
            # Add transformation items
            for transformation_id, transformation in stage_data['transformations'].items():
                transformation_text = f"Transformation {transformation_id}: {transformation['type']}"
                transformation_item = ProjectTreeItem([transformation_text, ""], transformations_root)
                transformations_root.appendChild(transformation_item)
            
            # Add timeseries category for this stage
            timeseries_text = f"Timeseries"
            timeseries_count = len(stage_data['timeseries'])
            timeseries_root = ProjectTreeItem([timeseries_text, str(timeseries_count)], stage_item)
            stage_item.appendChild(timeseries_root)
            
            # Add timeseries items
            for timeseries_id, timeseries in stage_data['timeseries'].items():
                timeseries_text = f"Timeseries {timeseries_id}: {timeseries['type']}"
                timeseries_item = ProjectTreeItem([timeseries_text, ""], timeseries_root)
                timeseries_root.appendChild(timeseries_item)
            
            # Add patterns category for this stage
            patterns_text = f"Patterns"
            patterns_count = len(stage_data['patterns'])
            patterns_root = ProjectTreeItem([patterns_text, str(patterns_count)], stage_item)
            stage_item.appendChild(patterns_root)
            
            # Add pattern items
            for pattern_id, pattern in stage_data['patterns'].items():
                pattern_text = f"Pattern {pattern_id}: {pattern['type']}"
                pattern_item = ProjectTreeItem([pattern_text, ""], patterns_root)
                patterns_root.appendChild(pattern_item)
            
            # Add recorders category for this stage
            recorders_text = f"Recorders"
            recorders_count = len(stage_data['recorders'])
            recorders_root = ProjectTreeItem([recorders_text, str(recorders_count)], stage_item)
            stage_item.appendChild(recorders_root)
            
            # Add recorder items
            for recorder_id, recorder in stage_data['recorders'].items():
                recorder_text = f"Recorder {recorder_id}: {recorder['type']}"
                recorder_item = ProjectTreeItem([recorder_text, ""], recorders_root)
                recorders_root.appendChild(recorder_item)
            
            # Add boundary conditions category for this stage
            bcs_text = f"Boundary Conditions"
            bcs_count = len(stage_data['boundary_conditions'])
            bcs_root = ProjectTreeItem([bcs_text, str(bcs_count)], stage_item)
            stage_item.appendChild(bcs_root)
            
            # Add boundary condition items
            for bc_id, bc in stage_data['boundary_conditions'].items():
                node_id = bc.get("node", "")
                dofs = bc.get("dofs", [])
                dof_str = ", ".join([str(d) for d in dofs]) if dofs else "None"
                bc_text = f"BC {bc_id}: Node {node_id} (DOFs: {dof_str})"
                bc_item = ProjectTreeItem([bc_text, ""], bcs_root)
                bcs_root.appendChild(bc_item)
            
            # Add load category for this stage
            loads_text = f"Loads"
            loads_count = len(stage_data['loads'])
            loads_root = ProjectTreeItem([loads_text, str(loads_count)], stage_item)
            stage_item.appendChild(loads_root)
            
            # Add load items
            for load_id, load in stage_data['loads'].items():
                load_type = load.get("type", "")
                target_id = load.get("target", "")
                dofs = load.get("dofs", [])
                values = load.get("values", [])
                
                # Format values for display (limit decimal places)
                formatted_values = []
                for val in values:
                    if isinstance(val, (int, float)):
                        formatted_values.append(f"{val:.2f}")
                    else:
                        formatted_values.append(str(val))
                
                value_str = ", ".join(formatted_values) if formatted_values else "None"
                load_text = f"Load {load_id}: {load_type} on Node {target_id} ({value_str})"
                load_item = ProjectTreeItem([load_text, ""], loads_root)
                loads_root.appendChild(load_item)
        
        # Add analysis category if has file path and it's HDF5
        if project.file_path and (project.file_path.lower().endswith('.h5') or 
                                 project.file_path.lower().endswith('.hdf5')):
            # Get analyses list
            analyses = project.get_analysis_results()
            
            if analyses:
                analysis_root = ProjectTreeItem(["Analysis Results", str(len(analyses))], project_root)
                project_root.appendChild(analysis_root)
                
                # Add analysis items
                for analysis in analyses:
                    analysis_id = analysis['id']
                    timestamp = analysis.get('timestamp', '')
                    if timestamp:
                        timestamp = timestamp.split('T')[0]  # Get just the date part
                        
                    analysis_text = f"Analysis {analysis_id}"
                    if timestamp:
                        analysis_text += f" ({timestamp})"
                        
                    analysis_item = ProjectTreeItem([analysis_text, ""], analysis_root)
                    analysis_root.appendChild(analysis_item)
        
        self.endResetModel()


class ModelExplorer:
    """Model explorer panel"""
    
    def __init__(self, tree_view):
        """Initialize with a tree view"""
        self.tree_view = tree_view
        
        # Create tree model
        self.tree_model = ModelExplorerTreeModel()
        self.tree_view.setModel(self.tree_model)
        
        # Configure tree view
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setAnimated(True)
        
        # Connect selection changed signal
        self.tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # Add context menu support
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        
        # To prevent auto-collapse on context menu
        self.last_expanded_state = {}
        
        # Keep reference to the current project
        self.current_project = None
    
    def show_context_menu(self, position):
        """Show context menu for tree view items"""
        # Get the index at the position
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return
        
        # Save current expanded state
        if index.isValid():
            self.last_expanded_state[index] = self.tree_view.isExpanded(index)
        
        # Get item text and parent 
        item = index.internalPointer()
        item_text = item.data(0)
        parent_item = item.parent()
        
        # Create context menu
        context_menu = QMenu(self.tree_view)
        
        # Check if this is a top-level item (project name) or its child
        is_top_level = parent_item == self.tree_model.root_item
        
        # Check if this is the "Model" item
        is_model = False
        if not is_top_level and parent_item.parent() == self.tree_model.root_item:
            if item_text == "Model":
                is_model = True
        
        # Check if this is the "Stages" category
        is_stages_category = False
        if not is_top_level and not is_model:
            if parent_item.data(0) == "Model" and item_text.startswith("Stages"):
                is_stages_category = True
                
        # Check if this is a specific stage
        is_stage = False
        stage_id = None
        if not is_top_level and not is_model and not is_stages_category:
            if parent_item.data(0).startswith("Stages") and item_text.startswith("Stage "):
                is_stage = True
                # Extract stage ID from text like "Stage 1: Initial Stage"
                try:
                    stage_id = int(item_text.split(':')[0].replace('Stage', '').strip())
                except (ValueError, IndexError):
                    stage_id = None
                    
        # Check if this is a category under a stage (Nodes, Elements, etc.)
        is_stage_category = False
        if not is_top_level and not is_model and not is_stages_category and not is_stage:
            if parent_item.data(0).startswith("Stage "):
                is_stage_category = True
                # Extract stage ID from parent text like "Stage 1: Initial Stage"
                try:
                    stage_id = int(parent_item.data(0).split(':')[0].replace('Stage', '').strip())
                except (ValueError, IndexError):
                    stage_id = None
        
        # Check if this is an entity under a stage category (node, element, etc.)
        is_stage_entity = False
        entity_type = None
        entity_id = None
        if not is_top_level and not is_model and not is_stages_category and not is_stage and not is_stage_category:
            grandparent = parent_item.parent()
            if grandparent and grandparent.data(0).startswith("Stage "):
                is_stage_entity = True
                # Extract stage ID from grandparent text like "Stage 1: Initial Stage"
                try:
                    stage_id = int(grandparent.data(0).split(':')[0].replace('Stage', '').strip())
                except (ValueError, IndexError):
                    stage_id = None
                
                # Determine what type of entity this is by examining parents
                entity_type = parent_item.data(0).split(' ')[0]  # Extract "Nodes" from "Nodes 5"
                
                # Extract ID based on item text format
                if entity_type == "Nodes":
                    # Format: "Node 1: (0.00, 0.00, 0.00)"
                    parts = item_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Node":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "node"  # Convert to singular
                elif entity_type == "Elements":
                    # Format: "Element 1: truss"
                    parts = item_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Element":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "element"  # Convert to singular
                elif entity_type == "Materials":
                    # Format: "Material 1: Steel"
                    parts = item_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Material":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "material"  # Convert to singular
                elif entity_type == "Sections":
                    # Format: "Section 1: WF"
                    parts = item_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Section":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "section"  # Convert to singular
                elif entity_type == "Constraints":
                    # Format: "Constraint 1: equalDOF" 
                    parts = item_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Constraint":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "constraint"  # Convert to singular
                elif entity_type == "Boundary":
                    # Format: "BC 1: Node 2 (DOFs: 1, 2, 3)"
                    parts = item_text.split(':')
                    if len(parts) > 0 and parts[0].strip().startswith("BC "):
                        entity_id = parts[0].strip().replace("BC ", "")
                        entity_type = "boundary_condition"
                elif entity_type == "Loads":
                    # Format: "Load 1: nodeLoad on Node 3 (10.00, 0.00, -20.00)"
                    parts = item_text.split(':')
                    if len(parts) > 0 and parts[0].strip().startswith("Load "):
                        entity_id = parts[0].strip().replace("Load ", "")
                        entity_type = "load"
                elif entity_type == "Recorders":
                    # Format: "Recorder 1: Node"
                    parts = item_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Recorder":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "recorder"  # Convert to singular
                elif entity_type == "Transformations":
                    # Format: "Transformation 1: Linear"
                    parts = item_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Transformation":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "transformation"  # Convert to singular
                elif entity_type == "Timeseries":
                    # Format: "Timeseries 1: Linear"
                    parts = item_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Timeseries":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "timeseries"  # Convert to singular
                elif entity_type == "Patterns":
                    # Format: "Pattern 1: Plain"
                    parts = item_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Pattern":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "pattern"  # Convert to singular
        
        # Add appropriate actions based on the type of item
        if is_top_level:
            # Top level item (project name) - no actions
            pass
        elif is_model:
            # "Model" item - allow deleting all contents
            delete_all_action = QAction("Delete All Model Contents", self.tree_view)
            delete_all_action.triggered.connect(lambda checked=False: self.delete_category_items("Model"))
            context_menu.addAction(delete_all_action)
        elif is_stages_category:
            # "Stages" category - allow adding a new stage
            add_stage_action = QAction("Add New Stage", self.tree_view)
            add_stage_action.triggered.connect(self.add_new_stage)
            context_menu.addAction(add_stage_action)
        elif is_stage:
            # Stage item - allow propagating to a new stage or deleting this stage
            
            # Don't allow deleting stage 0
            if stage_id != 0:
                delete_stage_action = QAction(f"Delete Stage {stage_id}", self.tree_view)
                delete_stage_action.triggered.connect(lambda checked=False, sid=stage_id: self.delete_stage(sid))
                context_menu.addAction(delete_stage_action)
            
            # Allow propagating to a new stage
            propagate_stage_action = QAction(f"Propagate Stage to New Stage", self.tree_view)
            propagate_stage_action.triggered.connect(lambda checked=False, sid=stage_id: self.propagate_stage_to_new(sid))
            context_menu.addAction(propagate_stage_action)
            
        elif is_stage_category or is_stage_entity:
            # Category under a stage - allow actions specific to that category
            if is_stage_category:
                category_text = item_text.split(' ')[0]  # Extract "Nodes" from "Nodes 5"
                # Allow deletion for all component categories
                all_categories = ["Nodes", "Elements", "Materials", "Sections", "Constraints", 
                                "Boundary", "Loads", "Recorders", "Transformations", 
                                "Timeseries", "Patterns"]
                if category_text in all_categories:
                    delete_all_action = QAction(f"Delete All {category_text} from Stage {stage_id}", self.tree_view)
                    delete_all_action.triggered.connect(lambda checked=False, cat=item_text, sid=stage_id: 
                                                       self.delete_category_items_from_stage(cat, sid))
                    context_menu.addAction(delete_all_action)
            
            # Entity under a stage - allow deleting this entity
            if is_stage_entity and entity_id:
                # Create user-friendly type name for display
                display_type = entity_type.rstrip('s')  # "Nodes" -> "Node"
                if display_type == "boundary_condition":
                    display_type = "BC"
                delete_action = QAction(f"Delete {display_type} from Stage {stage_id}", self.tree_view)
                delete_action.triggered.connect(lambda checked=False, t=entity_type, i=entity_id, sid=stage_id: 
                                               self.delete_item_from_stage(t, i, sid))
                context_menu.addAction(delete_action)
        
        # Show context menu if it has any actions
        if not context_menu.isEmpty():
            # Connect signals to maintain expansion state
            context_menu.aboutToShow.connect(lambda: self._preserve_expansion_state(index))
            context_menu.aboutToHide.connect(lambda: self._restore_expansion_state(index))
            context_menu.exec_(self.tree_view.viewport().mapToGlobal(position))
    
    def _preserve_expansion_state(self, index):
        """Preserve the expansion state before showing context menu"""
        if index.isValid():
            self.last_expanded_state[index] = self.tree_view.isExpanded(index)
    
    def _restore_expansion_state(self, index):
        """Restore the expansion state after context menu is closed"""
        if index.isValid() and index in self.last_expanded_state:
            self.tree_view.setExpanded(index, self.last_expanded_state[index])
    
    def delete_item(self, entity_type, entity_id):
        """Delete a specific entity"""
        # This will be implemented in the parent application
        # Signal to the parent application that we want to delete an item
        if hasattr(self, 'delete_callback') and self.delete_callback:
            self.delete_callback(entity_type, entity_id)
    
    def delete_item_from_stage(self, entity_type, entity_id, stage_id):
        """Delete a specific entity from a stage"""
        # This will be implemented in the parent application
        # Signal to the parent application that we want to delete an item from a stage
        if hasattr(self, 'delete_item_from_stage_callback') and self.delete_item_from_stage_callback:
            self.delete_item_from_stage_callback(entity_type, entity_id, stage_id)
    
    def delete_category_items(self, category_text):
        """Delete all items in a category"""
        # This will be implemented in the parent application
        # Signal to the parent application that we want to delete all items in a category
        if hasattr(self, 'delete_category_callback') and self.delete_category_callback:
            self.delete_category_callback(category_text)
            
    def delete_category_items_from_stage(self, category_text, stage_id):
        """Delete all items in a category from a specific stage"""
        # This will be implemented in the parent application
        # Signal to the parent application that we want to delete all items in a category from a stage
        if hasattr(self, 'delete_category_from_stage_callback') and self.delete_category_from_stage_callback:
            self.delete_category_from_stage_callback(category_text, stage_id)
            
    def add_new_stage(self):
        """Add a new stage"""
        # Signal to the parent application that we want to add a new stage
        if hasattr(self, 'add_stage_callback') and self.add_stage_callback:
            self.add_stage_callback()
            
    def delete_stage(self, stage_id):
        """Delete a stage"""
        # Signal to the parent application that we want to delete a stage
        if hasattr(self, 'delete_stage_callback') and self.delete_stage_callback:
            self.delete_stage_callback(stage_id)
            
    def propagate_stage_to_new(self, source_stage_id):
        """Propagate a stage to a new stage"""
        # Signal to the parent application that we want to propagate a stage to a new stage
        if hasattr(self, 'propagate_stage_callback') and self.propagate_stage_callback:
            self.propagate_stage_callback(source_stage_id)
    
    def set_delete_callbacks(self, delete_callback, delete_category_callback, delete_item_from_stage_callback=None, 
                           delete_category_from_stage_callback=None, add_stage_callback=None, 
                           delete_stage_callback=None, propagate_stage_callback=None):
        """Set callbacks for deletion and stage management actions"""
        self.delete_callback = delete_callback
        self.delete_category_callback = delete_category_callback
        self.delete_item_from_stage_callback = delete_item_from_stage_callback
        self.delete_category_from_stage_callback = delete_category_from_stage_callback
        self.add_stage_callback = add_stage_callback
        self.delete_stage_callback = delete_stage_callback
        self.propagate_stage_callback = propagate_stage_callback
    
    def update_model(self, project):
        """Update the model with new project data"""
        # Save reference to current project
        self.current_project = project
        
        # Update tree model
        self.tree_model.setupModelData(project)
        
        # Expand the first few levels by default
        self.tree_view.expandToDepth(1)
        
        # Ensure columns are properly sized
        self.tree_view.resizeColumnToContents(0)
        # Make sure the main column is at least 250px wide
        if self.tree_view.columnWidth(0) < 350:
            self.tree_view.setColumnWidth(0, 350)

    def on_selection_changed(self, selected, deselected):
        """Handle selection changes in the tree view"""
        indexes = selected.indexes()
        if indexes:
            # Get the selected item's text
            item = indexes[0].internalPointer()
            selected_text = item.data(0)
            
            # Update the model's selected item
            self.tree_model.selected_item_text = selected_text
            
            # Force a redraw of the tree view
            self.tree_model.layoutChanged.emit()
            
            # Check if this is an entity that can be selected in the scene
            parent_item = item.parent()
            
            # Skip if this is a top-level item (project name) or its direct child
            is_top_level = parent_item == self.tree_model.root_item
            is_model = False
            if not is_top_level and parent_item.parent() == self.tree_model.root_item:
                if selected_text == "Model":
                    is_model = True
            
            # Check if this is a stage-related item
            is_stage_parent = False
            is_stage = False
            stage_id = None
            if not is_top_level and not is_model:
                # Check if parent is "Model" and this is the "Stages" category
                if parent_item.data(0) == "Model" and selected_text.startswith("Stages"):
                    is_stage_parent = True
                
                # Check if parent is "Stages" and this is a stage item
                elif parent_item.data(0) == "Stages" and selected_text.startswith("Stage "):
                    is_stage = True
                    # Extract stage ID from text like "Stage 1: Initial Stage"
                    try:
                        stage_id = int(selected_text.split(':')[0].replace('Stage', '').strip())
                    except (ValueError, IndexError):
                        stage_id = None
            
            # Check if this is a component category under a stage (Nodes, Elements, etc.)
            is_stage_category = False
            stage_category_parent = None
            if not is_top_level and not is_model and not is_stage_parent and not is_stage:
                # If parent is a stage, this is a category like "Nodes" under that stage
                if parent_item.data(0).startswith("Stage "):
                    is_stage_category = True
                    stage_category_parent = parent_item
                    # Extract stage ID from text like "Stage 1: Initial Stage"
                    try:
                        stage_id = int(parent_item.data(0).split(':')[0].replace('Stage', '').strip())
                    except (ValueError, IndexError):
                        stage_id = None
            
            # Skip if this is a category item
            is_entity = False
            entity_type = None
            entity_id = None
            
            # Check if item is an actual entity (node, element, etc.)
            if not is_top_level and not is_model and not is_stage_parent and not is_stage and not is_stage_category:
                # The parent might be a category under a stage
                grandparent = parent_item.parent()
                is_under_stage = False
                
                if grandparent and grandparent.data(0).startswith("Stage "):
                    # We're under a stage's category - extract stage ID
                    is_under_stage = True
                    try:
                        stage_id = int(grandparent.data(0).split(':')[0].replace('Stage', '').strip())
                    except (ValueError, IndexError):
                        stage_id = None
                
                # Determine entity type from parent
                entity_type = parent_item.data(0).split(' ')[0]  # Extract "Nodes" from "Nodes 5"
                
                # Extract ID based on item text format
                if entity_type == "Nodes":
                    # Format: "Node 1: (0.00, 0.00, 0.00)"
                    parts = selected_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Node":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "node"  # Convert to singular
                elif entity_type == "Elements":
                    # Format: "Element 1: truss"
                    parts = selected_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Element":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "element"  # Convert to singular
                elif entity_type == "Materials":
                    # Format: "Material 1: Steel"
                    parts = selected_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Material":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "material"  # Convert to singular
                elif entity_type == "Sections":
                    # Format: "Section 1: WF" 
                    parts = selected_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Section":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "section"
                elif entity_type == "Constraints":
                    # Format: "Constraint 1: equalDOF"
                    parts = selected_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Constraint":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "constraint"
                elif entity_type == "Boundary":
                    # Format: "BC 1: Node 2 (DOFs: 1, 2, 3)"
                    parts = selected_text.split(':')
                    if len(parts) > 0 and parts[0].strip().startswith("BC "):
                        entity_id = parts[0].strip().replace("BC ", "")
                        entity_type = "boundary_condition"
                elif entity_type == "Loads":
                    # Format: "Load 1: nodeLoad on Node 3 (10.00, 0.00, -20.00)"
                    parts = selected_text.split(':')
                    if len(parts) > 0 and parts[0].strip().startswith("Load "):
                        entity_id = parts[0].strip().replace("Load ", "")
                        entity_type = "load"
                elif entity_type == "Recorders":
                    # Format: "Recorder 1: Node"
                    parts = selected_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Recorder":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "recorder"
                elif entity_type == "Transformations":
                    # Format: "Transformation 1: Linear"
                    parts = selected_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Transformation":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "transformation"
                elif entity_type == "Timeseries":
                    # Format: "Timeseries 1: Linear"
                    parts = selected_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Timeseries":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "timeseries"
                elif entity_type == "Patterns":
                    # Format: "Pattern 1: Plain"
                    parts = selected_text.split(' ')
                    if len(parts) > 1 and parts[0] == "Pattern":
                        entity_id = parts[1].rstrip(':')
                        entity_type = "pattern"
                
                # If we have a valid entity type and ID, mark this as an entity
                if entity_id and entity_type:
                    is_entity = True
                
                # If we have a valid entity and a scene selection callback, call it
                if is_entity and entity_id and entity_type in ["node", "element", "material", "section", "constraint", 
                                              "boundary_condition", "load", "recorder", 
                                              "transformation", "timeseries", "pattern"]:
                    if hasattr(self, 'scene_selection_callback') and self.scene_selection_callback:
                        # Pass the stage ID as well if we're under a stage
                        if is_under_stage and stage_id is not None:
                            self.scene_selection_callback(entity_type, entity_id, stage_id)
                        else:
                            # For backward compatibility, use without stage_id
                            self.scene_selection_callback(entity_type, entity_id)

    def set_scene_selection_callback(self, callback):
        """Set a callback to be called when an item is selected in the tree view
        
        The callback will be called with (object_type, object_id, stage_id=None) where:
        - object_type is 'node', 'element', 'material', 'section', 'constraint', 
                         'boundary_condition', 'load', 'recorder', 'transformation',
                         'timeseries', 'pattern'
        - object_id is the ID of the selected object
        - stage_id (optional) is the ID of the stage the object belongs to
        """
        self.scene_selection_callback = callback 
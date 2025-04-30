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
        
        # Add nodes category
        nodes_root = ProjectTreeItem(["Nodes", str(len(project.nodes))], model_root)
        model_root.appendChild(nodes_root)
        
        # Add node items
        for node_id, node in project.nodes.items():
            coords = node["coordinates"]
            node_text = f"Node {node_id}: ({coords[0]:.2f}, {coords[1]:.2f}, {coords[2]:.2f})"
            node_item = ProjectTreeItem([node_text, ""], nodes_root)
            nodes_root.appendChild(node_item)
        
        # Add elements category
        elements_root = ProjectTreeItem(["Elements", str(len(project.elements))], model_root)
        model_root.appendChild(elements_root)
        
        # Add element items
        for element_id, element in project.elements.items():
            element_text = f"Element {element_id}: {element['type']}"
            element_item = ProjectTreeItem([element_text, ""], elements_root)
            elements_root.appendChild(element_item)
        
        # Add materials category
        materials_root = ProjectTreeItem(["Materials", str(len(project.materials))], model_root)
        model_root.appendChild(materials_root)
        
        # Add material items
        for material_id, material in project.materials.items():
            material_text = f"Material {material_id}: {material['type']}"
            material_item = ProjectTreeItem([material_text, ""], materials_root)
            materials_root.appendChild(material_item)
        
        # Add sections category
        sections_root = ProjectTreeItem(["Sections", str(len(project.sections))], model_root)
        model_root.appendChild(sections_root)
        
        # Add section items
        for section_id, section in project.sections.items():
            section_text = f"Section {section_id}: {section['type']}"
            section_item = ProjectTreeItem([section_text, ""], sections_root)
            sections_root.appendChild(section_item)
        
        # Add constraints category
        constraints_root = ProjectTreeItem(["Constraints", str(len(project.constraints))], model_root)
        model_root.appendChild(constraints_root)
        
        # Add constraint items
        for constraint_id, constraint in project.constraints.items():
            constraint_text = f"Constraint {constraint_id}: {constraint['type']}"
            constraint_item = ProjectTreeItem([constraint_text, ""], constraints_root)
            constraints_root.appendChild(constraint_item)
        
        # Add transformations category
        transformations_root = ProjectTreeItem(["Transformations", str(len(project.transformations))], model_root)
        model_root.appendChild(transformations_root)
        
        # Add transformation items
        for transformation_id, transformation in project.transformations.items():
            transformation_text = f"Transformation {transformation_id}: {transformation['type']}"
            transformation_item = ProjectTreeItem([transformation_text, ""], transformations_root)
            transformations_root.appendChild(transformation_item)
        
        # Add timeseries category
        timeseries_root = ProjectTreeItem(["Timeseries", str(len(project.timeseries))], model_root)
        model_root.appendChild(timeseries_root)
        
        # Add timeseries items
        for timeseries_id, timeseries in project.timeseries.items():
            timeseries_text = f"Timeseries {timeseries_id}: {timeseries['type']}"
            timeseries_item = ProjectTreeItem([timeseries_text, ""], timeseries_root)
            timeseries_root.appendChild(timeseries_item)
        
        # Add patterns category
        patterns_root = ProjectTreeItem(["Patterns", str(len(project.patterns))], model_root)
        model_root.appendChild(patterns_root)
        
        # Add pattern items
        for pattern_id, pattern in project.patterns.items():
            pattern_text = f"Pattern {pattern_id}: {pattern['type']}"
            pattern_item = ProjectTreeItem([pattern_text, ""], patterns_root)
            patterns_root.appendChild(pattern_item)
        
        # Add recorders category
        recorders_root = ProjectTreeItem(["Recorders", str(len(project.recorders))], model_root)
        model_root.appendChild(recorders_root)
        
        # Add recorder items
        for recorder_id, recorder in project.recorders.items():
            recorder_text = f"Recorder {recorder_id}: {recorder['type']}"
            recorder_item = ProjectTreeItem([recorder_text, ""], recorders_root)
            recorders_root.appendChild(recorder_item)
        
        # Add boundary conditions category
        bcs_root = ProjectTreeItem(["Boundary Conditions", str(len(project.boundary_conditions))], model_root)
        model_root.appendChild(bcs_root)
        
        # Add boundary condition items
        for bc_id, bc in project.boundary_conditions.items():
            node_id = bc.get("node", "")
            dofs = bc.get("dofs", [])
            dof_str = ", ".join([str(d) for d in dofs]) if dofs else "None"
            bc_text = f"BC {bc_id}: Node {node_id} (DOFs: {dof_str})"
            bc_item = ProjectTreeItem([bc_text, ""], bcs_root)
            bcs_root.appendChild(bc_item)
        
        # Add load category
        loads_root = ProjectTreeItem(["Loads", str(len(project.loads))], model_root)
        model_root.appendChild(loads_root)
        
        # Add load items
        for load_id, load in project.loads.items():
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
        
        # Check if this is a category item (Nodes, Elements, etc)
        is_model_cat = False
        if not is_top_level and not is_model:
            # If parent is "Model", this is a category like "Nodes"
            if parent_item.data(0) == "Model":
                is_model_cat = True
        
        # Add appropriate actions based on the type of item
        if is_top_level:
            # Top level item (project name) - no actions
            pass
        elif is_model:
            # "Model" item - allow deleting all contents
            delete_all_action = QAction("Delete All Model Contents", self.tree_view)
            delete_all_action.triggered.connect(lambda checked=False: self.delete_category_items("Model"))
            context_menu.addAction(delete_all_action)
        elif is_model_cat:
            # Entity category item - allow deleting all items under this category
            category_text = item_text.split(' ')[0]  # Extract "Nodes" from "Nodes 5"
            # Allow deletion for all component categories
            all_categories = ["Nodes", "Elements", "Materials", "Sections", "Constraints", 
                              "Boundary", "Loads", "Recorders", "Transformations", 
                              "Timeseries", "Patterns"]
            if category_text in all_categories:
                delete_all_action = QAction(f"Delete All {category_text}", self.tree_view)
                delete_all_action.triggered.connect(lambda checked=False, cat=item_text: self.delete_category_items(cat))
                context_menu.addAction(delete_all_action)
        else:
            # Individual entity item - allow deleting this item
            # Determine what type of entity this is by examining parents
            entity_type = parent_item.data(0).split(' ')[0]  # Extract "Nodes" from "Nodes 5"
            entity_id = None
            
            # Extract ID based on item text format
            if entity_type == "Nodes":
                # Format: "Node 1: (0.00, 0.00, 0.00)"
                parts = item_text.split(' ')
                if len(parts) > 1 and parts[0] == "Node":
                    entity_id = parts[1].rstrip(':')
            elif entity_type == "Elements":
                # Format: "Element 1: truss"
                parts = item_text.split(' ')
                if len(parts) > 1 and parts[0] == "Element":
                    entity_id = parts[1].rstrip(':')
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
            
            if entity_id:
                # Create user-friendly type name for display
                display_type = entity_type.rstrip('s')  # "Nodes" -> "Node"
                if display_type == "boundary_condition":
                    display_type = "BC"
                delete_action = QAction(f"Delete {display_type}", self.tree_view)
                delete_action.triggered.connect(lambda checked=False, t=entity_type, i=entity_id: self.delete_item(t, i))
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
    
    def delete_category_items(self, category_text):
        """Delete all items in a category"""
        # This will be implemented in the parent application
        # Signal to the parent application that we want to delete all items in a category
        if hasattr(self, 'delete_category_callback') and self.delete_category_callback:
            self.delete_category_callback(category_text)
    
    def set_delete_callbacks(self, delete_callback, delete_category_callback):
        """Set callbacks for deletion actions"""
        self.delete_callback = delete_callback
        self.delete_category_callback = delete_category_callback
    
    def update_model(self, project):
        """Update the model explorer with project data"""
        # Save reference to current project
        self.current_project = project
        
        if project is None:
            self.tree_model.setupModelData(None)
            return
        
        # Update model with project
        self.tree_model.setupModelData(project)
        
        # Expand the model root
        self.tree_view.expandToDepth(1)
        
        # Ensure columns are properly sized
        self.tree_view.resizeColumnToContents(0)
        # Make sure the main column is at least 250px wide
        if self.tree_view.columnWidth(0) < 250:
            self.tree_view.setColumnWidth(0, 250)

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
            
            # Skip if this is a category item (Nodes, Elements, etc.)
            is_model_cat = False
            if not is_top_level and not is_model:
                # If parent is "Model", this is a category like "Nodes"
                if parent_item.data(0) == "Model":
                    is_model_cat = True
            
            # Process actual entity selection
            if not is_top_level and not is_model and not is_model_cat:
                # Determine what type of entity this is by examining its parent
                entity_type = parent_item.data(0).split(' ')[0]  # Extract "Nodes" from "Nodes 5"
                entity_id = None
                
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
                
                # If we have a valid entity type and ID, and a scene selection callback, call it
                if entity_id and entity_type in ["node", "element", "material", "section", "constraint", 
                                              "boundary_condition", "load", "recorder", 
                                              "transformation", "timeseries", "pattern"]:
                    if hasattr(self, 'scene_selection_callback') and self.scene_selection_callback:
                        self.scene_selection_callback(entity_type, entity_id)

    def set_scene_selection_callback(self, callback):
        """Set a callback to be called when an item is selected in the tree view
        
        The callback will be called with (object_type, object_id) where:
        - object_type is 'node', 'element', 'material', 'section', 'constraint', 
                         'boundary_condition', 'load', 'recorder', 'transformation',
                         'timeseries', 'pattern'
        - object_id is the ID of the selected object
        """
        self.scene_selection_callback = callback 
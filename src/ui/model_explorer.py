#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Model Explorer UI components
"""

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QFont
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QToolButton, QButtonGroup, QLabel


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
            if index.column() == 0 and index.parent() == QModelIndex():
                # Bold font for top-level items
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
        
        # Add boundary conditions category
        bcs_root = ProjectTreeItem(["Boundary Conditions", str(len(project.boundary_conditions))], model_root)
        model_root.appendChild(bcs_root)
        
        # Add load category
        loads_root = ProjectTreeItem(["Loads", str(len(project.loads))], model_root)
        model_root.appendChild(loads_root)
        
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
        
        # Create filter toolbar for the tree view
        if isinstance(self.tree_view.parent(), QFrame):
            self.create_filter_toolbar(self.tree_view.parent())
        
        # Keep reference to the current project
        self.current_project = None
    
    def create_filter_toolbar(self, parent_widget):
        """Create a toolbar for filtering entities in the model explorer"""
        # Create filter toolbar
        self.filter_frame = QFrame(parent_widget)
        self.filter_frame.setObjectName("filterToolbar")
        self.filter_frame.setMaximumHeight(40)
        self.filter_frame.setStyleSheet("""
            #filterToolbar {
                background-color: #F5F5F5;
                border-bottom: 1px solid #CCCCCC;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 3px;
                min-width: 50px;
            }
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border: 1px solid #CCCCCC;
            }
            QToolButton:checked {
                background-color: rgba(0, 0, 0, 0.15);
                border: 1px solid #BBBBBB;
            }
        """)
        
        # Create layout for the filter toolbar
        self.filter_layout = QHBoxLayout(self.filter_frame)
        self.filter_layout.setContentsMargins(5, 0, 5, 0)
        
        # Create filter label
        self.filter_label = QLabel("Show:")
        self.filter_layout.addWidget(self.filter_label)
        
        # Create filter buttons
        self.btn_show_all = QToolButton()
        self.btn_show_all.setText("All")
        self.btn_show_all.setToolTip("Show all entities")
        self.btn_show_all.setCheckable(True)
        self.btn_show_all.setChecked(True)  # Default: show all
        
        self.btn_show_nodes = QToolButton()
        self.btn_show_nodes.setText("Nodes")
        self.btn_show_nodes.setToolTip("Show only nodes")
        self.btn_show_nodes.setCheckable(True)
        
        self.btn_show_elements = QToolButton()
        self.btn_show_elements.setText("Elements")
        self.btn_show_elements.setToolTip("Show only elements")
        self.btn_show_elements.setCheckable(True)
        
        self.btn_show_materials = QToolButton()
        self.btn_show_materials.setText("Materials")
        self.btn_show_materials.setToolTip("Show only materials")
        self.btn_show_materials.setCheckable(True)
        
        self.btn_show_bcs = QToolButton()
        self.btn_show_bcs.setText("BCs")
        self.btn_show_bcs.setToolTip("Show only boundary conditions")
        self.btn_show_bcs.setCheckable(True)
        
        # Add buttons to layout
        self.filter_layout.addWidget(self.btn_show_all)
        self.filter_layout.addWidget(self.btn_show_nodes)
        self.filter_layout.addWidget(self.btn_show_elements)
        self.filter_layout.addWidget(self.btn_show_materials)
        self.filter_layout.addWidget(self.btn_show_bcs)
        self.filter_layout.addStretch()
        
        # Create button group to ensure only one filter is active
        self.filter_button_group = QButtonGroup(self.filter_frame)
        self.filter_button_group.addButton(self.btn_show_all)
        self.filter_button_group.addButton(self.btn_show_nodes)
        self.filter_button_group.addButton(self.btn_show_elements)
        self.filter_button_group.addButton(self.btn_show_materials)
        self.filter_button_group.addButton(self.btn_show_bcs)
        
        # Connect signals
        self.btn_show_all.clicked.connect(lambda: self.filter_by_entity_type(None))
        self.btn_show_nodes.clicked.connect(lambda: self.filter_by_entity_type("Nodes"))
        self.btn_show_elements.clicked.connect(lambda: self.filter_by_entity_type("Elements"))
        self.btn_show_materials.clicked.connect(lambda: self.filter_by_entity_type("Materials"))
        self.btn_show_bcs.clicked.connect(lambda: self.filter_by_entity_type("Boundary Conditions"))
        
        # Add filter toolbar to parent widget layout
        if isinstance(parent_widget.layout(), QVBoxLayout):
            # Insert at the beginning of the layout, before the tree view
            parent_widget.layout().insertWidget(0, self.filter_frame)
    
    def filter_by_entity_type(self, entity_type):
        """Filter the model explorer to show only entities of the specified type"""
        # Reapply the model data with filtering
        if self.current_project:
            self.update_model(self.current_project, filter_type=entity_type)
        
    def update_model(self, project, filter_type=None):
        """Update the model explorer with project data, optionally filtering by entity type"""
        # Save reference to current project
        self.current_project = project
        
        if project is None:
            self.tree_model.setupModelData(None)
            return
        
        # Create a temporary project view with filtered entities if needed
        if filter_type is None:
            # No filtering, just use the project as is
            self.tree_model.setupModelData(project)
        else:
            # Create a filtered view of the project
            from copy import copy
            filtered_project = copy(project)
            
            # Clear all entity collections
            filtered_project.nodes = {}
            filtered_project.elements = {}
            filtered_project.materials = {}
            filtered_project.boundary_conditions = {}
            filtered_project.loads = {}
            
            # Only populate the requested entity type
            if filter_type == "Nodes":
                filtered_project.nodes = project.nodes
            elif filter_type == "Elements":
                filtered_project.elements = project.elements
            elif filter_type == "Materials":
                filtered_project.materials = project.materials
            elif filter_type == "Boundary Conditions":
                filtered_project.boundary_conditions = project.boundary_conditions
            elif filter_type == "Loads":
                filtered_project.loads = project.loads
            
            # Update model with filtered project
            self.tree_model.setupModelData(filtered_project)
        
        # Expand the model root
        self.tree_view.expandToDepth(1)
        
        # Ensure columns are properly sized
        self.tree_view.resizeColumnToContents(0)
        # Make sure the main column is at least 250px wide
        if self.tree_view.columnWidth(0) < 250:
            self.tree_view.setColumnWidth(0, 250) 
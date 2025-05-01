"""
Dock panel widgets for Modsee.
"""

import logging
from typing import Optional, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem,
    QPushButton, QSplitter, QTextEdit, QTableWidget, QTableWidgetItem, 
    QHeaderView, QComboBox, QLineEdit, QFormLayout, QAbstractItemView, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor, QBrush, QAction

logger = logging.getLogger('modsee.ui.dock_widgets')


class ModelExplorerWidget(QWidget):
    """
    Widget for the Model Explorer dock panel.
    Displays a tree view of the model components.
    """
    
    def __init__(self, model_manager: Optional[Any] = None):
        """
        Initialize the Model Explorer widget.
        
        Args:
            model_manager: The model manager instance.
        """
        super().__init__()
        
        self.model_manager = model_manager
        self.category_items = {}
        
        self._init_ui()
        self._connect_signals()
        
        logger.debug("ModelExplorerWidget initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        # Create tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name", "Type", "ID"])
        self.tree_widget.setColumnWidth(0, 160)
        self.tree_widget.setColumnWidth(1, 100)
        self.tree_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.layout.addWidget(self.tree_widget)
        
        # Create filter line
        self.filter_layout = QHBoxLayout()
        self.filter_label = QLabel("Filter:")
        self.filter_layout.addWidget(self.filter_label)
        
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter by name or type")
        self.filter_edit.textChanged.connect(self._apply_filter)
        self.filter_layout.addWidget(self.filter_edit)
        
        self.layout.addLayout(self.filter_layout)
        
        # Create buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self._on_add)
        self.button_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self._on_remove)
        self.button_layout.addWidget(self.remove_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh)
        self.button_layout.addWidget(self.refresh_button)
        
        self.layout.addLayout(self.button_layout)
        
        # Initialize tree
        self._create_category_items()
    
    def _connect_signals(self):
        """Connect signals to slots."""
        if hasattr(self.model_manager, 'model_changed_signal'):
            self.model_manager.model_changed_signal.connect(self.refresh)
        if hasattr(self.model_manager, 'selection_changed_signal'):
            self.model_manager.selection_changed_signal.connect(self._update_selection_from_model)
    
    def _create_category_items(self):
        """Create root category items."""
        self.tree_widget.clear()
        
        # Create category items
        categories = [
            ("Nodes", "Group", ""),
            ("Elements", "Group", ""),
            ("Materials", "Group", ""),
            ("Sections", "Group", ""),
            ("Boundary Conditions", "Group", ""),
            ("Loads", "Group", "")
        ]
        
        for name, obj_type, obj_id in categories:
            item = QTreeWidgetItem(self.tree_widget, [name, obj_type, obj_id])
            # Set category style
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
            self.category_items[name.lower()] = item
        
        # Expand by default
        for item in self.category_items.values():
            item.setExpanded(True)
    
    def refresh(self):
        """Refresh the tree widget with current model data."""
        if not self.model_manager:
            return
            
        # Clear existing items but keep categories
        for category_item in self.category_items.values():
            category_item.takeChildren()
        
        # Add nodes
        if hasattr(self.model_manager, 'nodes'):
            self._populate_nodes()
            
        # Add elements
        if hasattr(self.model_manager, 'elements'):
            self._populate_elements()
            
        # Add materials
        if hasattr(self.model_manager, 'materials'):
            self._populate_materials()
            
        # Add sections
        if hasattr(self.model_manager, 'sections'):
            self._populate_sections()
        
        # Update selection highlights
        self._update_selection_from_model()
    
    def _populate_nodes(self):
        """Populate the tree with nodes from the model."""
        nodes_item = self.category_items["nodes"]
        
        # Handle different model_manager implementations
        if hasattr(self.model_manager, 'nodes'):
            # Registry-based implementation
            for node_id, node in enumerate(self.model_manager.nodes.all(), 1):
                node_name = node.metadata.name if hasattr(node, 'metadata') else f"Node {node_id}"
                node_item = QTreeWidgetItem(nodes_item, [node_name, "Node", str(node_id)])
                node_item.setData(0, Qt.ItemDataRole.UserRole, ("node", node_id))
        elif hasattr(self.model_manager, '_nodes'):
            # Dictionary-based implementation
            for node_id, node in self.model_manager._nodes.items():
                node_item = QTreeWidgetItem(nodes_item, [f"Node {node_id}", "Node", str(node_id)])
                node_item.setData(0, Qt.ItemDataRole.UserRole, ("node", node_id))
    
    def _populate_elements(self):
        """Populate the tree with elements from the model."""
        elements_item = self.category_items["elements"]
        
        # Handle different model_manager implementations
        if hasattr(self.model_manager, 'elements'):
            # Registry-based implementation
            for element_id, element in enumerate(self.model_manager.elements.all(), 1):
                element_type = element.get_element_type() if hasattr(element, 'get_element_type') else "Element"
                element_name = element.metadata.name if hasattr(element, 'metadata') else f"Element {element_id}"
                element_item = QTreeWidgetItem(elements_item, [element_name, element_type, str(element_id)])
                element_item.setData(0, Qt.ItemDataRole.UserRole, ("element", element_id))
        elif hasattr(self.model_manager, '_elements'):
            # Dictionary-based implementation
            for element_id, element in self.model_manager._elements.items():
                element_item = QTreeWidgetItem(elements_item, [f"Element {element_id}", "Element", str(element_id)])
                element_item.setData(0, Qt.ItemDataRole.UserRole, ("element", element_id))
    
    def _populate_materials(self):
        """Populate the tree with materials from the model."""
        materials_item = self.category_items["materials"]
        
        # Handle different model_manager implementations
        if hasattr(self.model_manager, 'materials'):
            # Registry-based implementation
            for material_id, material in enumerate(self.model_manager.materials.all(), 1):
                material_name = material.metadata.name if hasattr(material, 'metadata') else f"Material {material_id}"
                material_item = QTreeWidgetItem(materials_item, [material_name, "Material", str(material_id)])
                material_item.setData(0, Qt.ItemDataRole.UserRole, ("material", material_id))
        elif hasattr(self.model_manager, '_materials'):
            # Dictionary-based implementation
            for material_id, material in self.model_manager._materials.items():
                material_item = QTreeWidgetItem(materials_item, [f"Material {material_id}", "Material", str(material_id)])
                material_item.setData(0, Qt.ItemDataRole.UserRole, ("material", material_id))
    
    def _populate_sections(self):
        """Populate the tree with sections from the model."""
        sections_item = self.category_items["sections"]
        
        # Handle different model_manager implementations
        if hasattr(self.model_manager, 'sections'):
            # Registry-based implementation
            for section_id, section in enumerate(self.model_manager.sections.all(), 1):
                section_name = section.metadata.name if hasattr(section, 'metadata') else f"Section {section_id}"
                section_item = QTreeWidgetItem(sections_item, [section_name, "Section", str(section_id)])
                section_item.setData(0, Qt.ItemDataRole.UserRole, ("section", section_id))
        elif hasattr(self.model_manager, '_sections'):
            # Dictionary-based implementation
            for section_id, section in self.model_manager._sections.items():
                section_item = QTreeWidgetItem(sections_item, [f"Section {section_id}", "Section", str(section_id)])
                section_item.setData(0, Qt.ItemDataRole.UserRole, ("section", section_id))
    
    def _update_selection_from_model(self):
        """Update tree item selection based on model selection."""
        if not self.model_manager:
            return
            
        # Get current selection from model
        if hasattr(self.model_manager, 'get_selection'):
            selection = self.model_manager.get_selection()
        else:
            # No selection mechanism found
            return
            
        # Block signals to prevent selection feedback loop
        self.tree_widget.blockSignals(True)
        
        # Clear current selection
        self.tree_widget.clearSelection()
        
        # Highlight all tree items corresponding to selected objects
        for category_item in self.category_items.values():
            for i in range(category_item.childCount()):
                child = category_item.child(i)
                item_data = child.data(0, Qt.ItemDataRole.UserRole)
                
                if not item_data:
                    continue
                    
                obj_type, obj_id = item_data
                
                # Find corresponding object in model
                obj = None
                if obj_type == "node" and hasattr(self.model_manager, '_nodes'):
                    obj = self.model_manager._nodes.get(obj_id)
                elif obj_type == "element" and hasattr(self.model_manager, '_elements'):
                    obj = self.model_manager._elements.get(obj_id)
                
                # Check if object is selected
                if obj in selection:
                    child.setSelected(True)
                    # Ensure item is visible
                    self.tree_widget.scrollToItem(child)
        
        # Restore signals
        self.tree_widget.blockSignals(False)
    
    def _on_selection_changed(self):
        """Handle tree selection changed event."""
        if not self.model_manager:
            return
            
        # Get selected items
        selected_items = self.tree_widget.selectedItems()
        
        # Don't propagate selection if a category is selected
        for item in selected_items:
            if item in self.category_items.values():
                return
                
        # Convert to model objects
        selected_objs = []
        for item in selected_items:
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if not item_data:
                continue
                
            obj_type, obj_id = item_data
            
            # Find corresponding object in model
            obj = None
            if obj_type == "node" and hasattr(self.model_manager, '_nodes'):
                obj = self.model_manager._nodes.get(obj_id)
            elif obj_type == "element" and hasattr(self.model_manager, '_elements'):
                obj = self.model_manager._elements.get(obj_id)
            
            if obj:
                selected_objs.append(obj)
        
        # Update model selection
        if hasattr(self.model_manager, 'deselect_all') and hasattr(self.model_manager, 'select'):
            # Block signals to prevent selection feedback loop
            model_signals_blocked = False
            if hasattr(self.model_manager, 'blockSignals'):
                self.model_manager.blockSignals(True)
                model_signals_blocked = True
                
            # Update selection in model
            self.model_manager.deselect_all()
            for obj in selected_objs:
                self.model_manager.select(obj)
                
            # Restore signals
            if model_signals_blocked:
                self.model_manager.blockSignals(False)
    
    def _apply_filter(self, filter_text):
        """Apply filter to tree items."""
        # Show all items if filter is empty
        if not filter_text:
            for category_item in self.category_items.values():
                category_item.setHidden(False)
                for i in range(category_item.childCount()):
                    category_item.child(i).setHidden(False)
            return
            
        filter_text = filter_text.lower()
        
        # Check each item
        for category_name, category_item in self.category_items.items():
            visible_children = 0
            
            # Check each child
            for i in range(category_item.childCount()):
                child = category_item.child(i)
                
                # Check if item matches filter
                name = child.text(0).lower()
                type_text = child.text(1).lower()
                id_text = child.text(2).lower()
                
                if (filter_text in name or 
                    filter_text in type_text or 
                    filter_text in id_text):
                    child.setHidden(False)
                    visible_children += 1
                else:
                    child.setHidden(True)
            
            # Hide category if no children are visible
            category_item.setHidden(visible_children == 0)
    
    def _show_context_menu(self, position):
        """Show context menu for tree items."""
        # Get item at position
        item = self.tree_widget.itemAt(position)
        if not item:
            return
            
        # Create context menu
        menu = QMenu(self)
        
        # Add actions based on item type
        if item in self.category_items.values():
            # Category item
            category_name = item.text(0).lower()
            
            # Add 'Add' action
            add_action = QAction(f"Add {category_name[:-1] if category_name.endswith('s') else category_name}", self)
            add_action.triggered.connect(lambda: self._on_add_to_category(category_name))
            menu.addAction(add_action)
            
            # Add 'Expand/Collapse' actions
            if item.isExpanded():
                collapse_action = QAction("Collapse", self)
                collapse_action.triggered.connect(lambda: item.setExpanded(False))
                menu.addAction(collapse_action)
            else:
                expand_action = QAction("Expand", self)
                expand_action.triggered.connect(lambda: item.setExpanded(True))
                menu.addAction(expand_action)
        else:
            # Model object item
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if not item_data:
                return
                
            obj_type, obj_id = item_data
            
            # Add 'Remove' action
            remove_action = QAction(f"Remove {obj_type} {obj_id}", self)
            remove_action.triggered.connect(lambda: self._on_remove_item(obj_type, obj_id))
            menu.addAction(remove_action)
            
            # Add 'Rename' action
            rename_action = QAction("Rename", self)
            rename_action.triggered.connect(lambda: self._on_rename_item(item))
            menu.addAction(rename_action)
        
        # Show menu
        menu.exec(self.tree_widget.viewport().mapToGlobal(position))
    
    def _on_add(self):
        """Handle Add button clicked."""
        # Get selected category item
        selected_items = self.tree_widget.selectedItems()
        if not selected_items:
            # No selection, show add dialog for all types
            self._show_add_dialog()
            return
            
        # Check if a category is selected
        for item in selected_items:
            if item in self.category_items.values():
                category_name = item.text(0).lower()
                self._on_add_to_category(category_name)
                return
        
        # Model object is selected, not implemented yet
        self._show_add_dialog()
    
    def _on_add_to_category(self, category_name):
        """Handle Add to specific category."""
        logger.debug(f"Add to category: {category_name}")
        # Not fully implemented yet, placeholder for future functionality
        QMessageBox.information(
            self, "Add Object", 
            f"Adding {category_name[:-1] if category_name.endswith('s') else category_name} not implemented yet."
        )
    
    def _show_add_dialog(self):
        """Show dialog to add a new object."""
        # Not implemented yet, placeholder for future functionality
        QMessageBox.information(
            self, "Add Object", 
            "Adding objects not implemented yet."
        )
    
    def _on_remove(self):
        """Handle Remove button clicked."""
        # Get selected items
        selected_items = self.tree_widget.selectedItems()
        
        # Filter out category items
        model_items = [item for item in selected_items if item not in self.category_items.values()]
        
        if not model_items:
            return
            
        # Confirm remove
        count = len(model_items)
        reply = QMessageBox.question(
            self, "Remove Objects",
            f"Remove {count} selected object{'s' if count > 1 else ''}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        # Remove objects
        for item in model_items:
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if not item_data:
                continue
                
            obj_type, obj_id = item_data
            self._on_remove_item(obj_type, obj_id)
    
    def _on_remove_item(self, obj_type, obj_id):
        """Remove specific item from model."""
        logger.debug(f"Remove item: {obj_type} {obj_id}")
        
        if not self.model_manager:
            return
            
        # Remove object from model
        if obj_type == "node" and hasattr(self.model_manager, 'remove_node'):
            self.model_manager.remove_node(obj_id)
        elif obj_type == "element" and hasattr(self.model_manager, 'remove_element'):
            self.model_manager.remove_element(obj_id)
        else:
            # Not implemented yet
            QMessageBox.information(
                self, "Remove Object", 
                f"Removing {obj_type} {obj_id} not implemented yet."
            )
    
    def _on_rename_item(self, item):
        """Rename an item."""
        # Not implemented yet, would require appropriate APIs in model objects
        QMessageBox.information(
            self, "Rename Object", 
            "Renaming objects not implemented yet."
        )


class PropertiesWidget(QWidget):
    """
    Widget for the Properties dock panel.
    Displays and allows editing of selected model component properties.
    """
    
    def __init__(self, model_manager: Optional[Any] = None):
        """
        Initialize the Properties widget.
        
        Args:
            model_manager: The model manager instance.
        """
        super().__init__()
        
        self.model_manager = model_manager
        
        self._init_ui()
        
        logger.debug("PropertiesWidget initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        # Create type selector
        self.type_layout = QHBoxLayout()
        self.type_layout.setContentsMargins(0, 0, 0, 0)
        
        self.type_label = QLabel("Type:")
        self.type_layout.addWidget(self.type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Node", "Element", "Material", "Section"])
        self.type_combo.setEnabled(False)  # Not implemented yet
        self.type_layout.addWidget(self.type_combo)
        
        self.layout.addLayout(self.type_layout)
        
        # Create properties form
        self.form_layout = QFormLayout()
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add placeholder properties
        self.id_edit = QLineEdit()
        self.id_edit.setEnabled(False)
        self.form_layout.addRow("ID:", self.id_edit)
        
        self.name_edit = QLineEdit()
        self.name_edit.setEnabled(False)
        self.form_layout.addRow("Name:", self.name_edit)
        
        self.layout.addLayout(self.form_layout)
        
        # Add spacer
        self.layout.addStretch(1)
        
        # Set initial state
        self.set_no_selection()
    
    def set_no_selection(self):
        """Set the widget to show no selection state."""
        self.type_combo.setCurrentIndex(0)
        self.id_edit.setText("")
        self.name_edit.setText("")
        
        # Add placeholder text
        self.id_edit.setPlaceholderText("No selection")
        self.name_edit.setPlaceholderText("No selection")
    
    def refresh(self):
        """Refresh the properties with current selection data."""
        if self.model_manager:
            selection = self.model_manager.get_selection()
            
            if len(selection) == 1:
                # Single selection
                obj = next(iter(selection))
                
                # Determine object type
                if obj in self.model_manager._nodes.values():
                    self.type_combo.setCurrentIndex(0)  # Node
                    obj_id = next((k for k, v in self.model_manager._nodes.items() if v == obj), 0)
                elif obj in self.model_manager._elements.values():
                    self.type_combo.setCurrentIndex(1)  # Element
                    obj_id = next((k for k, v in self.model_manager._elements.items() if v == obj), 0)
                else:
                    obj_id = 0
                
                self.id_edit.setText(str(obj_id))
                self.name_edit.setText(f"Object {obj_id}")
            else:
                # No selection or multiple selection
                self.set_no_selection()


class ConsoleWidget(QWidget):
    """
    Widget for the Console dock panel.
    Displays log messages and command output.
    """
    
    def __init__(self):
        """Initialize the Console widget."""
        super().__init__()
        
        self._init_ui()
        
        logger.debug("ConsoleWidget initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        # Create text edit
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_edit.setStyleSheet("font-family: Consolas, Courier, monospace;")
        self.layout.addWidget(self.text_edit)
        
        # Create buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)
        self.button_layout.addWidget(self.clear_button)
        
        self.button_layout.addStretch(1)
        
        self.layout.addLayout(self.button_layout)
        
        # Add welcome message
        self.log("Welcome to Modsee Console")
        self.log("Ready.")
    
    def log(self, message: str):
        """
        Add a log message to the console.
        
        Args:
            message: The message to log.
        """
        self.text_edit.append(message)
    
    def clear(self):
        """Clear the console."""
        self.text_edit.clear() 
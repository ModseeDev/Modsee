"""
Dock panel widgets for Modsee.
"""

import logging
from typing import Optional, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem,
    QPushButton, QSplitter, QTextEdit, QTableWidget, QTableWidgetItem, 
    QHeaderView, QComboBox, QLineEdit, QFormLayout, QAbstractItemView, QMenu, QMessageBox,
    QScrollArea, QFrame, QCheckBox, QSpinBox, QDoubleSpinBox
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
        self._current_object = None
        self._current_object_id = None
        self._current_object_type = None
        self._form_widgets = {}
        self._updating_form = False
        
        self._init_ui()
        self._connect_signals()
        
        logger.debug("PropertiesWidget initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        # Create type label
        self.type_layout = QHBoxLayout()
        self.type_layout.setContentsMargins(0, 0, 0, 0)
        
        self.type_label = QLabel("Type:")
        self.type_layout.addWidget(self.type_label)
        
        self.type_value = QLabel("None")
        self.type_value.setStyleSheet("font-weight: bold;")
        self.type_layout.addWidget(self.type_value)
        
        self.type_layout.addStretch(1)
        
        # Add apply/reset buttons
        self.apply_button = QPushButton("Apply")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self._on_apply)
        self.type_layout.addWidget(self.apply_button)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.setEnabled(False)
        self.reset_button.clicked.connect(self._on_reset)
        self.type_layout.addWidget(self.reset_button)
        
        self.layout.addLayout(self.type_layout)
        
        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(line)
        
        # Create scrollable area for the form
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)
        self.form_layout.setContentsMargins(0, 4, 0, 4)
        self.form_layout.setSpacing(8)
        
        self.scroll_area.setWidget(self.form_widget)
        self.layout.addWidget(self.scroll_area)
        
        # Add no selection label
        self.no_selection_label = QLabel("No object selected")
        self.no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_selection_label.setStyleSheet("color: #888; padding: 20px;")
        self.layout.addWidget(self.no_selection_label)
        
        # Set initial state
        self.set_no_selection()
    
    def _connect_signals(self):
        """Connect signals to slots."""
        if self.model_manager and hasattr(self.model_manager, 'selection_changed_signal'):
            self.model_manager.selection_changed_signal.connect(self.refresh)
    
    def set_no_selection(self):
        """Set the widget to show no selection state."""
        self._current_object = None
        self._current_object_id = None
        self._current_object_type = None
        
        self.type_value.setText("None")
        self.scroll_area.setVisible(False)
        self.no_selection_label.setVisible(True)
        self.apply_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        
        # Clear form widgets
        self._clear_form()
    
    def _clear_form(self):
        """Clear all form widgets."""
        # Remove all widgets from the form layout
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)
        
        # Clear the widgets dictionary
        self._form_widgets.clear()
    
    def refresh(self):
        """Refresh the properties with current selection data."""
        if not self.model_manager:
            self.set_no_selection()
            return
        
        selection = self.model_manager.get_selection() if hasattr(self.model_manager, 'get_selection') else set()
        
        if len(selection) == 1:
            # Single selection
            obj = next(iter(selection))
            self._display_object_properties(obj)
        else:
            # No selection or multiple selection
            self.set_no_selection()
    
    def _display_object_properties(self, obj):
        """Display properties for the selected object."""
        self._updating_form = True
        
        # Determine object type and ID
        if hasattr(obj, 'get_type'):
            obj_type = obj.get_type().name.capitalize()
        else:
            # Determine from model_manager collections
            if hasattr(self.model_manager, '_nodes') and obj in self.model_manager._nodes.values():
                obj_type = "Node"
                obj_id = next((k for k, v in self.model_manager._nodes.items() if v == obj), 0)
            elif hasattr(self.model_manager, '_elements') and obj in self.model_manager._elements.values():
                obj_type = "Element"
                obj_id = next((k for k, v in self.model_manager._elements.items() if v == obj), 0)
            elif hasattr(self.model_manager, '_materials') and obj in self.model_manager._materials.values():
                obj_type = "Material"
                obj_id = next((k for k, v in self.model_manager._materials.items() if v == obj), 0)
            elif hasattr(self.model_manager, '_sections') and obj in self.model_manager._sections.values():
                obj_type = "Section"
                obj_id = next((k for k, v in self.model_manager._sections.items() if v == obj), 0)
            else:
                obj_type = "Unknown"
                obj_id = 0
        
        # If using ModelObjectType enum
        if hasattr(obj, 'id'):
            obj_id = obj.id
        
        # Update current object info
        self._current_object = obj
        self._current_object_id = obj_id
        self._current_object_type = obj_type
        
        # Update type label
        if hasattr(obj, 'get_element_type'):
            type_name = f"{obj_type}: {obj.get_element_type()}"
        elif hasattr(obj, 'get_material_type'):
            type_name = f"{obj_type}: {obj.get_material_type()}"
        elif hasattr(obj, 'get_section_type'):
            type_name = f"{obj_type}: {obj.get_section_type()}"
        else:
            type_name = obj_type
        
        self.type_value.setText(type_name)
        
        # Clear form and create new fields
        self._clear_form()
        
        # Common fields
        self._add_form_field("ID", obj_id, QLineEdit, editable=False)
        
        # Metadata fields
        if hasattr(obj, 'metadata'):
            self._add_form_section("Metadata")
            self._add_form_field("Name", obj.metadata.name, QLineEdit)
            self._add_form_field("Description", obj.metadata.description or "", QTextEdit)
            
            # Tags field
            if hasattr(obj.metadata, 'tags'):
                tags_str = ", ".join(obj.metadata.tags)
                self._add_form_field("Tags", tags_str, QLineEdit)
        
        # Object-specific fields
        if obj_type == "Node":
            self._create_node_form(obj)
        elif obj_type == "Element":
            self._create_element_form(obj)
        elif obj_type == "Material":
            self._create_material_form(obj)
        elif obj_type == "Section":
            self._create_section_form(obj)
        
        # Show form
        self.scroll_area.setVisible(True)
        self.no_selection_label.setVisible(False)
        self.apply_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        
        self._updating_form = False
    
    def _add_form_section(self, section_name):
        """Add a section header to the form."""
        label = QLabel(section_name)
        label.setStyleSheet("font-weight: bold; color: #444; margin-top: 6px;")
        
        # Add spacer if not the first item
        if self.form_layout.rowCount() > 0:
            spacer = QWidget()
            spacer.setFixedHeight(10)
            self.form_layout.addRow(spacer)
        
        self.form_layout.addRow(label)
        
        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #ccc;")
        self.form_layout.addRow(line)
    
    def _add_form_field(self, label, value, widget_type, 
                      editable=True, validator=None, 
                      options=None, field_name=None):
        """Add a field to the form.
        
        Args:
            label: Label text for the field
            value: Current value of the field
            widget_type: Type of widget to create (QLineEdit, QComboBox, etc.)
            editable: Whether the field should be editable
            validator: Optional validator for the field
            options: Optional list of options for combo box
            field_name: Optional field name (defaults to label)
        """
        # Create widget based on type
        if widget_type == QLineEdit:
            widget = QLineEdit()
            widget.setText(str(value) if value is not None else "")
            widget.setEnabled(editable)
            if validator:
                widget.setValidator(validator)
        
        elif widget_type == QTextEdit:
            widget = QTextEdit()
            widget.setPlainText(str(value) if value is not None else "")
            widget.setEnabled(editable)
            widget.setMaximumHeight(80)
        
        elif widget_type == QCheckBox:
            widget = QCheckBox()
            widget.setChecked(bool(value))
            widget.setEnabled(editable)
        
        elif widget_type == QComboBox:
            widget = QComboBox()
            if options:
                widget.addItems(options)
                if value in options:
                    widget.setCurrentText(value)
                elif isinstance(value, int) and value < len(options):
                    widget.setCurrentIndex(value)
            widget.setEnabled(editable)
        
        elif widget_type == QSpinBox:
            widget = QSpinBox()
            widget.setValue(int(value) if value is not None else 0)
            widget.setEnabled(editable)
        
        elif widget_type == QDoubleSpinBox:
            widget = QDoubleSpinBox()
            widget.setValue(float(value) if value is not None else 0.0)
            widget.setDecimals(6)  # Support for double precision
            widget.setEnabled(editable)
        
        else:
            # Default to QLabel for unsupported types
            widget = QLabel(str(value) if value is not None else "")
            widget.setEnabled(editable)
        
        # Add to form
        self.form_layout.addRow(label + ":", widget)
        
        # Store widget reference
        field_name = field_name or label.lower().replace(" ", "_")
        self._form_widgets[field_name] = widget
        
        # Connect change signals
        if editable:
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(lambda: self._on_field_changed(field_name))
            elif isinstance(widget, QTextEdit):
                widget.textChanged.connect(lambda: self._on_field_changed(field_name))
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(lambda: self._on_field_changed(field_name))
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(lambda: self._on_field_changed(field_name))
            elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                widget.valueChanged.connect(lambda: self._on_field_changed(field_name))
    
    def _on_field_changed(self, field_name):
        """Handle field value changed."""
        if not self._updating_form:
            self.apply_button.setEnabled(True)
            self.reset_button.setEnabled(True)
    
    def _create_node_form(self, node):
        """Create form for node properties."""
        self._add_form_section("Coordinates")
        
        # Node coordinates
        if hasattr(node, 'coordinates'):
            for i, coord in enumerate(node.coordinates):
                dim_name = ["X", "Y", "Z"][i]
                self._add_form_field(
                    f"{dim_name} Coordinate", 
                    coord, 
                    QDoubleSpinBox,
                    field_name=f"coordinate_{i}"
                )
        
        # Mass values if present
        if hasattr(node, 'mass') and node.mass:
            self._add_form_section("Mass")
            for i, mass in enumerate(node.mass):
                dim_name = ["X", "Y", "Z"][i]
                self._add_form_field(
                    f"{dim_name} Mass", 
                    mass, 
                    QDoubleSpinBox,
                    field_name=f"mass_{i}"
                )
        
        # Boundary conditions if present
        if hasattr(node, 'fixed_dofs') and node.fixed_dofs:
            self._add_form_section("Boundary Conditions")
            dof_names = ["X Translation", "X Rotation", "Y Translation", "Y Rotation", "Z Translation", "Z Rotation"]
            for i, fixed in enumerate(node.fixed_dofs):
                if i < len(dof_names):
                    self._add_form_field(
                        dof_names[i], 
                        fixed, 
                        QCheckBox,
                        field_name=f"fixed_dof_{i}"
                    )
    
    def _create_element_form(self, element):
        """Create form for element properties."""
        # Element nodes
        if hasattr(element, 'nodes'):
            self._add_form_section("Connectivity")
            nodes_str = ", ".join(str(node_id) for node_id in element.nodes)
            self._add_form_field("Node IDs", nodes_str, QLineEdit, field_name="nodes")
        
        # Material and section references
        if hasattr(element, 'material_id') and element.material_id is not None:
            self._add_form_field("Material ID", element.material_id, QSpinBox, field_name="material_id")
        
        if hasattr(element, 'section_id') and element.section_id is not None:
            self._add_form_field("Section ID", element.section_id, QSpinBox, field_name="section_id")
        
        # Custom properties
        if hasattr(element, 'properties') and element.properties:
            self._add_form_section("Properties")
            for key, value in element.properties.items():
                if isinstance(value, bool):
                    self._add_form_field(key, value, QCheckBox, field_name=f"prop_{key}")
                elif isinstance(value, int):
                    self._add_form_field(key, value, QSpinBox, field_name=f"prop_{key}")
                elif isinstance(value, float):
                    self._add_form_field(key, value, QDoubleSpinBox, field_name=f"prop_{key}")
                else:
                    self._add_form_field(key, str(value), QLineEdit, field_name=f"prop_{key}")
    
    def _create_material_form(self, material):
        """Create form for material properties."""
        # Material properties
        if hasattr(material, 'properties') and material.properties:
            self._add_form_section("Properties")
            for key, value in material.properties.items():
                if isinstance(value, bool):
                    self._add_form_field(key, value, QCheckBox, field_name=f"prop_{key}")
                elif isinstance(value, int):
                    self._add_form_field(key, value, QSpinBox, field_name=f"prop_{key}")
                elif isinstance(value, float):
                    self._add_form_field(key, value, QDoubleSpinBox, field_name=f"prop_{key}")
                else:
                    self._add_form_field(key, str(value), QLineEdit, field_name=f"prop_{key}")
    
    def _create_section_form(self, section):
        """Create form for section properties."""
        # Material references
        if hasattr(section, 'material_ids') and section.material_ids:
            self._add_form_section("Materials")
            materials_str = ", ".join(str(mat_id) for mat_id in section.material_ids)
            self._add_form_field("Material IDs", materials_str, QLineEdit, field_name="material_ids")
        
        # Section properties
        if hasattr(section, 'properties') and section.properties:
            self._add_form_section("Properties")
            for key, value in section.properties.items():
                if isinstance(value, bool):
                    self._add_form_field(key, value, QCheckBox, field_name=f"prop_{key}")
                elif isinstance(value, int):
                    self._add_form_field(key, value, QSpinBox, field_name=f"prop_{key}")
                elif isinstance(value, float):
                    self._add_form_field(key, value, QDoubleSpinBox, field_name=f"prop_{key}")
                else:
                    self._add_form_field(key, str(value), QLineEdit, field_name=f"prop_{key}")
    
    def _on_apply(self):
        """Apply changes to the model."""
        if not self._current_object:
            return
        
        try:
            # Apply changes based on object type
            if self._current_object_type == "Node":
                self._apply_node_changes()
            elif self._current_object_type == "Element":
                self._apply_element_changes()
            elif self._current_object_type == "Material":
                self._apply_material_changes()
            elif self._current_object_type == "Section":
                self._apply_section_changes()
            
            # Notify model that changes have been made
            if hasattr(self.model_manager, 'model_changed'):
                self.model_manager.model_changed()
            
            # Update UI
            self.apply_button.setEnabled(False)
            self.reset_button.setEnabled(False)
            
            logger.debug(f"Applied changes to {self._current_object_type} {self._current_object_id}")
        except Exception as e:
            logger.error(f"Error applying changes: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to apply changes: {str(e)}")
    
    def _on_reset(self):
        """Reset form to current model state."""
        if self._current_object:
            self._display_object_properties(self._current_object)
    
    def _apply_node_changes(self):
        """Apply changes to a node."""
        node = self._current_object
        
        # Apply metadata changes
        if hasattr(node, 'metadata'):
            if 'name' in self._form_widgets:
                node.metadata.name = self._form_widgets['name'].text()
            
            if 'description' in self._form_widgets:
                node.metadata.description = self._form_widgets['description'].toPlainText()
            
            if 'tags' in self._form_widgets:
                tags_text = self._form_widgets['tags'].text()
                node.metadata.tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
        
        # Apply coordinate changes
        if hasattr(node, 'coordinates'):
            for i in range(len(node.coordinates)):
                if f'coordinate_{i}' in self._form_widgets:
                    node.coordinates[i] = self._form_widgets[f'coordinate_{i}'].value()
        
        # Apply mass changes
        if hasattr(node, 'mass') and node.mass:
            for i in range(len(node.mass)):
                if f'mass_{i}' in self._form_widgets:
                    node.mass[i] = self._form_widgets[f'mass_{i}'].value()
        
        # Apply fixed DOF changes
        if hasattr(node, 'fixed_dofs') and node.fixed_dofs:
            for i in range(len(node.fixed_dofs)):
                if f'fixed_dof_{i}' in self._form_widgets:
                    node.fixed_dofs[i] = self._form_widgets[f'fixed_dof_{i}'].isChecked()
    
    def _apply_element_changes(self):
        """Apply changes to an element."""
        element = self._current_object
        
        # Apply metadata changes
        if hasattr(element, 'metadata'):
            if 'name' in self._form_widgets:
                element.metadata.name = self._form_widgets['name'].text()
            
            if 'description' in self._form_widgets:
                element.metadata.description = self._form_widgets['description'].toPlainText()
            
            if 'tags' in self._form_widgets:
                tags_text = self._form_widgets['tags'].text()
                element.metadata.tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
        
        # Apply node changes
        if hasattr(element, 'nodes') and 'nodes' in self._form_widgets:
            nodes_text = self._form_widgets['nodes'].text()
            try:
                node_ids = [int(id.strip()) for id in nodes_text.split(',') if id.strip()]
                element.nodes = node_ids
            except ValueError:
                raise ValueError("Node IDs must be comma-separated integers")
        
        # Apply material and section changes
        if hasattr(element, 'material_id') and 'material_id' in self._form_widgets:
            element.material_id = self._form_widgets['material_id'].value()
        
        if hasattr(element, 'section_id') and 'section_id' in self._form_widgets:
            element.section_id = self._form_widgets['section_id'].value()
        
        # Apply property changes
        if hasattr(element, 'properties'):
            for key in element.properties.keys():
                if f'prop_{key}' in self._form_widgets:
                    widget = self._form_widgets[f'prop_{key}']
                    if isinstance(widget, QLineEdit):
                        element.properties[key] = widget.text()
                    elif isinstance(widget, QCheckBox):
                        element.properties[key] = widget.isChecked()
                    elif isinstance(widget, QSpinBox):
                        element.properties[key] = widget.value()
                    elif isinstance(widget, QDoubleSpinBox):
                        element.properties[key] = widget.value()
    
    def _apply_material_changes(self):
        """Apply changes to a material."""
        material = self._current_object
        
        # Apply metadata changes
        if hasattr(material, 'metadata'):
            if 'name' in self._form_widgets:
                material.metadata.name = self._form_widgets['name'].text()
            
            if 'description' in self._form_widgets:
                material.metadata.description = self._form_widgets['description'].toPlainText()
            
            if 'tags' in self._form_widgets:
                tags_text = self._form_widgets['tags'].text()
                material.metadata.tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
        
        # Apply property changes
        if hasattr(material, 'properties'):
            for key in material.properties.keys():
                if f'prop_{key}' in self._form_widgets:
                    widget = self._form_widgets[f'prop_{key}']
                    if isinstance(widget, QLineEdit):
                        material.properties[key] = widget.text()
                    elif isinstance(widget, QCheckBox):
                        material.properties[key] = widget.isChecked()
                    elif isinstance(widget, QSpinBox):
                        material.properties[key] = widget.value()
                    elif isinstance(widget, QDoubleSpinBox):
                        material.properties[key] = widget.value()
    
    def _apply_section_changes(self):
        """Apply changes to a section."""
        section = self._current_object
        
        # Apply metadata changes
        if hasattr(section, 'metadata'):
            if 'name' in self._form_widgets:
                section.metadata.name = self._form_widgets['name'].text()
            
            if 'description' in self._form_widgets:
                section.metadata.description = self._form_widgets['description'].toPlainText()
            
            if 'tags' in self._form_widgets:
                tags_text = self._form_widgets['tags'].text()
                section.metadata.tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
        
        # Apply material IDs changes
        if hasattr(section, 'material_ids') and 'material_ids' in self._form_widgets:
            material_ids_text = self._form_widgets['material_ids'].text()
            try:
                material_ids = [int(id.strip()) for id in material_ids_text.split(',') if id.strip()]
                section.material_ids = material_ids
            except ValueError:
                raise ValueError("Material IDs must be comma-separated integers")
        
        # Apply property changes
        if hasattr(section, 'properties'):
            for key in section.properties.keys():
                if f'prop_{key}' in self._form_widgets:
                    widget = self._form_widgets[f'prop_{key}']
                    if isinstance(widget, QLineEdit):
                        section.properties[key] = widget.text()
                    elif isinstance(widget, QCheckBox):
                        section.properties[key] = widget.isChecked()
                    elif isinstance(widget, QSpinBox):
                        section.properties[key] = widget.value()
                    elif isinstance(widget, QDoubleSpinBox):
                        section.properties[key] = widget.value()


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
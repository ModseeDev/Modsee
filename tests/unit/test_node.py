"""
Unit tests for the Node class.

This module contains tests for verifying the functionality of the Node class.
"""

import unittest
from model.nodes import Node
from model.base.core import ModelMetadata, ModelObjectType


class TestNode(unittest.TestCase):
    """Test cases for the Node class."""

    def setUp(self):
        """Set up test fixtures."""
        self.metadata = ModelMetadata(
            name="Test Node",
            description="A test node",
            tags=["test", "node"],
            custom_properties={"color": "red"}
        )
        
    def test_node_initialization(self):
        """Test basic node initialization."""
        # Test 2D node
        node_2d = Node(1, self.metadata, [10.0, 20.0])
        self.assertEqual(node_2d.id, 1)
        self.assertEqual(node_2d.coordinates, [10.0, 20.0])
        self.assertEqual(node_2d.get_type(), ModelObjectType.NODE)
        self.assertIsNone(node_2d.mass)
        self.assertIsNone(node_2d.fixed_dofs)
        
        # Test 3D node
        node_3d = Node(2, self.metadata, [10.0, 20.0, 30.0])
        self.assertEqual(node_3d.coordinates, [10.0, 20.0, 30.0])
        
    def test_node_with_mass(self):
        """Test node with mass values."""
        node = Node(1, self.metadata, [10.0, 20.0, 30.0], mass=[1.0, 1.0, 1.0])
        self.assertEqual(node.mass, [1.0, 1.0, 1.0])
        
    def test_node_with_fixed_dofs(self):
        """Test node with fixed DOFs."""
        # 2D node with 4 DOFs (2 translational, 2 rotational)
        node_2d = Node(1, self.metadata, [10.0, 20.0], fixed_dofs=[True, False, False, True])
        self.assertEqual(node_2d.fixed_dofs, [True, False, False, True])
        
        # 3D node with 6 DOFs (3 translational, 3 rotational)
        node_3d = Node(2, self.metadata, [10.0, 20.0, 30.0], 
                     fixed_dofs=[True, True, True, False, False, False])
        self.assertEqual(node_3d.fixed_dofs, [True, True, True, False, False, False])
        
    def test_dof_access(self):
        """Test accessing DOF values."""
        node = Node(1, self.metadata, [10.0, 20.0, 30.0])
        
        # Default DOFs should be all free (not fixed)
        self.assertFalse(node.is_dof_fixed(0))  # X translation
        self.assertFalse(node.is_dof_fixed(1))  # Y translation
        self.assertFalse(node.is_dof_fixed(2))  # Z translation
        self.assertFalse(node.is_dof_fixed(3))  # X rotation
        self.assertFalse(node.is_dof_fixed(4))  # Y rotation
        self.assertFalse(node.is_dof_fixed(5))  # Z rotation
        
        # Set some DOFs as fixed
        node.set_fixed_dofs([True, False, True, False, False, True])
        self.assertTrue(node.is_dof_fixed(0))   # X translation
        self.assertFalse(node.is_dof_fixed(1))  # Y translation
        self.assertTrue(node.is_dof_fixed(2))   # Z translation
        self.assertFalse(node.is_dof_fixed(3))  # X rotation
        self.assertFalse(node.is_dof_fixed(4))  # Y rotation
        self.assertTrue(node.is_dof_fixed(5))   # Z rotation
        
    def test_coordinate_access(self):
        """Test accessing and modifying coordinates."""
        node = Node(1, self.metadata, [10.0, 20.0, 30.0])
        
        # Test getting coordinates
        self.assertEqual(node.get_x(), 10.0)
        self.assertEqual(node.get_y(), 20.0)
        self.assertEqual(node.get_z(), 30.0)
        
        # Test setting coordinates
        node.set_x(15.0)
        node.set_y(25.0)
        node.set_z(35.0)
        
        self.assertEqual(node.coordinates, [15.0, 25.0, 35.0])
        
    def test_validation(self):
        """Test node validation."""
        # Valid node
        node = Node(1, self.metadata, [10.0, 20.0, 30.0])
        self.assertTrue(node.validate())
        
        # Invalid: empty coordinates
        invalid_node = Node(2, self.metadata, [])
        self.assertFalse(invalid_node.validate())
        
        # Invalid: coordinates with more than 3 components
        invalid_node = Node(3, self.metadata, [10.0, 20.0, 30.0, 40.0])
        self.assertFalse(invalid_node.validate())
        
        # Invalid: mass with wrong number of components
        invalid_node = Node(4, self.metadata, [10.0, 20.0, 30.0], mass=[1.0, 2.0])
        self.assertFalse(invalid_node.validate())
        
        # Invalid: fixed_dofs with wrong number of components
        invalid_node = Node(5, self.metadata, [10.0, 20.0, 30.0], 
                         fixed_dofs=[True, False, True])
        self.assertFalse(invalid_node.validate())
        
    def test_serialization(self):
        """Test serialization to and from dictionary."""
        node = Node(1, self.metadata, [10.0, 20.0, 30.0], 
                 mass=[1.0, 2.0, 3.0], 
                 fixed_dofs=[True, False, True, False, False, True])
        
        # Serialize to dictionary
        node_dict = node.to_dict()
        
        # Deserialize from dictionary
        recreated_node = Node.from_dict(node_dict)
        
        # Check that the recreated node matches the original
        self.assertEqual(recreated_node.id, node.id)
        self.assertEqual(recreated_node.coordinates, node.coordinates)
        self.assertEqual(recreated_node.mass, node.mass)
        self.assertEqual(recreated_node.fixed_dofs, node.fixed_dofs)
        self.assertEqual(recreated_node.metadata.name, node.metadata.name)
        self.assertEqual(recreated_node.metadata.description, node.metadata.description)
        self.assertEqual(recreated_node.metadata.tags, node.metadata.tags)
        self.assertEqual(recreated_node.metadata.custom_properties, node.metadata.custom_properties)
        
    def test_opensees_code_generation(self):
        """Test OpenSees code generation."""
        node = Node(1, self.metadata, [10.0, 20.0, 30.0], 
                 mass=[1.0, 2.0, 3.0], 
                 fixed_dofs=[True, False, True, False, False, True])
        
        # Test TCL code generation
        tcl_code = node.to_opensees_tcl()
        self.assertIn("node 1 10.0 20.0 30.0", tcl_code)
        self.assertIn("mass 1 1.0 2.0 3.0", tcl_code)
        self.assertIn("fix 1 1 0 1 0 0 1", tcl_code)
        
        # Test Python code generation
        py_code = node.to_opensees_py()
        self.assertIn("ops.node(1, 10.0, 20.0, 30.0)", py_code)
        self.assertIn("ops.mass(1, 1.0, 2.0, 3.0)", py_code)
        self.assertIn("ops.fix(1, 1, 0, 1, 0, 0, 1)", py_code)


if __name__ == '__main__':
    unittest.main() 
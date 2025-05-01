"""
Unit tests for the Element classes.

This module contains tests for verifying the functionality of the Element classes.
"""

import unittest
from model.base.core import ModelMetadata, ModelObjectType
from model.elements import (
    Element, FrameElement, ElasticBeamColumn, DispBeamColumn,
    TrussElement, Truss2D, Truss3D,
    ShellElement, ShellMITC4, ShellDKGQ,
    SolidElement, Brick8Node, Brick20Node
)


class TestElementBase(unittest.TestCase):
    """Test cases for the base Element class."""

    def setUp(self):
        """Set up test fixtures."""
        self.metadata = ModelMetadata(
            name="Test Element",
            description="A test element",
            tags=["test", "element"],
            custom_properties={"color": "red"}
        )
    
    def test_element_type(self):
        """Test element type identification."""
        # Create concrete element classes for testing
        frame = ElasticBeamColumn(1, self.metadata, [1, 2], 1, 1)
        truss = Truss2D(2, self.metadata, [1, 2], 1, 100.0)
        shell = ShellMITC4(3, self.metadata, [1, 2, 3, 4], 1, 0.1)
        solid = Brick8Node(4, self.metadata, [1, 2, 3, 4, 5, 6, 7, 8], 1)
        
        # Test element types
        self.assertEqual(frame.get_type(), ModelObjectType.ELEMENT)
        self.assertEqual(truss.get_type(), ModelObjectType.ELEMENT)
        self.assertEqual(shell.get_type(), ModelObjectType.ELEMENT)
        self.assertEqual(solid.get_type(), ModelObjectType.ELEMENT)
        
        # Test specific element types
        self.assertEqual(frame.get_element_type(), "ElasticBeamColumn")
        self.assertEqual(truss.get_element_type(), "Truss2D")
        self.assertEqual(shell.get_element_type(), "ShellMITC4")
        self.assertEqual(solid.get_element_type(), "Brick8Node")


class TestFrameElements(unittest.TestCase):
    """Test cases for frame elements."""

    def setUp(self):
        """Set up test fixtures."""
        self.metadata = ModelMetadata(
            name="Test Frame",
            description="A test frame element",
            tags=["test", "frame"],
            custom_properties={"color": "blue"}
        )
    
    def test_elastic_beam_column(self):
        """Test elastic beam-column element."""
        beam = ElasticBeamColumn(1, self.metadata, [1, 2], 1, 1)
        
        # Test basic properties
        self.assertEqual(beam.id, 1)
        self.assertEqual(beam.nodes, [1, 2])
        self.assertEqual(beam.material_id, 1)
        self.assertEqual(beam.section_id, 1)
        self.assertEqual(beam.geom_transform_type, "Linear")
        
        # Test validation
        self.assertTrue(beam.validate())
        
        # Test invalid cases
        invalid_beam = ElasticBeamColumn(2, self.metadata, [1], 1, 1)
        self.assertFalse(invalid_beam.validate())
        self.assertIn("Frame element must have exactly 2 nodes", invalid_beam.validation_messages)
        
        invalid_beam = ElasticBeamColumn(3, self.metadata, [1, 2], None, 1)
        self.assertFalse(invalid_beam.validate())
        self.assertIn("Frame element must have a material assigned", invalid_beam.validation_messages)
        
        # Test OpenSees code generation
        tcl_code = beam.to_opensees_tcl()
        self.assertIn("element elasticBeamColumn 1 1 2", tcl_code)
        
        py_code = beam.to_opensees_py()
        self.assertIn("ops.element('elasticBeamColumn', 1, 1, 2", py_code)
    
    def test_disp_beam_column(self):
        """Test displacement-based beam-column element."""
        beam = DispBeamColumn(1, self.metadata, [1, 2], 1, 1, num_integration_points=5)
        
        # Test properties
        self.assertEqual(beam.num_integration_points, 5)
        
        # Test validation
        self.assertTrue(beam.validate())
        
        # Test invalid cases
        invalid_beam = DispBeamColumn(2, self.metadata, [1, 2], 1, 1, num_integration_points=1)
        self.assertFalse(invalid_beam.validate())
        self.assertIn("Displacement-based beam-column must have at least 2 integration points", 
                     invalid_beam.validation_messages)
        
        # Test OpenSees code generation
        tcl_code = beam.to_opensees_tcl()
        self.assertIn("element dispBeamColumn 1 1 2 5", tcl_code)
        
        py_code = beam.to_opensees_py()
        self.assertIn("ops.element('dispBeamColumn', 1, 1, 2, 5", py_code)
    
    def test_serialization(self):
        """Test serialization to and from dictionary."""
        beam = DispBeamColumn(1, self.metadata, [1, 2], 1, 1, 
                            num_integration_points=5,
                            geom_transform_type="PDelta",
                            mass_per_unit_length=0.1)
        
        # Serialize to dictionary
        beam_dict = beam.to_dict()
        
        # Check dictionary content
        self.assertEqual(beam_dict["id"], 1)
        self.assertEqual(beam_dict["nodes"], [1, 2])
        self.assertEqual(beam_dict["material_id"], 1)
        self.assertEqual(beam_dict["section_id"], 1)
        self.assertEqual(beam_dict["num_integration_points"], 5)
        self.assertEqual(beam_dict["geom_transform_type"], "PDelta")
        self.assertEqual(beam_dict["mass_per_unit_length"], 0.1)
        self.assertEqual(beam_dict["element_type"], "DispBeamColumn")
        
        # Deserialize from dictionary
        recreated_beam = DispBeamColumn.from_dict(beam_dict)
        
        # Check that the recreated beam matches the original
        self.assertEqual(recreated_beam.id, beam.id)
        self.assertEqual(recreated_beam.nodes, beam.nodes)
        self.assertEqual(recreated_beam.material_id, beam.material_id)
        self.assertEqual(recreated_beam.section_id, beam.section_id)
        self.assertEqual(recreated_beam.num_integration_points, beam.num_integration_points)
        self.assertEqual(recreated_beam.geom_transform_type, beam.geom_transform_type)
        self.assertEqual(recreated_beam.mass_per_unit_length, beam.mass_per_unit_length)


class TestTrussElements(unittest.TestCase):
    """Test cases for truss elements."""

    def setUp(self):
        """Set up test fixtures."""
        self.metadata = ModelMetadata(
            name="Test Truss",
            description="A test truss element",
            tags=["test", "truss"],
            custom_properties={"color": "green"}
        )
    
    def test_truss_element(self):
        """Test basic truss element."""
        truss = TrussElement(1, self.metadata, [1, 2], 1, 100.0)
        
        # Test basic properties
        self.assertEqual(truss.id, 1)
        self.assertEqual(truss.nodes, [1, 2])
        self.assertEqual(truss.material_id, 1)
        self.assertIsNone(truss.section_id)  # Truss doesn't use section
        self.assertEqual(truss.area, 100.0)
        
        # Test validation
        self.assertTrue(truss.validate())
        
        # Test invalid cases
        invalid_truss = TrussElement(2, self.metadata, [1], 1, 100.0)
        self.assertFalse(invalid_truss.validate())
        self.assertIn("Truss element must have exactly 2 nodes", invalid_truss.validation_messages)
        
        invalid_truss = TrussElement(3, self.metadata, [1, 2], 1, -1.0)
        self.assertFalse(invalid_truss.validate())
        self.assertIn("Truss element must have a positive area", invalid_truss.validation_messages)
        
        # Test OpenSees code generation
        tcl_code = truss.to_opensees_tcl()
        self.assertIn("element truss 1 1 2 100.0", tcl_code)
        
        py_code = truss.to_opensees_py()
        self.assertIn("ops.element('truss', 1, 1, 2, 100.0", py_code)
    
    def test_truss_2d_3d(self):
        """Test 2D and 3D truss elements."""
        truss2d = Truss2D(1, self.metadata, [1, 2], 1, 100.0)
        truss3d = Truss3D(2, self.metadata, [3, 4], 1, 100.0)
        
        # Test element types
        self.assertEqual(truss2d.get_element_type(), "Truss2D")
        self.assertEqual(truss3d.get_element_type(), "Truss3D")
        
        # Test serialization
        truss2d_dict = truss2d.to_dict()
        truss3d_dict = truss3d.to_dict()
        
        self.assertEqual(truss2d_dict["element_type"], "Truss2D")
        self.assertEqual(truss3d_dict["element_type"], "Truss3D")


class TestShellElements(unittest.TestCase):
    """Test cases for shell elements."""

    def setUp(self):
        """Set up test fixtures."""
        self.metadata = ModelMetadata(
            name="Test Shell",
            description="A test shell element",
            tags=["test", "shell"],
            custom_properties={"color": "yellow"}
        )
    
    def test_shell_mitc4(self):
        """Test MITC4 shell element."""
        shell = ShellMITC4(1, self.metadata, [1, 2, 3, 4], 1, 0.1)
        
        # Test basic properties
        self.assertEqual(shell.id, 1)
        self.assertEqual(shell.nodes, [1, 2, 3, 4])
        self.assertEqual(shell.material_id, 1)
        self.assertEqual(shell.thickness, 0.1)
        
        # Test validation
        self.assertTrue(shell.validate())
        
        # Test invalid cases
        invalid_shell = ShellMITC4(2, self.metadata, [1, 2, 3], 1, 0.1)
        self.assertFalse(invalid_shell.validate())
        self.assertIn("MITC4 shell element must have exactly 4 nodes", invalid_shell.validation_messages)
        
        invalid_shell = ShellMITC4(3, self.metadata, [1, 2, 3, 4], 1, -0.1)
        self.assertFalse(invalid_shell.validate())
        self.assertIn("Shell element must have a positive thickness", invalid_shell.validation_messages)
        
        # Test OpenSees code generation
        tcl_code = shell.to_opensees_tcl()
        self.assertIn("element ShellMITC4 1 1 2 3 4", tcl_code)
        
        py_code = shell.to_opensees_py()
        self.assertIn("ops.element('ShellMITC4', 1, 1, 2, 3, 4", py_code)


class TestSolidElements(unittest.TestCase):
    """Test cases for solid elements."""

    def setUp(self):
        """Set up test fixtures."""
        self.metadata = ModelMetadata(
            name="Test Solid",
            description="A test solid element",
            tags=["test", "solid"],
            custom_properties={"color": "orange"}
        )
    
    def test_brick_8node(self):
        """Test 8-node brick element."""
        brick = Brick8Node(1, self.metadata, [1, 2, 3, 4, 5, 6, 7, 8], 1)
        
        # Test basic properties
        self.assertEqual(brick.id, 1)
        self.assertEqual(brick.nodes, [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(brick.material_id, 1)
        
        # Test validation
        self.assertTrue(brick.validate())
        
        # Test invalid cases
        invalid_brick = Brick8Node(2, self.metadata, [1, 2, 3, 4, 5, 6, 7], 1)
        self.assertFalse(invalid_brick.validate())
        self.assertIn("8-node brick element must have exactly 8 nodes", invalid_brick.validation_messages)
        
        # Test OpenSees code generation
        tcl_code = brick.to_opensees_tcl()
        self.assertIn("element stdBrick 1 1 2 3 4 5 6 7 8", tcl_code)
        
        py_code = brick.to_opensees_py()
        self.assertIn("ops.element('stdBrick', 1, 1, 2, 3, 4, 5, 6, 7, 8", py_code)
    
    def test_brick_20node(self):
        """Test 20-node brick element."""
        nodes = list(range(1, 21))  # 20 nodes
        brick = Brick20Node(1, self.metadata, nodes, 1)
        
        # Test basic properties
        self.assertEqual(brick.id, 1)
        self.assertEqual(len(brick.nodes), 20)
        self.assertEqual(brick.material_id, 1)
        
        # Test validation
        self.assertTrue(brick.validate())
        
        # Test invalid cases
        invalid_nodes = list(range(1, 19))  # Only 18 nodes
        invalid_brick = Brick20Node(2, self.metadata, invalid_nodes, 1)
        self.assertFalse(invalid_brick.validate())
        self.assertIn("20-node brick element must have exactly 20 nodes", invalid_brick.validation_messages)


if __name__ == '__main__':
    unittest.main() 
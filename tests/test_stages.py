"""
Tests for the Stage management system.

This module provides tests for the Stage and StageManager classes.
"""

import unittest
from model.base.core import ModelMetadata
from model.stages import Stage, StageType, StageManager


class TestStage(unittest.TestCase):
    """Test cases for the Stage class."""
    
    def test_stage_creation(self):
        """Test creation of a Stage object."""
        metadata = ModelMetadata(name="Test Stage")
        stage = Stage(id=1, metadata=metadata, stage_type=StageType.STATIC)
        
        self.assertEqual(stage.id, 1)
        self.assertEqual(stage.metadata.name, "Test Stage")
        self.assertEqual(stage.stage_type, StageType.STATIC)
        self.assertEqual(stage.order, 0)  # Default value
        self.assertIsNone(stage.parent_stage_id)
        self.assertEqual(stage.description, "")
        self.assertFalse(stage.is_initial)
        
        # Test active sets are empty
        self.assertEqual(len(stage.active_nodes), 0)
        self.assertEqual(len(stage.active_elements), 0)
        self.assertEqual(len(stage.active_loads), 0)
        self.assertEqual(len(stage.active_boundary_conditions), 0)
    
    def test_add_remove_components(self):
        """Test adding and removing components from a stage."""
        metadata = ModelMetadata(name="Test Stage")
        stage = Stage(id=1, metadata=metadata, stage_type=StageType.STATIC)
        
        # Add components
        stage.add_node(101)
        stage.add_node(102)
        stage.add_element(201)
        stage.add_load(301)
        stage.add_boundary_condition(401)
        
        # Check components were added
        self.assertEqual(len(stage.active_nodes), 2)
        self.assertTrue(101 in stage.active_nodes)
        self.assertTrue(102 in stage.active_nodes)
        self.assertEqual(len(stage.active_elements), 1)
        self.assertEqual(len(stage.active_loads), 1)
        self.assertEqual(len(stage.active_boundary_conditions), 1)
        
        # Remove components
        self.assertTrue(stage.remove_node(101))
        self.assertTrue(stage.remove_element(201))
        self.assertFalse(stage.remove_load(302))  # Non-existent ID
        
        # Check components were removed
        self.assertEqual(len(stage.active_nodes), 1)
        self.assertFalse(101 in stage.active_nodes)
        self.assertTrue(102 in stage.active_nodes)
        self.assertEqual(len(stage.active_elements), 0)
    
    def test_analysis_parameters(self):
        """Test setting and getting analysis parameters."""
        metadata = ModelMetadata(name="Test Stage")
        stage = Stage(id=1, metadata=metadata, stage_type=StageType.STATIC)
        
        # Set parameters
        stage.set_analysis_parameter("solver", "Newton")
        stage.set_analysis_parameter("tolerance", 1e-6)
        stage.set_analysis_parameter("max_iterations", 100)
        
        # Get parameters
        self.assertEqual(stage.get_analysis_parameter("solver"), "Newton")
        self.assertEqual(stage.get_analysis_parameter("tolerance"), 1e-6)
        self.assertEqual(stage.get_analysis_parameter("max_iterations"), 100)
        self.assertIsNone(stage.get_analysis_parameter("non_existent"))
        self.assertEqual(stage.get_analysis_parameter("non_existent", "default"), "default")
    
    def test_serialization(self):
        """Test serialization to and from dictionary."""
        metadata = ModelMetadata(name="Test Stage")
        stage = Stage(
            id=1, 
            metadata=metadata, 
            stage_type=StageType.STATIC,
            order=2,
            description="Test stage description",
            is_initial=True
        )
        
        # Add components
        stage.add_node(101)
        stage.add_element(201)
        stage.set_analysis_parameter("solver", "Newton")
        
        # Serialize
        data = stage.to_dict()
        
        # Deserialize
        new_stage = Stage.from_dict(data)
        
        # Check values
        self.assertEqual(new_stage.id, 1)
        self.assertEqual(new_stage.metadata.name, "Test Stage")
        self.assertEqual(new_stage.stage_type, StageType.STATIC)
        self.assertEqual(new_stage.order, 2)
        self.assertEqual(new_stage.description, "Test stage description")
        self.assertTrue(new_stage.is_initial)
        self.assertTrue(101 in new_stage.active_nodes)
        self.assertTrue(201 in new_stage.active_elements)
        self.assertEqual(new_stage.get_analysis_parameter("solver"), "Newton")


class TestStageManager(unittest.TestCase):
    """Test cases for the StageManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = StageManager()
    
    def test_create_stage(self):
        """Test creating stages through the manager."""
        # Create a root stage
        stage1 = self.manager.create_stage(
            stage_type=StageType.STATIC,
            name="Root Stage",
            description="First stage",
            is_initial=True
        )
        
        # Create child stages
        stage2 = self.manager.create_stage(
            stage_type=StageType.STATIC,
            name="Child 1",
            order=1,
            parent_stage_id=stage1.id
        )
        
        stage3 = self.manager.create_stage(
            stage_type=StageType.STATIC,
            name="Child 2",
            order=2,
            parent_stage_id=stage1.id
        )
        
        # Create a grandchild stage
        stage4 = self.manager.create_stage(
            stage_type=StageType.DYNAMIC,
            name="Grandchild",
            parent_stage_id=stage2.id
        )
        
        # Check stages were created
        self.assertEqual(len(self.manager.get_all_stages()), 4)
        self.assertEqual(len(self.manager.get_root_stages()), 1)
        self.assertEqual(len(self.manager.get_child_stages(stage1.id)), 2)
        self.assertEqual(len(self.manager.get_child_stages(stage2.id)), 1)
    
    def test_stage_sequence(self):
        """Test getting stages in execution order."""
        # Create stages with different orders
        root1 = self.manager.create_stage(
            stage_type=StageType.STATIC,
            name="Root 1",
            order=1
        )
        
        root2 = self.manager.create_stage(
            stage_type=StageType.STATIC,
            name="Root 2",
            order=0
        )
        
        child1 = self.manager.create_stage(
            stage_type=StageType.STATIC,
            name="Child 1",
            order=1,
            parent_stage_id=root2.id
        )
        
        child2 = self.manager.create_stage(
            stage_type=StageType.STATIC,
            name="Child 2",
            order=0,
            parent_stage_id=root2.id
        )
        
        # Get sequence and check order
        sequence = self.manager.get_stage_sequence()
        self.assertEqual(len(sequence), 4)
        
        # Expected order is: root2 -> child2 -> child1 -> root1
        # With the depth-first traversal, root2 comes first, then its children in order
        self.assertEqual(sequence[0].metadata.name, "Root 2")
        self.assertEqual(sequence[1].metadata.name, "Child 2")
        self.assertEqual(sequence[2].metadata.name, "Child 1")
        self.assertEqual(sequence[3].metadata.name, "Root 1")
    
    def test_current_stage(self):
        """Test setting and getting current stage."""
        # Create stages
        stage1 = self.manager.create_stage(
            stage_type=StageType.STATIC,
            name="Stage 1"
        )
        
        stage2 = self.manager.create_stage(
            stage_type=StageType.STATIC,
            name="Stage 2"
        )
        
        # Initially no current stage
        self.assertIsNone(self.manager.get_current_stage())
        
        # Set current stage
        self.assertTrue(self.manager.set_current_stage(stage1.id))
        self.assertEqual(self.manager.get_current_stage().id, stage1.id)
        
        # Change current stage
        self.assertTrue(self.manager.set_current_stage(stage2.id))
        self.assertEqual(self.manager.get_current_stage().id, stage2.id)
        
        # Try setting to non-existent stage
        self.assertFalse(self.manager.set_current_stage(999))
    
    def test_serialization(self):
        """Test serialization to and from dictionary."""
        # Create stages
        self.manager.create_stage(
            stage_type=StageType.STATIC,
            name="Stage 1"
        )
        
        stage2 = self.manager.create_stage(
            stage_type=StageType.DYNAMIC,
            name="Stage 2"
        )
        
        # Set current stage
        self.manager.set_current_stage(stage2.id)
        
        # Serialize
        data = self.manager.to_dict()
        
        # Create new manager and deserialize
        new_manager = StageManager()
        new_manager.from_dict(data)
        
        # Check values
        self.assertEqual(len(new_manager.get_all_stages()), 2)
        self.assertEqual(new_manager.get_current_stage().metadata.name, "Stage 2")


if __name__ == '__main__':
    unittest.main() 
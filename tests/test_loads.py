"""
Tests for the Load classes.

This module contains unit tests for the Load base class and its derived classes.
"""

import unittest
from model.base.core import ModelMetadata
from model.loads import (
    Load, LoadType, LoadDirection,
    PointLoad, DistributedLoad, SelfWeightLoad, TimeVaryingLoad
)


class TestLoads(unittest.TestCase):
    """Test cases for Load classes."""
    
    def test_point_load(self):
        """Test the PointLoad class."""
        # Create a point load
        metadata = ModelMetadata(name="Test Point Load")
        point_load = PointLoad(
            id=1,
            metadata=metadata,
            node_id=10,
            direction=LoadDirection.Y,
            value=-10.0
        )
        
        # Test basic properties
        self.assertEqual(point_load.id, 1)
        self.assertEqual(point_load.metadata.name, "Test Point Load")
        self.assertEqual(point_load.node_id, 10)
        self.assertEqual(point_load.direction, LoadDirection.Y)
        self.assertEqual(point_load.value, -10.0)
        self.assertEqual(point_load.load_type, LoadType.POINT)
        
        # Test validation
        self.assertTrue(point_load.validate())
        
        # Test serialization and deserialization
        data = point_load.to_dict()
        restored_load = PointLoad.from_dict(data)
        
        self.assertEqual(restored_load.id, point_load.id)
        self.assertEqual(restored_load.metadata.name, point_load.metadata.name)
        self.assertEqual(restored_load.node_id, point_load.node_id)
        self.assertEqual(restored_load.direction, point_load.direction)
        self.assertEqual(restored_load.value, point_load.value)
        self.assertEqual(restored_load.load_type, point_load.load_type)
        
        # Test OpenSees code generation
        tcl_code = point_load.to_opensees_tcl()
        py_code = point_load.to_opensees_py()
        
        self.assertIn("load", tcl_code.lower())
        self.assertIn("10", tcl_code)
        self.assertIn("ops.load", py_code)
        self.assertIn("10", py_code)
    
    def test_distributed_load(self):
        """Test the DistributedLoad class."""
        # Create a distributed load
        metadata = ModelMetadata(name="Test Distributed Load")
        distributed_load = DistributedLoad(
            id=2,
            metadata=metadata,
            element_id=20,
            direction=LoadDirection.LOCAL_2,
            value_start=-5.0,
            value_end=-5.0
        )
        
        # Test basic properties
        self.assertEqual(distributed_load.id, 2)
        self.assertEqual(distributed_load.metadata.name, "Test Distributed Load")
        self.assertEqual(distributed_load.element_id, 20)
        self.assertEqual(distributed_load.direction, LoadDirection.LOCAL_2)
        self.assertEqual(distributed_load.value_start, -5.0)
        self.assertEqual(distributed_load.value_end, -5.0)
        self.assertEqual(distributed_load.load_type, LoadType.DISTRIBUTED)
        
        # Test validation
        self.assertTrue(distributed_load.validate())
        
        # Test serialization and deserialization
        data = distributed_load.to_dict()
        restored_load = DistributedLoad.from_dict(data)
        
        self.assertEqual(restored_load.id, distributed_load.id)
        self.assertEqual(restored_load.metadata.name, distributed_load.metadata.name)
        self.assertEqual(restored_load.element_id, distributed_load.element_id)
        self.assertEqual(restored_load.direction, distributed_load.direction)
        self.assertEqual(restored_load.value_start, distributed_load.value_start)
        self.assertEqual(restored_load.value_end, distributed_load.value_end)
        self.assertEqual(restored_load.load_type, distributed_load.load_type)
        
        # Test OpenSees code generation
        tcl_code = distributed_load.to_opensees_tcl()
        py_code = distributed_load.to_opensees_py()
        
        self.assertIn("eleload", tcl_code.lower())
        self.assertIn("20", tcl_code)
        self.assertIn("ops.eleLoad", py_code)
        self.assertIn("20", py_code)
    
    def test_self_weight_load(self):
        """Test the SelfWeightLoad class."""
        # Create a self-weight load
        metadata = ModelMetadata(name="Test Self-Weight Load")
        self_weight_load = SelfWeightLoad(
            id=3,
            metadata=metadata,
            element_ids=[30, 31, 32],
            direction=LoadDirection.Y,
            factor=-1.0
        )
        
        # Test basic properties
        self.assertEqual(self_weight_load.id, 3)
        self.assertEqual(self_weight_load.metadata.name, "Test Self-Weight Load")
        self.assertEqual(self_weight_load.element_ids, [30, 31, 32])
        self.assertEqual(self_weight_load.direction, LoadDirection.Y)
        self.assertEqual(self_weight_load.factor, -1.0)
        self.assertEqual(self_weight_load.load_type, LoadType.SELF_WEIGHT)
        
        # Test validation
        self.assertTrue(self_weight_load.validate())
        
        # Test serialization and deserialization
        data = self_weight_load.to_dict()
        restored_load = SelfWeightLoad.from_dict(data)
        
        self.assertEqual(restored_load.id, self_weight_load.id)
        self.assertEqual(restored_load.metadata.name, self_weight_load.metadata.name)
        self.assertEqual(restored_load.element_ids, self_weight_load.element_ids)
        self.assertEqual(restored_load.direction, self_weight_load.direction)
        self.assertEqual(restored_load.factor, self_weight_load.factor)
        self.assertEqual(restored_load.load_type, self_weight_load.load_type)
        
        # Test OpenSees code generation
        tcl_code = self_weight_load.to_opensees_tcl()
        py_code = self_weight_load.to_opensees_py()
        
        self.assertIn("pattern", tcl_code.lower())
        self.assertIn("-1.0", tcl_code)
        self.assertIn("ops.pattern", py_code)
        self.assertIn("-1.0", py_code)
    
    def test_time_varying_load(self):
        """Test the TimeVaryingLoad class."""
        # Create a time-varying load
        metadata = ModelMetadata(name="Test Time-Varying Load")
        time_varying_load = TimeVaryingLoad(
            id=4,
            metadata=metadata,
            node_id=40,
            direction=LoadDirection.X,
            time_series_id=1,
            factor=2.0
        )
        
        # Test basic properties
        self.assertEqual(time_varying_load.id, 4)
        self.assertEqual(time_varying_load.metadata.name, "Test Time-Varying Load")
        self.assertEqual(time_varying_load.node_id, 40)
        self.assertEqual(time_varying_load.direction, LoadDirection.X)
        self.assertEqual(time_varying_load.time_series_id, 1)
        self.assertEqual(time_varying_load.factor, 2.0)
        self.assertEqual(time_varying_load.load_type, LoadType.TIME_VARYING)
        
        # Test validation
        self.assertTrue(time_varying_load.validate())
        
        # Test serialization and deserialization
        data = time_varying_load.to_dict()
        restored_load = TimeVaryingLoad.from_dict(data)
        
        self.assertEqual(restored_load.id, time_varying_load.id)
        self.assertEqual(restored_load.metadata.name, time_varying_load.metadata.name)
        self.assertEqual(restored_load.node_id, time_varying_load.node_id)
        self.assertEqual(restored_load.direction, time_varying_load.direction)
        self.assertEqual(restored_load.time_series_id, time_varying_load.time_series_id)
        self.assertEqual(restored_load.factor, time_varying_load.factor)
        self.assertEqual(restored_load.load_type, time_varying_load.load_type)
        
        # Test OpenSees code generation
        tcl_code = time_varying_load.to_opensees_tcl()
        py_code = time_varying_load.to_opensees_py()
        
        self.assertIn("pattern", tcl_code.lower())
        self.assertIn("40", tcl_code)
        self.assertIn("2.0", tcl_code)
        self.assertIn("ops.pattern", py_code)
        self.assertIn("40", py_code)
        self.assertIn("2.0", py_code)


if __name__ == "__main__":
    unittest.main() 
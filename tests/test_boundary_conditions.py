"""
Tests for boundary condition classes.
"""

import unittest
from model.base.core import ModelMetadata
from model.boundary_conditions import (
    BoundaryConditionType,
    BoundaryCondition,
    FixedBoundaryCondition,
    SpringBoundaryCondition,
    DisplacementBoundaryCondition,
    MultiPointConstraint
)


class TestBoundaryCondition(unittest.TestCase):
    """Test cases for the base BoundaryCondition class."""
    
    def test_create_boundary_condition(self):
        """Test creating a basic boundary condition."""
        metadata = ModelMetadata(name="Test BC")
        bc = BoundaryCondition(id=1, metadata=metadata, node_id=2, 
                               bc_type=BoundaryConditionType.FIXED)
        
        self.assertEqual(bc.id, 1)
        self.assertEqual(bc.metadata.name, "Test BC")
        self.assertEqual(bc.node_id, 2)
        self.assertEqual(bc.bc_type, BoundaryConditionType.FIXED)
    
    def test_validate(self):
        """Test validation of boundary condition."""
        metadata = ModelMetadata(name="Test BC")
        bc1 = BoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                bc_type=BoundaryConditionType.FIXED)
        bc2 = BoundaryCondition(id=1, metadata=metadata, node_id=-1, 
                                bc_type=BoundaryConditionType.FIXED)
        
        self.assertTrue(bc1.validate())
        self.assertFalse(bc2.validate())
        self.assertIn("Node ID must be non-negative", bc2.validation_messages)
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        metadata = ModelMetadata(name="Test BC", description="Test description")
        bc = BoundaryCondition(id=1, metadata=metadata, node_id=2, 
                               bc_type=BoundaryConditionType.FIXED)
        
        bc_dict = bc.to_dict()
        bc2 = BoundaryCondition.from_dict(bc_dict)
        
        self.assertEqual(bc.id, bc2.id)
        self.assertEqual(bc.metadata.name, bc2.metadata.name)
        self.assertEqual(bc.metadata.description, bc2.metadata.description)
        self.assertEqual(bc.node_id, bc2.node_id)
        self.assertEqual(bc.bc_type, bc2.bc_type)


class TestFixedBoundaryCondition(unittest.TestCase):
    """Test cases for the FixedBoundaryCondition class."""
    
    def test_create_fixed_boundary_condition(self):
        """Test creating a fixed boundary condition."""
        metadata = ModelMetadata(name="Fixed BC")
        fixed_bc = FixedBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                          fixed_dofs=[True, True, False, False])
        
        self.assertEqual(fixed_bc.id, 1)
        self.assertEqual(fixed_bc.metadata.name, "Fixed BC")
        self.assertEqual(fixed_bc.node_id, 2)
        self.assertEqual(fixed_bc.bc_type, BoundaryConditionType.CUSTOM)
        self.assertEqual(fixed_bc.fixed_dofs, [True, True, False, False])
    
    def test_create_fixed(self):
        """Test creating a fully fixed boundary condition."""
        metadata = ModelMetadata(name="Fixed BC")
        fixed_bc = FixedBoundaryCondition.create_fixed(id=1, metadata=metadata, 
                                                       node_id=2, num_dofs=6)
        
        self.assertEqual(fixed_bc.fixed_dofs, [True, True, True, True, True, True])
        self.assertEqual(fixed_bc.bc_type, BoundaryConditionType.FIXED)
    
    def test_create_pinned(self):
        """Test creating a pinned boundary condition."""
        metadata = ModelMetadata(name="Pinned BC")
        
        # Test 2D pinned
        pinned_bc_2d = FixedBoundaryCondition.create_pinned(id=1, metadata=metadata, 
                                                           node_id=2, dimension=2)
        
        self.assertEqual(pinned_bc_2d.fixed_dofs, [True, True, False, False])
        self.assertEqual(pinned_bc_2d.bc_type, BoundaryConditionType.PINNED)
        
        # Test 3D pinned
        pinned_bc_3d = FixedBoundaryCondition.create_pinned(id=2, metadata=metadata, 
                                                           node_id=3, dimension=3)
        
        self.assertEqual(pinned_bc_3d.fixed_dofs, [True, True, True, False, False, False])
        self.assertEqual(pinned_bc_3d.bc_type, BoundaryConditionType.PINNED)
    
    def test_create_roller(self):
        """Test creating a roller boundary condition."""
        metadata = ModelMetadata(name="Roller BC")
        
        # Test 2D roller in X direction
        roller_x = FixedBoundaryCondition.create_roller(id=1, metadata=metadata, 
                                                       node_id=2, dimension=2, 
                                                       fixed_direction=0)
        
        self.assertEqual(roller_x.fixed_dofs, [True, False, False, False])
        self.assertEqual(roller_x.bc_type, BoundaryConditionType.ROLLER)
        
        # Test 3D roller in Y direction
        roller_y = FixedBoundaryCondition.create_roller(id=2, metadata=metadata, 
                                                       node_id=3, dimension=3, 
                                                       fixed_direction=1)
        
        self.assertEqual(roller_y.fixed_dofs, [False, True, False, False, False, False])
        self.assertEqual(roller_y.bc_type, BoundaryConditionType.ROLLER)
    
    def test_validate(self):
        """Test validation of fixed boundary condition."""
        metadata = ModelMetadata(name="Fixed BC")
        
        # Valid fixed BC
        bc1 = FixedBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                     fixed_dofs=[True, True, False, False])
        
        # Invalid fixed BC (odd number of DOFs)
        bc2 = FixedBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                     fixed_dofs=[True, True, False])
        
        # Invalid fixed BC (empty fixed_dofs)
        bc3 = FixedBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                     fixed_dofs=[])
        
        self.assertTrue(bc1.validate())
        self.assertFalse(bc2.validate())
        self.assertFalse(bc3.validate())
        self.assertIn("Number of fixed DOFs must be even (paired rotational and translational DOFs)", bc2.validation_messages)
        self.assertIn("Fixed DOFs list is required", bc3.validation_messages)
    
    def test_to_opensees(self):
        """Test OpenSees code generation."""
        metadata = ModelMetadata(name="Fixed BC")
        fixed_bc = FixedBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                          fixed_dofs=[True, False, True, False])
        
        # Test TCL code generation
        tcl_code = fixed_bc.to_opensees_tcl()
        self.assertEqual(tcl_code, "fix 2 1 0 1 0")
        
        # Test Python code generation
        py_code = fixed_bc.to_opensees_py()
        self.assertEqual(py_code, "ops.fix(2, 1, 0, 1, 0)")


class TestSpringBoundaryCondition(unittest.TestCase):
    """Test cases for the SpringBoundaryCondition class."""
    
    def test_create_spring_boundary_condition(self):
        """Test creating a spring boundary condition."""
        metadata = ModelMetadata(name="Spring BC")
        spring_bc = SpringBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                           spring_dofs=[0, 1], 
                                           spring_stiffness=[1000.0, 2000.0])
        
        self.assertEqual(spring_bc.id, 1)
        self.assertEqual(spring_bc.metadata.name, "Spring BC")
        self.assertEqual(spring_bc.node_id, 2)
        self.assertEqual(spring_bc.bc_type, BoundaryConditionType.SPRING)
        self.assertEqual(spring_bc.spring_dofs, [0, 1])
        self.assertEqual(spring_bc.spring_stiffness, [1000.0, 2000.0])
    
    def test_validate(self):
        """Test validation of spring boundary condition."""
        metadata = ModelMetadata(name="Spring BC")
        
        # Valid spring BC
        bc1 = SpringBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                     spring_dofs=[0, 1], 
                                     spring_stiffness=[1000.0, 2000.0])
        
        # Invalid spring BC (mismatched lengths)
        bc2 = SpringBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                     spring_dofs=[0, 1], 
                                     spring_stiffness=[1000.0])
        
        # Invalid spring BC (negative stiffness)
        bc3 = SpringBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                     spring_dofs=[0], 
                                     spring_stiffness=[-100.0])
        
        self.assertTrue(bc1.validate())
        self.assertFalse(bc2.validate())
        self.assertFalse(bc3.validate())
        self.assertIn("Number of spring DOFs (2) must match number of spring stiffness values (1)", 
                      bc2.validation_messages)
        self.assertIn("Spring stiffness must be positive", bc3.validation_messages)


class TestDisplacementBoundaryCondition(unittest.TestCase):
    """Test cases for the DisplacementBoundaryCondition class."""
    
    def test_create_displacement_boundary_condition(self):
        """Test creating a displacement boundary condition."""
        metadata = ModelMetadata(name="Displacement BC")
        disp_bc = DisplacementBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                               disp_dofs=[0, 1], 
                                               disp_values=[0.01, 0.02])
        
        self.assertEqual(disp_bc.id, 1)
        self.assertEqual(disp_bc.metadata.name, "Displacement BC")
        self.assertEqual(disp_bc.node_id, 2)
        self.assertEqual(disp_bc.bc_type, BoundaryConditionType.DISPLACEMENT)
        self.assertEqual(disp_bc.disp_dofs, [0, 1])
        self.assertEqual(disp_bc.disp_values, [0.01, 0.02])
    
    def test_validate(self):
        """Test validation of displacement boundary condition."""
        metadata = ModelMetadata(name="Displacement BC")
        
        # Valid displacement BC
        bc1 = DisplacementBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                           disp_dofs=[0, 1], 
                                           disp_values=[0.01, 0.02])
        
        # Invalid displacement BC (mismatched lengths)
        bc2 = DisplacementBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                           disp_dofs=[0, 1], 
                                           disp_values=[0.01])
        
        self.assertTrue(bc1.validate())
        self.assertFalse(bc2.validate())
        self.assertIn("Number of displacement DOFs (2) must match number of displacement values (1)", 
                      bc2.validation_messages)
    
    def test_to_opensees(self):
        """Test OpenSees code generation."""
        metadata = ModelMetadata(name="Displacement BC")
        disp_bc = DisplacementBoundaryCondition(id=1, metadata=metadata, node_id=2, 
                                              disp_dofs=[0, 2], 
                                              disp_values=[0.01, 0.03])
        
        # Test TCL code generation
        tcl_code = disp_bc.to_opensees_tcl()
        self.assertEqual(tcl_code, "sp 2 1 0.01\nsp 2 3 0.03")
        
        # Test Python code generation
        py_code = disp_bc.to_opensees_py()
        self.assertEqual(py_code, "ops.sp(2, 1, 0.01)\nops.sp(2, 3, 0.03)")


class TestMultiPointConstraint(unittest.TestCase):
    """Test cases for the MultiPointConstraint class."""
    
    def test_create_multi_point_constraint(self):
        """Test creating a multi-point constraint."""
        metadata = ModelMetadata(name="MPC")
        mpc = MultiPointConstraint(id=1, metadata=metadata,
                                  retained_node_id=2, retained_dof=1,
                                  constrained_node_id=3, constrained_dof=1,
                                  coefficient=1.0, constant=0.0)
        
        self.assertEqual(mpc.id, 1)
        self.assertEqual(mpc.metadata.name, "MPC")
        self.assertEqual(mpc.node_id, 3)  # constrained_node_id
        self.assertEqual(mpc.bc_type, BoundaryConditionType.MULTI_POINT)
        self.assertEqual(mpc.retained_node_id, 2)
        self.assertEqual(mpc.retained_dof, 1)
        self.assertEqual(mpc.constrained_dof, 1)
        self.assertEqual(mpc.coefficient, 1.0)
        self.assertEqual(mpc.constant, 0.0)
    
    def test_validate(self):
        """Test validation of multi-point constraint."""
        metadata = ModelMetadata(name="MPC")
        
        # Valid MPC
        mpc1 = MultiPointConstraint(id=1, metadata=metadata,
                                   retained_node_id=2, retained_dof=1,
                                   constrained_node_id=3, constrained_dof=1)
        
        # Invalid MPC (same node and DOF)
        mpc2 = MultiPointConstraint(id=1, metadata=metadata,
                                   retained_node_id=2, retained_dof=1,
                                   constrained_node_id=2, constrained_dof=1)
        
        # Invalid MPC (negative DOF)
        mpc3 = MultiPointConstraint(id=1, metadata=metadata,
                                   retained_node_id=2, retained_dof=-1,
                                   constrained_node_id=3, constrained_dof=1)
        
        self.assertTrue(mpc1.validate())
        self.assertFalse(mpc2.validate())
        self.assertFalse(mpc3.validate())
        self.assertIn("Retained and constrained DOFs cannot be the same", mpc2.validation_messages)
        self.assertIn("Retained DOF index must be non-negative", mpc3.validation_messages)
    
    def test_to_opensees(self):
        """Test OpenSees code generation."""
        metadata = ModelMetadata(name="MPC")
        
        # Equal DOF case (coefficient=1, constant=0)
        mpc1 = MultiPointConstraint(id=1, metadata=metadata,
                                   retained_node_id=2, retained_dof=1,
                                   constrained_node_id=3, constrained_dof=1)
        
        # General case
        mpc2 = MultiPointConstraint(id=2, metadata=metadata,
                                   retained_node_id=2, retained_dof=1,
                                   constrained_node_id=3, constrained_dof=1,
                                   coefficient=0.5, constant=0.1)
        
        # Test TCL code generation
        tcl_code1 = mpc1.to_opensees_tcl()
        tcl_code2 = mpc2.to_opensees_tcl()
        self.assertEqual(tcl_code1, "equalDOF 2 3 2")
        self.assertEqual(tcl_code2, "mp 3 2 0.5 2 2 0.1")
        
        # Test Python code generation
        py_code1 = mpc1.to_opensees_py()
        py_code2 = mpc2.to_opensees_py()
        self.assertEqual(py_code1, "ops.equalDOF(2, 3, 2)")
        self.assertEqual(py_code2, "ops.mp(3, 2, 0.5, 2, 2, 0.1)")


if __name__ == '__main__':
    unittest.main() 
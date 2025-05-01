"""
Test cases for material models.
"""

import unittest
from model.base.core import ModelMetadata
from model.materials.factory import MaterialFactory
from model.materials.elastic import ElasticMaterial, ElasticIsotropicMaterial
from model.materials.steel import SteelMaterial, ElasticPerfectlyPlasticSteel, BilinearSteel
from model.materials.concrete import ConcreteMaterial, ElasticConcrete, KentParkConcrete
from model.materials.other import AluminumMaterial, WoodMaterial, CustomMaterial


class TestMaterialModels(unittest.TestCase):
    """Test cases for material models."""
    
    def test_elastic_material(self):
        """Test elastic material creation and properties."""
        metadata = ModelMetadata(name="Test Elastic Material")
        elastic_material = ElasticMaterial(id=1, metadata=metadata, elastic_modulus=200000.0)
        
        self.assertEqual(elastic_material.id, 1)
        self.assertEqual(elastic_material.metadata.name, "Test Elastic Material")
        self.assertEqual(elastic_material.elastic_modulus, 200000.0)
        self.assertEqual(elastic_material.get_material_type(), "ElasticMaterial")
        
        # Test serialization
        material_dict = elastic_material.to_dict()
        self.assertEqual(material_dict["id"], 1)
        self.assertEqual(material_dict["properties"]["elastic_modulus"], 200000.0)
        
        # Test deserialization
        material_copy = ElasticMaterial.from_dict(material_dict)
        self.assertEqual(material_copy.id, elastic_material.id)
        self.assertEqual(material_copy.elastic_modulus, elastic_material.elastic_modulus)
    
    def test_elastic_isotropic_material(self):
        """Test elastic isotropic material creation and properties."""
        metadata = ModelMetadata(name="Test Isotropic Material")
        isotropic_material = ElasticIsotropicMaterial(
            id=2,
            metadata=metadata,
            elastic_modulus=200000.0,
            poisson_ratio=0.3
        )
        
        self.assertEqual(isotropic_material.elastic_modulus, 200000.0)
        self.assertEqual(isotropic_material.poisson_ratio, 0.3)
        self.assertAlmostEqual(isotropic_material.get_shear_modulus(), 76923.08, delta=0.1)
        
        # Test OpenSees code generation
        tcl_code = isotropic_material.to_opensees_tcl()
        self.assertIn("nDMaterial ElasticIsotropic 2 200000.0 0.3", tcl_code)
        
        py_code = isotropic_material.to_opensees_py()
        self.assertIn("ops.nDMaterial('ElasticIsotropic', 2, 200000.0, 0.3)", py_code)
    
    def test_steel_material(self):
        """Test steel material creation and properties."""
        metadata = ModelMetadata(name="Test Steel")
        steel = SteelMaterial(
            id=3,
            metadata=metadata,
            yield_stress=250.0
        )
        
        self.assertEqual(steel.elastic_modulus, SteelMaterial.DEFAULT_ELASTIC_MODULUS)
        self.assertEqual(steel.poisson_ratio, SteelMaterial.DEFAULT_POISSON_RATIO)
        self.assertEqual(steel.yield_stress, 250.0)
        self.assertEqual(steel.density, SteelMaterial.DEFAULT_DENSITY)
    
    def test_concrete_material(self):
        """Test concrete material creation and properties."""
        metadata = ModelMetadata(name="Test Concrete")
        concrete = ConcreteMaterial(
            id=4,
            metadata=metadata,
            compressive_strength=30.0
        )
        
        self.assertEqual(concrete.compressive_strength, 30.0)
        self.assertEqual(concrete.tensile_strength, 3.0)  # 10% of compressive strength
        # Calculated by ACI formula: E = 4700*sqrt(f'c)
        self.assertAlmostEqual(concrete.elastic_modulus, 4700.0 * (30.0 ** 0.5), delta=0.1)
    
    def test_material_factory(self):
        """Test material factory creates different material types."""
        metadata = ModelMetadata(name="Factory Test Material")
        
        # Create an elastic material
        elastic_props = {"elastic_modulus": 210000.0}
        elastic = MaterialFactory.create_material("ElasticMaterial", 10, metadata, elastic_props)
        self.assertEqual(elastic.get_material_type(), "ElasticMaterial")
        self.assertEqual(elastic.elastic_modulus, 210000.0)
        
        # Create a steel material
        steel_props = {"yield_stress": 350.0, "elastic_modulus": 200000.0}
        steel = MaterialFactory.create_material("SteelMaterial", 11, metadata, steel_props)
        self.assertEqual(steel.get_material_type(), "SteelMaterial")
        self.assertEqual(steel.yield_stress, 350.0)
        
        # Create a concrete material
        concrete_props = {"compressive_strength": 40.0}
        concrete = MaterialFactory.create_material("ConcreteMaterial", 12, metadata, concrete_props)
        self.assertEqual(concrete.get_material_type(), "ConcreteMaterial")
        self.assertEqual(concrete.compressive_strength, 40.0)


if __name__ == '__main__':
    unittest.main() 
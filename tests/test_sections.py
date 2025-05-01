"""
Tests for section models.

This module contains tests for section classes.
"""

import unittest
import math
from typing import Dict, Any

from model.base.core import ModelMetadata
from model.sections.base import Section
from model.sections.rectangle import RectangularSection, RectangularFiberSection
from model.sections.circular import CircularSection, CircularHollowSection
from model.sections.profile import ISection, WideFlange, Channel
from model.sections.factory import SectionFactory


class TestSectionModels(unittest.TestCase):
    """Test cases for section models."""
    
    def test_rectangular_section(self):
        """Test rectangular section creation and properties."""
        metadata = ModelMetadata(name="Test Rectangle")
        rect = RectangularSection(
            id=1,
            metadata=metadata,
            width=200.0,
            height=300.0,
            material_ids=[1]
        )
        
        # Basic properties
        self.assertEqual(rect.width, 200.0)
        self.assertEqual(rect.height, 300.0)
        self.assertEqual(rect.material_ids, [1])
        
        # Derived properties
        self.assertEqual(rect.area(), 60000.0)  # 200 * 300
        self.assertAlmostEqual(rect.moment_of_inertia()["Ixx"], 450000000.0)  # bh³/12
        self.assertAlmostEqual(rect.moment_of_inertia()["Iyy"], 200000000.0)  # hb³/12
        
        # Validation
        self.assertTrue(rect.validate())
    
    def test_circular_section(self):
        """Test circular section creation and properties."""
        metadata = ModelMetadata(name="Test Circle")
        circle = CircularSection(
            id=2,
            metadata=metadata,
            diameter=100.0,
            material_ids=[1]
        )
        
        # Basic properties
        self.assertEqual(circle.diameter, 100.0)
        self.assertEqual(circle.material_ids, [1])
        
        # Derived properties
        expected_area = math.pi * 50**2
        self.assertAlmostEqual(circle.area(), expected_area)
        
        expected_i = math.pi * 50**4 / 4
        self.assertAlmostEqual(circle.moment_of_inertia()["Ixx"], expected_i)
        self.assertAlmostEqual(circle.moment_of_inertia()["Iyy"], expected_i)
        
        # Validation
        self.assertTrue(circle.validate())
    
    def test_wide_flange_section(self):
        """Test wide flange section creation and properties."""
        metadata = ModelMetadata(name="Test W-Section")
        wf = WideFlange(
            id=3,
            metadata=metadata,
            height=300.0,
            flange_width=200.0,
            web_thickness=10.0,
            flange_thickness=15.0,
            material_ids=[1]
        )
        
        # Basic properties
        self.assertEqual(wf.height, 300.0)
        self.assertEqual(wf.flange_width, 200.0)
        self.assertEqual(wf.web_thickness, 10.0)
        self.assertEqual(wf.flange_thickness, 15.0)
        self.assertEqual(wf.material_ids, [1])
        
        # Validate the area calculation
        expected_area = 200.0 * 15.0 * 2 + 10.0 * (300.0 - 2 * 15.0)
        self.assertAlmostEqual(wf.area(), expected_area)
        
        # Validation
        self.assertTrue(wf.validate())
    
    def test_section_factory(self):
        """Test section factory creates different section types."""
        metadata = ModelMetadata(name="Factory Test Section")
        
        # Create a rectangular section
        rect_props = {"width": 100.0, "height": 200.0, "material_ids": [1]}
        rect = SectionFactory.create_section("RectangularSection", 10, metadata, rect_props)
        self.assertEqual(rect.get_section_type(), "RectangularSection")
        self.assertEqual(rect.width, 100.0)
        self.assertEqual(rect.height, 200.0)
        
        # Create a circular section
        circ_props = {"diameter": 150.0, "material_ids": [1]}
        circ = SectionFactory.create_section("CircularSection", 11, metadata, circ_props)
        self.assertEqual(circ.get_section_type(), "CircularSection")
        self.assertEqual(circ.diameter, 150.0)
        
        # Create a wide flange section
        wf_props = {
            "height": 300.0,
            "flange_width": 200.0,
            "web_thickness": 10.0,
            "flange_thickness": 15.0,
            "material_ids": [1]
        }
        wf = SectionFactory.create_section("WideFlange", 12, metadata, wf_props)
        self.assertEqual(wf.get_section_type(), "WideFlange")
        self.assertEqual(wf.height, 300.0)
        
        # Test convenience methods
        rect2 = SectionFactory.create_rectangular_section(
            id=20,
            metadata=metadata,
            width=120.0,
            height=240.0,
            material_ids=[1]
        )
        self.assertEqual(rect2.get_section_type(), "RectangularSection")
        self.assertEqual(rect2.width, 120.0)
        
        # Test invalid section type
        with self.assertRaises(ValueError):
            SectionFactory.create_section("NonExistentType", 13, metadata, {})
    
    def test_circular_hollow_section(self):
        """Test circular hollow section creation and properties."""
        metadata = ModelMetadata(name="Test Hollow Circle")
        hollow = CircularHollowSection(
            id=4,
            metadata=metadata,
            outer_diameter=100.0,
            wall_thickness=10.0,
            material_ids=[1]
        )
        
        # Basic properties
        self.assertEqual(hollow.outer_diameter, 100.0)
        self.assertEqual(hollow.wall_thickness, 10.0)
        self.assertEqual(hollow.inner_diameter, 80.0)  # 100 - 2*10
        
        # Derived properties
        expected_area = math.pi * (50**2 - 40**2)
        self.assertAlmostEqual(hollow.area(), expected_area)
        
        # Validation
        self.assertTrue(hollow.validate())
    
    def test_channel_section(self):
        """Test channel section creation and properties."""
        metadata = ModelMetadata(name="Test Channel")
        channel = Channel(
            id=5,
            metadata=metadata,
            height=200.0,
            flange_width=75.0,
            web_thickness=8.0,
            flange_thickness=12.0,
            material_ids=[1]
        )
        
        # Basic properties
        self.assertEqual(channel.height, 200.0)
        self.assertEqual(channel.flange_width, 75.0)
        self.assertEqual(channel.web_thickness, 8.0)
        self.assertEqual(channel.flange_thickness, 12.0)
        
        # Derived properties
        expected_area = 8.0 * 200.0 + 2 * 75.0 * 12.0 - 2 * 8.0 * 12.0
        self.assertAlmostEqual(channel.area(), expected_area)
        
        # Validation
        self.assertTrue(channel.validate())
    
    def test_section_serialization(self):
        """Test section serialization to and from dictionary."""
        metadata = ModelMetadata(name="Serialization Test")
        
        # Create a section
        original = RectangularSection(
            id=30,
            metadata=metadata,
            width=120.0,
            height=240.0,
            material_ids=[1, 2],
            properties={"custom_prop": "test"}
        )
        
        # Serialize to dictionary
        data = original.to_dict()
        
        # Deserialize from dictionary
        deserialized = RectangularSection.from_dict(data)
        
        # Check if they match
        self.assertEqual(deserialized.id, original.id)
        self.assertEqual(deserialized.metadata.name, original.metadata.name)
        self.assertEqual(deserialized.width, original.width)
        self.assertEqual(deserialized.height, original.height)
        self.assertEqual(deserialized.material_ids, original.material_ids)
        self.assertEqual(deserialized.properties.get("custom_prop"), "test")
    
    def test_section_validation(self):
        """Test section validation logic."""
        metadata = ModelMetadata(name="Validation Test")
        
        # Valid section
        valid = RectangularSection(
            id=40,
            metadata=metadata,
            width=100.0,
            height=200.0,
            material_ids=[1]
        )
        self.assertTrue(valid.validate())
        
        # Invalid - negative width
        invalid1 = RectangularSection(
            id=41,
            metadata=metadata,
            width=-10.0,
            height=200.0,
            material_ids=[1]
        )
        self.assertFalse(invalid1.validate())
        
        # Invalid - no material IDs
        invalid2 = RectangularSection(
            id=42,
            metadata=metadata,
            width=100.0,
            height=200.0,
            material_ids=[]
        )
        self.assertFalse(invalid2.validate())


if __name__ == '__main__':
    unittest.main() 
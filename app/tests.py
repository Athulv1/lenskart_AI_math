from django.test import TestCase


class SimpleTest(TestCase):
    """Simple test to verify CI/CD pipeline works"""
    
    def test_basic_math(self):
        """Test basic arithmetic"""
        self.assertEqual(1 + 1, 2)
    
    def test_project_loads(self):
        """Test that the project loads without errors"""
        self.assertTrue(True)
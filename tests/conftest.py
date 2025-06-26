#!/usr/bin/env python3
"""
Pytest configuration file for PDF Cracker tests.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path for imports
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

# Test configuration
def pytest_configure(config):
    """Configure pytest."""
    # Add custom markers
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")

# Test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    # Auto-mark tests based on name patterns
    for item in items:
        if "integration" in item.nodeid.lower():
            item.add_marker("integration")
        elif "test_" in item.name:
            item.add_marker("unit")
        
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ["generate", "wordlist", "large"]):
            item.add_marker("slow")
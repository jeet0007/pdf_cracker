#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for PDF Cracker tests.
"""

import sys
import os
import tempfile
from pathlib import Path
import pytest

# Add src directory to Python path for imports
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing (minimal PDF)."""
    # This is a minimal PDF content for testing
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Hello, World!) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000107 00000 n 
0000000179 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
274
%%EOF"""


@pytest.fixture
def sample_pdf_file(temp_file, sample_pdf_content):
    """Create a sample PDF file for testing."""
    with open(temp_file, 'wb') as f:
        f.write(sample_pdf_content)
    return temp_file


# Custom markers for test categorization
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "unit: marks unit tests")
    config.addinivalue_line("markers", "external: marks tests requiring external tools")


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on patterns."""
    for item in items:
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ["generate", "wordlist", "large"]):
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.nodeid.lower() or any(
            keyword in item.name.lower() for keyword in ["cli", "subprocess", "end_to_end"]
        ):
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
        
        # Mark external dependency tests
        if any(keyword in item.name.lower() for keyword in ["john", "crunch", "pdf2john"]):
            item.add_marker(pytest.mark.external)
#!/usr/bin/env python3
"""
Tests for PDF processor module.
"""

import tempfile
import os
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.pdf_processor import PDFProcessor, PDFHashManager


class TestPDFProcessor:
    """Test the PDFProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create PDFProcessor with mocked pdf2john path."""
        with patch.object(PDFProcessor, '_find_pdf2john') as mock_find:
            mock_find.return_value = '/opt/homebrew/share/john/pdf2john.pl'
            return PDFProcessor()
    
    def test_find_pdf2john_existing_path(self):
        """Test finding pdf2john when it exists."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = lambda path: path == '/usr/share/john/pdf2john.pl'
            
            processor = PDFProcessor()
            assert processor.pdf2john_path == '/usr/share/john/pdf2john.pl'
    
    def test_find_pdf2john_not_found(self):
        """Test pdf2john not found scenario."""
        with patch('os.path.exists', return_value=False), \
             patch('glob.glob', return_value=[]), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 1  # Command failed
            
            with pytest.raises(FileNotFoundError):
                PDFProcessor()
    
    @patch('subprocess.run')
    def test_extract_hash_success(self, mock_run, processor):
        """Test successful hash extraction."""
        # Mock subprocess result
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        mock_run.return_value.stderr = ""
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            result = processor.extract_hash(temp_pdf.name)
            assert result == "test.pdf:$pdf$4*4*128*-1024*1*16*..."
    
    @patch('subprocess.run')
    def test_extract_hash_file_not_found(self, mock_run, processor):
        """Test hash extraction with non-existent file."""
        with pytest.raises(FileNotFoundError):
            processor.extract_hash("/non/existent/file.pdf")
    
    @patch('subprocess.run')
    def test_extract_hash_extraction_failed(self, mock_run, processor):
        """Test hash extraction failure."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pdf2john')
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            with pytest.raises(RuntimeError):
                processor.extract_hash(temp_pdf.name)
    
    @patch('subprocess.run')
    def test_extract_hash_empty_output(self, mock_run, processor):
        """Test hash extraction with empty output."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            with pytest.raises(RuntimeError):
                processor.extract_hash(temp_pdf.name)
    
    @patch('subprocess.run')
    def test_save_hash_to_file(self, mock_run, processor, sample_pdf_content):
        """Test saving hash to file."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        mock_run.return_value.stderr = ""
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(sample_pdf_content)
            temp_pdf_path = temp_pdf.name
            
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_hash:
            temp_hash_path = temp_hash.name
            
        try:
            result = processor.save_hash_to_file(temp_pdf_path, temp_hash_path)
            
            # Check return value
            assert result == "test.pdf:$pdf$4*4*128*-1024*1*16*..."
            
            # Check file contents
            with open(temp_hash_path, 'r') as f:
                content = f.read()
            assert content.strip() == "test.pdf:$pdf$4*4*128*-1024*1*16*..."
            
        finally:
            if os.path.exists(temp_hash_path):
                os.unlink(temp_hash_path)
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
    
    @patch.object(PDFProcessor, 'extract_hash')
    def test_is_pdf_protected_true(self, mock_extract, processor):
        """Test PDF protection check - protected."""
        mock_extract.return_value = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            result = processor.is_pdf_protected(temp_pdf.name)
            assert result
    
    @patch.object(PDFProcessor, 'extract_hash')
    def test_is_pdf_protected_false(self, mock_extract, processor):
        """Test PDF protection check - not protected."""
        mock_extract.side_effect = RuntimeError("No hash")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            result = processor.is_pdf_protected(temp_pdf.name)
            assert not result
    
    @patch.object(PDFProcessor, 'extract_hash')
    @patch.object(PDFProcessor, 'is_pdf_protected')
    def test_get_pdf_info(self, mock_protected, mock_extract, processor, sample_pdf_content):
        """Test getting PDF information."""
        mock_protected.return_value = True
        mock_extract.return_value = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        
        # Create a temporary PDF file with actual content
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(sample_pdf_content)
            temp_pdf_path = temp_pdf.name
            
        try:
            info = processor.get_pdf_info(temp_pdf_path)
            
            assert info['path'] == temp_pdf_path
            assert info['exists']
            assert info['protected']
            assert info['hash'] == "test.pdf:$pdf$4*4*128*-1024*1*16*..."
            assert info['size'] > 0
        finally:
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)


class TestPDFHashManager:
    """Test the PDFHashManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create PDFHashManager with mocked pdf2john path."""
        with patch.object(PDFProcessor, '_find_pdf2john') as mock_find:
            mock_find.return_value = '/opt/homebrew/share/john/pdf2john.pl'
            return PDFHashManager(temp_dir)
    
    @patch.object(PDFProcessor, 'save_hash_to_file')
    def test_add_pdf(self, mock_save, manager):
        """Test adding PDF to batch."""
        mock_save.return_value = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            hash_file = manager.add_pdf(temp_pdf.name, "test")
            
            assert "test" in manager.hash_files
            assert manager.hash_files["test"]["pdf_path"] == temp_pdf.name
            assert hash_file.endswith("test.hash")
    
    @patch.object(PDFProcessor, 'save_hash_to_file')
    def test_get_combined_hash_file(self, mock_save, manager):
        """Test creating combined hash file."""
        mock_save.return_value = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf1, \
             tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf2:
            
            manager.add_pdf(temp_pdf1.name, "test1")
            manager.add_pdf(temp_pdf2.name, "test2")
            
            combined_file = manager.get_combined_hash_file()
            
            assert os.path.exists(combined_file)
            
            with open(combined_file, 'r') as f:
                lines = f.readlines()
            
            assert len(lines) == 2
    
    def test_context_manager(self, temp_dir):
        """Test context manager functionality."""
        with PDFHashManager(temp_dir) as manager:
            assert isinstance(manager, PDFHashManager)
        # Should clean up automatically


if __name__ == '__main__':
    import subprocess
    pytest.main([__file__])
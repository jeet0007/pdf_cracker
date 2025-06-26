#!/usr/bin/env python3
"""
Tests for PDF processor module.
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.pdf_processor import PDFProcessor, PDFHashManager


class TestPDFProcessor(unittest.TestCase):
    """Test the PDFProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the pdf2john path finding since we don't have actual PDFs for testing
        with patch.object(PDFProcessor, '_find_pdf2john') as mock_find:
            mock_find.return_value = '/opt/homebrew/share/john/pdf2john.pl'
            self.processor = PDFProcessor()
    
    def test_find_pdf2john_existing_path(self):
        """Test finding pdf2john when it exists."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = lambda path: path == '/usr/share/john/pdf2john.pl'
            
            processor = PDFProcessor()
            self.assertEqual(processor.pdf2john_path, '/usr/share/john/pdf2john.pl')
    
    def test_find_pdf2john_not_found(self):
        """Test pdf2john not found scenario."""
        with patch('os.path.exists', return_value=False), \
             patch('glob.glob', return_value=[]), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 1  # Command failed
            
            with self.assertRaises(FileNotFoundError):
                PDFProcessor()
    
    @patch('subprocess.run')
    def test_extract_hash_success(self, mock_run):
        """Test successful hash extraction."""
        # Mock subprocess result
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        mock_run.return_value.stderr = ""
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            result = self.processor.extract_hash(temp_pdf.name)
            self.assertEqual(result, "test.pdf:$pdf$4*4*128*-1024*1*16*...")
    
    @patch('subprocess.run')
    def test_extract_hash_file_not_found(self, mock_run):
        """Test hash extraction with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.processor.extract_hash("/non/existent/file.pdf")
    
    @patch('subprocess.run')
    def test_extract_hash_extraction_failed(self, mock_run):
        """Test hash extraction failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pdf2john')
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            with self.assertRaises(RuntimeError):
                self.processor.extract_hash(temp_pdf.name)
    
    @patch('subprocess.run')
    def test_extract_hash_empty_output(self, mock_run):
        """Test hash extraction with empty output."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            with self.assertRaises(RuntimeError):
                self.processor.extract_hash(temp_pdf.name)
    
    @patch('subprocess.run')
    def test_save_hash_to_file(self, mock_run):
        """Test saving hash to file."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        mock_run.return_value.stderr = ""
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf, \
             tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_hash:
            
            temp_hash_path = temp_hash.name
            
        try:
            result = self.processor.save_hash_to_file(temp_pdf.name, temp_hash_path)
            
            # Check return value
            self.assertEqual(result, "test.pdf:$pdf$4*4*128*-1024*1*16*...")
            
            # Check file contents
            with open(temp_hash_path, 'r') as f:
                content = f.read()
            self.assertEqual(content.strip(), "test.pdf:$pdf$4*4*128*-1024*1*16*...")
            
        finally:
            if os.path.exists(temp_hash_path):
                os.unlink(temp_hash_path)
    
    @patch.object(PDFProcessor, 'extract_hash')
    def test_is_pdf_protected_true(self, mock_extract):
        """Test PDF protection check - protected."""
        mock_extract.return_value = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            result = self.processor.is_pdf_protected(temp_pdf.name)
            self.assertTrue(result)
    
    @patch.object(PDFProcessor, 'extract_hash')
    def test_is_pdf_protected_false(self, mock_extract):
        """Test PDF protection check - not protected."""
        mock_extract.side_effect = RuntimeError("No hash")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            result = self.processor.is_pdf_protected(temp_pdf.name)
            self.assertFalse(result)
    
    @patch.object(PDFProcessor, 'extract_hash')
    @patch.object(PDFProcessor, 'is_pdf_protected')
    def test_get_pdf_info(self, mock_protected, mock_extract):
        """Test getting PDF information."""
        mock_protected.return_value = True
        mock_extract.return_value = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            info = self.processor.get_pdf_info(temp_pdf.name)
            
            self.assertEqual(info['path'], temp_pdf.name)
            self.assertTrue(info['exists'])
            self.assertTrue(info['protected'])
            self.assertEqual(info['hash'], "test.pdf:$pdf$4*4*128*-1024*1*16*...")
            self.assertGreater(info['size'], 0)


class TestPDFHashManager(unittest.TestCase):
    """Test the PDFHashManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        with patch.object(PDFProcessor, '_find_pdf2john') as mock_find:
            mock_find.return_value = '/opt/homebrew/share/john/pdf2john.pl'
            self.manager = PDFHashManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.object(PDFProcessor, 'save_hash_to_file')
    def test_add_pdf(self, mock_save):
        """Test adding PDF to batch."""
        mock_save.return_value = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            hash_file = self.manager.add_pdf(temp_pdf.name, "test")
            
            self.assertIn("test", self.manager.hash_files)
            self.assertEqual(self.manager.hash_files["test"]["pdf_path"], temp_pdf.name)
            self.assertTrue(hash_file.endswith("test.hash"))
    
    @patch.object(PDFProcessor, 'save_hash_to_file')
    def test_get_combined_hash_file(self, mock_save):
        """Test creating combined hash file."""
        mock_save.return_value = "test.pdf:$pdf$4*4*128*-1024*1*16*..."
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf1, \
             tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf2:
            
            self.manager.add_pdf(temp_pdf1.name, "test1")
            self.manager.add_pdf(temp_pdf2.name, "test2")
            
            combined_file = self.manager.get_combined_hash_file()
            
            self.assertTrue(os.path.exists(combined_file))
            
            with open(combined_file, 'r') as f:
                lines = f.readlines()
            
            self.assertEqual(len(lines), 2)
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with PDFHashManager(self.temp_dir) as manager:
            self.assertIsInstance(manager, PDFHashManager)
        # Should clean up automatically


if __name__ == '__main__':
    # Import subprocess here to avoid issues with mocking
    import subprocess
    unittest.main()
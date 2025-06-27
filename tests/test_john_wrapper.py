#!/usr/bin/env python3
"""
Tests for John the Ripper wrapper module.
"""

import tempfile
import os
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.john_wrapper import JohnWrapper, PDFCracker, CrackResult


class TestCrackResult:
    """Test the CrackResult dataclass."""
    
    def test_crack_result_success(self):
        """Test successful crack result."""
        result = CrackResult(
            success=True,
            password="12345678",
            time_taken=10.5,
            attempts=1000
        )
        
        assert result.success
        assert result.password == "12345678"
        assert result.time_taken == 10.5
        assert result.attempts == 1000
        assert result.error is None
    
    def test_crack_result_failure(self):
        """Test failed crack result."""
        result = CrackResult(
            success=False,
            error="No password found",
            time_taken=60.0,
            attempts=10000
        )
        
        assert not result.success
        assert result.password is None
        assert result.error == "No password found"
        assert result.time_taken == 60.0
        assert result.attempts == 10000


class TestJohnWrapper:
    """Test the JohnWrapper class."""
    
    @pytest.fixture
    def john_wrapper(self):
        """Create JohnWrapper with mocked john path."""
        with patch.object(JohnWrapper, '_find_john') as mock_find:
            mock_find.return_value = '/usr/bin/john'
            return JohnWrapper()
    
    def test_find_john_existing_path(self):
        """Test finding John when it exists."""
        with patch('os.path.exists') as mock_exists, \
             patch('subprocess.run') as mock_run:
            
            mock_exists.side_effect = lambda path: path == '/usr/bin/john'
            mock_run.return_value.returncode = 0
            
            john = JohnWrapper()
            assert john.john_path is not None
    
    def test_find_john_not_found(self):
        """Test John not found scenario."""
        with patch('os.path.exists', return_value=False), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 1
            
            with pytest.raises(FileNotFoundError):
                JohnWrapper()
    
    @patch('subprocess.Popen')
    def test_crack_hash_success(self, mock_popen, john_wrapper, temp_file):
        """Test successful hash cracking."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        mock_process.poll.return_value = 0
        mock_popen.return_value = mock_process
        
        with patch.object(john_wrapper, '_get_cracked_password') as mock_get_pwd:
            mock_get_pwd.return_value = "12345678"
            
            with tempfile.NamedTemporaryFile() as wordlist_file:
                result = john_wrapper.crack_hash(temp_file, wordlist_file.name)
                
                assert result.success
                assert result.password == "12345678"
                assert result.time_taken > 0
    
    @patch('subprocess.Popen')
    def test_crack_hash_failure(self, mock_popen, john_wrapper, temp_file):
        """Test failed hash cracking."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("", "Error: no passwords")
        mock_process.returncode = 1
        mock_process.poll.return_value = 1
        mock_popen.return_value = mock_process
        
        with tempfile.NamedTemporaryFile() as wordlist_file:
            result = john_wrapper.crack_hash(temp_file, wordlist_file.name)
            
            assert not result.success
            assert result.password is None
            assert "Error:" in result.error
    
    @patch('subprocess.run')
    def test_get_cracked_password_success(self, mock_run, john_wrapper, temp_file):
        """Test extracting cracked password."""
        mock_run.return_value.stdout = "test.pdf:password123\n1 password hash cracked"
        mock_run.return_value.returncode = 0
        
        password = john_wrapper._get_cracked_password(temp_file)
        assert password == "password123"
    
    @patch('subprocess.run')
    def test_get_cracked_password_no_result(self, mock_run, john_wrapper, temp_file):
        """Test extracting password when none found."""
        mock_run.return_value.stdout = ""
        mock_run.return_value.returncode = 0
        
        password = john_wrapper._get_cracked_password(temp_file)
        assert password is None
    
    def test_stop_cracking(self, john_wrapper):
        """Test stopping cracking process."""
        mock_process = MagicMock()
        john_wrapper._current_process = mock_process
        
        john_wrapper.stop()
        
        assert john_wrapper._stop_requested
        mock_process.terminate.assert_called_once()


class TestPDFCracker:
    """Test the PDFCracker class."""
    
    @pytest.fixture
    def pdf_cracker(self):
        """Create PDFCracker with mocked dependencies."""
        with patch.object(JohnWrapper, '_find_john') as mock_find_john, \
             patch('core.john_wrapper.PDFProcessor') as mock_pdf_processor:
            
            mock_find_john.return_value = '/usr/bin/john'
            return PDFCracker()
    
    def test_crack_pdf_file_not_found(self, pdf_cracker):
        """Test cracking non-existent PDF."""
        result = pdf_cracker.crack_pdf("non_existent.pdf", "wordlist.txt")
        
        assert not result.success
        assert "not found" in result.error
    
    @patch('pathlib.Path.exists')
    def test_crack_pdf_not_protected(self, mock_exists, pdf_cracker):
        """Test cracking unprotected PDF."""
        mock_exists.return_value = True
        pdf_cracker.pdf_processor.is_pdf_protected.return_value = False
        
        result = pdf_cracker.crack_pdf("test.pdf", "wordlist.txt")
        
        assert result.success
        assert result.password is None
        assert result.time_taken == 0.0
        assert result.attempts == 0
    
    @patch('pathlib.Path.exists')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.path.exists')
    @patch('os.unlink')
    def test_crack_pdf_success(self, mock_unlink, mock_path_exists, mock_temp, mock_pdf_exists, pdf_cracker):
        """Test successful PDF cracking."""
        mock_pdf_exists.return_value = True
        mock_path_exists.return_value = True
        
        mock_hash_file = MagicMock()
        mock_hash_file.name = "/tmp/test.hash"
        mock_temp.return_value.__enter__.return_value = mock_hash_file
        
        pdf_cracker.pdf_processor.is_pdf_protected.return_value = True
        pdf_cracker.pdf_processor.extract_hash.return_value = "test.pdf:$pdf$..."
        
        mock_result = CrackResult(success=True, password="12345678", time_taken=10.0)
        with patch.object(pdf_cracker.john, 'crack_hash') as mock_crack:
            mock_crack.return_value = mock_result
            
            result = pdf_cracker.crack_pdf("test.pdf", "wordlist.txt")
            
            assert result.success
            assert result.password == "12345678"
    
    @patch('pathlib.Path.exists')
    @patch('tempfile.NamedTemporaryFile')
    def test_crack_pdf_extraction_error(self, mock_temp, mock_exists, pdf_cracker):
        """Test PDF cracking with hash extraction error."""
        mock_exists.return_value = True
        
        mock_hash_file = MagicMock()
        mock_hash_file.name = "/tmp/test.hash"
        mock_temp.return_value.__enter__.return_value = mock_hash_file
        
        pdf_cracker.pdf_processor.is_pdf_protected.return_value = True
        pdf_cracker.pdf_processor.extract_hash.side_effect = Exception("Hash extraction failed")
        
        result = pdf_cracker.crack_pdf("test.pdf", "wordlist.txt")
        
        assert not result.success
        assert "Hash extraction failed" in result.error
    
    def test_stop(self, pdf_cracker):
        """Test stopping cracking process."""
        with patch.object(pdf_cracker.john, 'stop') as mock_stop:
            pdf_cracker.stop()
            mock_stop.assert_called_once()
#!/usr/bin/env python3
"""
Tests for Crunch wrapper module - focuses on number generation only.
"""

import os
import sys
from unittest.mock import patch
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.crunch_wrapper import CrunchWrapper


class TestCrunchWrapper:
    """Test the CrunchWrapper class for number generation."""
    
    @pytest.fixture
    def crunch_with_mock(self):
        """Create CrunchWrapper with mocked crunch path."""
        with patch.object(CrunchWrapper, '_find_crunch') as mock_find:
            mock_find.return_value = '/usr/bin/crunch'
            return CrunchWrapper()
    
    def test_find_crunch_existing_path(self):
        """Test finding crunch when it exists."""
        with patch('os.path.exists') as mock_exists, \
             patch('subprocess.run') as mock_run:
            
            mock_exists.side_effect = lambda path: path == '/usr/bin/crunch'
            mock_run.return_value.returncode = 0
            
            crunch = CrunchWrapper()
            assert crunch.crunch_path is not None
            assert crunch.has_crunch
    
    def test_find_crunch_not_found(self):
        """Test crunch not found scenario."""
        with patch('os.path.exists', return_value=False), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 1
            
            crunch = CrunchWrapper()
            assert crunch.crunch_path is None
            assert not crunch.has_crunch
    
    @patch('subprocess.run')
    def test_generate_number_range_with_crunch(self, mock_run, temp_file):
        """Test number range generation using crunch."""
        mock_run.return_value.returncode = 0
        
        crunch = CrunchWrapper()
        crunch.has_crunch = True
        crunch.crunch_path = '/usr/bin/crunch'
        
        result = crunch.generate_number_range(temp_file, 0, 9999, 4)
        
        assert result
        mock_run.assert_called()
        
        # Verify crunch was called with correct parameters
        call_args = mock_run.call_args[0][0]
        assert '/usr/bin/crunch' in call_args
        assert '4' in call_args  # min length
        assert '4' in call_args  # max length
        assert '0123456789' in call_args  # character set
    
    def test_generate_number_range_python_fallback(self, temp_file):
        """Test number range generation using Python fallback."""
        crunch = CrunchWrapper()
        crunch.has_crunch = False
        
        result = crunch.generate_number_range(temp_file, 0, 99, 4)
        
        assert result
        assert os.path.exists(temp_file)
        
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 100
        assert lines[0].strip() == "0000"
        assert lines[-1].strip() == "0099"
    
    def test_generate_number_range_with_progress(self, temp_file):
        """Test number range generation with progress callback."""
        crunch = CrunchWrapper()
        crunch.has_crunch = False
        
        progress_calls = []
        
        def progress_callback(progress, message):
            progress_calls.append((progress, message))
        
        result = crunch.generate_number_range(temp_file, 0, 99, 4, progress_callback)
        
        assert result
        assert len(progress_calls) > 0
        
        final_progress, final_message = progress_calls[-1]
        assert final_progress == 100
        assert "complete" in final_message.lower()
    
    @pytest.mark.parametrize("min_num,max_num,digits,expected_count", [
        (0, 9, 2, 10),         # 00-09
        (0, 99, 3, 100),       # 000-099  
        (1000, 1009, 4, 10),   # 1000-1009
    ])
    def test_number_range_parameters(self, temp_file, min_num, max_num, digits, expected_count):
        """Test number range generation with different parameters."""
        crunch = CrunchWrapper()
        crunch.has_crunch = False
        
        result = crunch.generate_number_range(temp_file, min_num, max_num, digits)
        
        assert result
        
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == expected_count
        
        # Check first and last entries have correct format
        first_line = lines[0].strip()
        last_line = lines[-1].strip()
        
        assert len(first_line) == digits
        assert len(last_line) == digits
        assert first_line == f"{min_num:0{digits}d}"
        assert last_line == f"{max_num:0{digits}d}"
    
    @patch('subprocess.run')
    def test_crunch_command_failure_fallback(self, mock_run, temp_file):
        """Test fallback to Python when crunch command fails."""
        # First call (crunch) fails, should fallback to Python
        mock_run.return_value.returncode = 1
        
        crunch = CrunchWrapper()
        crunch.has_crunch = True
        crunch.crunch_path = '/usr/bin/crunch'
        
        result = crunch.generate_number_range(temp_file, 0, 9, 2)
        
        # Should still succeed via Python fallback
        assert result
        assert os.path.exists(temp_file)
        
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 10
        assert lines[0].strip() == "00"
        assert lines[-1].strip() == "09"
    
    def test_number_generation_edge_cases(self, temp_file):
        """Test edge cases in number generation."""
        crunch = CrunchWrapper()
        crunch.has_crunch = False
        
        # Single number range
        result = crunch.generate_number_range(temp_file, 5, 5, 2)
        assert result
        
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 1
        assert lines[0].strip() == "05"
    
    def test_crunch_initialization(self):
        """Test CrunchWrapper initialization."""
        crunch = CrunchWrapper()
        assert hasattr(crunch, 'crunch_path')
        assert hasattr(crunch, 'has_crunch')
        assert isinstance(crunch.has_crunch, bool)
    
    @patch('subprocess.run')
    def test_crunch_which_command_check(self, mock_run):
        """Test crunch path detection using which command."""
        # Simulate crunch found via 'which' command
        mock_run.return_value.returncode = 0
        
        with patch('os.path.exists', return_value=False):
            crunch = CrunchWrapper()
            # Should find crunch via which command even if not in standard paths
            assert mock_run.called


if __name__ == '__main__':
    pytest.main([__file__])
#!/usr/bin/env python3
"""
Tests for Crunch wrapper module.
"""

from core.crunch_wrapper import CrunchWrapper
import tempfile
import os
from pathlib import Path
import sys
from unittest.mock import patch
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestCrunchWrapper:
    """Test the CrunchWrapper class."""

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
    def test_generate_date_wordlist_with_crunch(self, mock_run, crunch_with_mock, temp_file):
        """Test date wordlist generation using crunch."""
        mock_run.return_value.returncode = 0

        result = crunch_with_mock.generate_date_wordlist(
            temp_file, 2023, 2023, "DDMMYYYY"
        )

        assert result
        mock_run.assert_called()

    def test_generate_date_wordlist_python_fallback(self, temp_file):
        """Test date wordlist generation using Python fallback."""
        crunch = CrunchWrapper()
        crunch.has_crunch = False

        result = crunch.generate_date_wordlist(
            temp_file, 2023, 2023, "DDMMYYYY"
        )

        assert result
        assert os.path.exists(temp_file)

        with open(temp_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) == 365  # 2023 is not a leap year
        assert lines[0].strip() == "01012023"
        assert lines[-1].strip() == "31122023"

    @pytest.mark.parametrize("date_format,expected_first,expected_length", [
        ("DDMMYY", "010123", 6),
        ("YYYYMMDD", "20230101", 8),
        ("DDMMYYYY", "01012023", 8),
    ])
    def test_date_formats(self, temp_file, date_format, expected_first, expected_length):
        """Test different date formats."""
        crunch = CrunchWrapper()
        crunch.has_crunch = False

        result = crunch.generate_date_wordlist(
            temp_file, 2023, 2023, date_format
        )

        assert result

        with open(temp_file, 'r') as f:
            first_line = f.readline().strip()

        assert len(first_line) == expected_length
        assert first_line == expected_first

    def test_generate_date_wordlist_invalid_format(self, temp_file):
        """Test invalid date format."""
        crunch = CrunchWrapper()
        crunch.has_crunch = False

        result = crunch.generate_date_wordlist(
            temp_file, 2023, 2023, "INVALID"
        )

        assert not result

    @patch('subprocess.run')
    def test_generate_number_range_with_crunch(self, mock_run, temp_file):
        """Test number range generation using crunch."""
        mock_run.return_value.returncode = 0

        crunch = CrunchWrapper()
        crunch.has_crunch = True

        result = crunch.generate_number_range(temp_file, 0, 9999, 4)

        assert result
        mock_run.assert_called()

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

        result = crunch.generate_number_range(
            temp_file, 0, 99, 4, progress_callback)

        assert result
        assert len(progress_calls) > 0

        final_progress, final_message = progress_calls[-1]
        assert final_progress == 100
        assert "complete" in final_message.lower()

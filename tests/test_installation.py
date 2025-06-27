#!/usr/bin/env python3
"""
Installation verification tests for PDF Cracker simplified architecture.
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestInstallation:
    """Test installation and system requirements."""
    
    def test_python_version(self):
        """Test Python version meets requirements."""
        version = sys.version_info
        assert version.major >= 3
        assert version.minor >= 7
    
    @pytest.mark.external
    def test_john_the_ripper_available(self):
        """Test John the Ripper is available."""
        john_available = shutil.which('john') is not None
        
        if not john_available:
            pytest.skip("John the Ripper not found (optional for unit tests)")
        
        try:
            result = subprocess.run(['john', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            assert result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("John the Ripper not properly installed")
    
    @pytest.mark.external 
    def test_pdf2john_available(self):
        """Test pdf2john.pl is available."""
        paths = [
            '/usr/share/john/pdf2john.pl',
            '/opt/homebrew/share/john/pdf2john.pl',
            '/usr/local/share/john/pdf2john.pl'
        ]
        
        import glob
        glob_paths = glob.glob('/opt/homebrew/Cellar/john-jumbo/*/share/john/pdf2john.pl')
        paths.extend(glob_paths)
        
        pdf2john_found = any(Path(path).exists() for path in paths)
        
        if not pdf2john_found:
            pytest.skip("pdf2john.pl not found (needed for actual PDF processing)")
    
    def test_core_modules_import(self):
        """Test all core modules can be imported."""
        try:
            from core.john_wrapper import JohnWrapper, PDFCracker, CrackResult
            from core.crunch_wrapper import CrunchWrapper
            from core.pdf_processor import PDFProcessor
        except ImportError as e:
            pytest.fail(f"Failed to import core modules: {e}")
    
    def test_cli_modules_import(self):
        """Test CLI modules can be imported."""
        try:
            import utils.comprehensive_crack
            import utils.comprehensive_wordlist
            import utils.wordlist_gen
            
            assert hasattr(utils.comprehensive_crack, 'main')
            assert hasattr(utils.comprehensive_wordlist, 'main')
            assert hasattr(utils.wordlist_gen, 'main')
            
        except ImportError as e:
            pytest.fail(f"Failed to import CLI modules: {e}")
    
    def test_module_instantiation(self):
        """Test core modules can be instantiated."""
        from core.crunch_wrapper import CrunchWrapper
        from core.pdf_processor import PDFProcessor
        
        crunch = CrunchWrapper()
        assert crunch is not None
        
        try:
            pdf_proc = PDFProcessor()
            assert pdf_proc is not None
        except FileNotFoundError:
            pytest.skip("PDFProcessor requires pdf2john.pl")
    
    def test_executable_scripts_exist(self):
        """Test executable scripts exist."""
        project_root = Path(__file__).parent.parent
        scripts = [
            'pdf-crack',
            'pdf-comprehensive-wordlist', 
            'pdf-wordlist'
        ]
        
        for script in scripts:
            script_path = project_root / script
            assert script_path.exists(), f"Script {script} not found"
            
            if os.name != 'nt':  # Not Windows
                assert os.access(script_path, os.X_OK), f"Script {script} is not executable"


class TestQuickFunctionality:
    """Quick functionality tests that don't require external dependencies."""
    
    def test_crunch_wrapper_no_crunch(self):
        """Test CrunchWrapper works without crunch installed."""
        from core.crunch_wrapper import CrunchWrapper
        
        crunch = CrunchWrapper()
        assert crunch.has_crunch in [True, False]
    
    @pytest.mark.parametrize("year,expected_days", [
        (2020, 366),  # Leap year
        (2021, 365),  # Not leap year
        (2000, 366),  # Leap year (divisible by 400)
        (1900, 365),  # Not leap year (divisible by 100 but not 400)
    ])
    def test_date_calculation(self, year, expected_days):
        """Test date calculation functions."""
        from utils.wordlist_gen import calculate_date_count
        
        count = calculate_date_count(year, year)
        assert count == expected_days
    
    def test_comprehensive_stats(self):
        """Test comprehensive wordlist statistics."""
        from utils.comprehensive_wordlist import calculate_comprehensive_stats
        
        stats = calculate_comprehensive_stats(1)  # 1 year back
        
        assert 'gregorian_dates' in stats
        assert 'buddhist_dates' in stats
        assert 'numbers' in stats
        assert 'total_passwords' in stats
        
        # Numbers should always be 100 million
        assert stats['numbers'] == 100000000
        
        # Buddhist and Gregorian should have same count
        assert stats['gregorian_dates'] == stats['buddhist_dates']
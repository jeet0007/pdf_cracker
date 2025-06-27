#!/usr/bin/env python3

import subprocess
import os
from pathlib import Path
from typing import Union, Optional, Callable


class CrunchWrapper:
    """Simple wrapper for Crunch wordlist generator - focuses on number ranges and character combinations."""
    
    def __init__(self):
        self.crunch_path = self._find_crunch()
        self.has_crunch = self.crunch_path is not None
    
    def _find_crunch(self) -> Optional[str]:
        """Find Crunch executable."""
        crunch_paths = ['crunch', '/usr/bin/crunch', '/opt/homebrew/bin/crunch']
        
        for path in crunch_paths:
            if os.path.exists(path) or subprocess.run(['which', path], capture_output=True).returncode == 0:
                return path
        
        return None
    
    def generate_number_range(
        self,
        output_path: Union[str, Path],
        min_number: int = 0,
        max_number: int = 99999999,
        digits: int = 8,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> bool:
        """
        Generate number range wordlist.
        
        Args:
            output_path: Output file path
            min_number: Starting number
            max_number: Ending number (inclusive)
            digits: Number of digits (with zero padding)
            progress_callback: Optional progress callback
            
        Returns:
            True if successful, False otherwise
        """
        if self.has_crunch:
            return self._generate_numbers_with_crunch(output_path, digits, progress_callback)
        else:
            return self._generate_numbers_with_python(output_path, min_number, max_number, digits, progress_callback)
    
    def _generate_numbers_with_crunch(
        self,
        output_path: Union[str, Path],
        digits: int,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> bool:
        """Generate numbers using crunch."""
        try:
            if progress_callback:
                progress_callback(0, f"Generating {digits}-digit numbers with crunch")
            
            cmd = [
                self.crunch_path,
                str(digits), str(digits),
                '0123456789',
                '-o', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if progress_callback:
                    progress_callback(100, "Crunch number generation complete")
                return True
            else:
                return False
                
        except Exception:
            return False
    
    def _generate_numbers_with_python(
        self,
        output_path: Union[str, Path],
        min_number: int,
        max_number: int,
        digits: int,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> bool:
        """Generate numbers using Python (fallback)."""
        try:
            if progress_callback:
                progress_callback(0, f"Generating numbers {min_number:0{digits}d}-{max_number:0{digits}d} with Python")
            
            total_numbers = max_number - min_number + 1
            
            with open(output_path, 'w') as f:
                for i, number in enumerate(range(min_number, max_number + 1)):
                    f.write(f"{number:0{digits}d}\n")
                    
                    if progress_callback and i % 100000 == 0:
                        progress = (i / total_numbers) * 100
                        progress_callback(progress, f"Generated {i:,} numbers")
            
            if progress_callback:
                progress_callback(100, f"Python number generation complete - {total_numbers:,} numbers")
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            return False
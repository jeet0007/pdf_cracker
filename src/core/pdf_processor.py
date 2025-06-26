#!/usr/bin/env python3

import subprocess
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Union


class PDFProcessor:
    """Handle PDF password hash extraction using pdf2john."""
    
    def __init__(self):
        self.pdf2john_path = self._find_pdf2john()
    
    def _find_pdf2john(self) -> str:
        """Find pdf2john script on the system."""
        # Common paths for pdf2john
        possible_paths = [
            '/usr/share/john/pdf2john.pl',
            '/opt/homebrew/share/john/pdf2john.pl',
            '/usr/local/share/john/pdf2john.pl',
            '/opt/homebrew/Cellar/john-jumbo/*/share/john/pdf2john.pl',
        ]
        
        # Check exact paths first
        for path in possible_paths[:-1]:  # Exclude glob pattern
            if os.path.exists(path):
                return path
        
        # Check glob pattern
        import glob
        glob_matches = glob.glob(possible_paths[-1])
        if glob_matches:
            return glob_matches[0]
        
        # Try to find using which/whereis
        try:
            result = subprocess.run(['which', 'pdf2john'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        try:
            result = subprocess.run(['which', 'pdf2john.pl'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        raise FileNotFoundError(
            "pdf2john script not found. Please ensure John the Ripper is properly installed."
        )
    
    def extract_hash(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract password hash from PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Hash string suitable for John the Ripper
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            RuntimeError: If hash extraction fails
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # Run pdf2john to extract hash
            if self.pdf2john_path.endswith('.pl'):
                cmd = ['perl', self.pdf2john_path, str(pdf_path)]
            else:
                cmd = [self.pdf2john_path, str(pdf_path)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            hash_output = result.stdout.strip()
            
            if not hash_output:
                raise RuntimeError("No hash extracted from PDF")
            
            return hash_output
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            raise RuntimeError(f"Failed to extract hash: {error_msg}")
        except Exception as e:
            raise RuntimeError(f"Hash extraction failed: {str(e)}")
    
    def save_hash_to_file(self, pdf_path: Union[str, Path], hash_file: Union[str, Path]) -> str:
        """
        Extract hash and save to file.
        
        Args:
            pdf_path: Path to the PDF file
            hash_file: Path to save the hash
            
        Returns:
            The extracted hash string
        """
        hash_output = self.extract_hash(pdf_path)
        
        hash_file = Path(hash_file)
        hash_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(hash_file, 'w') as f:
            f.write(hash_output + '\n')
        
        return hash_output
    
    def is_pdf_protected(self, pdf_path: Union[str, Path]) -> bool:
        """
        Check if PDF file is password protected.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if password protected, False otherwise
        """
        try:
            hash_output = self.extract_hash(pdf_path)
            # Check if we get a valid hash (not the "not encrypted!" message)
            hash_output = hash_output.strip()
            return bool(hash_output) and "not encrypted" not in hash_output.lower()
        except:
            # If extraction fails, assume not protected or invalid PDF
            return False
    
    def get_pdf_info(self, pdf_path: Union[str, Path]) -> dict:
        """
        Get basic information about the PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF information
        """
        pdf_path = Path(pdf_path)
        
        info = {
            'path': str(pdf_path),
            'exists': pdf_path.exists(),
            'size': pdf_path.stat().st_size if pdf_path.exists() else 0,
            'protected': False,
            'hash': None
        }
        
        if info['exists']:
            try:
                info['protected'] = self.is_pdf_protected(pdf_path)
                if info['protected']:
                    info['hash'] = self.extract_hash(pdf_path)
            except Exception as e:
                info['error'] = str(e)
        
        return info


class PDFHashManager:
    """Manage multiple PDF hash files for batch processing."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
        self.processor = PDFProcessor()
        self.hash_files = {}
    
    def add_pdf(self, pdf_path: Union[str, Path], name: Optional[str] = None) -> str:
        """
        Add PDF to the batch and extract its hash.
        
        Args:
            pdf_path: Path to the PDF file
            name: Optional name for the PDF (defaults to filename)
            
        Returns:
            Hash file path
        """
        pdf_path = Path(pdf_path)
        name = name or pdf_path.stem
        
        hash_file = self.temp_dir / f"{name}.hash"
        hash_output = self.processor.save_hash_to_file(pdf_path, hash_file)
        
        self.hash_files[name] = {
            'pdf_path': str(pdf_path),
            'hash_file': str(hash_file),
            'hash': hash_output
        }
        
        return str(hash_file)
    
    def get_combined_hash_file(self) -> str:
        """
        Create a combined hash file for all PDFs.
        
        Returns:
            Path to combined hash file
        """
        combined_file = self.temp_dir / "combined_hashes.txt"
        
        with open(combined_file, 'w') as f:
            for name, info in self.hash_files.items():
                f.write(info['hash'] + '\n')
        
        return str(combined_file)
    
    def cleanup(self):
        """Clean up temporary hash files."""
        for info in self.hash_files.values():
            hash_file = Path(info['hash_file'])
            if hash_file.exists():
                hash_file.unlink()
        
        combined_file = self.temp_dir / "combined_hashes.txt"
        if combined_file.exists():
            combined_file.unlink()
        
        self.hash_files.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
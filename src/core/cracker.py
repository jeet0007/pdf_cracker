#!/usr/bin/env python3

import subprocess
import os
import tempfile
import time
import threading
from pathlib import Path
from typing import Optional, Union, Callable, Dict, Any
from dataclasses import dataclass

from .pdf_processor import PDFProcessor
from .password_generator import CrunchPasswordGenerator


@dataclass
class CrackResult:
    """Result of password cracking attempt."""
    success: bool
    password: Optional[str] = None
    time_taken: float = 0.0
    attempts: int = 0
    error: Optional[str] = None


class JohnCracker:
    """Use John the Ripper to crack PDF passwords."""
    
    def __init__(self):
        self.john_path = self._find_john()
        self.pdf_processor = PDFProcessor()
        self._current_process = None
        self._stop_requested = False
    
    def _find_john(self) -> str:
        """Find John the Ripper executable."""
        john_paths = ['john', '/usr/bin/john', '/opt/homebrew/bin/john']
        
        for path in john_paths:
            if os.path.exists(path) or subprocess.run(['which', path], capture_output=True).returncode == 0:
                return path
        
        raise FileNotFoundError("John the Ripper not found. Please install john.")
    
    def crack_with_wordlist(
        self,
        pdf_path: Union[str, Path],
        wordlist_path: Union[str, Path],
        progress_callback: Optional[Callable[[float, int], None]] = None
    ) -> CrackResult:
        """
        Crack PDF password using a wordlist.
        
        Args:
            pdf_path: Path to the PDF file
            wordlist_path: Path to the wordlist file
            progress_callback: Optional callback for progress updates (progress%, attempts)
            
        Returns:
            CrackResult object with the result
        """
        start_time = time.time()
        self._stop_requested = False
        
        try:
            # Extract hash from PDF
            with tempfile.NamedTemporaryFile(mode='w', suffix='.hash', delete=False) as hash_file:
                hash_output = self.pdf_processor.extract_hash(pdf_path)
                hash_file.write(hash_output)
                hash_file_path = hash_file.name
            
            try:
                # Run John the Ripper
                cmd = [
                    self.john_path,
                    '--wordlist=' + str(wordlist_path),
                    hash_file_path
                ]
                
                result = self._run_john_with_monitoring(cmd, progress_callback)
                
                if result.success:
                    # Get the cracked password
                    password = self._get_cracked_password(hash_file_path)
                    if password:
                        result.password = password
                        result.time_taken = time.time() - start_time
                        return result
                    else:
                        # John ran successfully but didn't find password
                        result.success = False
                        result.error = "No password found"
                        result.time_taken = time.time() - start_time
                
                return result
                
            finally:
                # Clean up hash file
                if os.path.exists(hash_file_path):
                    os.unlink(hash_file_path)
                
        except Exception as e:
            return CrackResult(
                success=False,
                error=str(e),
                time_taken=time.time() - start_time
            )
    
    def crack_with_date_range(
        self,
        pdf_path: Union[str, Path],
        start_year: int = 2000,
        end_year: int = 2030,
        progress_callback: Optional[Callable[[float, int], None]] = None
    ) -> CrackResult:
        """
        Crack PDF password using generated date range.
        
        Args:
            pdf_path: Path to the PDF file
            start_year: Start year for date generation
            end_year: End year for date generation
            progress_callback: Optional callback for progress updates
            
        Returns:
            CrackResult object with the result
        """
        try:
            # Generate wordlist
            generator = CrunchPasswordGenerator(start_year, end_year)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as wordlist_file:
                wordlist_path = wordlist_file.name
                generator.generate_wordlist_with_crunch(wordlist_path)
            
            try:
                return self.crack_with_wordlist(pdf_path, wordlist_path, progress_callback)
            finally:
                if os.path.exists(wordlist_path):
                    os.unlink(wordlist_path)
                
        except Exception as e:
            return CrackResult(success=False, error=str(e))
    
    def _run_john_with_monitoring(
        self,
        cmd: list,
        progress_callback: Optional[Callable[[float, int], None]] = None
    ) -> CrackResult:
        """Run John with progress monitoring."""
        try:
            self._current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor progress in a separate thread
            attempts = 0
            if progress_callback:
                monitor_thread = threading.Thread(
                    target=self._monitor_progress,
                    args=(progress_callback,)
                )
                monitor_thread.daemon = True
                monitor_thread.start()
            
            # Wait for completion
            stdout, stderr = self._current_process.communicate()
            
            if self._stop_requested:
                return CrackResult(success=False, error="Cancelled by user")
            
            if self._current_process.returncode == 0:
                # John ran successfully, now check if it actually found a password
                # by trying to extract it using --show
                return CrackResult(success=True, attempts=attempts)
            else:
                return CrackResult(success=False, error=stderr.strip(), attempts=attempts)
                
        except Exception as e:
            return CrackResult(success=False, error=str(e))
        finally:
            self._current_process = None
    
    def _monitor_progress(self, progress_callback: Callable[[float, int], None]):
        """Monitor John's progress and call the callback."""
        attempts = 0
        while self._current_process and self._current_process.poll() is None:
            if self._stop_requested:
                break
            
            attempts += 1000  # Rough estimate
            progress = min(attempts / 100000, 99.0)  # Cap at 99% until completion
            progress_callback(progress, attempts)
            
            time.sleep(1)
    
    def _get_cracked_password(self, hash_file_path: str) -> Optional[str]:
        """Extract cracked password from John's output."""
        try:
            # Try to show cracked passwords
            cmd = [self.john_path, '--show', hash_file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            output = result.stdout.strip()
            if output and ':' in output:
                # Format is usually "filename:password" on the first line
                first_line = output.split('\n')[0]
                if ':' in first_line:
                    password = first_line.split(':', 1)[1]
                    return password
            
            return None
            
        except Exception:
            return None
    
    def _has_cracked_password(self) -> bool:
        """Check if John has cracked any passwords."""
        try:
            cmd = [self.john_path, '--show']
            result = subprocess.run(cmd, capture_output=True, text=True)
            return bool(result.stdout.strip())
        except:
            return False
    
    def stop_cracking(self):
        """Stop the current cracking process."""
        self._stop_requested = True
        if self._current_process:
            self._current_process.terminate()
            try:
                self._current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._current_process.kill()


class PDFCracker:
    """High-level PDF password cracker."""
    
    def __init__(self):
        self.john_cracker = JohnCracker()
        self.pdf_processor = PDFProcessor()
    
    def crack_pdf(
        self,
        pdf_path: Union[str, Path],
        method: str = 'date_range',
        **kwargs
    ) -> CrackResult:
        """
        Crack PDF password using specified method.
        
        Args:
            pdf_path: Path to the PDF file
            method: Cracking method ('date_range', 'wordlist')
            **kwargs: Additional arguments for the method
            
        Returns:
            CrackResult object
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            return CrackResult(success=False, error=f"PDF file not found: {pdf_path}")
        
        # Check if PDF is password protected
        if not self.pdf_processor.is_pdf_protected(pdf_path):
            return CrackResult(
                success=True, 
                password=None, 
                error=None, 
                time_taken=0.0, 
                attempts=0
            )
        
        if method == 'date_range':
            return self.john_cracker.crack_with_date_range(pdf_path, **kwargs)
        elif method == 'wordlist':
            wordlist_path = kwargs.get('wordlist_path')
            if not wordlist_path:
                return CrackResult(success=False, error="wordlist_path required for wordlist method")
            # Remove wordlist_path from kwargs to avoid duplicate argument
            clean_kwargs = {k: v for k, v in kwargs.items() if k != 'wordlist_path'}
            return self.john_cracker.crack_with_wordlist(pdf_path, wordlist_path, **clean_kwargs)
        else:
            return CrackResult(success=False, error=f"Unknown method: {method}")
    
    def stop(self):
        """Stop any running cracking process."""
        self.john_cracker.stop_cracking()
    
    def get_pdf_info(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Get information about a PDF file."""
        return self.pdf_processor.get_pdf_info(pdf_path)
"""
PDF Cracker Core Modules

Simplified core modules for PDF password cracking:
- john_wrapper: Simple John the Ripper interface
- crunch_wrapper: Simple Crunch wordlist generator interface  
- pdf_processor: PDF protection detection and hash extraction
"""

from .john_wrapper import JohnWrapper, PDFCracker, CrackResult
from .crunch_wrapper import CrunchWrapper
from .pdf_processor import PDFProcessor

__all__ = ['JohnWrapper', 'PDFCracker', 'CrackResult', 'CrunchWrapper', 'PDFProcessor']
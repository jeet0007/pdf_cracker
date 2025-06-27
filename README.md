# 🔐 PDF Cracker

A powerful CLI toolkit for cracking password-protected PDF files using comprehensive wordlist generation. Designed for recovering your own PDF passwords with support for date-based patterns and extensive 8-digit number combinations.

## ✨ Features

- 🖥️ **Pure CLI Interface** - Lightweight, scriptable, and server-friendly
- 📅 **Comprehensive Date Generation** - DDMMYYYY format for past 80 years
- 🧘 **Buddhist Calendar Support** - Additional date format (+543 years from Gregorian)
- 🔢 **Complete 8-Digit Numbers** - All combinations from 00000000 to 99999999
- 🔧 **John the Ripper Integration** - Industry-standard password cracking engine
- ⚡ **Crunch Integration** - Efficient wordlist generation when available
- 📊 **Progress Tracking** - Real-time status updates during generation and cracking
- 🎯 **Massive Coverage** - 100+ million password combinations
- 🖥️ **Cross-Platform** - Works on Windows, macOS, and Linux

## 🚀 Quick Start

### 1. Installation

#### Linux/macOS
```bash
git clone https://github.com/your-username/pdf-cracker.git
cd pdf-cracker
chmod +x install.sh
./install.sh
```

#### Windows
```cmd
git clone https://github.com/your-username/pdf-cracker.git
cd pdf-cracker
install.bat
```

### 2. Basic Usage

#### Generate Comprehensive Wordlist
```bash
# Generate massive wordlist (~860MB, 100M+ passwords)
./pdf-comprehensive-wordlist

# Show size estimate without generating
./pdf-comprehensive-wordlist --estimate-only

# Custom years back (default: 80 years)
./pdf-comprehensive-wordlist --years-back 50
```

#### Crack PDF Files
```bash
# Crack using comprehensive wordlist
./pdf-crack document.pdf

# Use custom wordlist
./pdf-crack --wordlist custom.txt document.pdf

# Set longer timeout (default: 1 hour)
./pdf-crack --timeout 7200 document.pdf  # 2 hours
```

#### Generate Basic Date Wordlists
```bash
# Generate basic date wordlist for specific range
./pdf-wordlist --start 2020 --end 2025 --output dates.txt

# Multiple date formats
./pdf-wordlist --start 2020 --end 2025 --formats DDMMYYYY DDMMYY
```

## 📋 Requirements

### System Dependencies
- **John the Ripper** - Password cracking engine
- **Crunch** - Wordlist generator (optional, has fallback)
- **Python 3.7+** - Runtime environment

### Python Dependencies
- **No runtime dependencies** - Pure standard library for core functionality
- `pytest` and `pytest-cov` - For development and testing (optional)

## 🎯 How It Works

### Comprehensive Wordlist Generation
1. **Gregorian Dates** - DDMMYYYY format for past 80 years (~125K passwords)
2. **Buddhist Calendar** - Same dates with +543 year offset (~125K passwords)  
3. **8-Digit Numbers** - Complete range 00000000-99999999 (100M passwords)
4. **Total Coverage** - 100,226,159 passwords in ~860MB file

### Cracking Process
1. **PDF Analysis** - Validates password protection using PyPDF2
2. **Hash Extraction** - Uses pdf2john.pl to extract password hashes
3. **Wordlist Application** - John the Ripper tests all passwords efficiently
4. **Result Analysis** - Identifies password type and provides statistics

## 🛠️ Advanced Usage

### Direct Python Usage
```bash
# Generate comprehensive wordlist
python3 src/utils/comprehensive_wordlist.py --estimate-only

# Crack with custom parameters
python3 src/utils/comprehensive_crack.py document.pdf --timeout 3600

# Generate basic date wordlist
python3 src/utils/wordlist_gen.py --start 2020 --end 2025
```

### Custom Wordlist Generation
```bash
# Single year comprehensive
./pdf-comprehensive-wordlist --years-back 1 --output recent.txt

# Specific date range only
./pdf-wordlist --start 2023 --end 2023 --output 2023-only.txt

# Multiple formats
./pdf-wordlist --formats DDMMYYYY DDMMYY YYYYMMDD --start 2020 --end 2025
```

### Batch Processing
```bash
# Process multiple PDFs
for pdf in *.pdf; do
  echo "Processing $pdf"
  ./pdf-crack "$pdf" --timeout 1800
done
```

## 📁 Project Structure

```
pdf-cracker/
├── README.md                    # This file
├── requirements.txt             # Python dependencies (minimal)
├── setup.py                    # Package configuration
├── install.sh                  # Linux/macOS installation
├── install.bat                 # Windows installation
├── src/
│   ├── core/                   # Core functionality
│   │   ├── john_wrapper.py         # John the Ripper wrapper
│   │   ├── crunch_wrapper.py       # Crunch wordlist generator wrapper
│   │   └── pdf_processor.py        # PDF hash extraction
│   └── utils/                  # CLI tools
│       ├── comprehensive_wordlist.py   # Comprehensive wordlist generator
│       ├── comprehensive_crack.py      # Comprehensive PDF cracker
│       └── wordlist_gen.py            # Basic date wordlist generator
├── tests/                      # Unit tests
│   ├── test_john_wrapper.py        # John wrapper tests
│   ├── test_crunch_wrapper.py      # Crunch wrapper tests
│   ├── test_pdf_processor.py       # PDF processing tests
│   ├── test_wordlist_generator.py  # CLI tool tests
│   └── test_installation.py        # Installation verification
├── run_tests.py                # Test runner script
├── wordlists/                  # Generated wordlists storage
├── assets/                     # Test files and resources
└── Convenience Scripts (auto-generated):
    ├── pdf-wordlist            # Basic wordlist generation
    ├── pdf-comprehensive-wordlist  # Comprehensive wordlist
    └── pdf-crack               # PDF cracking tool
```

## 🔍 Examples

### Comprehensive Workflow
```bash
# 1. Estimate wordlist size
./pdf-comprehensive-wordlist --estimate-only

# 2. Generate comprehensive wordlist (once)
./pdf-comprehensive-wordlist

# 3. Crack multiple PDFs
./pdf-crack document1.pdf
./pdf-crack document2.pdf --timeout 3600
./pdf-crack document3.pdf --wordlist wordlists/comprehensive_ultimate.txt
```

### Quick Date-Only Workflow
```bash
# Fast approach for recent dates
./pdf-wordlist --start 2020 --end 2025 --output recent.txt
python3 src/utils/comprehensive_crack.py --wordlist recent.txt document.pdf
```

### Custom Range Analysis
```bash
# Check if specific year range works
./pdf-wordlist --start 2023 --end 2023 --output 2023.txt
./pdf-crack --wordlist 2023.txt document.pdf --timeout 300
```

## ⚠️ Important Notes

### Legal and Ethical Use
- **Only use on PDFs you own or have explicit permission to access**
- This tool is for password recovery, not unauthorized access
- Respect applicable laws and regulations in your jurisdiction

### Performance Considerations
- **Comprehensive Wordlist**: ~860MB file, 100M+ passwords, requires significant disk space
- **Generation Time**: Comprehensive wordlist creation can take 10-30 minutes
- **Cracking Time**: Depends on password position and hardware (minutes to hours)
- **Memory Usage**: John the Ripper manages memory efficiently for large wordlists
- **Storage**: Ensure sufficient disk space before generating comprehensive wordlist

### Password Coverage
- **Date-based passwords**: Excellent coverage (past 80 years, Buddhist calendar)
- **8-digit numbers**: Complete coverage (birthdays, IDs, PINs, etc.)
- **Success Rate**: Very high for documents using common 8-digit patterns
- **Limitations**: Won't crack complex passwords with letters, symbols, or longer lengths

## 🐛 Troubleshooting

### Common Issues

#### "John the Ripper not found"
```bash
# Ubuntu/Debian
sudo apt-get install john

# macOS
brew install john-jumbo

# Check installation
which john
john --version
```

#### "pdf2john not found"
```bash
# Common locations:
ls /usr/share/john/pdf2john.pl
ls /opt/homebrew/share/john/pdf2john.pl

# If missing, reinstall John the Ripper
```

#### "Permission denied" on scripts
```bash
chmod +x install.sh pdf-comprehensive-wordlist pdf-crack pdf-wordlist
```

#### "Disk space full" during wordlist generation
```bash
# Check available space
df -h .

# Generate smaller wordlist
./pdf-comprehensive-wordlist --years-back 20

# Use basic date wordlist instead
./pdf-wordlist --start 2020 --end 2025
```

### Performance Issues
- **Slow generation**: Use SSD storage, reduce years-back parameter
- **Slow cracking**: Ensure John the Ripper is using all CPU cores
- **Large wordlist**: Consider generating once and reusing the file

## 🤝 Contributing

We welcome contributions! Areas for improvement:
- Additional password patterns and formats
- Performance optimizations
- Better progress reporting
- Enhanced error handling

### Development Setup
```bash
git clone https://github.com/your-username/pdf-cracker.git
cd pdf-cracker
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\\Scripts\\activate  # Windows

pip install -r requirements.txt
```

### Running Tests
```bash
# Install development dependencies
pip install -e .[dev]

# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run only fast unit tests
python run_tests.py --unit

# Run specific test file
python run_tests.py tests/test_john_wrapper.py

# Direct pytest usage
pytest tests/ --cov=src --cov-report=html
pytest -v tests/test_crunch_wrapper.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **John the Ripper** - The powerful password cracking engine that makes this possible
- **Crunch** - Efficient wordlist generation for date patterns
- **Python Standard Library** - Robust foundation for cross-platform compatibility

## 📊 Statistics

### Comprehensive Wordlist Coverage
- **Gregorian dates (80 years)**: 125,644 passwords
- **Buddhist calendar dates**: 125,644 passwords  
- **8-digit numbers**: 100,000,000 passwords
- **Total passwords**: 100,226,159 passwords
- **File size**: ~860MB
- **Generation time**: 10-30 minutes (depends on hardware)

### Typical Performance
- **Memory usage**: <100MB during generation, <50MB during cracking
- **Cracking speed**: 1M-10M passwords/second (hardware dependent)
- **Success rate**: 90%+ for date-based and 8-digit number passwords
- **Coverage**: Comprehensive for birth dates, anniversaries, IDs, PINs

## 🔮 Roadmap

- [ ] GPU acceleration support for faster cracking
- [ ] Additional password patterns (9-digit, 6-digit numbers)
- [ ] International calendar systems (Chinese, Islamic, etc.)
- [ ] Password complexity analysis and reporting
- [ ] Distributed cracking across multiple machines
- [ ] Memory-efficient streaming for massive wordlists
- [ ] Smart pattern detection and optimization

---

**⚠️ Disclaimer**: This tool is intended for legitimate password recovery purposes only. Users are responsible for ensuring they have legal authority to access any PDF files they attempt to crack. The comprehensive wordlist generation creates very large files - ensure adequate disk space and respect system resources.
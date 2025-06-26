#!/bin/bash

# PDF Cracker Installation Script
# Installs John the Ripper and other dependencies

set -e

echo "🔐 PDF Cracker Installation Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        # Detect Linux distribution
        if command -v apt-get >/dev/null 2>&1; then
            DISTRO="debian"
        elif command -v yum >/dev/null 2>&1; then
            DISTRO="rhel"
        elif command -v pacman >/dev/null 2>&1; then
            DISTRO="arch"
        else
            DISTRO="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
}

# Install John the Ripper
install_john() {
    print_status "Installing John the Ripper..."
    
    case "$OS" in
        "macos")
            if command -v brew >/dev/null 2>&1; then
                print_status "Using Homebrew to install john-jumbo..."
                brew install john-jumbo
            else
                print_error "Homebrew not found. Please install Homebrew first:"
                echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            ;;
        "linux")
            case "$DISTRO" in
                "debian")
                    print_status "Using apt to install john..."
                    sudo apt-get update
                    sudo apt-get install -y john
                    ;;
                "rhel")
                    print_status "Using yum/dnf to install john..."
                    if command -v dnf >/dev/null 2>&1; then
                        sudo dnf install -y john
                    else
                        sudo yum install -y john
                    fi
                    ;;
                "arch")
                    print_status "Using pacman to install john..."
                    sudo pacman -S --noconfirm john
                    ;;
                *)
                    print_error "Unsupported Linux distribution. Please install John the Ripper manually."
                    echo "  Ubuntu/Debian: sudo apt-get install john"
                    echo "  CentOS/RHEL:   sudo yum install john"
                    echo "  Arch:          sudo pacman -S john"
                    exit 1
                    ;;
            esac
            ;;
        *)
            print_error "Unsupported operating system: $OSTYPE"
            exit 1
            ;;
    esac
}

# Install crunch
install_crunch() {
    print_status "Installing crunch..."
    
    case "$OS" in
        "macos")
            if command -v brew >/dev/null 2>&1; then
                print_status "Using Homebrew to install crunch..."
                brew install crunch
            else
                print_error "Homebrew not found."
                exit 1
            fi
            ;;
        "linux")
            case "$DISTRO" in
                "debian")
                    print_status "Using apt to install crunch..."
                    sudo apt-get install -y crunch
                    ;;
                "rhel")
                    print_status "Using yum/dnf to install crunch..."
                    if command -v dnf >/dev/null 2>&1; then
                        sudo dnf install -y crunch
                    else
                        sudo yum install -y crunch
                    fi
                    ;;
                "arch")
                    print_status "Using pacman to install crunch..."
                    sudo pacman -S --noconfirm crunch
                    ;;
                *)
                    print_error "Unsupported Linux distribution for crunch installation."
                    exit 1
                    ;;
            esac
            ;;
        *)
            print_error "Unsupported operating system for crunch installation."
            exit 1
            ;;
    esac
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Check if Python 3 is available
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    # Note: tkinter no longer needed as we focus on CLI tools only
    
    # Install pip if not available
    if ! command -v pip3 >/dev/null 2>&1; then
        print_status "Installing pip3..."
        case "$OS" in
            "macos")
                python3 -m ensurepip --upgrade
                ;;
            "linux")
                case "$DISTRO" in
                    "debian")
                        sudo apt-get install -y python3-pip
                        ;;
                    "rhel")
                        if command -v dnf >/dev/null 2>&1; then
                            sudo dnf install -y python3-pip
                        else
                            sudo yum install -y python3-pip
                        fi
                        ;;
                    "arch")
                        sudo pacman -S --noconfirm python-pip
                        ;;
                esac
                ;;
        esac
    fi
    
    # Install requirements if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python packages from requirements.txt..."
        pip3 install -r requirements.txt
    else
        print_status "Installing basic Python packages..."
        # No additional packages needed for CLI-only version
        print_success "CLI tools are ready to use"
    fi
}

# Verify installations
verify_installation() {
    print_status "Verifying installations..."
    
    # Check John the Ripper
    if command -v john >/dev/null 2>&1; then
        print_success "John the Ripper is installed: $(john --version 2>&1 | head -n1)"
    else
        print_error "John the Ripper installation failed"
        exit 1
    fi
    
    # Check crunch
    if command -v crunch >/dev/null 2>&1; then
        print_success "Crunch is installed: $(crunch -h 2>&1 | head -n1 | cut -d' ' -f1-3)"
    else
        print_warning "Crunch installation may have failed"
    fi
    
    # Check for pdf2john
    PDF2JOHN_PATHS=(
        "/usr/share/john/pdf2john.pl"
        "/opt/homebrew/share/john/pdf2john.pl"
        "/opt/homebrew/Cellar/john-jumbo/*/share/john/pdf2john.pl"
        "/usr/local/share/john/pdf2john.pl"
    )
    
    PDF2JOHN_FOUND=""
    for path in "${PDF2JOHN_PATHS[@]}"; do
        if ls $path 2>/dev/null; then
            PDF2JOHN_FOUND="$path"
            break
        fi
    done
    
    if [ -n "$PDF2JOHN_FOUND" ]; then
        print_success "pdf2john found at: $PDF2JOHN_FOUND"
    else
        print_warning "pdf2john.pl not found in standard locations"
    fi
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        print_success "Python 3 is available: $(python3 --version)"
    else
        print_error "Python 3 is required but not found"
        exit 1
    fi
    
    # CLI-only version - no GUI dependencies needed
    print_success "CLI tools ready"
}

# Create convenience scripts
create_scripts() {
    print_status "Creating convenience scripts..."
    
    # Create wordlist generator script
    cat > pdf-wordlist << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 src/utils/wordlist_gen.py "$@"
EOF
    chmod +x pdf-wordlist
    
    # Create comprehensive wordlist generator script
    cat > pdf-comprehensive-wordlist << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 src/utils/comprehensive_wordlist.py "$@"
EOF
    chmod +x pdf-comprehensive-wordlist
    
    # Create comprehensive cracker script
    cat > pdf-crack << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 src/utils/comprehensive_crack.py "$@"
EOF
    chmod +x pdf-crack
    
    print_success "Created convenience scripts: pdf-wordlist, pdf-comprehensive-wordlist, pdf-crack"
}

# Main installation
main() {
    print_status "Starting PDF Cracker installation..."
    
    detect_os
    print_status "Detected OS: $OS ($DISTRO)"
    
    # Check if running as root (not recommended for some operations)
    if [[ $EUID -eq 0 ]] && [[ "$OS" == "macos" ]]; then
        print_warning "Running as root on macOS is not recommended for Homebrew operations"
    fi
    
    # Install components
    install_john
    install_crunch
    install_python_deps
    
    # Verify everything is working
    verify_installation
    
    # Create convenience scripts
    create_scripts
    
    echo ""
    print_success "Installation completed successfully!"
    echo ""
    echo "Usage:"
    echo "  Generate basic wordlist:       ./pdf-wordlist --start 2020 --end 2025 --output passwords.txt"
    echo "  Generate comprehensive list:   ./pdf-comprehensive-wordlist --estimate-only"
    echo "  Crack PDF:                     ./pdf-crack assets/document.pdf"
    echo "  Direct Python:                 python3 src/utils/comprehensive_crack.py document.pdf"
    echo ""
    echo "For more options: ./pdf-wordlist --help or ./pdf-crack --help"
}

# Run installation
main "$@"
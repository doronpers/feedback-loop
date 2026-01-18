#!/bin/bash
###############################################################################
# Feedback Loop - One-Click Installer
###############################################################################
# This script downloads, installs, and starts feedback-loop automatically.
# Usage: curl -fsSL https://raw.githubusercontent.com/doronpers/feedback-loop/main/install.sh | bash
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Main installation function
main() {
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                    Feedback Loop Installer                        ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""

    OS=$(detect_os)
    log_info "Detected OS: $OS"

    # Check Python
    if ! command_exists python3; then
        log_error "Python 3 is required but not found."
        echo ""
        echo "Please install Python 3.8 or later:"
        case $OS in
            "linux")
                echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
                echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
                echo "  Arch: sudo pacman -S python python-pip"
                ;;
            "macos")
                echo "  Homebrew: brew install python3"
                echo "  Or download from: https://www.python.org/downloads/"
                ;;
            "windows")
                echo "  Download from: https://www.python.org/downloads/"
                ;;
        esac
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_success "Found Python $PYTHON_VERSION"

    # Check Python version
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        log_error "Python 3.8 or later is required. Found $PYTHON_VERSION"
        exit 1
    fi

    # Check git
    if ! command_exists git; then
        log_error "Git is required but not found."
        echo ""
        echo "Please install Git:"
        case $OS in
            "linux")
                echo "  Ubuntu/Debian: sudo apt install git"
                echo "  CentOS/RHEL: sudo yum install git"
                echo "  Arch: sudo pacman -S git"
                ;;
            "macos")
                echo "  Homebrew: brew install git"
                echo "  Or download from: https://git-scm.com/download/mac"
                ;;
            "windows")
                echo "  Download from: https://git-scm.com/download/win"
                ;;
        esac
        exit 1
    fi
    log_success "Found Git"

    # Clone repository
    if [ -d "feedback-loop" ]; then
        log_warning "feedback-loop directory already exists. Updating..."
        cd feedback-loop
        git pull
    else
        log_info "Cloning feedback-loop repository..."
        git clone https://github.com/doronpers/feedback-loop.git
        cd feedback-loop
    fi

    log_success "Repository ready"

    # Install dependencies
    log_info "Installing dependencies..."
    python3 -m pip install --upgrade pip
    python3 -m pip install -e .

    if [ $? -eq 0 ]; then
        log_success "Dependencies installed"
    else
        log_error "Failed to install dependencies"
        exit 1
    fi

    # Run quick start
    echo ""
    log_info "Starting feedback-loop..."
    echo ""

    exec python3 bin/fl-start
}

# Run main function
main "$@"

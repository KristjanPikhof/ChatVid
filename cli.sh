#!/bin/bash

# ChatVid CLI - Memvid Dataset Management Tool
# Main entry point that handles venv and delegates to Python CLI

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_CLI="$SCRIPT_DIR/memvid_cli.py"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to create and setup virtual environment
setup_venv() {
    print_info "Setting up virtual environment..."

    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment at $VENV_DIR"
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi

    # Activate venv
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1

    # Install/upgrade requirements
    if [ -f "$REQUIREMENTS" ]; then
        print_info "Installing dependencies from requirements.txt..."
        pip install -r "$REQUIREMENTS"
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found at $REQUIREMENTS"
        exit 1
    fi
}

# Function to activate existing venv
activate_venv() {
    source "$VENV_DIR/bin/activate"
}

# Check if this is first run or setup command
if [ ! -d "$VENV_DIR" ] || [ "$1" = "setup" ]; then
    setup_venv
else
    activate_venv
fi

# Suppress tokenizer warnings
export TOKENIZERS_PARALLELISM=false

# Check if Python CLI exists
if [ ! -f "$PYTHON_CLI" ]; then
    print_error "Python CLI not found at $PYTHON_CLI"
    exit 1
fi

# If no arguments, show help
if [ $# -eq 0 ]; then
    python "$PYTHON_CLI" --help
    exit 0
fi

# Delegate to Python CLI with all arguments
python "$PYTHON_CLI" "$@"

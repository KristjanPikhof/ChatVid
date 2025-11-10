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
PYTHON_CMD=""  # Global variable for validated Python command
PYTHON_CMD_FILE="$SCRIPT_DIR/.python-cmd"

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

# Parse Python version from command
# Args: $1 = python command (e.g., "python3")
# Output: "3.10" or "INVALID"
parse_python_version() {
    local cmd=$1
    local version_output

    # Capture both stdout and stderr
    version_output=$($cmd --version 2>&1 || echo "INVALID")

    # Extract major.minor (e.g., "Python 3.10.15" → "3.10")
    if [[ $version_output =~ Python[[:space:]]+([0-9]+)\.([0-9]+) ]]; then
        echo "${BASH_REMATCH[1]}.${BASH_REMATCH[2]}"
        return 0
    fi

    echo "INVALID"
    return 1
}

# Check if version is in supported range (3.10-3.13)
# Args: $1 = version string (e.g., "3.10")
# Returns: 0 if valid, 1 if not
is_valid_version() {
    local version=$1

    # Handle invalid input
    [[ $version == "INVALID" || -z $version ]] && return 1

    # Extract major and minor
    local major="${version%%.*}"
    local minor="${version#*.}"

    # Validate: must be 3.10, 3.11, 3.12, or 3.13
    if [[ $major -eq 3 ]] && [[ $minor -ge 10 ]] && [[ $minor -le 13 ]]; then
        return 0
    fi

    return 1
}

# Validates previously saved Python command
# Returns: 0 if valid, 1 if invalid/missing
validate_saved_python_cmd() {
    local saved_cmd version

    # Check if file exists and is readable
    if [[ ! -f "$PYTHON_CMD_FILE" ]]; then
        return 1
    fi

    saved_cmd=$(cat "$PYTHON_CMD_FILE" 2>/dev/null | tr -d '\n\r')

    # Check if command still exists in PATH
    if ! command -v "$saved_cmd" &> /dev/null; then
        print_warning "Previously saved Python command '$saved_cmd' no longer available"
        return 1
    fi

    # Check if version is still valid
    version=$(parse_python_version "$saved_cmd")
    if [[ $version == "INVALID" ]] || ! is_valid_version "$version"; then
        print_warning "Previously saved Python command '$saved_cmd' version changed to $version"
        return 1
    fi

    # All checks passed
    PYTHON_CMD="$saved_cmd"
    return 0
}

# Detects suitable Python command and saves to .python-cmd
# Returns: 0 on success, 1 on failure
# Sets global: PYTHON_CMD
detect_and_save_python_cmd() {
    local cmd version
    local candidates=("python3" "python")  # Priority order
    local found=0

    print_info "Detecting Python installation..."

    # Check each candidate
    for cmd in "${candidates[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            version=$(parse_python_version "$cmd")

            if [[ $version == "INVALID" ]]; then
                print_warning "$cmd found but version detection failed"
                continue
            fi

            if is_valid_version "$version"; then
                print_success "Found suitable Python: $cmd (version $version)"
                echo "$cmd" > "$PYTHON_CMD_FILE"
                PYTHON_CMD="$cmd"
                found=1
                break
            else
                print_warning "$cmd version $version not in supported range (3.10-3.13)"
            fi
        fi
    done

    if [[ $found -eq 0 ]]; then
        print_error "No suitable Python installation found"
        print_error ""
        print_error "ChatVid requires Python 3.10, 3.11, 3.12, or 3.13"
        print_error ""
        print_error "Checked commands:"
        print_error "  • python  (not found or incompatible)"
        print_error "  • python3 (not found or incompatible)"
        print_error ""
        print_error "Installation options:"
        print_error "  • Download from https://www.python.org/downloads/"
        print_error "  • Use system package manager:"
        print_error "    - macOS:   brew install python@3.12"
        print_error "    - Ubuntu:  sudo apt install python3.12"
        print_error "    - Windows: winget install Python.Python.3.12"
        print_error "  • Use version manager (pyenv, asdf, etc.)"
        return 1
    fi

    return 0
}

# Gets Python command using priority: env var > saved > detection
# Returns: 0 on success, exits on failure
# Sets global: PYTHON_CMD
get_python_cmd() {
    # Priority 1: Environment variable override
    if [[ -n "${CHATVID_PYTHON_CMD:-}" ]]; then
        local version
        print_info "Using Python from CHATVID_PYTHON_CMD: $CHATVID_PYTHON_CMD"

        version=$(parse_python_version "$CHATVID_PYTHON_CMD")
        if [[ $version == "INVALID" ]] || ! is_valid_version "$version"; then
            print_error "CHATVID_PYTHON_CMD='$CHATVID_PYTHON_CMD' is not valid (version $version)"
            print_error "Please set to a Python 3.10-3.13 executable"
            exit 1
        fi

        PYTHON_CMD="$CHATVID_PYTHON_CMD"
        return 0
    fi

    # Priority 2: Previously saved command
    if validate_saved_python_cmd; then
        return 0
    fi

    # Priority 3: Run full detection
    if ! detect_and_save_python_cmd; then
        exit 1
    fi

    return 0
}

# Function to create and setup virtual environment
setup_venv() {
    print_info "Setting up virtual environment..."

    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment at $VENV_DIR"
        "$PYTHON_CMD" -m venv "$VENV_DIR"
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

# Detect/validate Python command before any operations
get_python_cmd

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

# Delegate to Python CLI with all arguments
# (If no arguments, Python CLI will start interactive menu)
"$PYTHON_CMD" "$PYTHON_CLI" "$@"

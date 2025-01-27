#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Installing dependencies for pyenv and Python..."

# Function to check if a package is installed
is_installed() {
    dpkg -s "$1" &> /dev/null
}

# List of required packages
DEPENDENCIES=(
    build-essential
    curl
    libbz2-dev
    libreadline-dev
    libssl-dev
    libsqlite3-dev
    libffi-dev
    zlib1g-dev
    liblzma-dev
    tk-dev
)

# Install missing packages
echo "Checking and installing missing dependencies..."
for PACKAGE in "${DEPENDENCIES[@]}"; do
    if ! is_installed "$PACKAGE"; then
        echo "$PACKAGE is not installed. Installing..."
        sudo apt-get install -y "$PACKAGE"
    else
        echo "$PACKAGE is already installed."
    fi
done


# Install pyenv if not already installed
if ! command -v pyenv &> /dev/null; then
    echo "pyenv not found. Installing pyenv..."
    curl -fsSL https://pyenv.run | bash
else
    echo "pyenv is already installed."
fi

echo "Installing dependencies using pyenv..."

# Ensure pyenv is available in the current shell session
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
eval "$(pyenv virtualenv-init -)"

# Specify the Python version to use
PYTHON_VERSION="3.12.8"

# Install the required Python version if not already installed
if ! pyenv versions --bare | grep -q "^${PYTHON_VERSION}\$"; then
    echo "Installing Python ${PYTHON_VERSION} using pyenv..."
    pyenv install ${PYTHON_VERSION}
else
    echo "Python ${PYTHON_VERSION} is already installed."
fi

# Set the local Python version
pyenv local ${PYTHON_VERSION}

# Create and activate a virtual environment
VENV_NAME="killer_shARCs"
if [ ! -d "$(pyenv root)/versions/${VENV_NAME}" ]; then
    echo "Creating virtual environment '${VENV_NAME}'..."
    pyenv virtualenv ${PYTHON_VERSION} ${VENV_NAME}
else
    echo "Virtual environment '${VENV_NAME}' already exists."
fi
pyenv activate ${VENV_NAME}

# Install Python dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "No requirements.txt found. Skipping Python dependency installation."
fi

echo "All dependencies installed successfully."

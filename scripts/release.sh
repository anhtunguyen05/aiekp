#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting AIEKP CLI release process..."

# 1. Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf apps/cli/dist/

# 2. Build the package
echo "📦 Building package with uv..."
cd apps/cli
uv build

# 3. Upload to PyPI (requires twine and TWINE_USERNAME/TWINE_PASSWORD environment variables)
echo "☁️ Uploading to PyPI..."
# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo "Twine is not installed. Installing twine..."
    pip install twine
fi

# Upload the distribution files
twine upload dist/*

echo "✅ Release complete!"

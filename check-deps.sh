#!/usr/bin/env bash
# Script to analyze what's being installed

echo "Analyzing dependencies..."
echo ""

# Check pyproject.toml
echo "Dependencies in pyproject.toml:"
if [ -f pyproject.toml ]; then
    grep -A 20 "dependencies = \[" pyproject.toml | head -30
else
    echo "No pyproject.toml found"
fi

echo ""
echo "Checking for heavy packages in lockfile:"
if [ -f uv.lock ]; then
    echo "Searching for torch, nvidia, opencv..."
    grep -i "torch\|nvidia\|opencv\|triton" uv.lock | head -20
else
    echo "No uv.lock found"
fi

echo ""
echo "Current image sizes:"
docker images | grep dreamydormouse || echo "No images found"


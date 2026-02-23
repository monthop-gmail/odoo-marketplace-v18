#!/bin/bash
# ================================================
# Test Script for Part B - LINE Integration Tests
# ================================================
# These tests run without Odoo using mock services
# to verify LINE API integration logic
# ================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADDON_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$(dirname "$ADDON_DIR")")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Part B Tests - LINE Integration (Mock Mode)${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Set PYTHONPATH to include the addon
export PYTHONPATH="$ADDON_DIR:$PROJECT_DIR/addons:$PYTHONPATH"

# Change to addon directory for relative imports
cd "$ADDON_DIR"

echo -e "${YELLOW}Running tests from: $ADDON_DIR${NC}"
echo ""

# Run the tests
echo -e "${GREEN}Running Part B unit tests...${NC}"
echo ""

python3 -m pytest tests/test_part_b.py -v --tb=short 2>/dev/null

# If pytest is not available, fall back to unittest
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}pytest not available, falling back to unittest...${NC}"
    echo ""
    python3 -m unittest tests.test_part_b -v 2>&1
fi

# Get the exit code
EXIT_CODE=$?

echo ""
echo -e "${BLUE}================================================${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All Part B tests passed!${NC}"
else
    echo -e "${RED}Some tests failed. Exit code: $EXIT_CODE${NC}"
fi

echo -e "${BLUE}================================================${NC}"

exit $EXIT_CODE

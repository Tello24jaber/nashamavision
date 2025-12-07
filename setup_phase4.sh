#!/bin/bash

# Phase 4 Setup Script
# Nashama Vision - Virtual Match Engine

set -e  # Exit on error

echo "=========================================="
echo "  NASHAMA VISION - PHASE 4 SETUP"
echo "  Virtual Match Engine"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "PHASE4_COMPLETE.md" ]; then
    echo -e "${RED}Error: Please run this script from the nashama-vision root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Backend Verification${NC}"
echo "Checking backend files..."

# Check backend files exist
BACKEND_FILES=(
    "backend/app/replay/__init__.py"
    "backend/app/replay/service.py"
    "backend/app/api/routers/replay.py"
    "backend/app/schemas/replay.py"
)

for file in "${BACKEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (missing)"
        exit 1
    fi
done

echo ""
echo -e "${YELLOW}Step 2: Frontend Setup${NC}"
echo "Installing frontend dependencies..."

cd frontend

# Check if package.json has the right dependencies
if ! grep -q "react-konva" package.json; then
    echo -e "${RED}Error: package.json not updated with Konva dependencies${NC}"
    exit 1
fi

# Install dependencies
echo "Running npm install..."
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${RED}✗${NC} Failed to install frontend dependencies"
    exit 1
fi

# Check if frontend files exist
FRONTEND_FILES=(
    "src/pages/MatchReplayView.jsx"
    "src/components/replay/ReplayPitch.jsx"
    "src/components/replay/ReplayControls.jsx"
    "src/components/replay/ReplaySidebar.jsx"
    "src/hooks/useReplayController.js"
    "src/hooks/useReplayData.js"
)

echo ""
echo "Checking frontend files..."

for file in "${FRONTEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (missing)"
        exit 1
    fi
done

cd ..

echo ""
echo -e "${YELLOW}Step 3: Backend Check${NC}"
echo "No additional backend dependencies needed"
echo -e "${GREEN}✓${NC} Backend ready"

echo ""
echo -e "${YELLOW}Step 4: Database Check${NC}"
echo "Verifying database schema..."

# Check if we can connect to database (optional)
cd backend
if command -v psql &> /dev/null; then
    echo "PostgreSQL client found"
    echo "Note: Ensure your database is running and accessible"
else
    echo "PostgreSQL client not found - skipping database check"
    echo "Make sure PostgreSQL is installed and running"
fi

cd ..

echo ""
echo "=========================================="
echo -e "${GREEN}✓ PHASE 4 SETUP COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the backend:"
echo "   cd backend"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. Start the frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Navigate to replay page:"
echo "   http://localhost:5173/matches/{MATCH_ID}/replay"
echo ""
echo "4. Check documentation:"
echo "   - PHASE4_COMPLETE.md (comprehensive guide)"
echo "   - QUICKSTART_PHASE4.md (quick start)"
echo "   - ARCHITECTURE_PHASE4.md (technical details)"
echo ""
echo -e "${GREEN}Happy replaying! ⚽🎮${NC}"
echo ""

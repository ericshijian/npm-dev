#!/bin/bash

# i18n Code Validation Script
# This script checks for hardcoded Chinese/English text that should be internationalized

echo "🔍 Checking for i18n issues in TypeScript/TSX files..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for issues found
ISSUES=0

echo "1️⃣  Checking for hardcoded Chinese in JSX..."
echo "   (Looking for Chinese characters between > and < tags)"
echo ""

# Find hardcoded Chinese in JSX (excluding comments and conditionals)
CHINESE_RESULTS=$(grep -rn '">[^<]*[一-龟][^<]*<" app/ components/ --include="*.tsx" 2>/dev/null | \
  grep -v "//" | \
  grep -v "locale === 'zh'" | \
  grep -v "isChina ?" | \
  grep -v "locale === 'zh'?" || true)

if [ -z "$CHINESE_RESULTS" ]; then
  echo -e "${GREEN}✓ No hardcoded Chinese text found in JSX${NC}"
else
  echo -e "${RED}✗ Found hardcoded Chinese text:${NC}"
  echo "$CHINESE_RESULTS"
  echo ""
  ISSUES=$((ISSUES + 1))
fi

echo ""
echo "2️⃣  Checking for hardcoded English user-facing text..."
echo "   (Looking for English phrases >10 chars in JSX)"
echo ""

# Find potential hardcoded English in JSX
ENGLISH_RESULTS=$(grep -rn '">[A-Z][A-Za-z\s]{10,}<' app/ components/ --include="*.tsx" 2>/dev/null | \
  grep -v "//" | \
  grep -v "locale === 'zh'" | \
  grep -v "isChina ?" | \
  grep -v "aria-" | \
  grep -v "data-testid" || true)

if [ -z "$ENGLISH_RESULTS" ]; then
  echo -e "${GREEN}✓ No hardcoded English text found in JSX${NC}"
else
  echo -e "${YELLOW}⚠ Found potential hardcoded English (review manually):${NC}"
  echo "$ENGLISH_RESULTS"
  echo ""
  echo "   Note: Some results may be legitimate (aria-labels, test IDs)"
  echo ""
  ISSUES=$((ISSUES + 1))
fi

echo ""
echo "3️⃣  Checking for '寻找攻擂者' text..."
echo ""

# Find hardcoded "寻找攻擂者" that should be filtered
CHALLENGER_RESULTS=$(grep -rn "寻找攻擂者" app/ components/ --include="*.tsx" 2>/dev/null || true)

if [ -z "$CHALLENGER_RESULTS" ]; then
  echo -e "${GREEN}✓ No '寻找攻擂者' hardcoded text found${NC}"
else
  echo -e "${YELLOW}⚠ Found '寻找攻擂者' (ensure it's filtered in display logic):${NC}"
  echo "$CHALLENGER_RESULTS"
  echo ""
  ISSUES=$((ISSUES + 1))
fi

echo ""
echo "4️⃣  Checking exported arena JSON for proper i18n fields..."
echo ""

# Check if arenas have both en/zh fields in exported static JSON
DATA_CHECK=$(grep -c "\"championEn\"" public/data/arenas.json 2>/dev/null || echo "0")
TOTAL_ARENAS=$(grep -c "\"id\"" public/data/arenas.json 2>/dev/null || echo "0")

if [ "$DATA_CHECK" -eq "$TOTAL_ARENAS" ]; then
  echo -e "${GREEN}✓ All arenas have championEn field${NC}"
else
  echo -e "${YELLOW}⚠ Some arenas missing championEn field ($DATA_CHECK/$TOTAL_ARENAS)${NC}"
  ISSUES=$((ISSUES + 1))
fi

echo ""
echo "═══════════════════════════════════════════════════"
if [ $ISSUES -eq 0 ]; then
  echo -e "${GREEN}✓ All i18n checks passed!${NC}"
  echo ""
  echo "Your code follows proper internationalization practices."
  exit 0
else
  echo -e "${RED}✗ Found $ISSUES potential i18n issue(s)${NC}"
  echo ""
  echo "Please review the results above and fix any hardcoded text."
  echo "Remember to use: {locale === 'zh' ? '中文' : 'English'}"
  exit 1
fi

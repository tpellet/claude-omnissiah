#!/bin/bash
# Validate claude-omnissiah marketplace structure and configuration
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MARKETPLACE_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================"
echo "  Marketplace Validation"
echo "================================"
echo ""

ERRORS=0
WARNINGS=0

error() {
  echo "ERROR: $1"
  ((ERRORS++))
}

warn() {
  echo "WARN:  $1"
  ((WARNINGS++))
}

pass() {
  echo "PASS:  $1"
}

# Test 1: Validate all plugin.json files
echo "--- Checking plugin.json files ---"
while IFS= read -r -d '' file; do
  if jq empty "$file" 2>/dev/null; then
    name=$(jq -r '.name // "unnamed"' "$file")
    pass "$file (name: $name)"
  else
    error "$file is not valid JSON"
  fi
done < <(find "$MARKETPLACE_ROOT" -name "plugin.json" -print0)
echo ""

# Test 2: Validate all hooks.json files
echo "--- Checking hooks.json files ---"
while IFS= read -r -d '' file; do
  if jq empty "$file" 2>/dev/null; then
    pass "$file"
  else
    error "$file is not valid JSON"
  fi
done < <(find "$MARKETPLACE_ROOT" -name "hooks.json" -print0)
echo ""

# Test 3: Check for hardcoded archived paths
echo "--- Checking for archived paths ---"
ARCHIVED_PATTERNS=(
  "claude-ntfy"
  "claude-reload"
  "/Screenplays/"
)

for pattern in "${ARCHIVED_PATTERNS[@]}"; do
  # Search in scripts, commands, and config files
  matches=$(grep -r "$pattern" "$MARKETPLACE_ROOT" \
    --include="*.sh" \
    --include="*.md" \
    --include="*.json" \
    2>/dev/null | grep -v ".git" | grep -v "tests/" || true)

  if [[ -n "$matches" ]]; then
    # Filter out acceptable uses (README references to history, etc.)
    critical_matches=$(echo "$matches" | grep -v "README.md" | grep -v "# " || true)
    if [[ -n "$critical_matches" ]]; then
      error "Found archived path pattern '$pattern' in:"
      echo "$critical_matches" | head -5
    else
      pass "Pattern '$pattern' only in docs (acceptable)"
    fi
  else
    pass "No archived paths matching '$pattern'"
  fi
done
echo ""

# Test 4: Validate marketplace.json
echo "--- Checking marketplace.json ---"
MARKETPLACE_JSON="$MARKETPLACE_ROOT/marketplace.json"
if [[ -f "$MARKETPLACE_JSON" ]]; then
  if jq empty "$MARKETPLACE_JSON" 2>/dev/null; then
    pass "marketplace.json is valid JSON"

    # Check each rite path exists
    for rite_path in $(jq -r '.rites[].path' "$MARKETPLACE_JSON"); do
      full_path="$MARKETPLACE_ROOT/$rite_path"
      if [[ -d "$full_path" ]]; then
        pass "Rite path exists: $rite_path"
      else
        error "Rite path missing: $rite_path"
      fi
    done

    # Check each incantation path exists
    for inc_path in $(jq -r '.incantations[].path' "$MARKETPLACE_JSON"); do
      full_path="$MARKETPLACE_ROOT/$inc_path"
      if [[ -f "$full_path" ]]; then
        pass "Incantation exists: $inc_path"
      else
        error "Incantation missing: $inc_path"
      fi
    done
  else
    error "marketplace.json is not valid JSON"
  fi
else
  error "marketplace.json not found"
fi
echo ""

# Test 5: Check for ${CLAUDE_PLUGIN_ROOT} usage in plugin commands
echo "--- Checking plugin portability ---"
for rite_dir in "$MARKETPLACE_ROOT"/rites/*/; do
  rite_name=$(basename "$rite_dir")

  # Check commands for absolute paths (should use ${CLAUDE_PLUGIN_ROOT})
  if [[ -d "$rite_dir/commands" ]]; then
    abs_paths=$(grep -r "/Users/" "$rite_dir/commands" 2>/dev/null || true)
    if [[ -n "$abs_paths" ]]; then
      error "[$rite_name] Commands have absolute paths (should use \${CLAUDE_PLUGIN_ROOT}):"
      echo "$abs_paths" | head -3
    else
      pass "[$rite_name] Commands are portable"
    fi
  fi

  # Check hooks.json for absolute paths
  if [[ -f "$rite_dir/hooks/hooks.json" ]]; then
    abs_paths=$(grep "/Users/" "$rite_dir/hooks/hooks.json" 2>/dev/null || true)
    if [[ -n "$abs_paths" ]]; then
      error "[$rite_name] hooks.json has absolute paths:"
      echo "$abs_paths" | head -3
    else
      pass "[$rite_name] hooks.json is portable"
    fi
  fi
done
echo ""

# Summary
echo "================================"
echo "  Summary"
echo "================================"
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"

if [[ $ERRORS -gt 0 ]]; then
  echo ""
  echo "FAILED - fix errors before deploying"
  exit 1
else
  echo ""
  echo "PASSED - marketplace is valid"
  exit 0
fi

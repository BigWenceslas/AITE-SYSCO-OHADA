#!/usr/bin/env bash
# Lance les tests des modules AITE SYSCOHADA et résume le résultat.
# Usage : scripts/run_tests.sh <base> <modules séparés par des virgules> [étiquettes, défaut aite_syscohada]
# Variables facultatives : ODOO_BIN, ODOO_CONF, PYTHON (défauts : ../odoo18/odoo-bin, ./odoo.conf, ../venv/bin/python)
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DB="${1:?base de données attendue}"
MODULES="${2:?modules attendus}"
TAGS="${3:-aite_syscohada}"
ODOO_BIN="${ODOO_BIN:-$ROOT/../odoo18/odoo-bin}"
ODOO_CONF="${ODOO_CONF:-$ROOT/odoo.conf}"
PYTHON="${PYTHON:-$ROOT/../venv/bin/python}"
mkdir -p "$ROOT/logs"
LOG="$ROOT/logs/tests_$(date +%Y%m%d_%H%M%S).log"
start=$(date +%s)
# -u est indispensable : sans lui, --test-tags importe les tests de tous les modules installés
"$PYTHON" "$ODOO_BIN" -c "$ODOO_CONF" -d "$DB" -u "$MODULES" --test-enable --test-tags "$TAGS" \
  --stop-after-init --log-level=test > "$LOG" 2>&1
code=$?
grep -E "FAIL:|ERROR:|CRITICAL" "$LOG" | grep -v "security risk" | head -40
grep -E "of [0-9]+ tests" "$LOG" | tail -1
if grep -qE " [1-9][0-9]* failed| [1-9][0-9]* error" "$LOG"; then code=1; fi
echo "Journal : $LOG — durée $(( $(date +%s) - start )) s — code $code"
exit $code

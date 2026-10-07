#!/usr/bin/env bash
# Prépare la base des captures d'écran du guide : Odoo 18 en français, les deux sociétés de démonstration
# (bar-hôtel et services informatiques), administrateur « admin » / « admin » rattaché aux trois sociétés.
# Usage : scripts/guide/prepare_db.sh [base, défaut aite_guide]
# Variables facultatives : ODOO_BIN, ODOO_CONF, PYTHON (mêmes défauts que scripts/run_tests.sh)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DB="${1:-aite_guide}"
ODOO_BIN="${ODOO_BIN:-$ROOT/../odoo18/odoo-bin}"
ODOO_CONF="${ODOO_CONF:-$ROOT/odoo.conf}"
PYTHON="${PYTHON:-$ROOT/../venv/bin/python}"
if psql -lqt | cut -d'|' -f1 | grep -qw "$DB"; then
  echo "La base $DB existe déjà : la supprimer d'abord (dropdb $DB) ou choisir un autre nom." >&2
  exit 1
fi
start=$(date +%s)
# français chargé avant les modules : les libellés des lignes de TVA de l10n_cm sont repris en français par les
# déclarations que calculent les données de démonstration
"$PYTHON" "$ODOO_BIN" -c "$ODOO_CONF" -d "$DB" -i aite_syscohada_demo,aite_syscohada_demo_services \
  --load-language=fr_FR --without-demo=all --stop-after-init --log-level=warn
"$PYTHON" "$ODOO_BIN" shell -c "$ODOO_CONF" -d "$DB" --no-http --log-level=warn < "$ROOT/scripts/guide/prepare_db.py"
echo "Base $DB prête en $(( $(date +%s) - start )) s : démarrer Odoo sur cette base, puis scripts/guide/capture.js."

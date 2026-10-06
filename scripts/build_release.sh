#!/usr/bin/env bash
# Construit le paquet de livraison : un seul zip avec tous les modules AITE, les dépendances OCA, le guide et le
# lisez-moi d'installation (docs/installation.md, copié en README.md).
# Usage : scripts/build_release.sh [dossier des dépôts OCA, défaut : ../oca, celui de scripts/setup_dev.sh]
# Résultat : dist/aite_syscohada_odoo18_<version>_<date>.zip
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OCA="$(cd "${1:-$ROOT/../oca}" && pwd)"
MODULES="aite_syscohada_base aite_syscohada_mis aite_syscohada_community aite_syscohada_reports aite_syscohada_demo"
OCA_MODULES="mis-builder/mis_builder server-ux/date_range reporting-engine/report_xlsx"

version() { python3 -c "import ast, sys; print(ast.literal_eval(open(sys.argv[1]).read())['version'])" "$1/__manifest__.py"; }
VERSION="$(version "$ROOT/addons/aite_syscohada_community")"
NAME="aite_syscohada_odoo18_${VERSION}_$(date +%Y%m%d)"
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT
DEST="$BUILD/aite_syscohada_odoo18"
mkdir -p "$DEST/addons" "$DEST/oca" "$DEST/docs" "$ROOT/dist"

copy_module() {  # sources sans fichiers compilés ni caches
  (cd "$(dirname "$1")" && tar --exclude='__pycache__' --exclude='*.pyc' -cf - "$(basename "$1")") | tar -xf - -C "$2"
}

{
  echo "SYSCOHADA révisé pour Odoo 18 — AITE Consulting"
  echo "Paquet construit le $(date '+%d/%m/%Y à %H:%M')"
  echo "Dépôt AITE : commit $(git -C "$ROOT" rev-parse --short HEAD)$(git -C "$ROOT" diff --quiet HEAD -- addons docs || echo ' (avec modifications non validées)')"
  echo
  echo "Modules AITE :"
  for module in $MODULES; do
    copy_module "$ROOT/addons/$module" "$DEST/addons"
    echo "  $module $(version "$ROOT/addons/$module")"
  done
  echo
  echo "Modules OCA (branche 18.0, licence AGPL-3, LICENSE-<dépôt>) :"
  for path in $OCA_MODULES; do
    repo="${path%%/*}"
    module="${path##*/}"
    [ -f "$OCA/$path/__manifest__.py" ] || { echo "Module OCA introuvable : $OCA/$path" >&2; exit 1; }
    copy_module "$OCA/$path" "$DEST/oca"
    cp "$OCA/$repo/LICENSE" "$DEST/oca/LICENSE-$repo"
    echo "  $module $(version "$OCA/$path") — github.com/OCA/$repo, commit $(git -C "$OCA/$repo" rev-parse --short HEAD)"
  done
} > "$DEST/VERSIONS.txt"

cp "$ROOT/docs/installation.md" "$DEST/README.md"
cp "$ROOT/docs/guide-syscohada-odoo18.html" "$ROOT/docs/flux-comptables-syscohada.html" "$DEST/docs/"

rm -f "$ROOT/dist/$NAME.zip"
(cd "$BUILD" && zip -qr -X "$ROOT/dist/$NAME.zip" aite_syscohada_odoo18)
echo "Paquet : dist/$NAME.zip ($(du -h "$ROOT/dist/$NAME.zip" | cut -f1))"
cat "$DEST/VERSIONS.txt"

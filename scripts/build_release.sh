#!/usr/bin/env bash
# Construit le paquet de livraison : un seul zip avec tous les modules AITE et leurs dépendances OCA dans un même
# dossier addons/ (un seul chemin à déclarer dans addons_path), requirements.txt, les licences, le guide et le
# lisez-moi d'installation (docs/installation.md, copié en README.md).
# Usage : scripts/build_release.sh [dossier des dépôts OCA, défaut : ../oca, celui de scripts/setup_dev.sh]
# Résultat : dist/aite_syscohada_odoo18_<version>_<date>.zip, suffixé « _brouillon » s'il est construit avec des
# modifications non validées dans git (un tel zip ne se livre pas : on ne pourrait pas le reconstruire).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OCA="$(cd "${1:-$ROOT/../oca}" && pwd)"
MODULES="aite_syscohada_base aite_syscohada_mis aite_syscohada_community aite_syscohada_reports
  aite_syscohada_demo_common aite_syscohada_demo aite_syscohada_demo_services"
OCA_MODULES="mis-builder/mis_builder server-ux/date_range reporting-engine/report_xlsx"
# textes des licences GNU (paquet base-files de Debian et d'Ubuntu) : AGPL-3 vient du dépôt mis-builder
COMMON_LICENSES="/usr/share/common-licenses"
# bibliothèques Python livrées en roues universelles (paquets-python/), pour une installation sans Internet :
# celles de requirements.txt et leurs dépendances absentes d'Odoo (openupgradelib tire cssselect ; lxml est fourni)
PYTHON_WHEELS="openupgradelib cssselect"
PIP="${PIP:-python3 -m pip}"

manifest() { python3 -c "import ast, sys; print(ast.literal_eval(open(sys.argv[1]).read()).get(sys.argv[2], ''))" \
  "$1/__manifest__.py" "$2"; }
VERSION="$(manifest "$ROOT/addons/aite_syscohada_community" version)"
COMMIT="$(git -C "$ROOT" rev-parse --short HEAD)"
DIRTY=""
if [ -n "$(git -C "$ROOT" status --porcelain -- addons docs scripts)" ]; then
  DIRTY="_brouillon"
  echo "Attention : modifications non validées dans addons/, docs/ ou scripts/ : paquet « brouillon », à ne pas livrer." >&2
fi
NAME="aite_syscohada_odoo18_${VERSION}_$(date +%Y%m%d)${DIRTY}"
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT
DEST="$BUILD/aite_syscohada_odoo18"
mkdir -p "$DEST/addons" "$DEST/licences" "$DEST/docs" "$DEST/paquets-python" "$ROOT/dist"

copy_module() {  # sources sans fichiers compilés ni caches ; options de tar supplémentaires après les deux arguments
  local src="$1" dest="$2"; shift 2
  (cd "$(dirname "$src")" && tar --exclude='__pycache__' --exclude='*.pyc' "$@" -cf - "$(basename "$src")") \
    | tar -xf - -C "$dest"
}

{
  echo "SYSCOHADA révisé pour Odoo 18 — AITE Consulting"
  echo "Paquet construit le $(date '+%d/%m/%Y à %H:%M')"
  echo "Dépôt AITE : commit $COMMIT${DIRTY:+ (brouillon : modifications non validées)}"
  echo
  echo "Tous les modules sont dans addons/ : un seul chemin à déclarer dans addons_path."
  echo
  echo "Modules AITE (version, licence) :"
  for module in $MODULES; do
    copy_module "$ROOT/addons/$module" "$DEST/addons"
    echo "  $module $(manifest "$ROOT/addons/$module" version), $(manifest "$ROOT/addons/$module" license)"
  done
  echo
  # sans leurs tests : ils importent odoo_test_helper (dépendance de test des dépôts OCA, absente du paquet) et
  # feraient échouer toute installation avec --test-enable, dont les builds de développement d'Odoo.sh
  echo "Modules OCA, branche 18.0, sans leur dossier tests (version, licence, origine) :"
  for path in $OCA_MODULES; do
    repo="${path%%/*}"
    module="${path##*/}"
    [ -f "$OCA/$path/__manifest__.py" ] || { echo "Module OCA introuvable : $OCA/$path" >&2; exit 1; }
    copy_module "$OCA/$path" "$DEST/addons" --exclude="$module/tests"
    echo "  $module $(manifest "$OCA/$path" version), $(manifest "$OCA/$path" license)" \
      "— github.com/OCA/$repo, commit $(git -C "$OCA/$repo" rev-parse --short HEAD)"
  done
  echo
  echo "Textes des licences : licences/ (AGPL-3 ; LGPL-3 complétée par GPL-3 ; BSD-3-Clause de cssselect). OEEL-1 :"
  echo "licence d'Odoo Enterprise, dont le texte est fourni avec Odoo Enterprise."
} > "$DEST/VERSIONS.txt"

cp "$OCA/mis-builder/LICENSE" "$DEST/licences/AGPL-3"
for license in LGPL-3 GPL-3; do
  [ -f "$COMMON_LICENSES/$license" ] || { echo "Texte de licence introuvable : $COMMON_LICENSES/$license" >&2; exit 1; }
  cp "$COMMON_LICENSES/$license" "$DEST/licences/$license"
done
$PIP download --quiet --no-deps --only-binary=:all: --python-version 3.10 -d "$DEST/paquets-python" $PYTHON_WHEELS
unzip -p "$DEST"/paquets-python/cssselect-*.whl '*.dist-info/*LICENSE*' > "$DEST/licences/BSD-3-Clause-cssselect"
[ -s "$DEST/licences/BSD-3-Clause-cssselect" ] || { echo "Licence de cssselect introuvable dans sa roue" >&2; exit 1; }
cp "$ROOT/docs/installation.md" "$DEST/README.md"
cp "$ROOT/docs/guide-syscohada-odoo18.html" "$ROOT/docs/flux-comptables-syscohada.html" "$DEST/docs/"

# Contrôles du paquet, et requirements.txt tiré des dépendances Python déclarées par les manifestes :
# chaque dépendance d'un module est un module d'Odoo ou un module livré ; chaque licence a son texte.
python3 - "$DEST" <<'PY'
import ast, os, sys
dest = sys.argv[1]
addons = os.path.join(dest, "addons")
odoo_modules = {"account", "account_reports", "base", "board", "l10n_cm", "l10n_syscohada", "web"}
# OEEL-1 : licence d'Odoo Enterprise (aite_syscohada_reports, qui dépend d'account_reports), texte fourni par Odoo
texts = {"AGPL-3": ["AGPL-3"], "LGPL-3": ["LGPL-3", "GPL-3"], "OEEL-1": []}
packaged, python_deps = set(os.listdir(addons)), set()
for name in sorted(packaged):
    if not name.startswith("aite_") and os.path.isdir(os.path.join(addons, name, "tests")):
        sys.exit(f"Tests OCA livrés (ils exigent odoo_test_helper) : {name}")
for name in sorted(packaged):
    info = ast.literal_eval(open(os.path.join(addons, name, "__manifest__.py"), encoding="utf-8").read())
    for dep in info.get("depends", []):
        if dep not in packaged and dep not in odoo_modules:
            sys.exit(f"Dépendance absente du paquet : {name} → {dep}")
    for text in texts.get(info.get("license"), [None]):
        if not text or not os.path.exists(os.path.join(dest, "licences", text)):
            sys.exit(f"Texte de licence absent du paquet : {name} ({info.get('license')})")
    python_deps |= set(info.get("external_dependencies", {}).get("python", []))
with open(os.path.join(dest, "requirements.txt"), "w", encoding="utf-8") as requirements:
    requirements.write("".join(f"{dep}\n" for dep in sorted(python_deps)))
wheels = {f.split("-")[0].lower() for f in os.listdir(os.path.join(dest, "paquets-python"))}
missing = {dep.lower() for dep in python_deps} - wheels
if missing:
    sys.exit(f"Roue absente de paquets-python/ : {', '.join(sorted(missing))}")
PY

rm -f "$ROOT/dist/$NAME.zip"
(cd "$BUILD" && zip -qr -X "$ROOT/dist/$NAME.zip" aite_syscohada_odoo18)
echo "Paquet : dist/$NAME.zip ($(du -h "$ROOT/dist/$NAME.zip" | cut -f1))"
cat "$DEST/VERSIONS.txt"
echo "requirements.txt : $(tr '\n' ' ' < "$DEST/requirements.txt")"
echo "paquets-python : $(ls "$DEST/paquets-python" | tr '\n' ' ')"

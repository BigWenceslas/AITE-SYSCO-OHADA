#!/usr/bin/env bash
# Prépare l'environnement de développement : Odoo 18 Community, modules OCA, Python, odoo.conf.
# Prérequis (Ubuntu 22.04 ou 24.04) : git, python3-venv, python3-dev, build-essential, libpq-dev, libxml2-dev,
# libxslt1-dev, libldap2-dev, libsasl2-dev, libjpeg-dev, PostgreSQL avec un rôle au nom de l'utilisateur courant.
# Usage : scripts/setup_dev.sh [dossier de travail, défaut : dossier parent du dépôt]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(cd "${1:-$ROOT/..}" && pwd)"
cd "$WORK"
[ -d odoo18 ] || git clone --depth 1 --branch 18.0 https://github.com/odoo/odoo.git odoo18
mkdir -p oca oca_addons
for repo in mis-builder server-ux reporting-engine; do
  [ -d "oca/$repo" ] || git clone --depth 1 --branch 18.0 "https://github.com/OCA/$repo.git" "oca/$repo"
done
ln -sfn "$WORK/oca/mis-builder/mis_builder" oca_addons/mis_builder
ln -sfn "$WORK/oca/server-ux/date_range" oca_addons/date_range
ln -sfn "$WORK/oca/reporting-engine/report_xlsx" oca_addons/report_xlsx
[ -d venv ] || python3 -m venv venv
venv/bin/pip install --upgrade pip wheel
venv/bin/pip install -r odoo18/requirements.txt openupgradelib
cat > "$ROOT/odoo.conf" <<EOF
[options]
addons_path = $WORK/odoo18/odoo/addons,$WORK/odoo18/addons,$WORK/oca_addons,$ROOT/addons
admin_passwd = admin
without_demo = all
log_level = warn
data_dir = $WORK/odoo-data
EOF
echo "Environnement prêt dans $WORK."
echo "Créer la base : $WORK/venv/bin/python $WORK/odoo18/odoo-bin -c $ROOT/odoo.conf -d aite_dev -i aite_syscohada_community --stop-after-init"

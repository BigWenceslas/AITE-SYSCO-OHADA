# Régénère data/syscohada_reports.xml depuis le référentiel installé.
# Usage : odoo-bin shell -d <base> --no-http < tools/generate_enterprise_xml.py
import os
from odoo.modules.module import get_module_path

xml = env["aite.syscohada.enterprise"].generate_xml()
path = os.path.join(get_module_path("aite_syscohada_reports"), "data", "syscohada_reports.xml")
with open(path, "w", encoding="utf-8") as handle:
    handle.write(xml)
print("écrit :", path, len(xml), "caractères")

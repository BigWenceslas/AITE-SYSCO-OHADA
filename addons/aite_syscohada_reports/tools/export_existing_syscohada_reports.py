# Relevé des rapports SYSCOHADA déjà fournis par Odoo Enterprise (lot 0) : exporte lignes et formules en CSV.
# Usage : odoo-bin shell -d <base_enterprise> --no-http < tools/export_existing_syscohada_reports.py > releve_enterprise.csv
import csv, sys
writer = csv.writer(sys.stdout)
writer.writerow(["rapport", "xmlid", "ligne", "code", "niveau", "libellé expression", "moteur", "formule", "sous-formule", "portée de dates"])
reports = env["account.report"].search(["|", ("name", "ilike", "syscohada"), ("name", "ilike", "ohada")])
for report in reports:
    xmlid = report.get_external_id().get(report.id, "")
    if xmlid.startswith("aite_syscohada_reports."):
        continue
    for line in report.line_ids:
        for expr in line.expression_ids or [env["account.report.expression"]]:
            writer.writerow([report.name, xmlid, line.name, line.code, line.hierarchy_level, expr.label, expr.engine,
                             expr.formula, expr.subformula, expr.date_scope])

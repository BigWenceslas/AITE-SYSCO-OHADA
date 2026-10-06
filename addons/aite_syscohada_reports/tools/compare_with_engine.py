# Compare, sur une base réelle, les rapports Enterprise SYSCOHADA au moteur de référence.
# Usage : COMPANY_ID=1 DATE_FROM=2025-01-01 DATE_TO=2025-12-31 odoo-bin shell -d <base> --no-http < tools/compare_with_engine.py
import os
company = env["res.company"].browse(int(os.environ.get("COMPANY_ID", env.company.id)))
date_from, date_to = os.environ.get("DATE_FROM", "2025-01-01"), os.environ.get("DATE_TO", "2025-12-31")
expected = env["aite.syscohada.engine"].compute(company, date_from, date_to)
gaps = 0
for statement in ("actif", "passif", "resultat", "flux"):
    report = env.ref(f"aite_syscohada_reports.report_{statement}").with_company(company)
    single = statement in ("actif", "passif")
    date = {"date_to": date_to, "mode": "single", "filter": "custom"} if single else \
        {"date_from": date_from, "date_to": date_to, "mode": "range", "filter": "custom"}
    options = report.get_options({"date": date})
    for line in report._get_lines(options):
        model, res_id = report._get_model_info_from_id(line["id"])
        if model != "account.report.line":
            continue
        code = env["account.report.line"].browse(res_id).code
        cols = {c["expression_label"]: c.get("no_format") or 0.0 for c in line["columns"]}
        ref = expected[statement][code]
        pairs = [(k, cols.get(k, 0.0), ref[k]) for k in ("brut", "amort", "net")] if single and statement == "actif" else [("balance", cols.get("balance", 0.0), ref)]
        for label, got, want in pairs:
            if abs(got - want) > 0.5:
                gaps += 1
                print(f"ÉCART {statement} {code} {label} : Enterprise {got:,.0f} / moteur {want:,.0f}")
print("Terminé :", gaps, "écart(s)")

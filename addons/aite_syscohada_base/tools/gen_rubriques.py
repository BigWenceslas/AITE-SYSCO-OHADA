# -*- coding: utf-8 -*-
"""Génère data/aite.syscohada.rubrique.csv : référentiel unique des rubriques SYSCOHADA.

Syntaxe des formules de comptes : celle du moteur « account_codes » d'Odoo Enterprise
(préfixes, exclusions « \\(…) », suffixe D ou C = comptes à solde débiteur ou créditeur).
Les cellules DSF proviennent du relevé du classeur DSF Normal de la DGI (version du 09/03/2021).
"""
import csv, os

# code, libellé, type, formule brut, formule amort/dépréc, agrégation, note, ligne classeur, code DGI
ACTIF = [
    ("AD", "Immobilisations incorporelles", "subtotal", "", "", "AE+AF+AG+AH", "3", 12, ""),
    ("AE", "Frais de développement et de prospection", "detail", "211+2181+2191", "2811+28181+2911+29181+29191", "", "3", 13, ""),
    ("AF", "Brevets, licences, logiciels et droits similaires", "detail", "212+213+214+2193", "2812+2813+2814+2912+2913+2914+29193", "", "3", 14, ""),
    ("AG", "Fonds commercial et droit au bail", "detail", "215+216", "2815+2816+2915+2916", "", "3", 15, ""),
    ("AH", "Autres immobilisations incorporelles", "detail", "217+218\\(2181)+2198", "2817+2818\\(28181)+2917+2918\\(29181)+2919\\(29191,29193)", "", "3", 16, ""),
    ("AI", "Immobilisations corporelles", "subtotal", "", "", "AJ+AK+AL+AM+AN", "3", 17, ""),
    ("AJ", "Terrains", "detail", "22", "282+292", "", "3", 18, ""),
    ("AK", "Bâtiments", "detail", "231+232+233+237+2391+2393", "2831+2832+2833+2837+2931+2932+2933+2937+29391+29393", "", "3", 19, ""),
    ("AL", "Aménagements, agencements et installations", "detail", "234+235+238+239\\(2391,2393)", "2834+2835+2838+2934+2935+2938+2939\\(29391,29393)", "", "3", 20, ""),
    ("AM", "Matériel, mobilier et actifs biologiques", "detail", "24\\(245,2495)", "284\\(2845)+294\\(2945,2949)+2949\\(29495)", "", "3", 21, ""),
    ("AN", "Matériel de transport", "detail", "245+2495", "2845+2945+29495", "", "3", 22, ""),
    ("AP", "Avances et acomptes versés sur immobilisations", "detail", "251+252", "2951+2952", "", "3", 23, ""),
    ("AQ", "Immobilisations financières", "subtotal", "", "", "AR+AS", "4", 24, ""),
    ("AR", "Titres de participation", "detail", "26", "296", "", "4", 25, ""),
    ("AS", "Autres immobilisations financières", "detail", "27", "297", "", "4", 26, ""),
    ("AZ", "TOTAL ACTIF IMMOBILISÉ", "total", "", "", "AD+AI+AP+AQ", "", 27, ""),
    ("BA", "Actif circulant HAO", "detail", "48D", "498", "", "5", 28, ""),
    ("BB", "Stocks et encours", "detail", "31+32+33+34+35+36+37+38", "39", "", "6", 29, ""),
    ("BG", "Créances et emplois assimilés", "subtotal", "", "", "BH+BI+BJ", "", 30, "BC"),
    ("BH", "Fournisseurs, avances versées", "detail", "40D", "490", "", "17", 31, ""),
    ("BI", "Clients", "detail", "41D", "491", "", "7", 32, ""),
    ("BJ", "Autres créances", "detail", "18\\(181,182,183,184)D+42D+43D+44D+45D+46D+47\\(478,479)D", "492+493+494+495+496+497", "", "8", 33, ""),
    ("BK", "TOTAL ACTIF CIRCULANT", "total", "", "", "BA+BB+BG", "", 34, ""),
    ("BQ", "Titres de placement", "detail", "50", "590", "", "9", 35, ""),
    ("BR", "Valeurs à encaisser", "detail", "51", "591", "", "10", 36, ""),
    ("BS", "Banques, chèques postaux, caisse et assimilés", "detail", "52D+53D+54D+55D+57D+58D", "592+593+594", "", "11", 37, ""),
    ("BT", "TOTAL TRÉSORERIE-ACTIF", "total", "", "", "BQ+BR+BS", "", 38, ""),
    ("BU", "Écart de conversion-actif", "detail", "478", "", "", "12", 39, ""),
    ("BZ", "TOTAL GÉNÉRAL", "total", "", "", "AZ+BK+BT+BU", "", 40, ""),
]
# code, libellé, type, formule, agrégation, note, ligne classeur, code DGI
PASSIF = [
    ("CA", "Capital", "detail", "-101-102-103-104", "", "13", 12, ""),
    ("CB", "Apporteurs, capital non appelé", "detail", "-109", "", "13", 13, ""),
    ("CD", "Primes liées au capital social", "detail", "-105", "", "14", 14, ""),
    ("CE", "Écarts de réévaluation", "detail", "-106", "", "3e", 15, ""),
    ("CF", "Réserves indisponibles", "detail", "-111-112-113", "", "14", 16, ""),
    ("CG", "Réserves libres", "detail", "-118", "", "14", 17, ""),
    ("CH", "Report à nouveau", "detail", "-12", "", "14", 18, ""),
    ("CJ", "Résultat net de l'exercice", "detail", "-13-6-7-8-999999", "", "", 19, ""),
    ("CL", "Subventions d'investissement", "detail", "-14", "", "15", 20, ""),
    ("CM", "Provisions réglementées", "detail", "-15", "", "15", 21, ""),
    ("CP", "TOTAL CAPITAUX PROPRES ET RESSOURCES ASSIMILÉES", "total", "", "CA+CB+CD+CE+CF+CG+CH+CJ+CL+CM", "", 22, ""),
    ("DA", "Emprunts et dettes financières diverses", "detail", "-16-181-182-183-184", "", "16", 23, ""),
    ("DB", "Dettes de location-acquisition", "detail", "-17", "", "16", 24, ""),
    ("DC", "Provisions pour risques et charges", "detail", "-19", "", "16", 25, ""),
    ("DD", "TOTAL DETTES FINANCIÈRES ET RESSOURCES ASSIMILÉES", "total", "", "DA+DB+DC", "", 26, ""),
    ("DF", "TOTAL RESSOURCES STABLES", "total", "", "CP+DD", "", 27, ""),
    ("DH", "Dettes circulantes HAO", "detail", "-48C-4998", "", "5", 28, ""),
    ("DI", "Clients, avances reçues", "detail", "-41C", "", "7", 29, ""),
    ("DJ", "Fournisseurs d'exploitation", "detail", "-40C", "", "17", 30, ""),
    ("DK", "Dettes fiscales et sociales", "detail", "-42C-43C-44C", "", "18", 31, ""),
    ("DM", "Autres dettes", "detail", "-18\\(181,182,183,184)C-45C-46C-47\\(478,479)C", "", "19", 32, ""),
    ("DN", "Provisions pour risques à court terme", "detail", "-499\\(4998)-599", "", "19", 33, ""),
    ("DP", "TOTAL PASSIF CIRCULANT", "total", "", "DH+DI+DJ+DK+DM+DN", "", 34, ""),
    ("DQ", "Banques, crédits d'escompte", "detail", "-564-565", "", "20", 36, ""),
    ("DR", "Banques, établissements financiers et crédits de trésorerie", "detail", "-52C-53C-54C-55C-57C-58C-56\\(564,565)", "", "20", 37, ""),
    ("DT", "TOTAL TRÉSORERIE-PASSIF", "total", "", "DQ+DR", "", 38, ""),
    ("DV", "Écart de conversion-passif", "detail", "-479", "", "12", 39, "DY"),
    ("DZ", "TOTAL GÉNÉRAL", "total", "", "DF+DP+DT+DV", "", 40, ""),
]
# code, libellé, type, formule, agrégation, note, ligne, signe DSF (-1 : charge saisie en positif)
RESULTAT = [
    ("TA", "Ventes de marchandises", "detail", "-701", "", "21", 11, 1),
    ("RA", "Achats de marchandises", "detail", "-601", "", "22", 12, -1),
    ("RB", "Variation de stocks de marchandises", "detail", "-6031", "", "6", 13, -1),
    ("XA", "MARGE COMMERCIALE", "subtotal", "", "TA+RA+RB", "", 14, 1),
    ("TB", "Ventes de produits fabriqués", "detail", "-702-703-704", "", "21", 15, 1),
    ("TC", "Travaux, services vendus", "detail", "-705-706", "", "21", 16, 1),
    ("TD", "Produits accessoires", "detail", "-707", "", "21", 17, 1),
    ("XB", "CHIFFRE D'AFFAIRES", "subtotal", "", "TA+TB+TC+TD", "", 18, 1),
    ("TE", "Production stockée (ou déstockage)", "detail", "-73", "", "6", 19, 1),
    ("TF", "Production immobilisée", "detail", "-72", "", "21", 20, 1),
    ("TG", "Subventions d'exploitation", "detail", "-71", "", "21", 21, 1),
    ("TH", "Autres produits", "detail", "-75", "", "21", 22, 1),
    ("TI", "Transferts de charges d'exploitation", "detail", "-781", "", "12", 23, 1),
    ("RC", "Achats de matières premières et fournitures liées", "detail", "-602", "", "22", 24, -1),
    ("RD", "Variation de stocks de matières premières et fournitures liées", "detail", "-6032", "", "6", 25, -1),
    ("RE", "Autres achats", "detail", "-604-605-608", "", "22", 26, -1),
    ("RF", "Variation de stocks d'autres approvisionnements", "detail", "-6033", "", "6", 27, -1),
    ("RG", "Transports", "detail", "-61", "", "23", 28, -1),
    ("RH", "Services extérieurs", "detail", "-62-63", "", "24", 29, -1),
    ("RI", "Impôts et taxes", "detail", "-64", "", "25", 30, -1),
    ("RJ", "Autres charges", "detail", "-65", "", "26", 31, -1),
    ("XC", "VALEUR AJOUTÉE", "subtotal", "", "XB+RA+RB+TE+TF+TG+TH+TI+RC+RD+RE+RF+RG+RH+RI+RJ", "", 32, 1),
    ("RK", "Charges de personnel", "detail", "-66", "", "27", 33, -1),
    ("XD", "EXCÉDENT BRUT D'EXPLOITATION", "subtotal", "", "XC+RK", "28", 34, 1),
    ("TJ", "Reprises d'amortissements, provisions et dépréciations", "detail", "-791-798-799", "", "28", 35, 1),
    ("RL", "Dotations aux amortissements, aux provisions et dépréciations", "detail", "-681-691", "", "3C&28", 36, -1),
    ("XE", "RÉSULTAT D'EXPLOITATION", "subtotal", "", "XD+TJ+RL", "", 37, 1),
    ("TK", "Revenus financiers et assimilés", "detail", "-77", "", "29", 38, 1),
    ("TL", "Reprises de provisions et dépréciations financières", "detail", "-797", "", "28", 39, 1),
    ("TM", "Transferts de charges financières", "detail", "-787", "", "12", 40, 1),
    ("RM", "Frais financiers et charges assimilées", "detail", "-67", "", "29", 41, -1),
    ("RN", "Dotations aux provisions et aux dépréciations financières", "detail", "-687-697", "", "3C&28", 42, -1),
    ("XF", "RÉSULTAT FINANCIER", "subtotal", "", "TK+TL+TM+RM+RN", "", 43, 1),
    ("XG", "RÉSULTAT DES ACTIVITÉS ORDINAIRES", "subtotal", "", "XE+XF", "", 44, 1),
    ("TN", "Produits des cessions d'immobilisations", "detail", "-82", "", "3D", 45, 1),
    ("TO", "Autres produits HAO", "detail", "-84-86-88", "", "30", 46, 1),
    ("RO", "Valeurs comptables des cessions d'immobilisations", "detail", "-81", "", "3D", 47, -1),
    ("RP", "Autres charges HAO", "detail", "-83-85", "", "30", 48, -1),
    ("XH", "RÉSULTAT HORS ACTIVITÉS ORDINAIRES", "subtotal", "", "TN+TO+RO+RP", "", 49, 1),
    ("RQ", "Participation des travailleurs", "detail", "-87", "", "30", 50, -1),
    ("RS", "Impôts sur le résultat", "detail", "-89", "", "", 51, -1),
    ("XI", "RÉSULTAT NET", "total", "", "XG+XH+RQ+RS", "", 52, 1),
]
# Tableau des flux de trésorerie : formules du moteur (voir syscohada_engine.py)
FLUX = [
    ("ZA", "Trésorerie nette au 1er janvier", "detail", "B0:BT-B0:DT", "", "", 10, 1),
    ("FA", "Capacité d'autofinancement globale (CAFG)", "detail", "R:XI+P:681+P:687+P:691+P:697+P:85+P:791+P:797+P:798+P:799+P:86+P:81+P:654+P:82+P:754", "", "", 12, 1),
    ("FB", "Actif circulant HAO", "detail", "-V:BA+E:485-S:485", "", "", 13, -1),
    ("FC", "Variation des stocks", "detail", "-V:BB", "", "", 14, -1),
    ("FD", "Variation des créances", "detail", "-V:BG-V:BU", "", "", 15, -1),
    ("FE", "Variation du passif circulant", "detail", "V:DI+V:DJ+V:DK+V:DM+V:DN+V:DH+V:DV+E:481-S:481+E:482-S:482+E:465-S:465-E:166+S:166-E:176+S:176", "", "", 16, 1),
    ("ZB", "Flux de trésorerie provenant des activités opérationnelles", "subtotal", "", "FA+FB+FC+FD+FE", "", 18, 1),
    ("FF", "Décaissements liés aux acquisitions d'immobilisations incorporelles", "detail", "-DX:(21+251)-E:4811+S:4811", "", "", 20, -1),
    ("FG", "Décaissements liés aux acquisitions d'immobilisations corporelles", "detail", "-DX:(22+23+24+252)-E:481\\(4811)+S:481\\(4811)-E:482+S:482", "", "", 21, -1),
    ("FH", "Décaissements liés aux acquisitions d'immobilisations financières", "detail", "-DX:(26+27)", "", "", 22, -1),
    ("FI", "Encaissements liés aux cessions d'immobilisations incorporelles et corporelles", "detail", "-P:82\\(826)-P:754-E:485+S:485", "", "", 23, 1),
    ("FJ", "Encaissements liés aux cessions d'immobilisations financières", "detail", "-P:826+CX:(26+27)-P:816", "", "", 24, 1),
    ("ZC", "Flux de trésorerie provenant des activités d'investissement", "subtotal", "", "FF+FG+FH+FI+FJ", "", 25, 1),
    ("FK", "Augmentations de capital par apports nouveaux", "detail", "V:CA+V:CB+V:CD+V:CE+V:CF+V:CG+V:CH+V:CJ-R:XI-E:465+S:465+D:465+D:104", "", "", 27, 1),
    ("FL", "Subventions d'investissement reçues", "detail", "C:14", "", "", 28, 1),
    ("FM", "Prélèvements sur le capital", "detail", "-D:104", "", "", 29, -1),
    ("FN", "Dividendes versés", "detail", "-D:465", "", "", 30, -1),
    ("ZD", "Flux de trésorerie provenant des capitaux propres", "subtotal", "", "FK+FL+FM+FN", "", 31, 1),
    ("FO", "Emprunts", "detail", "C:16\\(166)", "", "", 33, 1),
    ("FP", "Autres dettes financières", "detail", "C:(17\\(176)+181+182+183+184)", "", "", 34, 1),
    ("FQ", "Remboursements des emprunts et autres dettes financières", "detail", "-D:(16\\(166)+17\\(176)+181+182+183+184)", "", "", 35, -1),
    ("ZE", "Flux de trésorerie provenant des capitaux étrangers", "subtotal", "", "FO+FP+FQ", "", 36, 1),
    ("ZF", "Flux de trésorerie provenant des activités de financement", "subtotal", "", "ZD+ZE", "", 37, 1),
    ("ZG", "Variation de la trésorerie nette de la période", "subtotal", "", "ZB+ZC+ZF", "", 38, 1),
    ("ZH", "Trésorerie nette au 31 décembre", "total", "", "ZA+ZG", "", 39, 1),
]

FIELDS = ["id", "statement", "code", "name", "sequence", "line_type", "formula", "formula_brut", "formula_amort",
          "aggregation", "note", "dsf_code", "dsf_sheet", "dsf_cell_brut", "dsf_cell_amort", "dsf_cell", "dsf_cell_n1", "dsf_sign"]

def rows():
    seq = 0
    for code, name, typ, brut, amort, agg, note, line, dgi in ACTIF:
        seq += 10
        yield {"id": f"rub_actif_{code}", "statement": "actif", "code": code, "name": name, "sequence": seq,
               "line_type": typ, "formula": "", "formula_brut": brut, "formula_amort": amort, "aggregation": agg,
               "note": note, "dsf_code": dgi or code, "dsf_sheet": "BILAN PAYSAGE", "dsf_cell_brut": f"D{line}",
               "dsf_cell_amort": f"E{line}", "dsf_cell": f"F{line}", "dsf_cell_n1": f"G{line}", "dsf_sign": 1}
    for code, name, typ, form, agg, note, line, dgi in PASSIF:
        seq += 10
        yield {"id": f"rub_passif_{code}", "statement": "passif", "code": code, "name": name, "sequence": seq,
               "line_type": typ, "formula": form, "formula_brut": "", "formula_amort": "", "aggregation": agg,
               "note": note, "dsf_code": dgi or code, "dsf_sheet": "BILAN PAYSAGE", "dsf_cell_brut": "",
               "dsf_cell_amort": "", "dsf_cell": f"K{line}", "dsf_cell_n1": f"L{line}", "dsf_sign": 1}
    for statement, sheet, items in (("resultat", "COMPTE DE RESULTAT", RESULTAT), ("flux", "TABLEAU DES FLUX DE TRESORERIE", FLUX)):
        for code, name, typ, form, agg, note, line, sign in items:
            seq += 10
            yield {"id": f"rub_{statement}_{code}", "statement": statement, "code": code, "name": name, "sequence": seq,
                   "line_type": typ, "formula": form, "formula_brut": "", "formula_amort": "", "aggregation": agg,
                   "note": note, "dsf_code": code, "dsf_sheet": sheet, "dsf_cell_brut": "", "dsf_cell_amort": "",
                   "dsf_cell": f"E{line}", "dsf_cell_n1": f"F{line}", "dsf_sign": sign}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "data", "aite.syscohada.rubrique.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        n = 0
        for r in rows():
            w.writerow(r); n += 1
    print("rubriques écrites :", n)

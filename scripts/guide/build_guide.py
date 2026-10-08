# Construit le guide HTML autonome (un seul fichier, captures d'écran comprises) depuis sa source Markdown.
# Usage : python scripts/guide/build_guide.py docs/guide/guide.md docs/guide-syscohada-odoo18.html
# Prérequis : pip install markdown. Les images « ![légende](captures/NN-nom.webp) » seules dans leur paragraphe
# deviennent des figures numérotées, intégrées en base64 (captures : scripts/guide/capture.js puis
# convert_captures.py).
import base64
import html
import os
import re
import sys
import unicodedata

import markdown

src, out = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
VERSION = "18.0.1.3.1"
DATE = "8 octobre 2026"


def webp_size(data):
    """Largeur et hauteur d'une image WebP, lues dans son en-tête."""
    assert data[:4] == b"RIFF" and data[8:12] == b"WEBP", "image WebP attendue"
    chunk = data[12:16]
    if chunk == b"VP8 ":
        return int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF
    if chunk == b"VP8L":
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1

# En-tête du document : titre et ligne de date remplacés par un bandeau propre
lines = text.splitlines()
assert lines[0].startswith("# ")
title = lines[0][2:].strip()
body_md = "\n".join(lines[1:])


def slug(s, used):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower() or "section"
    base, n = s, 2
    while s in used:
        s, n = f"{base}-{n}", n + 1
    used.add(s)
    return s


md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
content = md.convert(body_md)

# Identifiants des titres et table des matières
used, toc = set(), []


def add_id(m):
    level, inner = m.group(1), m.group(2)
    plain = html.unescape(re.sub(r"<[^>]+>", "", inner))
    ident = slug(plain, used)
    if level == "2":
        toc.append((plain, ident, []))
    elif toc:
        toc[-1][2].append((plain, ident))
    return f'<h{level} id="{ident}">{inner}<a class="anchor" href="#{ident}" aria-label="Lien vers cette section">#</a></h{level}>'


content = re.sub(r"<h([23])>(.*?)</h\1>", add_id, content)

# Montants : espace fine insécable entre les groupes de chiffres (12 345 678), hors code et hors balises
def thin_spaces(text):
    return re.sub(r"(?<=\d) (?=\d{3}(?!\d))", "\u202f", text)


content = "".join(part if part.startswith("<") else thin_spaces(part)
                  for part in re.split(r"(<pre>.*?</pre>|<code>.*?</code>|<[^>]+>)", content, flags=re.S))

# Figures : captures intégrées, numérotées, agrandies au clic ; table des figures en annexe
figures = []


def add_figure(m):
    caption, path = html.unescape(m.group(1)), m.group(2)
    data = open(os.path.join(os.path.dirname(src), path), "rb").read()
    width, height = webp_size(data)
    number = len(figures) + 1
    ident = f"figure-{number}"
    figures.append((number, ident, caption))
    encoded = base64.b64encode(data).decode()
    return (f'<figure class="shot" id="{ident}"><button class="zoom" type="button" '
            f'aria-label="Agrandir la figure {number}"><img src="data:image/webp;base64,{encoded}" '
            f'alt="{html.escape(caption)}" width="{width}" height="{height}" loading="lazy" decoding="async"></button>'
            f'<figcaption><strong>Figure {number}.</strong> {thin_spaces(html.escape(caption, quote=False))}</figcaption></figure>')


content = re.sub(r'<p><img alt="([^"]*)" src="(captures/[^"]+\.webp)" ?/?></p>', add_figure, content)
table = "".join(f'<li><a href="#{i}">Figure {n}.</a> {html.escape(c.split(" : ")[0].split(". ")[0], quote=False)}</li>'
                for n, i, c in figures)
content = content.replace("<!-- table des figures -->", f'<ol class="figures">{table}</ol>')
words = len(re.sub(r"<[^>]+>", " ", content).split())
# Coupures possibles après « _ » et « . » dans le code des tableaux, jamais au milieu d'un mot
def soft_breaks(m):
    cell = m.group(0)
    return re.sub(r"<code>(.*?)</code>", lambda c: "<code>" + re.sub(r"([_./])", r"\1<wbr>", c.group(1)) + "</code>", cell)
content = re.sub(r"<td>.*?</td>", soft_breaks, content, flags=re.S)
# Tableaux défilants sur petit écran
content = content.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
# Les sections de niveau 2 deviennent des blocs <section>
parts = re.split(r'(?=<h2 id=")', content)
content = "".join(f'<section class="chapter">{p}</section>' if p.startswith("<h2") else p for p in parts)

toc_html = []
for name, ident, subs in toc:
    sub = "".join(f'<li><a href="#{i}">{html.escape(n)}</a></li>' for n, i in subs)
    toc_html.append(
        f'<li class="toc-ch"><a href="#{ident}">{html.escape(name)}</a>'
        + (f'<ul class="toc-sub">{sub}</ul>' if sub else "") + "</li>")
toc_html = "\n".join(toc_html)
words_fr = f"{words:,}".replace(",", "\u202f")

page = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guide SYSCOHADA Odoo 18</title>
<meta name="description" content="Guide complet des modules AITE SYSCOHADA révisé pour Odoo 18 : installation, paramétrage, saisie, états financiers, déclaration I/TVA-IR, clôture, tests, développement.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;0,8..60,600;1,8..60,400&display=swap">
<style>
:root {{
  --paper:#F3F4F8; --surface:#FFFFFF; --ink:#221A35; --ink-soft:#5B5470; --line:#DCD9E6;
  --violet:#5B2C8F; --violet-soft:#EEE7F8; --on-violet:#FFFFFF;
  --teal:#087880; --teal-soft:#DFF1F2; --orange:#B8520F; --orange-soft:#FBEADB; --odoo:#714B67;
  --code-bg:#F1EEF7;
  --font-text:"Source Serif 4","Source Serif Pro",Georgia,"Times New Roman",serif;
  --font-ui:"Poppins","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
  --font-mono:ui-monospace,"SFMono-Regular",Menlo,Consolas,"Liberation Mono",monospace;
  color-scheme: light;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper:#141119; --surface:#1C1824; --ink:#EFEBF7; --ink-soft:#ADA5C2; --line:#383049;
    --violet:#BB95F4; --violet-soft:#2C2143; --on-violet:#17121F;
    --teal:#5CCBD2; --teal-soft:#12302F; --orange:#F2A35C; --orange-soft:#33230F; --odoo:#C99BBE;
    --code-bg:#251F31; color-scheme: dark;
  }}
}}
:root[data-theme="dark"] {{
  --paper:#141119; --surface:#1C1824; --ink:#EFEBF7; --ink-soft:#ADA5C2; --line:#383049;
  --violet:#BB95F4; --violet-soft:#2C2143; --on-violet:#17121F;
  --teal:#5CCBD2; --teal-soft:#12302F; --orange:#F2A35C; --orange-soft:#33230F; --odoo:#C99BBE;
  --code-bg:#251F31; color-scheme: dark;
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; scroll-padding-top: 72px; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:var(--font-text); font-size:17px; line-height:1.6; }}
a {{ color:var(--violet); text-underline-offset:2px; }}
.topbar {{ position:sticky; top:0; z-index:20; display:flex; align-items:center; gap:12px; padding:10px 20px;
  background:var(--surface); border-bottom:1px solid var(--line); font-family:var(--font-ui); font-size:14px; }}
.topbar .brand {{ font-weight:600; color:var(--ink); text-decoration:none; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.topbar .brand span {{ color:var(--violet); }}
.topbar .spacer {{ flex:1; }}
.btn {{ font:inherit; font-size:13px; padding:6px 12px; border-radius:8px; border:1px solid var(--line); background:var(--surface); color:var(--ink); cursor:pointer; }}
.btn:hover {{ border-color:var(--violet); color:var(--violet); }}
#toc-toggle {{ display:none; }}
.layout {{ display:grid; grid-template-columns:300px minmax(0,1fr); max-width:1320px; margin:0 auto; }}
nav.toc {{ position:sticky; top:53px; align-self:start; height:calc(100vh - 53px); overflow:auto; padding:20px 12px 40px 20px;
  font-family:var(--font-ui); font-size:13.5px; border-right:1px solid var(--line); }}
nav.toc input {{ width:100%; font:inherit; padding:8px 10px; border-radius:8px; border:1px solid var(--line); background:var(--surface); color:var(--ink); margin-bottom:12px; }}
nav.toc ul {{ list-style:none; margin:0; padding:0; }}
nav.toc .toc-ch > a {{ display:block; font-weight:600; padding:6px 8px; border-radius:6px; color:var(--ink); text-decoration:none; }}
nav.toc .toc-sub a {{ display:block; padding:3px 8px 3px 18px; color:var(--ink-soft); text-decoration:none; border-radius:6px; }}
nav.toc a:hover {{ background:var(--violet-soft); color:var(--violet); }}
nav.toc a.active {{ background:var(--violet-soft); color:var(--violet); }}
nav.toc .toc-sub {{ display:none; margin-bottom:6px; }}
nav.toc .toc-ch.open .toc-sub, nav.toc.filtering .toc-sub {{ display:block; }}
nav.toc .hidden {{ display:none !important; }}
main {{ padding:0 40px 80px; min-width:0; }}
.hero {{ margin:32px 0 8px; padding:28px 32px; border-radius:14px; background:var(--violet); color:var(--on-violet); }}
.hero h1 {{ font-family:var(--font-ui); font-size:30px; line-height:1.25; margin:0 0 10px; font-weight:700; }}
.hero p {{ margin:0; font-family:var(--font-ui); font-size:14px; opacity:.92; }}
.hero .meta {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:16px; }}
.hero .meta span {{ font-family:var(--font-ui); font-size:12.5px; padding:4px 10px; border-radius:99px; background:rgba(255,255,255,.16); }}
section.chapter {{ background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:8px 32px 24px; margin-top:24px; }}
h2 {{ font-family:var(--font-ui); font-size:24px; margin:24px 0 12px; color:var(--violet); font-weight:600; }}
h3 {{ font-family:var(--font-ui); font-size:18px; margin:28px 0 8px; font-weight:600; }}
h2 .anchor, h3 .anchor {{ margin-left:8px; font-size:.75em; color:var(--line); text-decoration:none; opacity:0; }}
h2:hover .anchor, h3:hover .anchor {{ opacity:1; color:var(--ink-soft); }}
p, li {{ max-width:78ch; }}
ul, ol {{ padding-left:1.4em; }}
li {{ margin:4px 0; }}
strong {{ font-weight:600; }}
code {{ font-family:var(--font-mono); font-size:.86em; background:var(--code-bg); padding:.1em .35em; border-radius:4px; word-break:break-word; }}
section.chapter p, section.chapter li {{ overflow-wrap:break-word; }}
pre {{ background:var(--code-bg); border:1px solid var(--line); border-radius:10px; padding:14px 16px; overflow:auto; font-size:14px; line-height:1.5; }}
pre code {{ background:none; padding:0; font-size:inherit; word-break:normal; }}
blockquote {{ margin:16px 0; padding:10px 16px; border-left:4px solid var(--teal); background:var(--teal-soft); border-radius:6px; }}
.table-wrap {{ overflow-x:auto; margin:14px 0 18px; border:1px solid var(--line); border-radius:10px; }}
table {{ border-collapse:collapse; width:100%; font-family:var(--font-ui); font-size:13.5px; line-height:1.45; }}
th, td {{ text-align:left; vertical-align:top; padding:8px 12px; border-bottom:1px solid var(--line); }}
th {{ background:var(--violet-soft); color:var(--ink); font-weight:600; white-space:nowrap; }}
tr:last-child td {{ border-bottom:none; }}
tbody tr:nth-child(even) td {{ background:color-mix(in srgb, var(--paper) 55%, var(--surface)); }}
td code {{ font-size:.92em; word-break:normal; overflow-wrap:normal; }}
h4 {{ font-family:var(--font-ui); font-size:16px; margin:24px 0 6px; font-weight:600; color:var(--teal); }}
figure.shot {{ margin:18px 0 24px; }}
figure.shot button.zoom {{ display:block; width:100%; padding:0; border:1px solid var(--line); border-radius:10px;
  overflow:hidden; background:var(--surface); cursor:zoom-in; }}
figure.shot img {{ display:block; width:100%; height:auto; }}
figure.shot figcaption {{ font-family:var(--font-ui); font-size:13.5px; line-height:1.5; color:var(--ink-soft); margin-top:8px; }}
figure.shot figcaption strong {{ color:var(--ink); }}
ol.figures {{ font-family:var(--font-ui); font-size:14px; list-style:none; padding:0; }}
ol.figures li {{ max-width:none; }}
.lightbox {{ position:fixed; inset:0; z-index:50; display:none; align-items:center; justify-content:center; padding:20px;
  background:rgba(12,9,18,.9); cursor:zoom-out; }}
.lightbox.open {{ display:flex; }}
.lightbox img {{ max-width:100%; max-height:100%; border-radius:8px; box-shadow:0 12px 40px rgba(0,0,0,.5); }}
footer {{ margin:40px 0 0; font-family:var(--font-ui); font-size:12.5px; color:var(--ink-soft); }}
#to-top {{ font-family:var(--font-ui); position:fixed; right:18px; bottom:18px; z-index:30; display:none; }}
@media (max-width: 960px) {{
  .layout {{ grid-template-columns:minmax(0,1fr); }}
  #toc-toggle {{ display:inline-block; }}
  nav.toc {{ position:fixed; top:53px; left:0; width:min(320px, 88vw); z-index:25; background:var(--surface);
    transform:translateX(-105%); transition:transform .2s ease; box-shadow:0 8px 24px rgba(0,0,0,.18); }}
  nav.toc.open {{ transform:none; }}
  main {{ padding:0 16px 60px; }}
  section.chapter {{ padding:4px 16px 18px; }}
  .hero {{ padding:22px 18px; }}
  .hero h1 {{ font-size:23px; }}
  body {{ font-size:16px; }}
  #print-btn {{ display:none; }}
}}
@media print {{
  .topbar, nav.toc, #to-top, .anchor {{ display:none !important; }}
  .layout {{ display:block; }}
  body {{ background:#fff; color:#000; font-size:11pt; }}
  section.chapter {{ border:none; padding:0; break-before:page; }}
  .hero {{ background:#fff; color:#000; border:2px solid #000; }}
  .table-wrap {{ overflow:visible; }}
  figure.shot {{ break-inside:avoid; }}
  figure.shot button.zoom {{ border:none; }}
  .lightbox {{ display:none !important; }}
  th {{ background:#eee; }}
}}
</style>
</head>
<body>
<header class="topbar">
  <button class="btn" id="toc-toggle" aria-controls="toc" aria-expanded="false">Sommaire</button>
  <a class="brand" href="#top"><span>AITE</span> · Guide SYSCOHADA révisé pour Odoo 18</a>
  <div class="spacer"></div>
  <button class="btn" id="theme-toggle" type="button" aria-label="Changer de thème">Thème</button>
  <button class="btn" id="print-btn" type="button" onclick="window.print()">Imprimer</button>
</header>
<div class="layout" id="top">
  <nav class="toc" id="toc" aria-label="Sommaire">
    <input type="search" id="toc-filter" placeholder="Filtrer le sommaire…" aria-label="Filtrer le sommaire">
    <ul>
{toc_html}
    </ul>
  </nav>
  <main>
    <div class="hero">
      <h1>{html.escape(title)}</h1>
      <p>Installation, paramétrage, saisie, états financiers, déclaration mensuelle I/TVA-IR, clôture, tests et développement des modules AITE pour Odoo 18 Community, illustrés sur deux sociétés de démonstration : un bar-hôtel et une société de services informatiques.</p>
      <div class="meta">
        <span>{DATE}</span><span>Modules {VERSION}</span><span>AITE Consulting, Douala</span><span>Odoo 18.0 Community</span><span>Dépôt BigWenceslas/AITE-SYSCO-OHADA</span><span>{len(figures)} captures d'écran</span><span>{words_fr} mots</span>
      </div>
    </div>
{content}
    <footer>Guide établi pour les modules AITE SYSCOHADA (branche claude/keen-bohr-76nuin). Taux et barèmes fiscaux : à vérifier à chaque loi de finances ; les positions fiscales engageantes se valident avec un expert-comptable agréé.</footer>
  </main>
</div>
<button class="btn" id="to-top" type="button" onclick="window.scrollTo({{top:0}})">Haut de page</button>
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Capture agrandie"><img alt=""></div>
<script>
(function () {{
  var root = document.documentElement;
  try {{ var t = localStorage.getItem("aite-guide-theme"); if (t) root.setAttribute("data-theme", t); }} catch (e) {{}}
  document.getElementById("theme-toggle").addEventListener("click", function () {{
    var dark = root.getAttribute("data-theme") === "dark" ||
      (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
    var next = dark ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try {{ localStorage.setItem("aite-guide-theme", next); }} catch (e) {{}}
  }});
  var toc = document.getElementById("toc"), tog = document.getElementById("toc-toggle");
  tog.addEventListener("click", function () {{
    var o = toc.classList.toggle("open"); tog.setAttribute("aria-expanded", o ? "true" : "false");
  }});
  toc.addEventListener("click", function (e) {{ if (e.target.tagName === "A") toc.classList.remove("open"); }});
  var filter = document.getElementById("toc-filter");
  var norm = function (s) {{ return s.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase(); }};
  filter.addEventListener("input", function () {{
    var q = norm(filter.value.trim());
    toc.classList.toggle("filtering", q.length > 0);
    toc.querySelectorAll(".toc-ch").forEach(function (ch) {{
      var any = norm(ch.firstElementChild.textContent).indexOf(q) >= 0;
      ch.querySelectorAll(".toc-sub li").forEach(function (li) {{
        var hit = !q || norm(li.textContent).indexOf(q) >= 0;
        li.classList.toggle("hidden", !hit && !any);
        if (hit && q) any = true;
      }});
      ch.classList.toggle("hidden", !any && q.length > 0);
    }});
  }});
  var links = {{}};
  toc.querySelectorAll("a").forEach(function (a) {{ links[a.getAttribute("href").slice(1)] = a; }});
  var heads = document.querySelectorAll("main h2[id], main h3[id]");
  var current = null;
  var onScroll = function () {{
    var y = window.scrollY + 90, id = null;
    heads.forEach(function (h) {{ if (h.offsetTop <= y) id = h.id; }});
    if (id !== current) {{
      if (current && links[current]) links[current].classList.remove("active");
      toc.querySelectorAll(".toc-ch.open").forEach(function (c) {{ c.classList.remove("open"); }});
      current = id;
      if (id && links[id]) {{ links[id].classList.add("active"); links[id].closest(".toc-ch").classList.add("open"); }}
    }}
    document.getElementById("to-top").style.display = window.scrollY > 800 ? "inline-block" : "none";
  }};
  window.addEventListener("scroll", onScroll, {{ passive: true }}); onScroll();
  var box = document.getElementById("lightbox"), big = box.querySelector("img");
  document.querySelectorAll("figure.shot button.zoom").forEach(function (b) {{
    b.addEventListener("click", function () {{
      var img = b.querySelector("img"); big.src = img.src; big.alt = img.alt; box.classList.add("open");
    }});
  }});
  box.addEventListener("click", function () {{ box.classList.remove("open"); }});
  document.addEventListener("keydown", function (e) {{ if (e.key === "Escape") box.classList.remove("open"); }});
}})();
</script>
</body>
</html>
"""
open(out, "w", encoding="utf-8").write(page)
print("écrit :", out, len(page), "octets ;", len(toc), "chapitres ;", sum(len(t[2]) for t in toc), "sous-parties ;",
      len(figures), "figures ;", words, "mots")

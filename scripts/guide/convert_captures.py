# Convertit les captures PNG de capture.js en WebP pour le guide (environ dix fois plus léger, texte net).
# Usage : python scripts/guide/convert_captures.py <dossier des PNG> docs/guide/captures   (Pillow requis)
import pathlib
import sys

from PIL import Image

source, target = map(pathlib.Path, sys.argv[1:3])
target.mkdir(parents=True, exist_ok=True)
total = 0
for png in sorted(source.glob("[0-9][0-9]-*.png")):
    webp = target / f"{png.stem}.webp"
    Image.open(png).convert("RGB").save(webp, "WEBP", quality=82, method=6)
    total += webp.stat().st_size
    print(f"{webp.name} : {webp.stat().st_size // 1024} Ko")
print(f"total : {total // 1024} Ko")

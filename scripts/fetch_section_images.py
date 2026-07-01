#!/usr/bin/env python3
"""Download section images (client promos + Pexels) and update content/*/_index.md."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
IMAGES_DIR = ROOT / "static" / "images"
PROMOS = IMAGES_DIR / "promotions"

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=900"

CLIENT_PNG: dict[str, str] = {
    "hero.webp": "sear-saturday.png",
    "promotions.webp": "magic-mondays.png",
}

PEXELS: dict[str, tuple[str, str]] = {
    "appetizers.webp": (PEX.format(id="2338407"), "Pexels #2338407"),
    "soups.webp": (PEX.format(id="539451"), "Pexels #539451"),
    "salads.webp": (PEX.format(id="1279330"), "Pexels #1279330"),
    "sides.webp": (PEX.format(id="410648"), "Pexels #410648"),
    "kids-menu.webp": (PEX.format(id="699953"), "Pexels #699953"),
    "premium-steak-menu.webp": (PEX.format(id="3535384"), "Pexels #3535384"),
    "entrees.webp": (PEX.format(id="618785"), "Pexels #618785"),
    "pastas.webp": (PEX.format(id="2097090"), "Pexels #2097090"),
    "burgers-and-sandwiches.webp": (PEX.format(id="769289"), "Pexels #769289"),
    "desserts.webp": (PEX.format(id="2089718"), "Pexels #2089718"),
    "mocktails.webp": (PEX.format(id="1267325"), "Pexels #1267325"),
    "hot-drinks.webp": (PEX.format(id="302899"), "Pexels #302899"),
    "lattes.webp": (PEX.format(id="654642"), "Pexels #654642"),
    "floral-teas.webp": (PEX.format(id="1132558"), "Pexels #1132558"),
    "cocktails.webp": (PEX.format(id="274192"), "Pexels #274192"),
    "shots.webp": (PEX.format(id="1126728"), "Pexels #1126728"),
    "scotch-and-whiskey.webp": (PEX.format(id="696218"), "Pexels #696218"),
    "vodka.webp": (PEX.format(id="1126728"), "Pexels #1126728"),
    "gin.webp": (PEX.format(id="274192"), "Pexels #274192"),
    "cognac.webp": (PEX.format(id="696218"), "Pexels #696218"),
    "rum.webp": (PEX.format(id="696218"), "Pexels #696218"),
    "tequila.webp": (PEX.format(id="2087742"), "Pexels #2087742"),
    "liqueur.webp": (PEX.format(id="848612"), "Pexels #848612"),
    "wines.webp": (PEX.format(id="1283219"), "Pexels #1283219"),
    "beers.webp": (PEX.format(id="1304540"), "Pexels #1304540"),
    "soft-drinks.webp": (PEX.format(id="1199957"), "Pexels #1199957"),
    "breakfast-kids.webp": (PEX.format(id="699953"), "Pexels #699953"),
    "breakfast-grass-fed.webp": (PEX.format(id="3535384"), "Pexels #3535384"),
    "breakfast-meadow.webp": (PEX.format(id="1640777"), "Pexels #1640777"),
    "breakfast-build-your-own.webp": (PEX.format(id="1028737"), "Pexels #1028737"),
    "breakfast-drinks.webp": (PEX.format(id="654642"), "Pexels #654642"),
    "slideshow-steak.webp": (PEX.format(id="3535384"), "Pexels #3535384"),
    "slideshow-wine.webp": (PEX.format(id="1283219"), "Pexels #1283219"),
}

SECTIONS: dict[str, str] = {
    "promotions": "promotions.webp",
    "appetizers": "appetizers.webp",
    "soups": "soups.webp",
    "salads": "salads.webp",
    "sides": "sides.webp",
    "kids-menu": "kids-menu.webp",
    "premium-steak-menu": "premium-steak-menu.webp",
    "entrees": "entrees.webp",
    "pastas": "pastas.webp",
    "burgers-and-sandwiches": "burgers-and-sandwiches.webp",
    "desserts": "desserts.webp",
    "mocktails": "mocktails.webp",
    "hot-drinks": "hot-drinks.webp",
    "lattes": "lattes.webp",
    "floral-teas": "floral-teas.webp",
    "cocktails": "cocktails.webp",
    "shots": "shots.webp",
    "scotch-and-whiskey": "scotch-and-whiskey.webp",
    "vodka": "vodka.webp",
    "gin": "gin.webp",
    "cognac": "cognac.webp",
    "rum": "rum.webp",
    "tequila": "tequila.webp",
    "liqueur": "liqueur.webp",
    "wines": "wines.webp",
    "beers": "beers.webp",
    "soft-drinks": "soft-drinks.webp",
    "breakfast-kids": "breakfast-kids.webp",
    "breakfast-grass-fed": "breakfast-grass-fed.webp",
    "breakfast-meadow": "breakfast-meadow.webp",
    "breakfast-build-your-own": "breakfast-build-your-own.webp",
    "breakfast-drinks": "breakfast-drinks.webp",
}


def img(name: str) -> str:
    return f"images/{name}"


def convert_png_to_webp(src: Path, dest: Path) -> bool:
    from PIL import Image

    if not src.exists():
        return dest.exists()
    Image.open(src).save(dest, "WEBP", quality=85)
    print(f"OK {dest.name} (from {src.name})")
    return True


def download_pexels(filename: str, url: str) -> bool:
    from PIL import Image

    webp = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"SKIP {filename}: HTTP {e.code}")
        return webp.exists()
    Image.open(BytesIO(data)).save(webp, "WEBP", quality=85)
    print(f"OK {filename}")
    return True


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    weight_m = re.search(r"^weight:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"') if title_m else section.replace("-", " ").title()
    weight = weight_m.group(1).strip().strip('"') if weight_m else "1"
    body = body_after_frontmatter(raw)

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        body = "<p>Premium SEAR Steakhouse</p>"
    text = (
        "---\n"
        'title: "Premium SEAR Steakhouse"\n'
        f"image: {img('hero.webp')}\n"
        "images:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('premium-steak-menu.webp')}\n"
        f"    - image: {img('wines.webp')}\n"
        f"    - image: {img('cocktails.webp')}\n"
        "slideshow:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('slideshow-steak.webp')}\n"
        f"    - image: {img('entrees.webp')}\n"
        f"    - image: {img('slideshow-wine.webp')}\n"
        f"    - image: {img('promotions.webp')}\n"
        f"    - image: {img('desserts.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    credits: list[str] = []

    for dest, src_name in CLIENT_PNG.items():
        src = PROMOS / src_name
        if convert_png_to_webp(src, IMAGES_DIR / dest):
            credits.append(f"- {dest} — Premium SEAR (client promo, from promotions/{src_name})")

    for filename, (url, credit) in PEXELS.items():
        if download_pexels(filename, url):
            credits.append(f"- {filename} — {credit}")

    missing = [s for s, f in SECTIONS.items() if not (IMAGES_DIR / f).exists()]
    if missing:
        print("Missing:", ", ".join(missing))
        return

    for section, image_file in SECTIONS.items():
        update_section_index(section, image_file)

    if (IMAGES_DIR / "hero.webp").exists():
        update_home_index()

    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos:\n" + "\n".join(credits) + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()

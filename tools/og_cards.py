"""Render the 1200x630 link-preview images (Discord, social networks) from the real pages.

Needs the local server (python -m http.server 8765 --directory docs) and Microsoft Edge.
Run it again after a change to a page opening, then tools/build.py so the image URLs get a new stamp.
"""
import os
import subprocess
import tempfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE = "http://localhost:8765/"
NAV = 58
CARDS = {
    "home": "index.html",
    "who-let-the-zoo-out": "jeux/who-let-the-zoo-out/index.html",
}
CAPSULES = {"bloomstead": os.path.join(ROOT, "docs", "assets", "img", "bloomstead", "main_capsule.png")}


def shoot(url, path):
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=9000",
                    "--window-size=1440,1000", f"--screenshot={path}", url], check=True, capture_output=True)


def main():
    out = os.path.join(ROOT, "docs", "assets", "og")
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name, rel in CARDS.items():
            raw = os.path.join(tmp, name + ".png")
            shoot(BASE + rel, raw)
            im = Image.open(raw).convert("RGB")
            height = round(1440 * 630 / 1200)
            top = NAV + 12 if name == "home" else NAV
            card = im.crop((0, top, 1440, top + height)).resize((1200, 630), Image.LANCZOS)
            card.save(os.path.join(out, name + ".jpg"), "JPEG", quality=88, optimize=True, progressive=True)
            print(name, "ok")
    for name, src in CAPSULES.items():
        im = Image.open(src).convert("RGB")
        im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
        top = im.height - 630
        im.crop((0, top, 1200, top + 630)).save(os.path.join(out, name + ".jpg"), "JPEG", quality=88, optimize=True, progressive=True)
        print(name, "ok (capsule)")


if __name__ == "__main__":
    main()

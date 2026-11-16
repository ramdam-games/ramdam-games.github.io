"""Copy and compress the game media used by the site into docs/assets/img.

Sources stay in the game projects; run again after new captures.
"""
import os
import sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets", "img")
FOURRIERE = r"E:\CoopBase"
BLOOMSTEAD_SITE = os.path.join(os.path.expanduser("~"), "Desktop", "Bloomstead_site", "media")
CUTOUTS = sys.argv[1] if len(sys.argv) > 1 else None

FOURRIERE_SHOTS = {
    "bernard-mairie": "Shots/c_show_1/show_boss_taunt.png",
    "mme-pichon": "Shots/faces1/face_MmePichon.png",
    "poele": "Shots/shops3/tour_shop_pan.png",
    "camionnette": "Shots/c_show_1/show_parked_side.png",
    "plage": "Shots/shops3/tour_shop_ShopBuoy.png",
    "fete": "Shots/people2/tour_people_talk_start.png",
    "lama": "Shots/c_show_1/show_animal_6.png",
    "fin": "Shots/ending1/tour_ending_2.png",
    "bave": "Shots/host/arrived_job.png",
    "lunette": "Shots/c_show_1/show_fps_aim.png",
    "fourriere": "Shots/c_show_1/show_pound.png",
    "maire": "Shots/faces1/face_Maire.png",
    "dede": "Shots/faces1/face_Dede.png",
    "hyper": "Shots/shops3/tour_shop_ShopMegaphone.png",
    "boss-charge": "Shots/boss3/tour_boss_charge.png",
    "carte": "Shots/ending1/tour_c1_map.png",
}

BLOOMSTEAD_SHOTS = {
    "hero": "hero.jpg",
    "accueil": "title_screen.jpg",
    "prairie": "screenshot_01_factory_meadow.png",
    "jungle": "screenshot_02_bloom_wave_jungle.png",
    "desert": "screenshot_03_desert.png",
    "sakura": "screenshot_04_sakura.png",
    "carte": "screenshot_05_world_map.png",
    "jardin": "screenshot_06_garden.png",
    "ile": "screenshot_07_living_island.png",
}


def save_jpg(src, dst, width):
    im = Image.open(src).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "JPEG", quality=84, optimize=True, progressive=True)


def save_webp_alpha(src, dst, height):
    im = Image.open(src).convert("RGBA")
    if im.height > height:
        im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "WEBP", quality=88, method=6)


def copy_png(src, dst, scale=1):
    im = Image.open(src)
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, optimize=True)


def main():
    for name, rel in FOURRIERE_SHOTS.items():
        src = os.path.join(FOURRIERE, rel)
        save_jpg(src, os.path.join(OUT, "fourriere", name + ".jpg"), 1600)
        save_jpg(src, os.path.join(OUT, "fourriere", "thumbs", name + ".jpg"), 640)
    for name, rel in BLOOMSTEAD_SHOTS.items():
        src = os.path.join(BLOOMSTEAD_SITE, rel)
        save_jpg(src, os.path.join(OUT, "bloomstead", name + ".jpg"), 1600)
        save_jpg(src, os.path.join(OUT, "bloomstead", "thumbs", name + ".jpg"), 640)
    for name in ("logo.png", "mascot.png", "crystal.png", "main_capsule.png"):
        copy_png(os.path.join(BLOOMSTEAD_SITE, name), os.path.join(OUT, "bloomstead", name))
    machines = os.path.join(BLOOMSTEAD_SITE, "machines")
    for f in os.listdir(machines):
        copy_png(os.path.join(machines, f), os.path.join(OUT, "bloomstead", "machines", f))
    if CUTOUTS:
        for f in os.listdir(CUTOUTS):
            if f.endswith(".png"):
                save_webp_alpha(os.path.join(CUTOUTS, f), os.path.join(OUT, "fourriere", "cast", f[:-4] + ".webp"), 480)
    total = 0
    for dirpath, _, files in os.walk(OUT):
        total += sum(os.path.getsize(os.path.join(dirpath, f)) for f in files)
    print(f"media: {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()

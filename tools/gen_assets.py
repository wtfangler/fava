"""Builds src/resourcepack (title logo, splash texts, pack icon) from the author's ORIGINAL artwork in brand/.

Nothing is redrawn: the logo is placed 1:1 and the icon is only scaled to the pack-icon size.
The other brand files (banners, icons, gallery) are used as they are by the website and for Modrinth.
"""
import json
import os
import shutil

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BRAND = os.path.join(ROOT, "brand")
RP = os.path.join(ROOT, "src", "resourcepack")


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf8", newline="\n") as f:
        f.write(data if isinstance(data, str) else json.dumps(data, indent=2, ensure_ascii=False))


shutil.rmtree(RP, ignore_errors=True)
write(os.path.join(RP, "pack.mcmeta"), {"pack": {"description": "Fancy Vanilla: logo, menu i napisy", "min_format": [88, 0], "max_format": [97, 1]}})

# title screen logo: the author's menu wordmark (1023x151) centred 1:1 on the 1024x256 title sprite
wordmark = Image.open(os.path.join(BRAND, "logo", "wordmark-menu.png")).convert("RGBA")
title = Image.new("RGBA", (1024, 256), (0, 0, 0, 0))
# vanilla only draws the top 176 px of the 256 px sprite, so centre the wordmark inside that band
title.alpha_composite(wordmark, ((1024 - wordmark.width) // 2, (176 - wordmark.height) // 2))
tdir = os.path.join(RP, "assets/minecraft/textures/gui/title")
os.makedirs(tdir, exist_ok=True)
for name in ("minecraft", "minceraft"):
    title.save(os.path.join(tdir, f"{name}.png"))
Image.new("RGBA", (512, 64), (0, 0, 0, 0)).save(os.path.join(tdir, "edition.png"))  # hides "Java Edition"

write(os.path.join(RP, "assets/minecraft/texts/splashes.txt"), """Fancy Vanilla!
Vanilla, tylko ładniejsza!
Minecraft, jakiego znasz. Trochę lepszy.
Szybciej i piękniej!
Siedem er czeka!
Od drewna do post-endu!
Tempered ukłon w Twoją stronę!
Zostaw vanillę w spokoju. Dopieść ją!
Optymalizacja pod maską!
Prostota to elegancja!
Najpierw drewno, potem reszta!
Smok pokonany. Co dalej?
Epilog czeka po smoku!
Dziennik pod klawiszem J!
Pozdrowienia z Polski!
Plain old Minecraft, but fancy!
Gentle on the eyes, light on the CPU!
Seven ages await!
The dragon is down. What next?
Polished, not changed!
""")
Image.open(os.path.join(BRAND, "icons", "icon-release-512.jpg")).convert("RGB").resize((256, 256), Image.LANCZOS).save(os.path.join(RP, "pack.png"))
print("resource pack ready:", RP)

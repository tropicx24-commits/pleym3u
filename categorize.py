
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re

INPUT_FILE = "playlist.m3u"
CATEGORY_FILE = "categories.json"

REMOVE_WORDS = [
    "HD", "FHD", "UHD", "4K", "HEVC",
    "H265", "H264", "1080P", "720P"
]

# --------------------------------------------------
# Kategorileri yükle
# --------------------------------------------------

with open(CATEGORY_FILE, "r", encoding="utf-8") as f:
    categories = json.load(f)


# --------------------------------------------------
# Metin normalleştirme
# --------------------------------------------------

def normalize(text):
    text = text.upper()

    for w in REMOVE_WORDS:
        text = text.replace(w, "")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# --------------------------------------------------
# Otomatik kategori bul
# --------------------------------------------------

def get_category(name):

    n = normalize(name)

    for category, words in categories.items():

        for word in words:

            if normalize(word) in n:
                return category

    return "Diğer"


# --------------------------------------------------
# Playlist oku
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()


output = []

i = 0


# --------------------------------------------------
# Kanalları işle
# --------------------------------------------------

while i < len(lines):

    line = lines[i]

    if line.startswith("#EXTINF"):

        # Kanal adı
        if "," in line:
            name = line.split(",", 1)[1].strip()
        else:
            name = ""

        # --------------------------------------------------
        # Mevcut group-title değerini bul
        # --------------------------------------------------

        match = re.search(
            r'group-title="([^"]*)"',
            line,
            re.IGNORECASE
        )

        existing_category = ""

        if match:
            existing_category = match.group(1).strip()


        # --------------------------------------------------
        # Manuel kategori varsa KORU
        # --------------------------------------------------

        if existing_category and existing_category.lower() != "diğer":

            category = existing_category

        else:

            # group-title yoksa veya Diğer ise
            # otomatik kategorilendir
            category = get_category(name)


        # --------------------------------------------------
        # Eski group-title bilgisini kaldır
        # --------------------------------------------------

        line = re.sub(
            r'\s*group-title="[^"]*"',
            "",
            line,
            flags=re.IGNORECASE
        )


        # --------------------------------------------------
        # Yeni group-title ekle
        # --------------------------------------------------

        if line.startswith("#EXTINF:-1"):

            line = re.sub(
                r'^#EXTINF:-1',
                f'#EXTINF:-1 group-title="{category}"',
                line,
                count=1
            )


        output.append(line)


        # Yayın URL'sini de ekle
        if i + 1 < len(lines):
            output.append(lines[i + 1])

        i += 2

    else:

        output.append(line)

        i += 1


# --------------------------------------------------
# Playlist'i kaydet
# --------------------------------------------------

with open(INPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(output)


print("Kategori işlemi tamamlandı.")
print("Manuel group-title değerleri korundu.")
print("Diğer kategorisindeki kanallar otomatik kategorilendirildi.")


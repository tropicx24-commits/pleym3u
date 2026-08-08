
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
# Film kontrolü
# --------------------------------------------------

def is_movie(line, name):

    line_lower = line.lower()
    name_clean = name.strip()

    # 1. tvg-year varsa
    if re.search(r'\btvg-year="(?:19|20)\d{2}"', line_lower):
        return True

    # 2. TMDB logo
    if "image.tmdb.org" in line_lower:
        return True

    # 3. Film sitesi poster adresi
    film_patterns = [
        "/poster/film/",
        "/poster/filmler/",
        "fullhdfilm",
        "filmizlesene",
        "film-izle",
        "filmposter"
    ]

    for pattern in film_patterns:
        if pattern in line_lower:
            return True

    # 4. Kanal adının sonunda yıl
    if re.search(r'\((?:19|20)\d{2}\)\s*$', name_clean):
        return True

    # 5. Kanal adının sonunda boşluk + yıl
    if re.search(r'\s(?:19|20)\d{2}\s*$', name_clean):
        return True

    return False


# --------------------------------------------------
# Otomatik kategori
# --------------------------------------------------

def get_category(line, name):

    # Önce film kontrolü
    if is_movie(line, name):
        return "Film"

    n = normalize(name)

    # categories.json kuralları
    for category, words in categories.items():

        # "diğer" kategorisini otomatik eşleştirme
        if category.lower() == "diğer":
            continue

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

film_count = 0
manual_count = 0
auto_count = 0
other_count = 0


# --------------------------------------------------
# Playlist işle
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
        # Mevcut group-title kontrolü
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
        # Manuel kategori varsa koru
        # --------------------------------------------------

        if existing_category and existing_category.lower() != "diğer":

            category = existing_category
            manual_count += 1


        else:

            # Otomatik kategori
            category = get_category(line, name)
            auto_count += 1


        # --------------------------------------------------
        # Sayaçlar
        # --------------------------------------------------

        if category == "Film":
            film_count += 1

        if category == "Diğer":
            other_count += 1


        # --------------------------------------------------
        # Eski group-title kaldır
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

        line = re.sub(
            r'^#EXTINF:-1',
            f'#EXTINF:-1 group-title="{category}"',
            line,
            count=1
        )


        output.append(line)


        # URL satırı
        if i + 1 < len(lines):
            output.append(lines[i + 1])

        i += 2

    else:

        output.append(line)
        i += 1


# --------------------------------------------------
# Playlist kaydet
# --------------------------------------------------

with open(INPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(output)


# --------------------------------------------------
# Sonuç
# --------------------------------------------------

print("========================================")
print("Kategori işlemi tamamlandı.")
print("========================================")
print(f"Manuel kategoriler : {manual_count}")
print(f"Otomatik kategoriler: {auto_count}")
print(f"Bulunan filmler    : {film_count}")
print(f"Diğer kalanlar     : {other_count}")
print("========================================")


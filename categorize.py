
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

    for word in REMOVE_WORDS:
        text = text.replace(word, "")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# --------------------------------------------------
# FILM KAYNAKLARINI KONTROL ET
# --------------------------------------------------

def is_movie(line, name):

    line_lower = line.lower()
    name_clean = name.strip()

    # 1. tvg-year
    if re.search(r'\btvg-year="(?:19|20)\d{2}"', line_lower):
        return True

    # 2. TMDB
    if "image.tmdb.org" in line_lower:
        return True

    # 3. HDFilmizle
    movie_sources = [
        "hdfilmizle.life",
        "fullhdfilmizlesene.de",
        "fullhdfilmizle",
        "filmizlesene",
        "film-izle",
        "/poster/film/",
        "/poster/filmler/",
        "/poster/thumb/",
        "filmposter",
        "movieposter"
    ]

    for source in movie_sources:
        if source in line_lower:
            return True

    # 4. Film adının sonunda yıl
    if re.search(r'\((?:19|20)\d{2}\)\s*$', name_clean):
        return True

    # 5. Film adının sonunda boşluk + yıl
    if re.search(r'\s(?:19|20)\d{2}\s*$', name_clean):
        return True

    return False


# --------------------------------------------------
# OTOMATİK KATEGORİ
# --------------------------------------------------

def get_category(line, name):

    # Öncelik 1: Film kaynakları
    if is_movie(line, name):
        return "Film"

    n = normalize(name)

    # --------------------------------------------------
    # Özel otomatik kurallar
    # --------------------------------------------------

    # SPOR
    sport_words = [
        "SPOR",
        "SPORT",
        "SPORTS",
        "S SPORT",
        "SMART SPOR",
        "TIVIBU SPOR",
        "BEIN SPORTS",
        "TRT SPOR",
        "EUROSPORT",
        "ALKASS",
        "CRICKET",
        "WWE",
        "ESPN",
        "SKY SPORTS",
        "SPORT TV",
        "ACC NETWORK",
        "NBA TV",
        "NFL",
        "NHL",
        "MLB"
    ]

    for word in sport_words:
        if normalize(word) in n:
            return "Spor"


    # RADYO
    radio_words = [
        "RADYO",
        "RADIO",
        "FM ",
        "FM",
        "RADYOTV"
    ]

    for word in radio_words:
        if normalize(word) in n:
            return "Radyo"


    # MÜZİK
    music_words = [
        "MUSIC",
        "MÜZİK",
        "NUMBERONE",
        "NUMBER ONE",
        "NUMBER1",
        "NR1",
        "MTV",
        "POWER FM",
        "DREAM TV",
        "DREAM FM",
        "KRAL"
    ]

    for word in music_words:
        if normalize(word) in n:
            return "Müzik"


    # HABER
    news_words = [
        "NEWS",
        "NEWS HD",
        "HABER",
        "HABERLER",
        "CNN",
        "BBC NEWS",
        "SKY NEWS",
        "EURONEWS",
        "AL JAZEERA",
        "MSNBC",
        "FOX NEWS",
        "POLSTAT NEWS"
    ]

    for word in news_words:
        if normalize(word) in n:
            return "Haber"


    # BELGESEL
    documentary_words = [
        "NAT GEO",
        "NATGEO",
        "NATIONAL GEOGRAPHIC",
        "DISCOVERY",
        "ANIMAL PLANET",
        "HISTORY",
        "HISTORY CHANNEL",
        "SCIENCE",
        "DOCUMENTARY",
        "BELGESEL",
        "YABAN TV",
        "NATURE"
    ]

    for word in documentary_words:
        if normalize(word) in n:
            return "Belgesel"


    # ÇOCUK
    kids_words = [
        "KIDS",
        "ÇOCUK",
        "CARTOON",
        "NICKELODEON",
        "NICK JR",
        "DISNEY",
        "BOOMERANG",
        "BABY TV"
    ]

    for word in kids_words:
        if normalize(word) in n:
            return "Çocuk"


    # --------------------------------------------------
    # categories.json
    # --------------------------------------------------

    for category, words in categories.items():

        # Diğer'i otomatik eşleştirmiyoruz
        if category.lower() == "diğer":
            continue

        for word in words:

            if normalize(word) in n:
                return category


    # Hiçbir kategori bulunamazsa
    return "Diğer"


# --------------------------------------------------
# PLAYLIST OKU
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()


output = []

i = 0

manual_count = 0
auto_count = 0
film_count = 0
other_count = 0
sport_count = 0
radio_count = 0
music_count = 0
news_count = 0
documentary_count = 0
kids_count = 0


# --------------------------------------------------
# PLAYLIST İŞLE
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
        # Mevcut group-title
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
            manual_count += 1

        else:

            category = get_category(line, name)
            auto_count += 1


        # --------------------------------------------------
        # Sayaçlar
        # --------------------------------------------------

        if category == "Film":
            film_count += 1

        elif category == "Spor":
            sport_count += 1

        elif category == "Radyo":
            radio_count += 1

        elif category == "Müzik":
            music_count += 1

        elif category == "Haber":
            news_count += 1

        elif category == "Belgesel":
            documentary_count += 1

        elif category == "Çocuk":
            kids_count += 1

        elif category == "Diğer":
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
# PLAYLIST KAYDET
# --------------------------------------------------

with open(INPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(output)


# --------------------------------------------------
# SONUÇ
# --------------------------------------------------

print("========================================")
print("Kategori işlemi tamamlandı.")
print("========================================")
print(f"Manuel kategoriler : {manual_count}")
print(f"Otomatik kategoriler: {auto_count}")
print("----------------------------------------")
print(f"Film               : {film_count}")
print(f"Spor               : {sport_count}")
print(f"Radyo              : {radio_count}")
print(f"Müzik              : {music_count}")
print(f"Haber              : {news_count}")
print(f"Belgesel           : {documentary_count}")
print(f"Çocuk              : {kids_count}")
print(f"Diğer              : {other_count}")
print("========================================")


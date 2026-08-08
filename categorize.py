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

def is_movie(line, name, stream_url=""):

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
        if source in combined_lower:
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

def get_category(line, name, stream_url=""):

    # --------------------------------------------------
    # 1. FILM KAYNAKLARI
    # --------------------------------------------------

    if is_movie(line, name, stream_url):
        return "Film"

    line_lower = line.lower()
    n = normalize(name)

    # HDFilmizle
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
            return "Film"


    # --------------------------------------------------
    # 2. SPOR
    # --------------------------------------------------

    sport_words = [
        "SPOR", "SPORT", "SPORTS", "S SPORT",
        "SMART SPOR", "TIVIBU SPOR", "BEIN SPORTS",
        "TRT SPOR", "EUROSPORT", "ALKASS", "CRICKET",
        "WWE", "ESPN", "SKY SPORTS", "SPORT TV",
        "ACC NETWORK", "NBA TV", "NFL", "NHL", "MLB",
        "WILLOW",

        # DAZN
        "DAZN", "DAZN F1", "DAZN LALIGA", "DAZN LIGUE 1",

        # FOX / Soccer / Deportes
        "FOX SOCCER", "FOX SPORTS", "FOX DEPORTES",
        "DEPORTES", "SOCCER", "FOOTBALL", "GOL PLAY", "LALIGA",

        # Basketball / American sports
        "NBA", "NFL NETWORK", "NFL REDZONE", "ESPN2", "ESPNU",

        # Fight / Wrestling
        "UFC", "BOXING", "WRESTLING", "FIGHT NETWORK",

        # Tennis / Motor / Golf / Racing
        "TENNIS", "TENNIS+", "MOTOR", "MOTORSPORT",
        "MOTOR RACING", "FORMULA 1", "F1",
        "GOLF", "GOLF CHANNEL", "RACING",

        # Other sports
        "WILLOW", "YES NETWORK"
    ]

    for word in sport_words:
        if normalize(word) in n:
            return "Spor"


    # --------------------------------------------------
    # 3. BELGESEL
    # --------------------------------------------------

    documentary_words = [
        "NAT GEO",
        "NAT GEO WILD",
        "NATGEO",
        "NATIONAL GEOGRAPHIC",
        "DISCOVERY",
        "ANIMAL PLANET",
        "HISTORY",
        "HISTORY CHANNEL",
        "SMITHSONIAN",
        "SCIENCE",
        "DOCUMENTARY",
        "BELGESEL",
        "YABAN TV",
        "NATURE",
        "NATURE TIME",
        "IZ TV",
        "VIASAT",
        "OUTDOOR CHANNEL"
    ]

    for word in documentary_words:
        if normalize(word) in n:
            return "Belgesel"


    # --------------------------------------------------
    # 4. RADYO
    # --------------------------------------------------

    radio_words = [
        "RADYO",
        "RADIO",
        "RADYOTV"
    ]

    for word in radio_words:
        if normalize(word) in n:
            return "Radyo"

    # FM kontrolü
    if re.search(r'\bFM\b', n):
        return "Radyo"


    # --------------------------------------------------
    # 5. MÜZİK
    # --------------------------------------------------

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


    # --------------------------------------------------
    # 6. HABER
    # --------------------------------------------------

    news_words = [
        "NEWS",
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


    # --------------------------------------------------
    # 7. ÇOCUK
    # --------------------------------------------------

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
    # 8. WEBCAM
    # --------------------------------------------------
    # Genel "PORT" veya tek başına "CAM" gibi kelimeler
    # kullanılmıyor. Böylece normal TV kanalları yanlışlıkla
    # WebCam yapılmaz.

    webcam_name_words = [
        "WEBCAM",
        "WEB CAMERA",
        "LIVE CAM",
        "BEACH CAM",
        "CITY CAM",
        "CITY CAMERA",
        "TRAFFIC CAM",
        "SQUARE CAM",
        "BEACH CAMERA",
        "PORT CAM",
        "HARBOUR CAM",
        "HARBOR CAM",
        "MARINA CAM",
        "AIRPORT CAM",
        "SKI CAM",
        "MOUNTAIN CAM",
        "LAKE CAM",
        "BIG BROTHER CAM",
        "BIG BROTHER QUADVIEW"
    ]

    for word in webcam_name_words:
        if normalize(word) in n:
            return "WebCam"

    stream_lower = stream_url.lower()

    webcam_url_words = [
        "webcam",
        "webcamera",
        "livecam",
        "live-cam",
        "earthcam",
        "ozolio",
        "webcamera.pl"
    ]

    for word in webcam_url_words:
        if word in stream_lower:
            return "WebCam"


    # --------------------------------------------------
    # 9. categories.json
    # --------------------------------------------------

    for category, words in categories.items():

        # Diğer'i otomatik eşleştirme
        if category.lower() == "diğer":
            continue

        for word in words:

            if normalize(word) in n:
                return category


    # --------------------------------------------------
    # 9. HİÇBİR ŞEY BULUNAMADI
    # --------------------------------------------------

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

            stream_url = ""
            if i + 1 < len(lines):
                stream_url = lines[i + 1].strip()

            category = get_category(line, name, stream_url)
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

        elif category == "WebCam":
            webcam_count += 1

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
print(f"WebCam             : {webcam_count}")
print(f"Diğer              : {other_count}")
print("========================================")

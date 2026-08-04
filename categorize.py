#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re

INPUT_FILE = "playlist.m3u"
OUTPUT_FILE = "playlist.m3u"
CATEGORY_FILE = "categories.json"
ORDER = [
    "Haber",
    "Ulusal",
    "Spor",
    "Film",
    "Dizi",
    "Belgesel",
    "Çocuk",
    "Müzik",
    "Radyo",
    "WebCam",
    "Diğer"
]

# Kategori dosyasını oku
with open(CATEGORY_FILE, "r", encoding="utf-8") as f:
    categories = json.load(f)

# Aranmayacak kelimeler
REMOVE_WORDS = [
    "HD", "FHD", "UHD", "4K", "HEVC",
    "H265", "H264", "1080P", "720P",
    "|", "[", "]", "()"
]

def normalize(text):
    text = text.upper()

    for w in REMOVE_WORDS:
        text = text.replace(w, "")

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_category(name):

    n = normalize(name)

    for category, words in categories.items():

        for word in words:

            if normalize(word) in n:
                return category

    return "Diğer"


with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

output = []

i = 0

while i < len(lines):

    line = lines[i]

    if line.startswith("#EXTINF"):

        name = line.split(",", 1)[1].strip()

        category = get_category(name)

        # eski group-title varsa sil
        line = re.sub(r'group-title="[^"]*"', "", line)

        # çift boşlukları temizle
        line = re.sub(r"\s+", " ", line)

        line = re.sub(
            r'^#EXTINF:-1',
            f'#EXTINF:-1 group-title="{category}"',
            line
        )

        output.append(line)

        if i + 1 < len(lines):
            output.append(lines[i + 1])

        i += 2

    else:
        output.append(line)
        i += 1


from collections import defaultdict

groups = defaultdict(list)

i = 0
while i < len(new_lines):
    line = new_lines[i]

    if line.startswith("#EXTINF"):
        url = new_lines[i + 1]

        m = re.search(r'group-title="([^"]+)"', line)
        if m:
            category = m.group(1)
        else:
            category = "Diğer"

        groups[category].append(line)
        groups[category].append(url)

        i += 2
    else:
        i += 1


with open("playlist.m3u", "w", encoding="utf-8") as out:

    out.write("#EXTM3U\n")

    for category in ORDER:

        if category not in groups:
            continue

        out.write(f"\n# ===== {category} =====\n")

        for item in groups[category]:
            out.write(item)

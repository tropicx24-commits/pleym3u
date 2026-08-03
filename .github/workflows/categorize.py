#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re

INPUT_FILE = "playlist.m3u"
OUTPUT_FILE = "playlist.m3u"
CATEGORY_FILE = "categories.json"

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

        name = line.split(",")[-1].strip()

        category = get_category(name)

        # eski group-title varsa sil
        line = re.sub(r'group-title="[^"]*"', "", line)

        # çift boşlukları temizle
        line = re.sub(r"\s+", " ", line)

        if "#EXTINF:-1" in line:
            line = line.replace(
                "#EXTINF:-1",
                f'#EXTINF:-1 group-title="{category}"'
            )

        output.append(line)

        if i + 1 < len(lines):
            output.append(lines[i + 1])

        i += 2

    else:
        output.append(line)
        i += 1


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(output)

print("Kategorilendirme tamamlandı.")

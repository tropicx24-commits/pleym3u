#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from collections import Counter

stats = Counter()
unmatched = set()

INPUT_FILE = "playlist.m3u"
CATEGORY_FILE = "categories.json"

# Temizlenecek ifadeler
REMOVE_WORDS = {
    "HD", "FHD", "UHD", "4K",
    "HEVC", "H265", "H264",
    "1080P", "720P", "576P",
    "50FPS", "60FPS",
    "BACKUP", "VIP"
}

# Kategorileri yükle
with open(CATEGORY_FILE, "r", encoding="utf-8") as f:
    categories = json.load(f)


def normalize(text):
    """Karşılaştırma için metni sadeleştir."""
    if not text:
        return ""

    text = text.upper()

    for word in REMOVE_WORDS:
        text = text.replace(word, " ")

    text = text.replace("_", " ")
    text = text.replace("-", " ")
    text = text.replace(".", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_attr(line, attr):
    """EXTINF satırından attribute oku."""
    m = re.search(rf'{attr}="([^"]+)"', line, re.IGNORECASE)
    if m:
        return m.group(1)
    return ""


git add playlist.m3u report.json unmatched.txt

    search_text = " ".join([
        channel_name,
        extract_attr(extinf_line, "tvg-name"),
        extract_attr(extinf_line, "tvg-id"),
    ])

    search_text = normalize(search_text)

    best_category = "Diğer"
    best_score = 0

    for category, keywords in categories.items():

        for keyword in keywords:

            key = normalize(keyword)

            if key and key in search_text:

                score = len(key)

                if score > best_score:
                    best_score = score
                    best_category = category

    return best_category


with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

output = []

i = 0

while i < len(lines):

    line = lines[i]

    if line.startswith("#EXTINF"):

        try:
            channel_name = line.split(",", 1)[1].strip()
        except Exception:
            output.append(line)
            i += 1
            continue

        category = get_category(line, channel_name)

        # Eski group-title sil
        line = re.sub(r'\s*group-title="[^"]*"', "", line)

        # Yeni group-title ekle
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

with open(INPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(output)
stats["Toplam"] = sum(stats.values())

with open("report.json", "w", encoding="utf-8") as f:
    json.dump(dict(stats), f, ensure_ascii=False, indent=4)

with open("unmatched.txt", "w", encoding="utf-8") as f:
    for ch in sorted(unmatched):
        f.write(ch + "\n")
print("Kategori işlemi tamamlandı.")

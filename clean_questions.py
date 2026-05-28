#!/usr/bin/env python3
"""清洗 scraped_questions.json — 去除低质量题目"""
import json, re

with open('/Users/liuyuqi/translation-practice/scraped_questions.json') as f:
    data = json.load(f)

print(f"Before: {len(data)} questions")

clean = []
for item in data:
    en = item['english']
    zh = item['chinese']
    ok = True

    # ——— Length ———
    words = en.split()
    if len(words) < 6 or len(words) > 40:
        continue
    if len(zh) < 8 or len(zh) > 200:
        continue
    if len(en) > 220:
        continue

    # ——— Chinese quality ———
    # Remove questions where Chinese has significant English mixed in
    en_chars = sum(1 for c in zh if c.isascii() and c.isalpha())
    if en_chars > 4:
        continue

    # Starts with number (list items from documents)
    if re.match(r'^\d{1,4}[\.\s、)]', zh.strip()):
        continue

    # Starts with year
    if re.match(r'^\d{4}年', zh.strip()):
        continue

    # Contains citation markers
    if '见《' in zh or '参见' in zh or '注《' in zh:
        continue

    # Chinese too short relative to English (incomplete translation)
    if len(zh) < len(en) * 0.25:
        continue

    # ——— English quality ———
    # All caps sentences
    upper_ratio = sum(1 for c in en if c.isupper()) / max(1, sum(1 for c in en if c.isalpha()))
    if upper_ratio > 0.4 and len(en) > 20:
        continue

    # Too many numbers
    digits = sum(1 for c in en if c.isdigit())
    if digits > len(en) * 0.06:
        continue

    # Starts with (a) (b) etc or bullet points
    if re.match(r'^\s*[\(（][a-z]+[\)）]', en):
        continue

    # UN-speak: starts with "Recalling", "Emphasizing", "Noting", "Requests" etc
    if re.match(r'^\s*(Recalling|Emphasizing|Noting|Requests|Encourages|Urges|Calls upon|Welcomes|Reaffirms|Expresses|Takes note|Decides|Invites|Also|Further)\s', en):
        continue

    # Contains placeholder text
    if '[TO BE' in en or '[to be' in en or '[...]' in en:
        continue

    # ——— Categories that need stricter checks ———
    cat = item.get('category', 'daily')

    # kaoyan: should be thoughtful/philosophical, not UN docs
    if cat == 'kaoyan':
        un_words = ['committee', 'state party', 'general assembly', 'resolution',
                     'convention on', 'United Nations', 'member state', 'secretary']
        if any(kw in en.lower() for kw in un_words):
            # Re-classify as ielts instead of dropping
            item['category'] = 'ielts'

    clean.append(item)

# Dedup again
seen = set()
unique = []
for p in clean:
    key = p['english'].lower()[:60]
    if key not in seen:
        seen.add(key)
        unique.append(p)

# Cap per category at 400
from collections import defaultdict
counts = defaultdict(int)
final = []
for p in unique:
    cat = p['category']
    if counts[cat] < 400:
        counts[cat] += 1
        final.append(p)

# Re-index
for i, p in enumerate(final):
    p['id'] = f"s{i+1:04d}"

# Save
with open('/Users/liuyuqi/translation-practice/scraped_questions.json', 'w') as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

print(f"After: {len(final)} questions")
print(f"Categories: {dict(counts)}")

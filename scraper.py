#!/usr/bin/env python3
"""DualLingo 题库爬虫 — OPUS-100 (100万中英句对) + 考研真题"""

import re
import json
import time
import random
import os
from datasets import load_dataset

CATEGORY_KEYWORDS = {
    "ielts": [
        "environment", "pollution", "climate", "carbon emission", "global warming",
        "renewable energy", "sustainable development", "biodiversity", "ecosystem",
        "urbanization", "immigration", "cultural diversity", "globalization",
        "public health", "healthcare system", "tourism industry", "economic growth",
        "unemployment", "inflation", "international trade", "diplomatic",
        "human rights", "gender equality", "social welfare", "crime rate",
        "technological innovation", "digital divide", "cybersecurity"
    ],
    "cet": [
        "campus life", "extracurricular", "scholarship", "undergraduate",
        "postgraduate", "tuition fee", "bachelor", "master degree",
        "dormitory", "canteen", "semester", "curriculum", "syllabus",
        "lecture hall", "professor", "assignment", "internship",
        "graduate school", "freshman", "sophomore", "credit hour"
    ],
    "kaoyan": [
        "philosophical", "psychological", "evolutionary", "consciousness",
        "moral reasoning", "ethical", "cognitive science", "intellectual",
        "empirical evidence", "theoretical framework", "doctrine",
        "civilization", "cultural heritage", "rational inquiry",
        "fundamental principle", "species evolution", "human nature"
    ],
    "academic": [
        "research", "data analysis", "hypothesis", "methodology",
        "experiment", "statistical", "empirical", "theoretical",
        "literature review", "peer review", "publication",
        "finding suggest", "study demonstrate", "evidence indicate",
        "observation", "conclusion draw", "significant difference"
    ]
}

def classify_sentence(en_text):
    lower = en_text.lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in keywords if kw in lower)
    best = max(scores, key=scores.get)
    return best if scores[best] >= 1 else "daily"

def clean_chinese(text):
    """Remove English/roman text mixed into Chinese"""
    # Remove trailing English/punctuation
    text = re.sub(r'\s*[A-Za-z][A-Za-z\s,.!?;:()\[\]"\'\-]*$', '', text)
    return text.strip()

def main():
    all_pairs = []

    # ================================================================
    # Source 1: OPUS-100 (1M pairs, sample to get quality sentences)
    # ================================================================
    print("[OPUS-100] Loading dataset...")
    ds = load_dataset("opus100", "en-zh", split="train")
    total = len(ds)
    print(f"  Total pairs: {total}")

    # Shuffle and sample indices for diversity
    sample_size = 40000  # Process 40K, expect ~3-6K after stricter filtering
    indices = random.sample(range(total), min(sample_size, total))
    print(f"  Sampling {len(indices)} pairs...")

    for i, idx in enumerate(indices):
        if i % 2000 == 0:
            print(f"  Processing {i}/{sample_size}...")

        item = ds[int(idx)]
        trans = item['translation']
        en = trans['en'].strip()
        zh = trans['zh'].strip()

        # Quality filters
        words = en.split()
        if len(words) < 6 or len(words) > 50:
            continue
        if len(zh) < 8 or len(zh) > 250:
            continue
        # Remove pairs with too much English mixed in Chinese
        en_chars_in_zh = sum(1 for c in zh if c.isascii() and c.isalpha())
        if en_chars_in_zh > len(zh) * 0.2:
            continue
        # Remove Chinese starting with numbers (list enumerations from UN docs)
        if re.match(r'^\d{1,4}[\.\s、]', zh):
            continue
        # Clean the Chinese text
        zh = clean_chinese(zh)
        if len(zh) < 6:
            continue
        # Remove pairs where English has too many numbers/symbols
        if sum(1 for c in en if c.isdigit()) > len(en) * 0.1:
            continue

        all_pairs.append({"english": en, "chinese": zh})

    print(f"  OPUS-100 filtered: {len(all_pairs)} pairs")

    # ================================================================
    # Source 2: 考研真题 (manually curated from koolearn)
    # ================================================================
    print("\n[Kaoyan] Adding curated exam sentences...")
    kaoyan_sentences = [
        # 2013 考研英语一翻译
        {"english": "Yet when one looks at the photographs of the gardens created by the homeless, it strikes one that, for all their diversity of styles, these gardens speak of various other fundamental urges beyond that of decoration and creative expression.", "chinese": "然而，看着无家可归者绘制出的花园图片时，人们会突然想到，尽管这些花园风格多样，它们都显示了人类除了装饰和创造性表达之外的其他各种基本诉求"},
        {"english": "A sacred place of peace, however crude it may be, is a distinctly human need, as opposed to shelter, which is a distinctly animal need.", "chinese": "无论地方多么简陋不堪，寻求一片静谧圣土是人类特有的需求，而动物需要的仅是避难栖息之地"},
        {"english": "The gardens of the homeless, which are in effect homeless gardens, introduce form into an urban environment where it either didn't exist or was not discernible as such.", "chinese": "无家可归者的花园实际上是一个毫无家庭气息的地方，给城市环境带来了一种新的形式"},
        {"english": "Most of us give in to a demoralization of spirit which we usually blame on some psychological conditions, until one day we find ourselves in a garden and feel the oppression vanish as if by magic.", "chinese": "我们大多数人会深陷于精神萎靡的状态，并常常将此归咎为一些心理原因，直到某天我们发现自己置身花园中，感到如魔法般烦闷尽消"},
        {"english": "It is this implicit or explicit reference to nature that fully justifies the use of the word garden, though in a liberated sense, to describe these synthetic constructions.", "chinese": "正是对自然的这种或隐晦含蓄或清晰直白的提及，充分证实了用花园一词来描述这些虚拟建筑是合乎情理的，即使是从毫无拘泥的意义来讲的"},
    ]
    for s in kaoyan_sentences:
        s["category"] = "kaoyan"
        all_pairs.append(s)

    # ================================================================
    # Dedup & Categorize
    # ================================================================
    seen = set()
    unique = []
    for p in all_pairs:
        key = p["english"].lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(p)

    print(f"\n  After dedup: {len(unique)} unique pairs")

    for p in unique:
        if "category" not in p:
            p["category"] = classify_sentence(p["english"])

    # ================================================================
    # Build output — limit to a reasonable practice bank size
    # ================================================================
    # Ensure diversity: take max 500 per category
    from collections import defaultdict
    cat_counts = defaultdict(int)
    output = []
    random.shuffle(unique)

    for p in unique:
        cat = p["category"]
        if cat_counts[cat] < 500:
            cat_counts[cat] += 1
            output.append(p)

    # Assign IDs
    for i, p in enumerate(output):
        p["id"] = f"s{i+1:04d}"

    # Reorder fields
    output = [{
        "id": p["id"],
        "chinese": p["chinese"].strip(),
        "english": p["english"].strip(),
        "category": p.get("category", "daily")
    } for p in output]

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_questions.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"Saved {len(output)} questions -> {out_path}")
    print(f"Category breakdown: {dict(cat_counts)}")
    print(f"\nYou can import this JSON directly in DualLingo's 题库管理 page.")

if __name__ == "__main__":
    main()

import re

def format_reference(ref):
    # 1. Bold the year: (2020) → **(2020)**
    ref = re.sub(r"\((\d{4})\)", r"**(\1)**", ref)

    # 2. Remove DOI links
    ref = re.sub(r"https?://doi\.org/\S+", "", ref, flags=re.IGNORECASE)

    # 3. Clean extra whitespace after removal
    ref = re.sub(r"\s{2,}", " ", ref).strip()

    return ref

def correct_references(refs):
    return [format_reference(ref) for ref in refs]
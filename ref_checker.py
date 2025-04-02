import re
from collections import Counter, defaultdict

def extract_references(text):
    match = re.search(r"(References|REFERENCES)[\s\n]+(.+)", text, re.DOTALL)
    if match:
        refs_section = match.group(2)
        references = refs_section.strip().split("\n")
        return [r.strip() for r in references if len(r.strip()) > 30]
    return []

def check_duplicates(refs):
    return [item for item, count in Counter(refs).items() if count > 1]

def check_self_citations(refs, author_name=""):
    if not author_name:
        return []
    return [r for r in refs if author_name.lower() in r.lower()]

def check_qubahan(refs):
    return [r for r in refs if "Qubahan Academic Journal".lower() in r.lower()]

def check_apa_format(refs):
    bold_violations = []
    doi_violations = []
    for r in refs:
        if not re.search(r"\*\*\(\d{4}\)\*\*", r):
            bold_violations.append(r)
        if "doi.org" in r.lower():
            doi_violations.append(r)
    return bold_violations, doi_violations

def check_multiple_mentions(refs):
    author_counts = Counter()
    author_refs = defaultdict(list)

    for ref in refs:
        # Remove citation number at start like [1]
        ref_clean = re.sub(r"^\[\d+\]\s*", "", ref)

        # Extract author block before the year
        match = re.search(r"(.+?)\(\d{4}\)", ref_clean)
        author_block = match.group(1) if match else ref_clean.split(".")[0]

        # Remove et al., and unwanted symbols
        author_block = re.sub(r"\bet al\.?", "", author_block, flags=re.IGNORECASE)
        author_block = re.sub(r"[^A-Za-z.,\- ]+", "", author_block)
        author_block = re.sub(r"\s{2,}", " ", author_block).strip()

        # Split by common delimiters
        authors = re.split(r",| and | & ", author_block)

        for author in authors:
            author = author.strip()
            if not author or len(author) < 3:
                continue
            if re.fullmatch(r"\d{4}", author) or author.isdigit():
                continue
            key = author.lower()
            author_counts[key] += 1
            author_refs[key].append(ref)

    return {author: author_refs[author] for author, count in author_counts.items() if count >= 4}

def check_missing_citations(text, refs):
    missing = []
    for i, ref in enumerate(refs):
        if f"[{i+1}]" not in text:
            missing.append(i + 1)
    return missing

def check_references(text, author_name=""):
    results = {}
    refs = extract_references(text)
    if not refs:
        return {"error": "No references found. Ensure your document contains a 'References' section."}

    results["Total References"] = len(refs)
    results["Duplicate References"] = check_duplicates(refs)
    results["Self-Citations"] = check_self_citations(refs, author_name)
    results["Qubahan Citations"] = check_qubahan(refs)
    bold_violations, doi_violations = check_apa_format(refs)
    results["APA Style Violations"] = {
        "Missing Bold Year": bold_violations,
        "Contains DOI": doi_violations
    }
    results["Highly Cited Authors (≥4)"] = check_multiple_mentions(refs)
    results["Missing In-Text Citations"] = check_missing_citations(text, refs)
    results["Extracted References"] = refs
    return results

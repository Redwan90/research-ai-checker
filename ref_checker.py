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
        ref_clean = re.sub(r"^\[\d+\]\s*", "", ref)

        # Match initials with surname: e.g., M. Karimi, A. Smith
        candidates = re.findall(r"\b[A-Z]\.\s*[A-Z][a-z]+", ref_clean)

        for name in candidates:
            norm_name = re.sub(r"\s+", " ", name).strip().lower()
            author_counts[norm_name] += 1
            author_refs[norm_name].append(ref)

    return {
        author: list(set(author_refs[author]))
        for author, count in author_counts.items()
        if count >= 4
    }

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

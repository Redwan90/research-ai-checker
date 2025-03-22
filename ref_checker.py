import re
from collections import Counter

def extract_references(text):
    match = re.search(r"(References|REFERENCES)[\s\n]+(.+)", text, re.DOTALL)
    if match:
        refs_section = match.group(2)
        references = refs_section.strip().split("\n")
        return [r.strip() for r in references if len(r.strip()) > 30]
    return []

def check_duplicates(refs):
    duplicates = [item for item, count in Counter(refs).items() if count > 1]
    return duplicates

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
    author_refs = {}
    for ref in refs:
        authors_part = ref.split("(")[0]
        authors = re.split(r",| and |&", authors_part)
        authors = [a.strip().lower() for a in authors if len(a.strip()) > 3]
        for author in authors:
            author_counts[author] += 1
            if author not in author_refs:
                author_refs[author] = []
            author_refs[author].append(ref)
    result = {author: author_refs[author] for author, count in author_counts.items() if count >= 4}
    return result

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
    results["APA Style Violations"] = {"Missing Bold Year": bold_violations, "Contains DOI": doi_violations}
    results["Highly Cited Authors (≥4)"] = check_multiple_mentions(refs)
    results["Extracted References"] = refs
    return results

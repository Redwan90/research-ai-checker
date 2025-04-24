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
    author_refs = {}
    for ref in refs:
        authors_part = ref.split("(")[0]
        authors = re.split(r",| and |&", authors_part)
        authors = [a.strip().lower() for a in authors if len(a.strip()) > 3 and not re.search(r"\d", a)]
        for author in authors:
            author_counts[author] += 1
            author_refs.setdefault(author, []).append(ref)
    # Only authors cited more than 4 times
    return {author: author_refs[author]
            for author, count in author_counts.items()
            if count > 4}

def extract_intext_citations(text):
    matches = re.findall(r"\[([^]]+)\]", text)
    cited = set()
    for m in matches:
        parts = re.split(r"[,\s]+", m)
        for p in parts:
            if '-' in p or '–' in p:
                start, end = re.split(r"[-–]", p)
                cited.update(range(int(start), int(end) + 1))
            elif p.isdigit():
                cited.add(int(p))
    return cited

def find_missing_intext_citations(text, refs):
    cited = extract_intext_citations(text)
    return [i for i in range(1, len(refs) + 1) if i not in cited]

def check_references(text, author_name=""):
    results = {}
    refs = extract_references(text)
    if not refs:
        return {"error": "No references found. Ensure your document contains a 'References' section."}

    # Basic stats
    results["Total References"] = len(refs)
    results["Duplicate References"] = check_duplicates(refs)
    results["Self-Citations"] = check_self_citations(refs, author_name)

    # Qubahan citations: allow up to 2
    qaj = check_qubahan(refs)
    results["Qubahan Citations"] = qaj
    if len(qaj) > 2:
        # citations beyond the first two are excess
        results["Excess Qubahan Citations"] = qaj[2:]

    # APA style checks
    bold_v, doi_v = check_apa_format(refs)
    results["APA Style Violations"] = {
        "Missing Bold Year": bold_v,
        "Contains DOI": doi_v
    }

    # Highly cited authors
    results["Highly Cited Authors (>4)"] = check_multiple_mentions(refs)

    # Missing in-text citations
    results["Missing In-Text Citations"] = find_missing_intext_citations(text, refs)

    # Finally the raw list
    results["Extracted References"] = refs
    return results

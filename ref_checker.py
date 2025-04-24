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
    return [r for r in refs if "qubahan academic journal" in r.lower()]

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
    return {
        author: author_refs[author]
        for author, count in author_counts.items()
        if count > 4
    }

def extract_intext_citations(text):
    cited = set()
    # 1) ranges like [3-5] or [3–5]
    for m in re.finditer(r"\[(\d+)\s*[-–]\s*(\d+)\]", text):
        start, end = map(int, m.groups())
        cited.update(range(start, end + 1))
    # remove those ranges so we don't parse them again
    text_clean = re.sub(r"\[\d+\s*[-–]\s*\d+\]", "", text)
    # 2) singles or comma-separated, e.g. [1], [1,2,5]
    for m in re.finditer(r"\[(\d+(?:\s*,\s*\d+)*)\]", text_clean):
        nums = re.split(r"\s*,\s*", m.group(1))
        for num in nums:
            if num.isdigit():
                cited.add(int(num))
    return cited

def find_missing_intext_citations(text, refs):
    cited = extract_intext_citations(text)
    return [i for i in range(1, len(refs) + 1) if i not in cited]

def check_references(text, author_name=""):
    results = {}
    refs = extract_references(text)
    if not refs:
        return {"error": "No references found. Ensure your document contains a 'References' section."}

    results["Total References"] = len(refs)
    results["Duplicate References"] = check_duplicates(refs)
    results["Self-Citations"] = check_self_citations(refs, author_name)

    # Qubahan citations: allow up to 2
    qaj = check_qubahan(refs)
    results["Qubahan Citations"] = qaj
    if len(qaj) > 2:
        results["Excess Qubahan Citations"] = qaj[2:]

    bold_v, doi_v = check_apa_format(refs)
    results["APA Style Violations"] = {
        "Missing Bold Year": bold_v,
        "Contains DOI": doi_v
    }

    results["Highly Cited Authors (>4)"] = check_multiple_mentions(refs)
    results["Missing In-Text Citations"] = find_missing_intext_citations(text, refs)
    results["Extracted References"] = refs
    return results

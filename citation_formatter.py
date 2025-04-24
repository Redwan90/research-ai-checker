# citation_formatter.py

import re

def correct_references(refs):
    """
    Take a list of reference strings and return a new list
    where each reference is formatted in APA style with:
      - the year bolded
      - the DOI turned into a clickable link
    """
    return [format_reference(r) for r in refs]

def format_reference(ref):
    # 1) Bold the year: find "(2023)" etc.
    #    Replace with **(2023)** so Streamlit shows it in bold.
    ref = re.sub(
        r'\(\s*(\d{4})\s*\)',
        r'**(\1)**',
        ref
    )

    # 2) Turn any DOI into a markdown hyperlink
    #    First, if it already contains "https://doi.org/…"
    doi_url_match = re.search(r'https?://doi\.org/[^\s,;]+', ref, flags=re.IGNORECASE)
    if doi_url_match:
        url = doi_url_match.group(0)
        # For display, we’ll show just the suffix after doi.org/
        suffix = url.split('doi.org/')[-1]
        md_link = f"[doi:{suffix}]({url})"
        ref = ref.replace(url, md_link)
    else:
        # Otherwise, look for a bare DOI like "10.1234/abcd.efgh"
        doi_plain_match = re.search(r'(10\.\d{4,9}/[^\s,;]+)', ref)
        if doi_plain_match:
            doi = doi_plain_match.group(1)
            url = f"https://doi.org/{doi}"
            md_link = f"[doi:{doi}]({url})"
            ref = ref.replace(doi, md_link)

    return ref

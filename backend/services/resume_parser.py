import re
from io import BytesIO

from PyPDF2 import PdfReader

from services.domain_catalog import DOMAINS

COMMON_CERTIFICATIONS = [
    "AWS Certified", "Azure Fundamentals", "Google Cloud", "TensorFlow Developer",
    "Cisco", "CompTIA", "Oracle Certified", "Microsoft Certified", "IBM Data Science",
    "Meta Front-End", "Meta Back-End", "Scrum", "Kubernetes", "Docker Certified",
]


def extract_text_from_pdf(file_storage):
    stream = BytesIO(file_storage.read())
    try:
        reader = PdfReader(stream)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise ValueError("Could not read this PDF resume. Please upload a valid text-based PDF.") from exc

    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        raise ValueError("No readable text found in this PDF. Please upload a text-based resume.")
    return cleaned


def _catalog_terms():
    buckets = {
        "skills": set(),
        "programming_languages": set(),
        "frameworks": set(),
        "tools": set(),
        "databases": set(),
        "platforms": set(),
        "technologies": set(),
    }
    for metadata in DOMAINS.values():
        for bucket in buckets:
            buckets[bucket].update(metadata.get(bucket, []))
    return buckets


def _find_terms(text, terms):
    found = []
    lower_text = text.lower()
    for term in sorted(terms):
        pattern = r"(?<![a-z0-9+#.])" + re.escape(term.lower()) + r"(?![a-z0-9+#.])"
        if re.search(pattern, lower_text):
            found.append(term)
    return found


def _count_section_items(text, section_names):
    lower_text = text.lower()
    for section in section_names:
        match = re.search(rf"{section}\s*[:\-]?\s*(.+?)(education|skills|certifications|experience|achievements|$)", lower_text)
        if match:
            body = match.group(1)
            bullets = re.findall(r"([•\-*]|\d+\.)\s+", body)
            if bullets:
                return len(bullets)
    return 0


def _find_certifications(text):
    found = _find_terms(text, COMMON_CERTIFICATIONS)
    cert_section = re.search(r"certifications?\s*[:\-]?\s*(.+?)(projects|experience|skills|education|achievements|$)", text, re.I)
    if cert_section:
        candidates = re.split(r"[•\n;,]|(?:\s+-\s+)", cert_section.group(1))
        for candidate in candidates:
            value = candidate.strip(" .:-")
            if 3 <= len(value) <= 80 and value not in found:
                found.append(value)
    return [{"name": value} for value in found[:12]]


def _find_section_items(text, section_names, stop_sections):
    stop_pattern = "|".join(stop_sections)
    for section in section_names:
        match = re.search(rf"{section}\s*[:\-]?\s*(.+?)({stop_pattern}|$)", text, re.I | re.S)
        if not match:
            continue
        body = match.group(1).strip()
        candidates = re.split(r"(?:\n|[â€¢•]|(?:\s+-\s+)|(?:\d+\.\s+))", body)
        items = []
        for candidate in candidates:
            value = re.sub(r"\s+", " ", candidate).strip(" .:-")
            if 4 <= len(value) <= 140:
                items.append(value)
        return items[:10]
    return []


def _find_education(text):
    items = _find_section_items(
        text,
        ["education", "academics?"],
        ["skills", "projects", "certifications", "experience", "achievements", "hackathons"],
    )
    return items[:5]


def _find_achievements(text):
    items = _find_section_items(
        text,
        ["achievements?", "awards?", "honou?rs?"],
        ["skills", "projects", "certifications", "experience", "education", "hackathons"],
    )
    return [{"title": item} for item in items[:8]]


def _find_hackathons(text):
    items = _find_section_items(
        text,
        ["hackathons?", "competitions?"],
        ["skills", "projects", "certifications", "experience", "education", "achievements"],
    )
    return [{"name": item} for item in items[:8]]


def parse_resume(file_storage):
    text = extract_text_from_pdf(file_storage)
    terms = _catalog_terms()

    extracted = {
        "skills": _find_terms(text, terms["skills"]),
        "programming_languages": _find_terms(text, terms["programming_languages"]),
        "frameworks": _find_terms(text, terms["frameworks"]),
        "tools": _find_terms(text, terms["tools"]),
        "databases": _find_terms(text, terms["databases"]),
        "platforms": _find_terms(text, terms["platforms"]),
        "technologies": _find_terms(text, terms["technologies"]),
        "certifications": _find_certifications(text),
        "achievements": _find_achievements(text),
        "hackathons": _find_hackathons(text),
        "education": _find_education(text),
        "projects": _count_section_items(text, ["projects?", "academic projects?"]),
        "internships": _count_section_items(text, ["internships?", "work experience", "experience"]),
        "resume_text": text,
    }
    extracted["analysis"] = {
        "text_length": len(text),
        "has_education": bool(extracted["education"]),
        "has_projects": extracted["projects"] > 0,
        "has_experience": extracted["internships"] > 0,
        "has_certifications": bool(extracted["certifications"]),
        "has_achievements": bool(extracted["achievements"]),
    }
    return extracted

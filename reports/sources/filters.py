from urllib.parse import urlparse


def normalize_company_slug(company):
    return "".join(character.lower() for character in company if character.isalnum())


def get_domain(url):
    return urlparse(url).netloc.lower().removeprefix("www.")


def is_likely_company_owned_source(url, company):
    domain = get_domain(url)
    company_slug = normalize_company_slug(company)

    if not company_slug:
        return False

    compact_domain = "".join(character for character in domain if character.isalnum())

    return company_slug in compact_domain


def keep_external_sources_only(candidates, company):
    return [
        candidate
        for candidate in candidates
        if not is_likely_company_owned_source(candidate.url, company)
    ]

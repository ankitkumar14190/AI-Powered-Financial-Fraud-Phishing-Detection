from urllib.parse import ParseResult
import ipaddress


def is_https(parsed: ParseResult) -> bool:
    """True if the URL uses the https:// scheme."""
    return parsed.scheme == "https"


def uses_ip_address(parsed: ParseResult) -> bool:
    """
    True if the hostname is a raw IP address instead of a domain name.
    Legitimate sites almost never do this; it's a classic phishing tell.
    """
    if not parsed.hostname:
        return False
    try:
        ipaddress.ip_address(parsed.hostname)
        return True
    except ValueError:
        return False


def is_long_url(url: str, threshold: int = 75) -> bool:
    """True if the URL exceeds a suspicious length."""
    return len(url) > threshold


def has_at_symbol(url: str) -> bool:
    """
    True if the URL contains '@'. Browsers ignore everything before '@' in
    the authority component, a common trick to disguise the real domain.
    """
    return "@" in url


def has_hyphen_in_domain(parsed: ParseResult) -> bool:
    """True if the domain itself contains a hyphen (e.g. paypal-secure.com)."""
    return "-" in parsed.netloc


def has_excessive_subdomains(parsed: ParseResult, max_dots: int = 3) -> bool:
    """True if the domain has an unusually deep subdomain chain."""
    return parsed.netloc.count(".") > max_dots


def find_suspicious_keywords(url: str, keywords: list) -> list:
    """Return the subset of `keywords` that appear (case-insensitively) in the URL."""
    lower_url = url.lower()
    return [word for word in keywords if word in lower_url]

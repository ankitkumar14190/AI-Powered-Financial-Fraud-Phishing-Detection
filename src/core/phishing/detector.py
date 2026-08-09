"""
Rule-based phishing URL detector.

Fixes vs the original version:
  * BUG: `except:` (bare except) silently swallowed every possible error,
    including typos and programming mistakes, not just the expected
    ValueError from ipaddress.ip_address(). Now catches ValueError only.
  * BUG: parsed.hostname can be None (e.g. for a malformed URL like "not a url"),
    which used to raise inside the bare except and get hidden. Now handled
    explicitly in url_features.uses_ip_address().
  * No input validation previously existed -- an empty string or a URL with
    no scheme (e.g. "example.com") silently produced a low, misleading score.
    analyze() now raises a clear ValueError the UI layer can catch and display.
  * All scoring logic now delegates to url_features.py (pure functions) and
    rules.py (weights/thresholds), so this class is just orchestration.
"""

from urllib.parse import urlparse

from src.core.phishing import url_features
from src.core.phishing.rules import WEIGHTS, SUSPICIOUS_KEYWORDS, classify_risk
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class PhishingDetector:
    """Heuristic, rule-based phishing URL scorer (0-100, higher = riskier)."""

    def __init__(self):
        self.suspicious_keywords = SUSPICIOUS_KEYWORDS

    def analyze(self, url: str) -> dict:
        """
        Score a URL for phishing risk.

        Raises:
            ValueError: if `url` is empty/blank or has no network location
                        (e.g. missing scheme), since scoring garbage input
                        produces a misleading result.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        url = url.strip()
        parsed = urlparse(url)

        if not parsed.netloc:
            raise ValueError(
                "Could not parse a domain from this URL. "
                "Make sure it includes a scheme, e.g. https://example.com"
            )

        score = 0
        reasons = []

        if not url_features.is_https(parsed):
            score += WEIGHTS["not_https"]
            reasons.append("Not using HTTPS")

        if url_features.uses_ip_address(parsed):
            score += WEIGHTS["ip_address"]
            reasons.append("IP address used instead of a domain name")

        if url_features.is_long_url(url):
            score += WEIGHTS["long_url"]
            reasons.append("Unusually long URL")

        if url_features.has_at_symbol(url):
            score += WEIGHTS["at_symbol"]
            reasons.append("'@' symbol detected in URL")

        if url_features.has_hyphen_in_domain(parsed):
            score += WEIGHTS["hyphen_in_domain"]
            reasons.append("Hyphen in domain name")

        if url_features.has_excessive_subdomains(parsed):
            score += WEIGHTS["excessive_subdomains"]
            reasons.append("Excessive number of subdomains")

        matched_keywords = url_features.find_suspicious_keywords(
            url, self.suspicious_keywords
        )
        for word in matched_keywords:
            score += WEIGHTS["keyword"]
            reasons.append(f"Suspicious keyword: '{word}'")

        score = min(score, 100)
        risk = classify_risk(score)

        logger.info("Scanned URL scored %s (%s)", score, risk)

        return {
            "score": score,
            "risk": risk,
            "reasons": reasons,
        }


def finalize_result(heuristic_result: dict, intel: dict) -> dict:
    """
    Combine a heuristic PhishingDetector.analyze() result with a
    (possibly unavailable) ThreatIntelClient.check_url() result into the
    final score/risk shown to the user.
    """
    from src.core.phishing.rules import apply_threat_intel_adjustment, classify_risk

    final_score = apply_threat_intel_adjustment(heuristic_result["score"], intel)
    final_risk = classify_risk(final_score)

    reasons = list(heuristic_result["reasons"])
    if intel.get("available") and (intel.get("malicious") or intel.get("suspicious")):
        reasons.append(
            f"VirusTotal: {intel.get('malicious', 0)} engine(s) flagged malicious, "
            f"{intel.get('suspicious', 0)} flagged suspicious"
        )

    return {"score": final_score, "risk": final_risk, "reasons": reasons}

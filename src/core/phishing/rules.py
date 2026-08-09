from src.config.config import PHISHING_SAFE_THRESHOLD, PHISHING_SUSPICIOUS_THRESHOLD

# Score contribution of each heuristic when it fires.
WEIGHTS = {
    "not_https": 20,
    "ip_address": 25,
    "long_url": 15,
    "at_symbol": 20,
    "hyphen_in_domain": 10,
    "excessive_subdomains": 10,
    "keyword": 5,
}

SUSPICIOUS_KEYWORDS = [
    "login",
    "verify",
    "secure",
    "update",
    "bank",
    "account",
    "paypal",
    "signin",
    "confirm",
    "password",
    "wallet",
    "crypto",
]


def classify_risk(score: int) -> str:
    """Map a numeric 0-100 score to a human-readable risk label."""
    if score < PHISHING_SAFE_THRESHOLD:
        return "🟢 Safe"
    if score < PHISHING_SUSPICIOUS_THRESHOLD:
        return "🟡 Suspicious"
    return "🔴 Dangerous"


def apply_threat_intel_adjustment(heuristic_score: int, intel: dict) -> int:
    """
    Blend the local heuristic score with an external VirusTotal verdict.

    If VirusTotal wasn't available (no API key, request failed, etc.) the
    heuristic score passes through untouched -- external intel is a bonus
    signal, never a hard requirement.

    If multiple engines flag the URL as malicious, that's a much stronger
    signal than any single heuristic, so it pushes the score straight to
    the top of the "Dangerous" band regardless of the heuristic result.
    """
    if not intel.get("available"):
        return heuristic_score

    malicious = intel.get("malicious", 0)
    suspicious = intel.get("suspicious", 0)

    if malicious > 0:
        return 100
    if suspicious > 0:
        return max(heuristic_score, PHISHING_SUSPICIOUS_THRESHOLD)

    return heuristic_score

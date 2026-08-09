"""
Optional VirusTotal integration for the phishing detector.

Design goal: the heuristic scanner (detector.py) must keep working with
zero configuration, since that's what makes the project easy to demo/judge.
This client is purely additive -- if no API key is configured, callers get
back {"available": False, ...} and the UI just skips this section.

Get a free VirusTotal API key at https://www.virustotal.com/gui/join-us
and set it as the VT_API_KEY environment variable, or in
.streamlit/secrets.toml as:
    VT_API_KEY = "your-key-here"
"""

import base64
import os

import requests

from src.utils.helpers import get_logger

logger = get_logger(__name__)

VT_URL_ENDPOINT = "https://www.virustotal.com/api/v3/urls"
REQUEST_TIMEOUT_SECONDS = 10


def _resolve_api_key(explicit_key: str = None) -> str:
    """Priority: explicit arg > Streamlit secrets > environment variable."""
    if explicit_key:
        return explicit_key

    try:
        import streamlit as st
        if "VT_API_KEY" in st.secrets:
            return st.secrets["VT_API_KEY"]
    except Exception:
        # st.secrets raises if no secrets.toml exists at all -- that's fine,
        # it just means the key isn't configured that way.
        pass

    return os.environ.get("VT_API_KEY", "")


class ThreatIntelClient:
    """Thin wrapper around the VirusTotal v3 URLs API."""

    def __init__(self, api_key: str = None):
        self.api_key = _resolve_api_key(api_key)

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def check_url(self, url: str) -> dict:
        """
        Look up `url` in VirusTotal's community reputation database.

        Returns a dict shaped either as:
            {"available": False, "reason": "..."}
        or:
            {"available": True, "malicious": int, "suspicious": int,
             "harmless": int, "undetected": int}
        """
        if not self.is_configured():
            return {
                "available": False,
                "reason": "No VirusTotal API key configured.",
            }

        headers = {"x-apikey": self.api_key}
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

        try:
            response = requests.get(
                f"{VT_URL_ENDPOINT}/{url_id}",
                headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            if response.status_code == 404:
                # VirusTotal has never seen this URL -- submit it for analysis.
                submit = requests.post(
                    VT_URL_ENDPOINT,
                    headers=headers,
                    data={"url": url},
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
                submit.raise_for_status()
                return {
                    "available": True,
                    "malicious": 0,
                    "suspicious": 0,
                    "harmless": 0,
                    "undetected": 0,
                    "note": "First time this URL was seen — submitted for scanning. "
                            "Check again in a minute for full results.",
                }

            response.raise_for_status()
            stats = response.json()["data"]["attributes"]["last_analysis_stats"]

            return {
                "available": True,
                "malicious": stats.get("malicious", 0),
                "suspicious": stats.get("suspicious", 0),
                "harmless": stats.get("harmless", 0),
                "undetected": stats.get("undetected", 0),
            }

        except requests.RequestException:
            logger.exception("VirusTotal lookup failed for URL: %s", url)
            return {
                "available": False,
                "reason": "VirusTotal request failed. Check your API key and network connection.",
            }

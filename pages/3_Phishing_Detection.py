"""
Phishing Detection page.

New in this version: an optional VirusTotal threat-intel lookup that
enriches the local heuristic score. Fully optional -- if no VT_API_KEY is
configured, the page still works exactly as before and just shows an
info banner explaining how to enable it.
"""

import streamlit as st

from src.core.phishing.detector import PhishingDetector, finalize_result
from src.core.phishing.threat_intel import ThreatIntelClient
from src.database.db import save_phishing_scan
from src.utils.helpers import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Phishing Detection | Fraud & Phishing Detection", page_icon="🌐")

st.title("🌐 Phishing URL Detection")
st.caption("Paste a full URL (including https://) to run it against the heuristic scanner.")


@st.cache_resource(show_spinner=False)
def load_detector() -> PhishingDetector:
    return PhishingDetector()


@st.cache_resource(show_spinner=False)
def load_threat_intel() -> ThreatIntelClient:
    return ThreatIntelClient()


intel_client = load_threat_intel()
if not intel_client.is_configured():
    st.info(
        "ℹ️ VirusTotal enrichment is disabled. Set a `VT_API_KEY` environment "
        "variable or add it to `.streamlit/secrets.toml` to enable it. "
        "The heuristic scanner below works either way."
    )

url = st.text_input("Enter URL", placeholder="https://example.com")

if st.button("Analyze URL", type="primary"):

    detector = load_detector()

    try:
        heuristic_result = detector.analyze(url)
    except ValueError as e:
        st.warning(f"⚠️ {e}")
        st.stop()
    except Exception:
        logger.exception("Unexpected error analyzing URL: %s", url)
        st.error("An unexpected error occurred. Check logs/app.log for details.")
        st.stop()

    intel = {"available": False}
    if intel_client.is_configured():
        with st.spinner("Checking VirusTotal..."):
            intel = intel_client.check_url(url)

    result = finalize_result(heuristic_result, intel)

    try:
        save_phishing_scan(url, result["score"], result["risk"], result["reasons"])
    except Exception:
        # Persistence failure shouldn't block showing the result to the user.
        logger.exception("Failed to save phishing scan to database.")

    st.metric("Risk Score", f"{result['score']}%")
    st.subheader(result["risk"])

    if intel.get("available"):
        vt_col1, vt_col2, vt_col3 = st.columns(3)
        vt_col1.metric("🔴 Malicious", intel.get("malicious", 0))
        vt_col2.metric("🟡 Suspicious", intel.get("suspicious", 0))
        vt_col3.metric("🟢 Harmless", intel.get("harmless", 0))
        if intel.get("note"):
            st.caption(intel["note"])
    elif intel_client.is_configured():
        st.caption(f"VirusTotal lookup unavailable: {intel.get('reason', 'unknown error')}")

    st.write("### Findings")
    if len(result["reasons"]) == 0:
        st.success("No suspicious indicators found.")
    else:
        for reason in result["reasons"]:
            st.write("•", reason)

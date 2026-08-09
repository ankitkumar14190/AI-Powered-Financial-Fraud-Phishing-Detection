from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos


class _DashboardPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Fraud & Phishing Detection - Summary Report",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 8, datetime.now().strftime("Generated on %Y-%m-%d %H:%M"),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(4)

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def line(self, label: str, value):
        self.set_font("Helvetica", "", 11)
        self.cell(0, 8, f"{label}: {value}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_dashboard_pdf(
    fraud_summary: dict,
    phishing_summary: dict,
    unified: dict,
) -> bytes:
    """
    Build a one-page PDF summarizing fraud stats, phishing stats, and the
    unified risk score. Returns raw PDF bytes suitable for st.download_button.
    """
    pdf = _DashboardPDF()
    pdf.add_page()

    pdf.section_title("Fraud Detection Summary")
    pdf.line("Total Transactions Scanned", fraud_summary.get("total", 0))
    pdf.line("Flagged as Fraud", fraud_summary.get("frauds", 0))
    pdf.line("Legitimate", fraud_summary.get("legitimate", 0))
    pdf.ln(4)

    pdf.section_title("Phishing Detection Summary")
    pdf.line("Total URLs Scanned", phishing_summary.get("total", 0))
    pdf.line("Dangerous", phishing_summary.get("dangerous", 0))
    pdf.line("Suspicious", phishing_summary.get("suspicious", 0))
    pdf.line("Safe", phishing_summary.get("safe", 0))
    pdf.ln(4)

    pdf.section_title("Unified Risk Assessment")
    pdf.line("Combined Risk Score", f"{unified.get('combined_score', 0)}/100")
    pdf.line("Fraud Rate", f"{unified.get('fraud_rate', 0)}%")
    pdf.line("Phishing Risk Rate", f"{unified.get('phishing_rate', 0)}%")

    return bytes(pdf.output())

# 🛡️ AI-Powered Financial Fraud & Phishing Detection Platform

## Team Name: ENIGMA

## Deployment link:- https://ai-powered-financial-fraud-phishing-detection-fpo2wyb5kz9kdgjx.streamlit.app/

## Project PPT:- https://docs.google.com/presentation/d/1zWp34CKI7Rb-FRGtLULha3TJmxHzDe3y/edit?usp=sharing&ouid=111010281849703793989&rtpof=true&sd=true

## Demo Video:- https://drive.google.com/file/d/1x_wx8rOOWEiJe8ZRA0qvO_4PzcRDHkGV/view?usp=sharing

## Documentation link:- https://drive.google.com/file/d/1VzACTqEAecDE88BUNETUo-Z70aUVmtt6/view?usp=sharing

## Overview

An AI-powered cybersecurity and FinTech platform that detects:

* Fraudulent financial transactions using a trained Random Forest model
* Suspicious phishing URLs using rule-based cybersecurity heuristics
* Risk analytics through an interactive dashboard covering both modules

## Features

### 💳 Fraud Detection
* Random Forest classifier, trained on the standard `creditcard.csv` schema
* Batch CSV upload with column validation and clear error messages
* Confidence scores per transaction
* Cached model loading for fast repeat scans

### 🌐 Phishing Detection
* HTTPS validation, IP-address hosts, `@` trick detection
* Hyphenated/excessive-subdomain domain checks
* Suspicious keyword matching
* Every scan is saved to history

* **SHAP explainability**: single-transaction check shows the top 5 features that pushed the model's decision
* **VirusTotal enrichment** (optional): blends the heuristic score with real-world engine verdicts

### 📊 Dashboard
* Separate tabs for fraud and phishing history
* Summary metrics, distribution charts, and daily volume trend charts
* CSV export per history table, and a one-page PDF summary report
* Backed by SQLite

### 🧭 Unified Risk Score
* Blends fraud rate (60%) and phishing risk rate (40%) into a single 0-100 organizational risk indicator

## Tech Stack

* Python, Streamlit
* Scikit-learn, Pandas, NumPy
* SQLite, Joblib

## Project Structure

```text
app.py
pages/
  1_Home.py
  2_Fraud_Detection.py
  3_Phishing_Detection.py
  4_Dashboard.py
  5_About.py
src/
  config/config.py          # single source of truth for all paths & constants
  core/fraud/                # training, preprocessing, batch prediction
  core/phishing/              # feature extraction, rules, detector
  database/db.py             # SQLite persistence for both modules
  dashboard/dashboard.py      # shared data-shaping helpers
  utils/helpers.py           # logging setup
models/
database/
logs/
assets/
```

## Installation

```bash
git clone <repo-url>
cd AI-Powered-Financial-Fraud-Phishing-Detection

python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

## Training the fraud model

Place `creditcard.csv` in `data/`, then:

```bash
python -m src.core.fraud.train_model
```

This writes `models/fraud_model.pkl` and `models/scaler.pkl`.

## Running the app

```bash
streamlit run app.py
```

## Optional: VirusTotal enrichment

Get a free API key at https://www.virustotal.com/gui/join-us, then either:

```bash
export VT_API_KEY="your-key-here"   # macOS/Linux
set VT_API_KEY=your-key-here        # Windows
```

or create `.streamlit/secrets.toml`:

```toml
VT_API_KEY = "your-key-here"
```

The Phishing Detection page works fully without this -- it's an optional enrichment layer.

## Logs

All modules log to `logs/app.log` (and the console) via `src/utils/helpers.get_logger`.

## Future Scope

* Explainable AI (SHAP) for fraud predictions
* XGBoost as an alternative model
* Real-time phishing intelligence APIs
* Email alerts
* User authentication

## Creditcard.csv
Get the Creditcard.csv from the https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud/data. You need to create a free account on kaggle to download this datasets. 

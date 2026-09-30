# SecureSpend — AI Credit Card Fraud Detection

SecureSpend is a polished Flask portfolio application for evaluating credit-card transaction risk. It presents a professional banking-style workspace with secure accounts, explainable ensemble signals, audit history, and category analytics.

> This project is an educational fraud-monitoring demonstration. It does not connect to a payment processor or make live authorization decisions.

## Live demo

Try the deployed application: **[SecureSpend on Render](https://secure-spend-ai-fraud-detection.onrender.com)**

> The free Render service may take up to a minute to wake after inactivity. Use test/demo transaction details only; never enter real card information.

## Highlights

- Secure registration and login with Werkzeug password hashing and user sessions
- Responsive risk operations dashboard with real per-user metrics
- Transaction risk assessment using transparent SVM, KNN, and ANN-style signals
- Persistent SQLite audit trail, masked card display, result views, and analytics
- Professional design system: modern cards, loading state, motion, mobile navigation, accessible form states, and banking-focused color palette
- Optional trained model artifacts and dataset retained for future ML pipeline integration

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`, create an account, and run a transaction analysis.

## Email alerts (optional)

SecureSpend sends an email for a **Review required** assessment when an SMTP account is configured. Set these environment variables before starting the app:

```powershell
$env:SMTP_HOST = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SMTP_USERNAME = "your-email@gmail.com"
$env:SMTP_PASSWORD = "your-app-password"
$env:ALERT_FROM = "your-email@gmail.com"
python app.py
```

For Gmail, create an App Password first; never place real passwords in source code or commit them to GitHub.

## Technology

Python · Flask · SQLite · HTML/CSS · JavaScript · Scikit-learn · TensorFlow/Keras

## Project structure

```text
app.py                 # Routes, auth, SQLite persistence, risk workflow
templates/             # Responsive Jinja UI views
static/                # Design system and interaction behavior
models/                # Pre-trained SVM, KNN, ANN artifacts
creditcard.csv         # Source dataset (not committed)
```

## Deployment note

Set a strong `SECRET_KEY` environment variable before deployment. For production, use a managed database, enforce HTTPS, add CSRF protection/rate limiting, and keep all sensitive datasets and model artifacts out of public repositories.

## Model integrity note

The included dataset models expect anonymized `V1`–`V28` and `Amount` inputs. Those signals cannot be derived reliably from card holder, merchant, city, or transaction channel data. The app therefore uses a transparent contextual risk assessment for the visible workflow. To deploy the saved SVM/KNN/ANN artifacts for real inference, add the feature-engineering pipeline used during their training, or retrain all three models on a dataset that contains the form fields collected by this application.

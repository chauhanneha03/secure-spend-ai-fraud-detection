# SecureSpend interview guide

## 30-second project explanation

“SecureSpend is a Flask-based credit-card transaction risk-monitoring application. I built secure registration and login, stored user-scoped transaction assessments in SQLite, and created a responsive operations dashboard with history, category analytics, and configurable SMTP alerts for high-risk checks. I designed the interface as a banking-style product and added automated tests plus a GitHub Actions workflow.”

## Architecture

`Browser → Flask routes → SQLite database → Jinja templates/CSS/JavaScript`

- `app.py`: routing, sessions, risk assessment, persistence, dashboard queries
- `templates/`: server-rendered pages using Jinja
- `static/`: responsive styles and lightweight interactions
- `utils/email_service.py`: optional SMTP welcome and fraud-risk alerts
- `tests/`: automated end-to-end smoke test

## Questions recruiters may ask

### Why Flask?

Flask is lightweight, readable, and ideal for demonstrating clear backend routing, session handling, database access, and server-rendered pages in a portfolio project.

### How are passwords protected?

Passwords are never stored as plain text. Werkzeug generates a salted password hash on registration and verifies it on login.

### How does the fraud decision work?

The visible workflow uses an explainable contextual score based on amount, category, channel, and city. This makes the demo understandable. The included SVM/KNN/ANN files use anonymized dataset features, so a matching feature pipeline or retraining is required for production inference.

### Why SQLite?

SQLite is simple and reliable for a local portfolio demo. In production, I would use PostgreSQL with migrations, managed backups, and connection pooling.

### How do email alerts work?

When risk exceeds the review threshold, the app calls an SMTP service. Credentials are read from environment variables, never committed to the repository.

### What would you improve for production?

CSRF protection, rate limiting, PostgreSQL, background email jobs, structured logging, error monitoring, role-based access, HTTPS, automated deployment, and a real model feature pipeline.

## Resume bullet

Built **SecureSpend**, a responsive Flask fraud-risk monitoring platform with secure hashed authentication, SQLite audit trails, high-risk SMTP alerts, transaction analytics, automated pytest coverage, and GitHub Actions CI.

## Demo flow

1. Register a test account and sign in.
2. Show the dashboard metrics and risk posture.
3. Submit a low-risk transaction, then a high-risk one.
4. Explain the result page and email alert.
5. Open transaction history and category analytics.
6. Close with the production improvements listed above.

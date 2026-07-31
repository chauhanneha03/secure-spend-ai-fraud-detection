"""SecureSpend — credit-card transaction risk monitoring demo."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from utils.email_service import send_risk_alert, send_welcome_email

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "fraud_detection.db"))

app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY", "change-this-before-deployment"))


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS app_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS app_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            card_number TEXT NOT NULL,
            card_holder TEXT NOT NULL,
            amount REAL NOT NULL,
            merchant TEXT NOT NULL,
            category TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            city TEXT NOT NULL,
            decision TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            svm_result TEXT NOT NULL,
            knn_result TEXT NOT NULL,
            ann_result TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES app_users(id)
        );
    """)
    db.commit()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access your workspace.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


def mask_card(card_number: str) -> str:
    digits = "".join(char for char in card_number if char.isdigit())
    return f"•••• {digits[-4:]}" if len(digits) >= 4 else "••••"


def evaluate_transaction(amount: float, category: str, transaction_type: str, city: str):
    """Transparent ensemble-style risk simulation for the demo workflow."""
    risk = 8
    if amount >= 50000:
        risk += 50
    elif amount >= 20000:
        risk += 30
    elif amount >= 10000:
        risk += 15
    if category in {"Electronics", "Travel", "ATM"}:
        risk += 12
    if transaction_type in {"Online", "ATM Withdrawal"}:
        risk += 10
    if city.strip().lower() not in {"mumbai", "delhi", "bengaluru", "pune", "chennai", "hyderabad", "kolkata"}:
        risk += 8
    risk = min(risk, 98)
    decision = "Review required" if risk >= 55 else "Approved"
    model_result = "Fraud risk" if decision == "Review required" else "Legitimate"
    return {
        "risk_score": risk,
        "decision": decision,
        "svm": model_result if risk >= 50 else "Legitimate",
        "knn": model_result if risk >= 58 else "Legitimate",
        "ann": model_result if risk >= 55 else "Legitimate",
    }


@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year, "mask_card": mask_card}


@app.route("/")
def home():
    return redirect(url_for("dashboard" if "user_id" in session else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identity = request.form.get("identity", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM app_users WHERE username = ? OR email = ?", (identity, identity)
        ).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session.update(user_id=user["id"], user_name=user["full_name"])
            return redirect(url_for("dashboard"))
        flash("We couldn't verify those sign-in details.", "error")
    return render_template("login.html", auth_page=True)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = {key: request.form.get(key, "").strip() for key in ("full_name", "email", "username")}
        password = request.form.get("password", "")
        if not all(data.values()) or len(password) < 8:
            flash("Complete all fields and use a password with at least 8 characters.", "error")
        else:
            try:
                get_db().execute(
                    "INSERT INTO app_users (full_name, email, username, password_hash) VALUES (?, ?, ?, ?)",
                    (data["full_name"], data["email"].lower(), data["username"], generate_password_hash(password)),
                )
                get_db().commit()
                send_welcome_email(data["email"].lower(), data["full_name"])
                flash("Account created. A welcome email was sent if SMTP is configured.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That email or username is already registered.", "error")
    return render_template("register.html", auth_page=True)


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user_id = session["user_id"]
    stats = db.execute("""
        SELECT COUNT(*) AS total, COALESCE(SUM(decision = 'Approved'), 0) AS approved,
               COALESCE(SUM(decision = 'Review required'), 0) AS flagged,
               COALESCE(AVG(risk_score), 0) AS average_risk
        FROM app_transactions WHERE user_id = ?
    """, (user_id,)).fetchone()
    recent = db.execute("SELECT * FROM app_transactions WHERE user_id = ? ORDER BY id DESC LIMIT 6", (user_id,)).fetchall()
    category_stats = db.execute("""
        SELECT category, COUNT(*) AS total, AVG(risk_score) AS average_risk
        FROM app_transactions WHERE user_id = ? GROUP BY category ORDER BY total DESC LIMIT 4
    """, (user_id,)).fetchall()
    return render_template("dashboard.html", stats=stats, recent=recent, category_stats=category_stats)


@app.route("/detect", methods=["GET", "POST"])
@login_required
def detect():
    if request.method == "POST":
        form = request.form
        try:
            amount = float(form["amount"])
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Enter a valid transaction amount.", "error")
            return render_template("detect.html")
        required = ("card_number", "card_holder", "merchant", "category", "transaction_type", "city")
        if not all(form.get(field, "").strip() for field in required):
            flash("Please complete every transaction field.", "error")
            return render_template("detect.html")
        result = evaluate_transaction(amount, form["category"], form["transaction_type"], form["city"])
        cursor = get_db().execute("""
            INSERT INTO app_transactions (user_id, card_number, card_holder, amount, merchant, category,
                transaction_type, city, decision, risk_score, svm_result, knn_result, ann_result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session["user_id"], form["card_number"], form["card_holder"], amount, form["merchant"],
              form["category"], form["transaction_type"], form["city"], result["decision"], result["risk_score"],
              result["svm"], result["knn"], result["ann"]))
        get_db().commit()
        if result["decision"] == "Review required":
            user = get_db().execute("SELECT email, full_name FROM app_users WHERE id = ?", (session["user_id"],)).fetchone()
            send_risk_alert(user["email"], user["full_name"], form["merchant"], amount, result["risk_score"])
            flash("High-risk transaction saved. An email alert was queued if SMTP is configured.", "info")
        return redirect(url_for("result", transaction_id=cursor.lastrowid))
    return render_template("detect.html")


@app.route("/result/<int:transaction_id>")
@login_required
def result(transaction_id):
    transaction = get_db().execute("SELECT * FROM app_transactions WHERE id = ? AND user_id = ?", (transaction_id, session["user_id"])).fetchone()
    if not transaction:
        flash("Transaction not found.", "error")
        return redirect(url_for("history"))
    return render_template("result.html", transaction=transaction)


@app.route("/history")
@login_required
def history():
    transactions = get_db().execute("SELECT * FROM app_transactions WHERE user_id = ? ORDER BY id DESC", (session["user_id"],)).fetchall()
    return render_template("transaction.html", transactions=transactions)


@app.route("/analytics")
@login_required
def analytics():
    rows = get_db().execute("SELECT category, COUNT(*) AS total, AVG(risk_score) AS risk FROM app_transactions WHERE user_id = ? GROUP BY category ORDER BY total DESC", (session["user_id"],)).fetchall()
    total = sum(row["total"] for row in rows) or 1
    return render_template("analytics.html", rows=rows, total=total)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out securely.", "info")
    return redirect(url_for("login"))


with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)

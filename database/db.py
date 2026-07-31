import sqlite3
from config import DATABASE_PATH

# Create connection
def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            password TEXT DEFAULT '123456',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_number TEXT NOT NULL,
            amount REAL NOT NULL,
            merchant TEXT,
            transaction_type TEXT,
            city TEXT,
            prediction TEXT,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Create user
def create_user(card_number, name, email, phone):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR IGNORE INTO users (card_number, name, email, phone)
        VALUES (?, ?, ?, ?)
    ''', (card_number, name, email, phone))

    conn.commit()
    conn.close()

# Get user by card number
def get_user(card_number):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE card_number = ?', (card_number,))
    user = cursor.fetchone()

    conn.close()
    return user

# Save transaction
def save_transaction(card_number, amount, merchant, transaction_type, city, prediction, confidence):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO transactions
        (card_number, amount, merchant, transaction_type, city, prediction, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (card_number, amount, merchant, transaction_type, city, prediction, confidence))

    conn.commit()
    conn.close()

# Get recent transactions
def get_recent_transactions(limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM transactions
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))

    transactions = cursor.fetchall()

    conn.close()
    return transactions

# Dashboard statistics
def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM transactions')
    total_transactions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM transactions WHERE prediction = 'Fraud'")
    fraud_transactions = cursor.fetchone()[0]

    legitimate_transactions = total_transactions - fraud_transactions

    conn.close()

    return {
        'total_users': total_users,
        'total_transactions': total_transactions,
        'fraud_transactions': fraud_transactions,
        'legitimate_transactions': legitimate_transactions
    }
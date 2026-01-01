import sqlite3
import pandas as pd
from pathlib import Path
import json

datasets = {
    "Data/branches.csv": "branches",
    "Data/customers.csv": "customers",
    "Data/accounts.csv": "accounts",
    "Data/loans.csv": "loans",
    "Data/credit_cards.json": "creditcards",
    "Data/transactions.csv": "transactions",
    "Data/support_tickets.csv": "supporttickets"
}

class BankSightDB:

    def __init__(self, db_name="Database/BankSight.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # ALL TABLE NAMES AND COLUMN NAMES MUST BE LOWERCASE
        #1 Customers Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                gender CHAR(1),
                age INTEGER,
                city VARCHAR(100),
                account_type VARCHAR(50),
                join_date TEXT
            );
        """)
 #2 Branches Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS branches (
                branch_id INTEGER PRIMARY KEY,
                branch_name VARCHAR(255) NOT NULL,
                city VARCHAR(100),
                manager_name VARCHAR(255),
                total_employees INTEGER,
                branch_revenue REAL,
                opening_date TEXT,
                performance_rating INTEGER
            );
        """)
#3 Accounts Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER PRIMARY KEY,
                customer_id VARCHAR(20) NOT NULL,
                account_balance REAL NOT NULL DEFAULT 0.0,
                last_updated TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            );
        """)
#4  Transactions Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                txn_id VARCHAR(20) PRIMARY KEY,
                customer_id VARCHAR(20) NOT NULL,
                txn_type VARCHAR(50) NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                txn_time TEXT NOT NULL,
                status VARCHAR(20) NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            );
        """)
#5 Loans Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                loan_id INTEGER PRIMARY KEY,
                customer_id VARCHAR(20) NOT NULL,
                branch VARCHAR(255), 
                loan_type VARCHAR(50),
                loan_amount REAL,
                account_id INTEGER,
                interest_rate REAL,
                loan_term_months INTEGER,
                start_date TEXT,
                end_date TEXT,
                loan_status VARCHAR(20),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (branch) REFERENCES branches(branch_name)
            );
        """)
#6 CreditCards Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS creditcards (
                card_id INTEGER PRIMARY KEY,
                branch VARCHAR(255),
                customer_id VARCHAR(20) NOT NULL,
                account_id INTEGER NOT NULL,
                card_number VARCHAR(20) UNIQUE NOT NULL,
                card_type VARCHAR(50),
                card_network VARCHAR(50),
                credit_limit REAL,
                current_balance REAL,
                issued_date TEXT,
                expiry_date TEXT,
                status VARCHAR(20),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (account_id) REFERENCES accounts(account_id)
            );
        """)
#7 SupportTickets Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS supporttickets (
                ticket_id VARCHAR(20) PRIMARY KEY,
                customer_id VARCHAR(20) NOT NULL,
                account_id INTEGER,
                loan_id INTEGER,
                branch_name VARCHAR(255),
                issue_category TEXT,
                description TEXT,
                date_opened TEXT,
                date_closed TEXT,
                priority TEXT,
                status TEXT,
                resolution_remarks TEXT,
                support_agent TEXT,
                channel TEXT,
                customer_rating INTEGER,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
                FOREIGN KEY (loan_id) REFERENCES loans(loan_id) ON DELETE SET NULL,
                FOREIGN KEY (branch_name) REFERENCES branches(branch_name) ON DELETE SET NULL
            );
        """)
        
        self.conn.commit()
        print("Tables created successfully.")

    def extract_data(self, file_path):
        """Extract data from a CSV or JSON file.

        Supports:
        - CSV files (.csv)
        - JSON files (.json), where JSON can be:
          - an array of objects
          - newline-delimited JSON (NDJSON / JSON Lines)
          - a single object or dict-of-lists (normalized automatically)
        Returns a pandas.DataFrame on success or None on failure.
        """
        p = Path(file_path)
        suffix = p.suffix.lower()

        try:
            if suffix == '.csv':
                df = pd.read_csv(file_path)
            elif suffix == '.json':
                # Try common JSON formats
                try:
                    df = pd.read_json(file_path, orient='records')
                except ValueError:
                    try:
                        df = pd.read_json(file_path, lines=True)
                    except ValueError:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            obj = json.load(f)
                        if isinstance(obj, list):
                            df = pd.json_normalize(obj)
                        elif isinstance(obj, dict):
                            # dict-of-lists -> DataFrame, otherwise wrap single record
                            if all(isinstance(v, list) for v in obj.values()):
                                df = pd.DataFrame(obj)
                            else:
                                df = pd.json_normalize([obj])
                        else:
                            raise ValueError("Unsupported JSON structure")
            else:
                raise ValueError(f"Unsupported file type: {suffix!r}")
            print("Data extraction successful.")
            return df
        except Exception as e:
            print(f"Error during data extraction: {e}")
            return None

    def transform_and_load(self, file_path, table_name):
        df = self.extract_data(file_path)
        if df is not None:
            # 1. Standardize column names
            df.columns = [c.lower() for c in df.columns]
            
            # 2. Fix the ID type mismatchs
            df = df.loc[:, ~df.columns.duplicated()]
            
            # 3. Handle duplicates BEFORE loading
            # If you are appending to an existing table, you must drop duplicates 
            # that match the Primary Key
            df = df.drop_duplicates()

            try:
                date_cols = [col for col in df.columns if 'date' in col or 'time' in col]
                for col in date_cols:
                 df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                # Use 'append' but wrap in a try-except to catch duplicates
                df.to_sql(table_name, self.conn, if_exists='append', index=False)
                self.conn.commit()
                print(f"Loaded {len(df)} records into {table_name} successfully.")
            except sqlite3.IntegrityError:
                print(f"Skipping {table_name}: Data already exists or violates constraints.")
            except Exception as e:
                print(f"Error loading data into {table_name}: {e}")
        else:
            print(f"Skipping {table_name}: Data extraction failed.")

    def verify_data(self):
    # Must be lowercase to match your SQL
        tables = ["customers", "branches", "accounts", "transactions", "loans", "creditcards", "supporttickets"]
        print("\n--- FINAL DATABASE AUDIT ---")
        for t in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {t}")
                print(f"{t}: {self.cursor.fetchone()[0]} rows")
            except Exception as e:
                print(f"Error auditing {t}: {e}")
    def close_connection(self):
        self.conn.close()

if __name__ == "__main__":
    db = BankSightDB()
    db.create_tables()
    for file_path, table_name in datasets.items():
        db.transform_and_load(file_path, table_name)
    db.verify_data()
    db.close_connection()
#
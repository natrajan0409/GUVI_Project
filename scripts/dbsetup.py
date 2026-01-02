import sqlite3
import pandas as pd
from pathlib import Path
import json
import warnings

datasets = {
    "Data/customers.csv": "customers",
    "Data/branches.csv": "branches",
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
                phnumber VARCHAR(20) NOT NULL,
                gender CHAR(1),
                age INTEGER CHECK (age >= 18),
                city VARCHAR(100),
                account_type VARCHAR(50),
                join_date DATE,
                UNIQUE(name, Phnumber,account_type)
            );
        """)
 #2 Branches Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS branches (
                branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_name VARCHAR(255) UNIQUE NOT NULL,
                city VARCHAR(100),
                manager_name VARCHAR(255),
                total_employees INTEGER,
                branch_revenue REAL,
                opening_date TEXT,
                performance_rating INTEGER CHECK (performance_rating BETWEEN 1 AND 5)
            );
        """)
#3 Accounts Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id VARCHAR(20) NOT NULL,
            account_balance REAL NOT NULL DEFAULT 0.0,
            last_updated DATE,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            );
        """)
#4  Transactions Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
            txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            customer_id VARCHAR(20) NOT NULL,
            txn_type VARCHAR(50) NOT NULL,
            amount REAL NOT NULL CHECK (amount > 0),
            txn_time TEXT NOT NULL,
            status VARCHAR(20) NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
            );
        """)
#5 Loans Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id VARCHAR(20) NOT NULL,
            branch_name VARCHAR(255),
            loan_type VARCHAR(50),
            loan_amount REAL,
            interest_rate REAL,
            loan_term_months INTEGER,
            start_date TEXT,
            end_date TEXT,
            loan_status VARCHAR(20),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
            FOREIGN KEY (branch_name) REFERENCES branches(branch_name)
            );
        """)
#6 CreditCards Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS creditcards (
            card_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id VARCHAR(20) NOT NULL,
            account_id INTEGER NOT NULL,
            card_number VARCHAR(20) UNIQUE NOT NULL,
            card_type VARCHAR(50),
            card_network VARCHAR(50),
            credit_limit REAL,
            current_balance REAL DEFAULT 0.0,
            issued_date TEXT,
            expiry_date TEXT,
            status VARCHAR(20),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
            );
        """)
#7 SupportTickets Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS supporttickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            customer_rating INTEGER CHECK (customer_rating BETWEEN 1 AND 5),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
            FOREIGN KEY (loan_id) REFERENCES loans(loan_id) ON DELETE SET NULL,
            FOREIGN KEY (branch_name) REFERENCES branches(branch_name)
            );
        """)
        
        self.conn.commit()
        print("Tables created successfully.")

        # Ensure schema compatibility for datasets that contain extra columns
        # e.g., loans.csv contains 'account_id', credit_cards.json contains 'branch' which maps to branch_name
        self.ensure_columns('loans', {'account_id': 'INTEGER'})
        self.ensure_columns('creditcards', {'branch_name': 'VARCHAR(255)'})

        # If certain tables are empty, recreate them with more compatible schemas
        # - allow nullable phnumber in customers (many records lack phone numbers)
        # - make txn_id and ticket_id TEXT primary keys to accept alphanumeric ids
        self.recreate_table_if_empty('customers', '''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phnumber VARCHAR(20),
                gender CHAR(1),
                age INTEGER CHECK (age >= 18),
                city VARCHAR(100),
                account_type VARCHAR(50),
                join_date DATE,
                UNIQUE(name, phnumber)
            );
        ''')

        self.recreate_table_if_empty('transactions', '''
            CREATE TABLE IF NOT EXISTS transactions (
                txn_id VARCHAR(20) PRIMARY KEY,
                account_id INTEGER,
                customer_id VARCHAR(20) NOT NULL,
                txn_type VARCHAR(50) NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                txn_time TEXT NOT NULL,
                status VARCHAR(20) NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
            );
        ''')

        self.recreate_table_if_empty('supporttickets', '''
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
                customer_rating INTEGER CHECK (customer_rating BETWEEN 1 AND 5),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
                FOREIGN KEY (loan_id) REFERENCES loans(loan_id) ON DELETE SET NULL,
                FOREIGN KEY (branch_name) REFERENCES branches(branch_name)
            );
        ''')

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

    def ensure_columns(self, table_name, columns):
        """Ensure the given columns exist in the table; if not, add them via ALTER TABLE.

        columns: dict mapping column_name -> sql_type (e.g. {'account_id': 'INTEGER'})
        """
        try:
            existing = {r[1] for r in self.cursor.execute(f"PRAGMA table_info({table_name})").fetchall()}
        except Exception:
            # Table doesn't exist yet
            existing = set()

        for col, sqltype in columns.items():
            if col not in existing:
                try:
                    self.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {sqltype}")
                    print(f"Added missing column {col} to {table_name}.")
                except Exception as e:
                    print(f"Could not add column {col} to {table_name}: {e}")
        self.conn.commit()

    def transform_and_load(self, file_path, table_name):
        df = self.extract_data(file_path)
        if df is not None:
            # 1. Standardize column names
            df.columns = [c.lower() for c in df.columns]
            
            # 2. Fix the ID type mismatchs and duplicate columns
            df = df.loc[:, ~df.columns.duplicated()]
            
            # 3. Handle duplicates BEFORE loading
            df = df.drop_duplicates()

            try:
                # Normalize date/time-like columns (use dayfirst=True — datasets use dd-mm-YYYY)
                date_cols = [col for col in df.columns if 'date' in col or 'time' in col]
                for col in date_cols:
                    # Suppress ambiguous parsing warnings from pandas for mixed formats
                    with warnings.catch_warnings():
                        warnings.filterwarnings('ignore', message='Parsing dates')
                        df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')

                # Table-specific column mappings (common differences between data and schema)
                mappings = {
                    'loans': {'branch': 'branch_name'},
                    'creditcards': {'branch': 'branch_name'}
                }
                if table_name in mappings:
                    df = df.rename(columns=mappings[table_name])

                # Align DataFrame columns with target table columns
                try:
                    pragma = self.cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
                    table_cols = [r[1] for r in pragma]
                    pk_cols = [r[1] for r in pragma if r[5] == 1]
                except Exception:
                    table_cols = list(df.columns)
                    pk_cols = []

                # Keep only columns that exist in the target table
                insert_cols = [c for c in df.columns if c in table_cols]
                df = df.loc[:, insert_cols]

                if df.empty:
                    print(f"No matching columns to insert into {table_name}.")
                    return

                # Best-effort: remove rows whose PK already exists (if PK is present both in df and table)
                try:
                    if pk_cols and pk_cols[0] in df.columns:
                        pk = pk_cols[0]
                        existing = pd.read_sql(f"SELECT {pk} FROM {table_name}", self.conn)[pk].astype(str)
                        df = df[~df[pk].astype(str).isin(existing)]
                except Exception:
                    pass

                if df.empty:
                    print(f"No new records to load into {table_name}.")
                    return

                # Use INSERT OR IGNORE to avoid halting on unique/constraint violations
                cols_sql = ", ".join(insert_cols)
                placeholders = ", ".join(["?" for _ in insert_cols])
                insert_sql = f"INSERT OR IGNORE INTO {table_name} ({cols_sql}) VALUES ({placeholders})"

                try:
                    # Insert in chunks to avoid huge single transactions
                    # Prepare rows, replacing NaN/NaT with None for sqlite
                    df_to_insert = df[insert_cols].copy()
                    df_to_insert = df_to_insert.where(pd.notnull(df_to_insert), None)
                    rows = [tuple(x) for x in df_to_insert.itertuples(index=False, name=None)]
                    chunk = 500
                    candidate_count = len(rows)
                    for i in range(0, candidate_count, chunk):
                        batch = rows[i:i+chunk]
                        self.cursor.executemany(insert_sql, batch)
                        self.conn.commit()
                    print(f"Loaded {candidate_count} candidate records into {table_name} (INSERT OR IGNORE).")
                except sqlite3.IntegrityError as e:
                    print(f"Skipping {table_name}: Data violates constraints: {e}")
                except Exception as e:
                    print(f"Error loading data into {table_name}: {e}")
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

    def clear_tables(self):
        """Delete all rows from known tables (does not drop table schema)."""
        tables = ["customers", "branches", "accounts", "transactions", "loans", "creditcards", "supporttickets"]
        for t in tables:
            try:
                self.cursor.execute(f"DELETE FROM {t}")
            except Exception as e:
                print(f"Error clearing {t}: {e}")
        self.conn.commit()
        print("All tables cleared.")

    def recreate_table_if_empty(self, table_name, create_sql):
        """If table exists and is empty (or doesn't exist), drop and recreate it using create_sql.
        This is safe for empty development DBs to change schema to better fit datasets.
        """
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            cnt = self.cursor.fetchone()[0]
        except Exception:
            cnt = 0
        if cnt == 0:
            try:
                self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                self.cursor.execute(create_sql)
                self.conn.commit()
                print(f"Recreated {table_name} with updated schema")
            except Exception as e:
                print(f"Failed to recreate {table_name}: {e}")

    def is_initialized(self):
        """Return True if any of the core tables contain rows."""
        tables = ["customers", "branches", "accounts"]
        for t in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {t}")
                if self.cursor.fetchone()[0] > 0:
                    return True
            except sqlite3.OperationalError:
                # Table does not exist yet
                continue
        return False

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
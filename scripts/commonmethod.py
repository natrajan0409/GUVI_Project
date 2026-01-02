"""Utilities for database access used across the project."""

from __future__ import annotations

import sqlite3
from typing import Optional, Sequence

import pandas as pd
from typing import List

DB_PATH: str = "Database/BankSight.db"

__all__ = [
    "DB_PATH",
    "get_connection",
    "run_query",
    "execute_action",
    "get_next_customer_id",
]

import random

def luhn_checksum(card_number: str) -> int:
    """Calculate Luhn checksum for a card number string."""
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(digits_of(d*2))
    return total % 10

def generate_card_number(prefix: str = "4", length: int = 16) -> str:
    """
    Generate a valid test credit card number.
    - prefix: starting digits (default '4' for Visa)
    - length: total length (default 16)
    """
    number = prefix
    while len(number) < (length - 1):
        number += str(random.randint(0, 9))
    # Calculate check digit
    check_digit = luhn_checksum(number + "0")
    if check_digit != 0:
        check_digit = 10 - check_digit
    return number + str(check_digit)

# Example usage:
print("Auto-generated CC number:", generate_card_number())

def to_float(val):
    """Safely converts any DB result to a float."""
    if hasattr(val, 'iloc'): # It's a DataFrame or Series
        return float(val.iloc[0, 0]) if val.ndim > 1 else float(val.iloc[0])
    if isinstance(val, list): # It's a list
        return float(val[0])
    return float(val)

def get_connection() -> sqlite3.Connection:
    """Return a sqlite3 connection to the project's database."""
    # Centralized connection point; check_same_thread=False used for multi-threaded contexts
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def run_query(query: str, params: Optional[Sequence] = None) -> pd.DataFrame:
    """Execute a SELECT query and return results as a DataFrame.

    Args:
        query: SQL query to execute.
        params: Optional sequence of parameters for parameterized queries.
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn, params=params)


def execute_action(query: any, params: Optional[Sequence] = None) -> None:
    """Execute an INSERT/UPDATE/DELETE statement and commit the transaction.
    
    Args:
        query: SQL statement to execute.
        params: Optional sequence of parameters for parameterized queries.
    """
    print(f"Executing query: {query}, params: {params}")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()


def get_next_customer_id() -> str:
    """Generate the next customer id using the existing highest `customer_id`.

    Expected format: 'CUS{number}', e.g. 'CUS101' or 'CUS520'.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT customer_id FROM customers ORDER BY customer_id DESC LIMIT 1"
        )
        result = cursor.fetchone()
        if result:
            last_id = result[0]
            # Extract numbers from 'CUS520' -> '520'
            number_part = int("".join(filter(str.isdigit, str(last_id)))) if last_id else 100
            print(f"Last Customer ID: {last_id}, Next Number Part: {number_part + 1}")
            return f"CUS{number_part + 1}"
        return "CUS101"
    
def get_customer_id_by_name(name: str) -> Optional[str]:
    """Fetch customer_id based on customer name.

    Args:
        name: Name of the customer.

    Returns:
        The customer_id if found, else None.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT customer_id FROM customers WHERE name = ?", (name,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
def get_branch_names() -> List[str]:
    """Fetch all branch names from the branches table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT branch_name FROM branches")
        results = cursor.fetchall()
        if not results:
            print("No branches found in database.")
            return []
        return [row[0] for row in results]


def get_account_by_customer_id(customer_id:any) -> List[str]:
    """Fetch all branch names from the branches table.

    Returns:
        A list of branch names.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT account_id FROM accounts WHERE customer_id = ?", (customer_id,))
        result = cursor.fetchone()
        return result[0] if result else None
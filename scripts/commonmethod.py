"""Utilities for database access used across the project."""

from __future__ import annotations

import sqlite3
from typing import Optional, Sequence

import pandas as pd

DB_PATH: str = "Database/BankSight.db"

__all__ = [
    "DB_PATH",
    "get_connection",
    "run_query",
    "execute_action",
    "get_next_customer_id",
]


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
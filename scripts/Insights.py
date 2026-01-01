"""Streamlit Insights page for BankSight Dashboard."""

from __future__ import annotations
import pandas as pd
import streamlit as st
from scripts.commonmethod import run_query
# Page Config
st.set_page_config(page_title="BankSight Dashboard", layout="wide")


class InsightsPage:
    def render(self, conn):
        st.title("BankSight Insights")
        st.write("Explore key insights from the banking data.")
        # Place your 15 questions logic here
        
        category = st.selectbox(
            "Select categories to explore",
            [
                "CUSTOMER & ACCOUNT ANALYSIS",
                "TRANSACTION BEHAVIOR",
                "LOAN INSIGHTS",
                "BRANCH & PERFORMANCE",
                "SUPPORT TICKETS & CUSTOMER EXPERIENCE",
            ],
        )

        if category == "CUSTOMER & ACCOUNT ANALYSIS":
            question = st.selectbox(
                "Select Questions to explore",
                [
                    "Q1: How many customers exist per city, and what is their average account balance?",
                    "Q2: Which account type (Savings, Current, Loan, etc.) holds the highest total balance?",
                    "Q3: Who are the top 10 customers by total account balance across all account types?",
                    "Q4: Which customers opened accounts in 2023 with a balance above ₹1,00,000?",
                ],
            )

            if question == "Q1: How many customers exist per city, and what is their average account balance?":
                query = """
                SELECT c.city, COUNT(c.customer_id) AS customer_count, AVG(a.account_balance) AS avg_balance
                FROM customers c
                JOIN accounts a ON c.customer_id = a.customer_id
                GROUP BY c.city
                ORDER BY customer_count DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

            elif question == "Q2: Which account type (Savings, Current, Loan, etc.) holds the highest total balance?":
                query = """
                SELECT cs.account_type, SUM(a.account_balance) AS total_balance
                FROM accounts a
                JOIN Customers cs ON cs.customer_id = a.customer_id
                GROUP BY cs.account_type
                ORDER BY total_balance DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

            elif question == "Q3: Who are the top 10 customers by total account balance across all account types?":
                query = """
                SELECT c.customer_id, c.name, SUM(a.account_balance) AS total_balance
                FROM customers c
                JOIN accounts a ON c.customer_id = a.customer_id
                GROUP BY c.customer_id, c.name
                ORDER BY total_balance DESC
                LIMIT 10;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

            elif question == "Q4: Which customers opened accounts in 2023 with a balance above ₹1,00,000?":
                query = """
                SELECT c.customer_id, c.name, a.account_id, a.account_balance, c.join_date
                FROM customers c
                JOIN accounts a ON c.customer_id = a.customer_id
                WHERE strftime('%Y', c.join_date) = '2023' AND a.account_balance > 100000
                ORDER BY a.account_balance DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

        elif category == "TRANSACTION BEHAVIOR":
            question = st.selectbox(
                "Select Questions to explore",
                [
                    "Q5: What is the total transaction volume (sum of amounts) by transaction type?",
                    "Q6: How many failed transactions occurred for each transaction type?",
                    "Q7: What is the total number of transactions per transaction type?",
                    "Q8: Which accounts have 5 or more high-value transactions above ₹20,000?",
                ],
            )

            if question == "Q5: What is the total transaction volume (sum of amounts) by transaction type?":
                query = """
                SELECT txn_type, SUM(amount) AS total_volume
                FROM transactions
                GROUP BY txn_type
                ORDER BY total_volume DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

            elif question == "Q6: How many failed transactions occurred for each transaction type?":
                query = """
                SELECT txn_type, COUNT(*) AS failed_count
                FROM transactions
                WHERE status = 'Failed'
                GROUP BY txn_type
                ORDER BY failed_count DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

            elif question == "Q7: What is the total number of transactions per transaction type?":
                query = """
                SELECT txn_type, COUNT(txn_type) AS total_count
                FROM transactions
                GROUP BY txn_type
                ORDER BY total_count DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

            elif question == "Q8: Which accounts have 5 or more high-value transactions above ₹20,000?":
                query = """
                SELECT account_id as account_number, COUNT(*) AS high_value_txn_count
                FROM transactions ts
                JOIN accounts ac ON ac.customer_id = ts.customer_id
                WHERE amount > 20000
                GROUP BY account_id
                HAVING high_value_txn_count >= 5
                ORDER BY high_value_txn_count DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")


        elif category == "LOAN INSIGHTS":
            question = st.selectbox(
                "Select Questions to explore",
                [
                    "Q9: What is the average loan amount and interest rate by loan type (Personal, Auto, Home, etc.)?",
                    "Q10: Which customers currently hold more than one active or approved loan?",
                    "Q11: Who are the top 5 customers with the highest outstanding (non-closed) loan amounts?",
                ],
            )

            if question == "Q9: What is the average loan amount and interest rate by loan type (Personal, Auto, Home, etc.)?":
                query = """
                SELECT loan_type, AVG(loan_amount) AS avg_loan_amount, AVG(interest_rate) AS avg_interest_rate
                FROM loans
                GROUP BY loan_type
                ORDER BY avg_loan_amount DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

            elif question == "Q10: Which customers currently hold more than one active or approved loan?":
                query = """
                SELECT c.customer_id, c.name, COUNT(l.loan_id) AS active_loan_count
                FROM customers c
                JOIN loans l ON c.customer_id = l.customer_id
                WHERE l.loan_status IN ('Active', 'Approved')
                GROUP BY c.customer_id, c.name
                HAVING COUNT(l.loan_id) > 1
                ORDER BY active_loan_count DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

            elif question == "Q11: Who are the top 5 customers with the highest outstanding (non-closed) loan amounts?":
                query = """
                SELECT
                    c.customer_id,
                    c.name,
                    SUM(l.loan_amount) AS total_outstanding
                FROM customers c
                JOIN loans l ON c.customer_id = l.customer_id
                GROUP BY c.customer_id, c.name
                ORDER BY total_outstanding DESC
                LIMIT 5;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

        elif category == "BRANCH & PERFORMANCE":
            question = st.selectbox(
                "Select Questions to explore",
                [
                    "Q12: What is the average loan amount per branch?",
                    "Q13: How many customers exist in each age group (e.g., 18–25, 26–35, etc.)?",
                ],
            )
            if question == "Q12: What is the average loan amount per branch?":
                query = """
                SELECT b.branch_name, AVG(l.loan_amount) AS avg_loan_amount
                FROM branches b
                JOIN loans l ON b.branch_name = l.branch
                GROUP BY b.branch_name
                ORDER BY avg_loan_amount DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")
            elif question == "Q13: How many customers exist in each age group (e.g., 18–25, 26–35, etc.)?":
                query = """
                SELECT 
                    CASE 
                        WHEN age BETWEEN 18 AND 25 THEN '18-25'
                        WHEN age BETWEEN 26 AND 35 THEN '26-35'
                        WHEN age BETWEEN 36 AND 45 THEN '36-45'
                        WHEN age BETWEEN 46 AND 55 THEN '46-55'
                        WHEN age BETWEEN 56 AND 65 THEN '56-65'
                        ELSE '66+'
                    END AS age_group,
                    COUNT(*) AS customer_count
                FROM customers
                GROUP BY age_group
                ORDER BY age_group;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

        elif category == "SUPPORT TICKETS & CUSTOMER EXPERIENCE":
            question = st.selectbox(
                "Select Questions to explore",
                [
                    "Q14: Which issue categories have the longest average resolution time?",
                    "Q15: Which support agents have resolved the most critical tickets with high customer ratings (≥4)?",
                ],
            )
            if question == "Q14: Which issue categories have the longest average resolution time?":
                query = """
                SELECT issue_category, AVG(julianday(date_closed) - julianday(date_opened)) AS avg_resolution_time
                FROM supporttickets
                GROUP BY issue_category
                ORDER BY avg_resolution_time DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")
            elif question == "Q15: Which support agents have resolved the most critical tickets with high customer ratings (≥4)?":
                query = """
                SELECT support_agent, COUNT(*) AS high_rating_tickets
                FROM supporttickets
                WHERE priority = 'High' AND customer_rating >= 4 AND status = 'Closed'
                GROUP BY support_agent
                HAVING COUNT(*) > 1
                ORDER BY high_rating_tickets DESC;
                """
                try:
                    df = run_query(query)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")
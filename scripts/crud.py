
import streamlit as st
from scripts.commonmethod import run_query

# Import handlers
from scripts.crud_handlers import customers, branches, accounts, transactions, loans, creditcards

class CRUDOperationsPage:       
    def render(self, conn):
        st.title("🛠️ CRUD Operations")
        st.write("Perform Create, Read, Update, and Delete operations.")

        # Whitelisted tables
        valid_tables = ["customers", "branches", "accounts", "transactions", "loans", "creditcards"]
        
        operation = st.selectbox("Select Operation", ["Create", "Read", "Update", "Delete"])
        table_name = st.selectbox("Select Table", valid_tables)
        
        if table_name not in valid_tables:
            st.error("Invalid table selection.")
            return

        if operation == "Create":
            if table_name == "customers": customers.create_customer()
            elif table_name == "branches": branches.create_branch()
            elif table_name == "accounts": accounts.create_account()
            elif table_name == "transactions": transactions.create_transaction()
            elif table_name == "loans": loans.create_loan()
            elif table_name == "creditcards": creditcards.create_creditcard()
            
        elif operation == "Read":
            self.handle_read(table_name)
            
        elif operation == "Update":
            if table_name == "customers": customers.update_customer()
            elif table_name == "branches": branches.update_branch()
            elif table_name == "accounts": accounts.update_account()
            elif table_name == "transactions": transactions.update_transaction()
            elif table_name == "loans": loans.update_loan()
            elif table_name == "creditcards": creditcards.update_creditcard()
            
        elif operation == "Delete":
            if table_name == "customers": customers.delete_customer()
            elif table_name == "branches": branches.delete_branch()
            elif table_name == "accounts": accounts.delete_account()
            elif table_name == "transactions": transactions.delete_transaction()
            elif table_name == "loans": loans.delete_loan()
            elif table_name == "creditcards": creditcards.delete_creditcard()

    def handle_read(self, table_name):
        st.subheader(f"Read records from {table_name}")
        try:
            # table_name is whitelisted above
            df = run_query(f"SELECT * FROM {table_name}")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to read from {table_name}: {e}")
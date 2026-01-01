import streamlit as st
import sqlite3
import pandas as pd
import datetime
import pandas as pd

# Page Config
st.set_page_config(page_title="BankSight Dashboard", layout="wide")

# Function to generate custom_id 
def get_next_customer_id(cursor):
    # Fetch the last ID to continue the sequence (e.g., CUS520 -> CUS521)
    cursor.execute("SELECT customer_id FROM customers ORDER BY customer_id DESC LIMIT 1")
    result = cursor.fetchone()
    if result:
        # Extract the number, increment it, and format it back
        last_id = result[0]
        number_part = int(''.join(filter(str.isdigit, last_id)))
        return f"C{number_part + 1}"
    return "C01" # Fallback for empty table


# function to get cusomter id based on  user selected customer name
def get_customer_id_by_name(cursor, name):
    cursor.execute("SELECT customer_id FROM customers WHERE name = ?", (name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def run_query(query, params=None):
    """Run a SQL query using a fresh SQLite connection and return a DataFrame."""
    try:
        with sqlite3.connect("Database/BankSight.db", check_same_thread=False) as conn_local:
            if params:
                return pd.read_sql(query, conn_local, params=params)
            return pd.read_sql(query, conn_local)
    except Exception:
        # Re-raise so callers can handle and display friendly messages
        raise

# Sidebar Navigation

st.sidebar.title("BankSight Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📊 Data Explorer", "🧠 Insights","💰 CRUD Operations"])

if page == "🏠 Home":
    st.title("Welcome to BankSight")
    st.write("Data successfully loaded. Use the sidebar to explore.")
    
    st.write("### Database Row Counts")
    for table in ["customers", "branches", "accounts", "transactions"]:
        try:
            count = run_query(f"SELECT COUNT(*) FROM {table}").iloc[0,0]
        except Exception:
            count = 0
        st.metric(label=table.capitalize(), value=count)

elif page == "📊 Data Explorer":
    st.title("Raw Data Viewer")
    # Dynamically list tables from the SQLite DB to avoid hardcoding
    try:
        tables = run_query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")['name'].tolist()
    except Exception:
        tables = ["customers", "branches", "accounts", "transactions"]

    table_name = st.selectbox("Select Table", tables)

    if table_name:
        try:
            df = run_query(f"SELECT * FROM {table_name} LIMIT 100")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load table {table_name}: {e}")

elif page == "🧠 Insights":
    st.title("BankSight Insights")
    st.write("Explore key insights from the banking data.")

    category = st.selectbox("Select categories to explore", ["CUSTOMER & ACCOUNT ANALYSIS", "TRANSACTION BEHAVIOR", "LOAN INSIGHTS", "BRANCH & PERFORMANCE", "SUPPORT TICKETS & CUSTOMER EXPERIENCE"])

    if category == "CUSTOMER & ACCOUNT ANALYSIS":
        question = st.selectbox("Select Questions to explore", [
            "Q1: How many customers exist per city, and what is their average account balance?",
            "Q2: Which account type (Savings, Current, Loan, etc.) holds the highest total balance?",
            "Q3: Who are the top 10 customers by total account balance across all account types?",
            "Q4: Which customers opened accounts in 2023 with a balance above ₹1,00,000?",
        ])

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
			join Customers cs on( cs.customer_id= a.customer_id)
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
        question = st.selectbox("Select Questions to explore", [
            "Q5: What is the total transaction volume (sum of amounts) by transaction type?",
            "Q6: How many failed transactions occurred for each transaction type?",
            "Q7: What is the total number of transactions per transaction type?",
            "Q8: Which accounts have 5 or more high-value transactions above ₹20,000?",
        ])

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
			join accounts  ac on(ac.customer_id=ts.customer_id) 
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
        question = st.selectbox("Select Questions to explore", [
            "Q9: What is the average loan amount and interest rate by loan type (Personal, Auto, Home, etc.)?",
            "Q10: Which customers currently hold more than one active or approved loan?",
            "Q11: Who are the top 5 customers with the highest outstanding (non-closed) loan amounts?",
        ])

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
JOIN loans l 
    ON c.customer_id = l.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_outstanding DESC
LIMIT 5;            """
            try:
                df = run_query(query)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Query failed: {e}")

    elif category == "BRANCH & PERFORMANCE":
        question = st.selectbox("Select Questions to explore", ["Q12: What is the average loan amount per branch?","Q13: How many customers exist in each age group (e.g., 18–25, 26–35, etc.)?"])
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
        question = st.selectbox("Select Questions to explore", ["Q14: Which issue categories have the longest average resolution time?","Q15: Which support agents have resolved the most critical tickets with high customer ratings (≥4)?"])
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

    st.title("CRUD Operations")

    
elif page == "CRUD Operations":
    st.title("CRUD Operations")
    st.write("Perform Create, Read, Update, and Delete operations.")

    operation = st.selectbox("Select Operation", ["Create", "Read", "Update", "Delete"])
    table_name = st.selectbox("Select Table", ["customers", "branches", "accounts", "transactions"])
if operation == "Create":
    st.subheader(f"Create a new record in {table_name}")

    if table_name == "customers":
        with sqlite3.connect("Database/BankSight.db") as conn_local:
            custom_id = get_next_customer_id(conn_local.cursor())

        with st.form("customer_form"):
            st.info(f"New Customer ID: {custom_id}")
            name = st.text_input("Name")
            gender = st.selectbox("Gender", ["M", "F", "O"])
            age = st.number_input("Age", min_value=18)
            city = st.text_input("City")
            account_type = st.selectbox("Account Type", ["Savings", "Current", "Premium"])
            join_date = datetime.date.today().strftime('%Y-%m-%d')
            submit_button = st.form_submit_button("Add Customer")

        if submit_button:
            if not name:
                st.error("Name is required!")
            else:
                try:
                    with sqlite3.connect("Database/BankSight.db") as conn_local:
                        conn_local.execute(
                            "INSERT INTO customers (customer_id, name, gender, age, city, account_type, join_date) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                            (custom_id, name, gender, age, city, account_type, join_date)
                        )
                        conn_local.commit()
                    st.success(f"Customer {name} added successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Failed to add customer: {e}")

    elif table_name == "branches":
        with st.form("branch_form"):
            branch_name = st.text_input("Branch Name")
            city = st.text_input("City")
            manager_name = st.text_input("Manager Name")
            total_employees = st.number_input("Total Employees", min_value=1)
            branch_revenue = st.number_input("Branch Revenue", min_value=0)
            opening_date = datetime.date.today().strftime('%Y-%m-%d')
            performance_rating = st.number_input("Performance Rating", min_value=1, max_value=5)
            submit_button = st.form_submit_button("Add Branch")

        if submit_button:
            if not branch_name:
                st.error("Branch Name is required!")
            else:
                try:
                    with sqlite3.connect("Database/BankSight.db") as conn_local:
                        conn_local.execute(
                            "INSERT INTO branches (branch_name, city, manager_name, total_employees, branch_revenue, opening_date, performance_rating) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                            (branch_name, city, manager_name, total_employees, branch_revenue, opening_date, performance_rating)
                        )
                        conn_local.commit()
                    st.success(f"Branch {branch_name} added successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Failed to add branch: {e}")
    elif table_name == "accounts":
        with sqlite3.connect("Database/BankSight.db") as conn_local:
            customer = run_query("SELECT name FROM customers")['name'].tolist()
        with st.form("account_form"):
            st.subheader("Select Customer") 
            customer_names = customer
            selected_name = st.selectbox("Customer Name", customer_names)
            customer_id = get_customer_id_by_name(conn_local.cursor(), selected_name)
            account_balance = st.number_input("Account Balance", min_value=0)
            open_date = datetime.date.today().strftime('%Y-%m-%d')
            submit_button = st.form_submit_button("Add Account")

        if submit_button:
            if not customer_id:
                st.error("Customer ID is required!")
            else:
                try:
                    with sqlite3.connect("Database/BankSight.db") as conn_local:
                        conn_local.execute(
                            "INSERT INTO accounts (customer_id,account_balance, last_updated) VALUES (?, ?, ?)", 
                            (customer_id,  account_balance, open_date)
                        )
                        conn_local.commit()
                    st.success(f"Account for Customer ID {customer_id} added successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Failed to add account: {e}")            

    elif table_name == "transactions":
        with sqlite3.connect("Database/BankSight.db") as conn_local:
            customer_names = run_query("SELECT name FROM customers")['name'].tolist()

        with st.form("transaction_form"):
            st.subheader("Select Customer")
            selected_name = st.selectbox("Customer Name", customer_names)

    # Account selection
            customer_id = get_customer_id_by_name(conn_local.cursor(), selected_name)
            select_account = run_query("SELECT account_id FROM accounts WHERE customer_id = ?", (customer_id,))['account_id'].tolist()
            account = st.selectbox("Select Account", select_account)
            bankbalance = run_query("SELECT account_balance FROM accounts WHERE account_id = ?", (account,)).iloc[0,0]
            st.info(f"Current Account Balance: ₹{bankbalance}")

    # Transaction details
            status = st.selectbox("Transaction Status", ["Success", "Failed", "Pending"])
            txn_type = st.selectbox("Transaction Type", ["Deposit", "Withdrawal", "Transfer"])
            amount = st.number_input("Transaction Amount", min_value=1)

    # ✅ Submit button must be inside the form
            submit_button = st.form_submit_button("Add Transaction")


        if submit_button:
          with sqlite3.connect("Database/BankSight.db") as conn:
           cursor = conn.cursor()
           cursor.execute("SELECT account_balance, customer_id FROM accounts WHERE account_id = ?", (account,))
        record = cursor.fetchone()

        if record:
            current_balance, cust_id = record
            
            # Use a boolean flag instead of 'return'
            is_valid = True
            if txn_type == "Debit":
                if (current_balance - amount) < 1000:
                    st.error(f"Transaction Denied! Minimum balance of ₹1,000 required. Current: ₹{current_balance}")
                    is_valid = False
                else:
                    new_balance = current_balance - amount
            else:
                new_balance = current_balance + amount

            if is_valid: # Only run this if the check passed
                try:
                    # Update Account
                    cursor.execute("UPDATE accounts SET account_balance = ? WHERE account_id = ?", (new_balance, acc_id))
                    
                    # Log Transaction
                    new_txn_id = f"T{int(datetime.datetime.now().timestamp())}" # Shorter ID
                    cursor.execute("""
                        INSERT INTO transactions (txn_id, customer_id, txn_type, amount, txn_time, status) 
                        VALUES (?, ?, ?, ?, ?, ?)""", 
                        (new_txn_id, cust_id, txn_type, amount, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Success'))
                    
                    conn.commit() # Save both
                    st.success(f"Success! New Balance: ₹{new_balance:.2f}")
                    st.balloons()
                except Exception as e:
                    st.error(f"Database Error: {e}")
        else:
            st.error("Account ID not found.")


            

    elif operation == " 👁️ Read":
        st.subheader(f"Read records from {table_name}")
        try:
            df = run_query(f"SELECT * FROM {table_name} LIMIT 100")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to read from {table_name}: {e}")

    elif operation == " ✏️ Update":
        st.subheader(f"Update a record in {table_name}")
        record_id = st.text_input("Record ID to update")
        new_value = st.text_input("New Value (for demonstration)")
        if st.button("Update Record"):
            try:
                with sqlite3.connect("Database/BankSight.db", check_same_thread=False) as conn_local:
                    conn_local.execute(f"UPDATE {table_name} SET name = ? WHERE id = ?", (new_value, record_id))
                    conn_local.commit()
                st.success("Record updated successfully!")
            except Exception as e:
                st.error(f"Failed to update record: {e}")

    elif operation == " 🗑️ Delete":
        st.subheader(f"Delete a record from {table_name}")
        record_id = st.text_input("Record ID to delete")
        if st.button("Delete Record"):
            try:
                with sqlite3.connect("Database/BankSight.db", check_same_thread=False) as conn_local:
                    conn_local.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
                    conn_local.commit()
                st.success("Record deleted successfully!")
            except Exception as e:
                st.error(f"Failed to delete record: {e}")
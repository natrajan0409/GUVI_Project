import streamlit as st
import sqlite3
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
# Import correctly from your centralized method file
from scripts.commonmethod import execute_action, generate_card_number, get_account_by_customer_id, get_next_customer_id, get_customer_id_by_name, run_query,to_float,get_branch_names

# Page Config
st.set_page_config(page_title="BankSight Dashboard", layout="wide")

class CRUDOperationsPage:       
    def render(self,conn):
        st.title("🛠️ CRUD Operations")
        st.write("Perform Create, Read, Update, and Delete operations.")

        operation = st.selectbox("Select Operation", ["Create", "Read", "Update", "Delete"])
        table_name = st.selectbox("Select Table", ["customers", "branches", "accounts", "transactions","loans","creditcards"])
        if operation == "Create":
            self.handle_create(table_name)
        elif operation == "Read":
            self.handle_read(table_name)
        elif operation == "Update":
            self.handle_update(table_name)
        elif operation == "Delete":
            self.handle_delete(table_name)  
    
    
    def handle_create(self, table_name):
        if table_name == "customers":
            with sqlite3.connect("Database/BankSight.db") as conn_local:
                custom_id = get_next_customer_id()
                print(f"Generated Customer ID: {custom_id}")

            with st.form("customer_form"):
                st.info(f"New Customer ID: {custom_id}")
                name = st.text_input("Name")
                gender = st.selectbox("Gender", ["M", "F", "O"])
                age = st.number_input("Age", min_value=18)
                city = st.text_input("City")
                PhNo=st.number_input("Phone Number", min_value=1000000000, max_value=9999999999)
                account_type = st.selectbox("Account Type", ["Savings", "Current", "Premium"])
                join_date = datetime.date.today().strftime('%Y-%m-%d')
                submit_button = st.form_submit_button("Add Customer")
            if submit_button:
                if not name:
                    st.error("Name is required!")
                else:
                    try:
                        with sqlite3.connect("Database/BankSight.db") as conn_local:
                            cursor = conn_local.cursor()
                            # Check if name + phone already exists
                            cursor.execute(
                                "SELECT 1 FROM customers WHERE name = ? AND Phnumber = ? AND account_type = ?",
                                (name, PhNo,account_type)   # <-- make sure you capture phnumber from form
                            )
                            exists = cursor.fetchone()

                            if exists:
                                st.error("This name + phone + account_type combination already exists!")
                            else:
                                cursor.execute(
                                    "INSERT INTO customers (customer_id, name, Phnumber, gender, age, city, account_type, join_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                    (custom_id, name, PhNo, gender, age, city, account_type, join_date)
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

        elif table_name == "loans":
            with sqlite3.connect("Database/BankSight.db") as conn_local:
                customer = run_query("SELECT name FROM customers")['name'].tolist()
                st.subheader("Select Customer")
                customer_names = customer
                selected_name = st.selectbox("Customer Name", customer_names)
                customer_id = get_customer_id_by_name(selected_name)
            with st.form("loan_form"):

                accunt = run_query("SELECT account_id FROM accounts WHERE customer_id = ?", (customer_id,))['account_id'].tolist()
                print(f"Selected Customer ID for Loans: {customer_id},{accunt}")
                st.subheader("Select Account")
                selected_account = st.selectbox("Account ID", accunt)
                branch = run_query("SELECT branch_name FROM branches")['branch_name'].tolist()
                st.subheader("Select Branch")
                selected_branch = st.selectbox("Branch Name", branch)
                loan_amount = st.number_input("Loan Amount", min_value=0)
                interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, format="%.2f")
                loan_type = st.selectbox("loan_type", ["Personal", "Auto", "Home", "Business", "Loan Against Property", "Education"])
                loan_status = st.selectbox("loan_status", ["Active", "Inactive","Closed", "Defaulted"])
                loan_duration_months = st.number_input("Loan Duration (Months)", min_value=1)
                start_date = datetime.date.today().strftime('%Y-%m-%d')
                submit_button = st.form_submit_button("Add Loan")

            if submit_button:
                if not customer_id:
                    st.error("Customer ID is required!")
                else:
                    try:
                        with sqlite3.connect("Database/BankSight.db") as conn_local:
                            conn_local.execute(
                                "INSERT INTO loans (customer_id,branch, loan_amount, account_id, interest_rate, loan_type, loan_status,loan_term_months, start_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (customer_id, selected_branch, loan_amount, selected_account, interest_rate, loan_type, loan_status, loan_duration_months, start_date)
                            )
                            conn_local.commit()
                        st.success(f"Loan for Customer ID {customer_id} added successfully!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Failed to add loan: {e}")
                
        elif table_name == "accounts":
            with sqlite3.connect("Database/BankSight.db") as conn_local:
                customer = run_query("SELECT name FROM customers")['name'].tolist()
            with st.form("account_form"):
                st.subheader("Select Customer")
                customer_names = customer
                selected_name = st.selectbox("Customer Name", customer_names)
                customer_id = get_customer_id_by_name(selected_name)
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
                                (customer_id, account_balance, open_date)
                            )
                            conn_local.commit()
                        st.success(f"Account for Customer ID {customer_id} added successfully!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Failed to add account: {e}")

        elif table_name == "transactions":
            with sqlite3.connect("Database/BankSight.db") as conn_local:
                T_customer= run_query("SELECT name FROM customers")['name'].tolist()
                st.subheader("Select Customer")
                selected_name = st.selectbox("Customer Name", T_customer)
                print(f"Selected Customer name for Transactions: {selected_name}")
                txn_type = st.selectbox("Transaction Type", ["Deposit", "Withdrawal", "Transfer", "loan Payment", "Debit", "Credit payment"])
                if txn_type == "loan Payment" or txn_type == "Credit payment":
                    st.info("Note: Transcation status will be set to 'Pending' for loan and credit payments. staff will verify and update accordingly.")
                with st.form("transaction_form"):
                    
                    cursor = conn_local.cursor()
                    customer_id = get_customer_id_by_name(selected_name)
                    run_query("SELECT customer_id FROM customers WHERE name = ?", (selected_name,))
                    print(f"Selected Customer ID for Transactions: {customer_id}")

                    select_account = run_query(
                        "SELECT account_id FROM accounts WHERE customer_id = ?", (customer_id,)
                    )['account_id'].tolist()
                    account = st.selectbox("Select Account", select_account)

                    bankbalance = run_query(
                        "SELECT account_balance FROM accounts WHERE account_id = ?", (account,)
                    ).iloc[0, 0]
                    st.info(f"Current Account Balance: ₹{bankbalance}")

                    # Transaction details
                    if txn_type == "loan Payment":
                       try:
                            Loanoutstanding = run_query(
                                "SELECT loan_amount FROM loans WHERE customer_id = ?", (customer_id,)
                            ).iloc[0, 0]
                       except Exception as e:  
                           Loanoutstanding = 0
                           if Loanoutstanding == 0:
                               st.warning("No loan found for this customer.")
                           else:
                                st.info(f"Current Loan Outstanding: ₹{Loanoutstanding}")
                                status = st.selectbox("Transaction Status", ["Pending"],disabled=True)
                    elif txn_type == "Credit payment":
                        try:
                            creditcard_due = run_query(
                                "SELECT current_balance  FROM creditcards WHERE customer_id = ?", (customer_id,)
                            ).iloc[0, 0]
                        except Exception as e:
                            creditcard_due = 0
                            if creditcard_due == 0:
                                st.warning("No credit card found for this customer.")
                            else:
                                st.info(f"Current Credit Card Due: ₹{creditcard_due}")
                                status = st.selectbox("Transaction Status", ["Pending"],disabled=True)                       
                    else:
                        status = st.selectbox("Transaction Status", ["Success", "Failed", "Pending"])
                    amount = st.number_input("Transaction Amount", min_value=1)

                    # ✅ Submit button INSIDE the form
                    submit_button = st.form_submit_button("Add Transaction")

            if submit_button:
                with sqlite3.connect("Database/BankSight.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT account_balance, customer_id FROM accounts WHERE account_id = ?", (account,))
                record = cursor.fetchone()

                if record:
                    current_balance, T_customer = record

                    # Use a boolean flag instead of 'return'
                    is_valid = True
                    if txn_type == "Debit":  # Assuming "Debit" is intended for withdrawals/transfers from account
                        if (current_balance - amount) < 1000:
                            st.error(f"Transaction Denied! Minimum balance of ₹1,000 required. Current: ₹{current_balance}")
                            is_valid = False
                        else:
                            new_balance = current_balance - amount
                    elif txn_type == "loan Payment":
                        new_balance = current_balance + amount

                    elif txn_type == "Withdrawal" or txn_type == "Transfer":
                        if (current_balance - amount) < 1000:
                            st.error(f"Transaction Denied! Minimum balance of ₹1,000 required. Current: ₹{current_balance}")
                            is_valid = False
                        else:
                            new_balance = current_balance - amount
                    else: # Deposit
                        new_balance = current_balance + amount

                    if is_valid:  # Only run this if the check passed
                        # Update Account
                        if status != "success" and status != "Success":
                            new_txn_id = f"T{int(datetime.datetime.now().timestamp())}"  # Shorter ID
                            cursor.execute("""
                                    INSERT INTO transactions (txn_id, customer_id, txn_type, amount, txn_time, status)
                                    VALUES (?, ?, ?, ?, ?, ?)""",
                                    (new_txn_id, customer_id, txn_type, amount, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status))

                            conn.commit() 
                            st.success(f"Transaction logged with status {status}. No balance update.")
                            st.balloons()
                        elif txn_type == "loan Payment" or txn_type == "Credit payment":
                            try:
                                # Log Transaction
                                new_txn_id = f"T{int(datetime.datetime.now().timestamp())}"  # Shorter ID
                                cursor.execute("""
                                    INSERT INTO transactions (txn_id, customer_id, txn_type, amount, txn_time, status)
                                    VALUES (?, ?, ?, ?, ?, ?)""",
                                    (new_txn_id, customer_id, txn_type, amount, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status))

                                conn.commit()  # Save both
                                st.success(f"Success! New Balance: ₹{new_balance:.2f}")
                                st.balloons()
                            except Exception as e:
                                st.error(f"Database Error: {e}")
                        else:
                         try:
                                # Update Account
                                cursor.execute("UPDATE accounts SET account_balance = ? WHERE account_id = ?", (new_balance, account))

                                # Log Transaction
                                new_txn_id = f"T{int(datetime.datetime.now().timestamp())}"  # Shorter ID
                                cursor.execute("""
                                    INSERT INTO transactions (txn_id, customer_id, txn_type, amount, txn_time, status)
                                    VALUES (?, ?, ?, ?, ?, ?)""",
                                    (new_txn_id, customer_id, txn_type, amount, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status))

                                conn.commit()  # Save both
                                st.success(f"Success! New Balance: ₹{new_balance:.2f}")
                                st.balloons()
                         except Exception as e:
                                st.error(f"Database Error: {e}")
                else:
                    st.error("Account ID not found.")
        elif table_name == "creditcards":
            with sqlite3.connect("Database/BankSight.db") as conn_local:
                customer = run_query("SELECT name FROM customers")['name'].tolist()
                customer_names = customer
                selected_name = st.selectbox("Customer Name", customer_names)
                
            with st.form("creditcard_form"):
                st.subheader("Select Customer")
                customer_id = get_customer_id_by_name(selected_name)
                accounts = get_account_by_customer_id(customer_id)
                branch_names = get_branch_names()
                branch = st.selectbox("Select Branch", branch_names)
                selected_account = st.selectbox("Select Account", accounts)
                if 'temp_card_number' not in st.session_state:
                 st.session_state.temp_card_number = generate_card_number()
                card_number = st.text_input("Credit Card Number", st.session_state.temp_card_number, disabled=True)
                card_type = st.selectbox("Card Type", ["Business", "Platinum", "Gold", "Silver", "Bronze"])
                card_network = st.selectbox("Card Network", ["Visa", "MasterCard", "American Express", "Discover"])
                credit_limit = st.number_input("Credit Limit", min_value=0)
                current_balance = 0.0
                issue_date_obj = datetime.date.today()
                expiry_date_obj = issue_date_obj + relativedelta(years=15)
                issue_date = issue_date_obj.strftime('%Y-%m-%d')
                expiry_date = expiry_date_obj.strftime('%Y-%m-%d')
                status = st.selectbox("Card Status", ["Active", "Inactive", "Blocked"])
                submit_button = st.form_submit_button("Add Credit Card")

            if submit_button:
                if not customer_id:
                    st.error("Customer ID is required!")
                else:
                    try:
                        with sqlite3.connect("Database/BankSight.db") as conn_local:
                            conn_local.execute(
                                """INSERT INTO creditcards 
                                (branch, customer_id, account_id, card_number, card_type, card_network, 
                                    credit_limit, current_balance, issued_date, expiry_date, status) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (branch, customer_id, selected_account, card_number, card_type, card_network,
                                credit_limit, current_balance, issue_date, expiry_date, status)
                            )
                            conn_local.commit()
                        st.success(f"Credit Card for Customer ID {customer_id} added successfully!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Failed to add credit card: {e}")
    def handle_read(self, table_name):
        st.subheader(f"Read records from {table_name}")
        try:
            df = run_query(f"SELECT * FROM {table_name}")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to read from {table_name}: {e}")

    def handle_update(self, table_name):
        st.subheader(f"Update a record in {table_name}")
        if table_name == "customers":
             with sqlite3.connect("Database/BankSight.db") as conn_local:
                T_customer= run_query("SELECT name FROM customers")['name'].tolist()
                st.subheader("Select Customer")
                selected_name = st.selectbox("Customer Name", T_customer)
                print(f"Selected Customer name for Transactions: {selected_name}")
                record = run_query("SELECT * FROM customers WHERE name = ?", (selected_name,))
                if record.empty:
                    st.error("Customer not found!")
                    return
                record_id = record.iloc[0]['customer_id']
                gender = st.selectbox("Gender", ["M", "F", "O"])
                age = st.number_input("Age", min_value=18)
                city = st.text_input("City")
                account_type = st.selectbox("Account Type", ["Savings", "Current", "Premium"])
                join_date = datetime.date.today().strftime('%Y-%m-%d')
            
             if st.button("Update customers Record"):

                try:
                    with sqlite3.connect("Database/BankSight.db", check_same_thread=False) as conn_local:
                        conn_local.execute(f"UPDATE {table_name} SET name = ?, gender = ?, age = ?, city = ?, account_type = ?, join_date = ? WHERE customer_id = ?", (selected_name, gender, age, city, account_type, join_date, record_id))
                        conn_local.commit()
                    st.success("Record updated successfully!")
                except Exception as e:
                 st.error(f"Failed to update record: {e}")    

        elif table_name == "branches":
            # 1. Selection happens OUTSIDE the form to fetch current data
            branch_names = run_query("SELECT branch_name FROM branches")['branch_name'].tolist()
            selected_branch_name = st.selectbox("Select Branch to Update", branch_names)
            
            # 2. Fetch current record to pre-fill the form
            record = run_query("SELECT * FROM branches WHERE branch_name = ?", (selected_branch_name,))
            
            if not record.empty:
                row = record.iloc[0]
                branch_id = row['branch_id'] # Keep this hidden for the WHERE clause

                # 3. Use a form to capture the new values
                with st.form("update_branch_form"):
                    st.subheader(f"Editing Branch: {selected_branch_name} (ID: {branch_id})")
                    
                    new_name = st.text_input("Branch Name", value=row['branch_name'])
                    new_city = st.text_input("City", value=row['city'])
                    new_manager = st.text_input("Manager Name", value=row['manager_name'])
                    new_emp = st.number_input("Total Employees", min_value=1, value=int(row['total_employees']))
                    new_rev = st.number_input("Branch Revenue", min_value=0.0, value=float(row['branch_revenue']))
                    try:
                        # Assuming your DB format is YYYY-MM-DD
                        current_date_obj = datetime.datetime.strptime(row['opening_date'], '%Y-%m-%d').date()
                    except:
                        # Fallback to today if the DB date is empty or corrupted
                        current_date_obj = datetime.date.today()
                    new_date_val = st.date_input("Opening Date", value=current_date_obj)
                    new_date = new_date_val.strftime('%Y-%m-%d')
                    new_rating = st.slider("Performance Rating", 1, 5, value=int(row['performance_rating']))
                    
                    submit_update = st.form_submit_button("Update Branch Details")

                # 4. Process the Update
                if submit_update:
                    try:
                       with sqlite3.connect("Database/BankSight.db", check_same_thread=False) as conn_local:
                           conn_local.execute("""UPDATE branches 
                               SET branch_name=?, city=?, manager_name=?, total_employees=?, 
                                branch_revenue=?, opening_date=?, performance_rating=? 
                                WHERE branch_id=?""",
                                (new_name, new_city, new_manager, int(new_emp), float(new_rev), new_date, int(new_rating), int(branch_id)))
                           conn_local.commit()
                       st.success(f"Branch '{new_name}' updated successfully!")
                       st.balloons()
                    except Exception as e:
                        st.error(f"Failed to update record: {e}")   
            else:
                st.warning("Branch details could not be retrieved.")

        elif table_name == "accounts":
          # 1. Selection happens OUTSIDE the form to fetch current data
            accounts = run_query("SELECT customer_id FROM accounts")['customer_id'].tolist()
            selected_account = st.selectbox("Select Account to Update", accounts)
            
            # 2. Fetch current record to pre-fill the form
            record = run_query("SELECT * FROM accounts WHERE customer_id = ?", (selected_account,))
            
            if not record.empty:
                row = record.iloc[0]
                account_id = row['account_id'] # Keep this hidden for the WHERE clause
                with st.form("update_account_form"):
                    st.subheader(f"Editing Account for Customer ID: {selected_account} (Account ID: {account_id})")
                    
                    new_balance = st.number_input("Account Balance", min_value=0.0, value=float(row['account_balance']))
                    new_date = datetime.date.today().strftime('%Y-%m-%d')
                    
                    submit_update = st.form_submit_button("Update Account Details")

                # 4. Process the Update
                if submit_update:
                    try:
                       with sqlite3.connect("Database/BankSight.db", check_same_thread=False) as conn_local:
                           conn_local.execute("""UPDATE accounts 
                               SET account_balance=?, last_updated=? 
                                WHERE account_id=?""",
                                (float(new_balance), new_date, int(account_id)))
                           conn_local.commit()
                       st.success(f"Account for Customer ID '{selected_account}' updated successfully!")
                       st.balloons()
                    except Exception as e:
                        st.error(f"Failed to update record: {e}")
            else:
                st.warning("Account details could not be retrieved.")

        elif table_name == "transactions":
        
            with sqlite3.connect("Database/BankSight.db") as conn_local:
                st.info("Only 'Failed' and 'Pending' transactions can be updated.,If selected  customer does not have any faile transaction then no data will be shown")
                T_customer= run_query("SELECT name FROM customers")['name'].tolist()
                st.subheader("Select Customer")
                selected_name = st.selectbox("Customer Name", T_customer)
                result =run_query("SELECT * FROM transactions WHERE customer_id = (SELECT customer_id FROM customers WHERE name = ?) AND status IN ('Failed', 'Pending')",
                         (selected_name,))
                Tran_id = result['txn_id'].tolist()
                selected_txn = st.selectbox("Select Transaction ID", Tran_id)
                print(f"Selected Transaction ID for Update: {selected_txn}")
                trx_type=result['txn_type'].tolist()
                trx_type = trx_type[0] if trx_type else None
                print(f"Selected Transaction Type for Update: {trx_type}")
                customer_id = get_customer_id_by_name(selected_name)
                loan_id =run_query("SELECT loan_id FROM loans WHERE customer_id = ? ", (customer_id,))['loan_id'].tolist()
                loan_id = loan_id[0] if loan_id else None
                if selected_txn:
                    # 1. Fetch all previous data AND the account_id associated with this txn
                    old_txn = run_query(
                        "SELECT status, txn_type, amount,txn_id,customer_id FROM transactions WHERE txn_id = ?", 
                        (selected_txn,)
                    ) 

                    if not old_txn.empty:
                        row = old_txn.iloc[0]
                        old_status, old_type, old_amount, associated_account ,customer_id = row['status'], row['txn_type'], row['amount'], row['txn_id'],row['customer_id']
                        print(f"Fetched Transaction - Status: {old_status}, Type: {old_type}, Amount: {old_amount}, Account: {associated_account}")    
                        current_loan_balance = run_query("SELECT loan_amount FROM loans WHERE customer_id = ?", (customer_id,))['loan_amount'].tolist()
                        current_loan_balance = current_loan_balance[0]
                        with st.form("transaction_update_form"):
                # Pre-fill with current DB values
                            new_status = st.selectbox("Update Status", ["Success", "Failed", "Pending"], 
                                                    index=["Success", "Failed", "Pending"].index(old_status))
                            st.text(f"Transaction amount: {old_amount} (Unchangeable)")
                            new_amount = st.number_input("Adjust Amount", min_value=1.0, value=float(old_amount))
                            submit_button = st.form_submit_button(" Update Changes")

                        if submit_button:
                            print(f" after submmit btn Updating Transaction ID: {selected_txn} to Status: {new_status}, Amount: {new_amount}, Type: {trx_type}")
                            if trx_type=="loan Payment":
                                st.info("Note: Loan Payment transactions do not affect account balances.")
                                print(f"Current Loan Balance before update: ₹{current_loan_balance}")
                                 # Calculate new loan balance
                                
                                clean_loan_balance = to_float(current_loan_balance)
                                clean_new_amount = float(new_amount)
                                loan_new_balance = clean_loan_balance - clean_new_amount
                                date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                print(f"Calculating new loan balance:{loan_new_balance}")
                                if loan_new_balance <0:
                                    
                                    execute_action("UPDATE loans SET loan_amount = ?,end_date = ? WHERE loan_id = ?", (loan_new_balance, date, loan_id))
                                    execute_action(
                                        "UPDATE transactions SET status = ?, amount = ?, txn_time = ? WHERE txn_id = ?",
                                        (new_status, new_amount, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), selected_txn))
                                    st.success("Database synchronized successfully!")
                                    st.balloons()
                                else:
                                    execute_action("UPDATE loans SET loan_amount = ?,end_date = ? WHERE loan_id = ?", (loan_new_balance, date, loan_id))
                                    execute_action(
                                        "UPDATE transactions SET status = ?, amount = ?, txn_time = ? WHERE txn_id = ?",
                                        (new_status, new_amount, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), selected_txn))
                                    st.success("Database synchronized successfully!")
                                    st.balloons()
                            else:
                                with sqlite3.connect("Database/BankSight.db") as conn:
                                    cursor = conn.cursor()
                                    # Use 'customer_id' fetched from the transaction itself
                                    print(f"Using Associated Account ID: {customer_id} for balance adjustments.")
                                    current_balance=  run_query("SELECT account_balance FROM accounts WHERE customer_id = ?", (customer_id,))
                                    # cursor.execute("SELECT account_balance FROM accounts WHERE customer_id ?", (customer_id,))
                                    # current_balance = cursor.fetchone()[0]
                                    print(f"Current Balance before update: ₹{current_balance}")

                                    # 2. REVERSE: If it was Success, put money back/take it out
                                    temp_balance = current_balance
                                    if old_status == "Success":
                                        if old_type in ["Withdrawal", "Transfer"]:
                                            temp_balance += old_amount
                                        else:
                                            temp_balance -= old_amount

                                    # 3. APPLY: Only move money if the NEW status is Success
                                    final_balance = temp_balance
                                    is_valid = True
                                    
                                    if new_status == "Success":
                                        if old_type in ["Withdrawal", "Transfer"]: # Using old_type as txn_type usually doesn't change
                                            if (temp_balance - new_amount) < 1000:
                                                st.error(f"Denied! Balance would fall below ₹1,000. Available: ₹{temp_balance}")
                                                is_valid = False
                                            else:
                                                final_balance = temp_balance - new_amount
                                        else:
                                            final_balance = temp_balance + new_amount
                                    if is_valid:
                                        # UPDATE BOTH TABLES IN ONE TRANSACTION
                                        print(f"Final Balance to be set: ₹{final_balance} and customer_id: {customer_id}")
                                        print(f"Updating Transaction ID: {selected_txn} to Status: {new_status}, Amount: {new_amount}")
                                        try:
                                            # If final_balance is a Series, this gets the actual number
                                            clean_balance = float(final_balance.iloc[0]) if hasattr(final_balance, 'iloc') else float(final_balance)
                                        except Exception:
                                            clean_balance = float(final_balance)

                                        execute_action(
                                                    "UPDATE accounts SET account_balance = ? WHERE customer_id = ?", 
                                                    (clean_balance, customer_id) # Ensure actual_customer_id is a string/int
                                                )  
                                        # cursor.execute("UPDATE accounts SET account_balance = ? WHERE customer_id = ?", (final_balance, customer_id))
                                        execute_action(
                                            "UPDATE transactions SET status = ?, amount = ?, txn_time = ? WHERE txn_id = ?",
                                            (new_status, new_amount, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), selected_txn))
                                        st.success("Database synchronized successfully!")
                                        st.balloons()
    

        elif table_name == "loans":
            # st.info("Loan updates are currently not supported in this interface.")
            with sqlite3.connect("Database/BankSight.db") as conn_local:
                customer = run_query("SELECT name FROM customers")['name'].tolist()
                st.subheader("Select Customer")
                customer_names = customer
                selected_name = st.selectbox("Customer Name", customer_names)
                customer_id = get_customer_id_by_name(selected_name)
                loan_id =run_query("SELECT loan_id FROM loans WHERE customer_id = ? ", (customer_id,))['loan_id'].tolist()
            with st.form("loan_form"):

                accunt = run_query("SELECT account_id FROM accounts WHERE customer_id = ?", (customer_id,))['account_id'].tolist()
                print(f"Selected Customer ID for Loans: {customer_id},{accunt}")
                st.subheader("Select Account")
                selected_account = st.selectbox("Account ID", accunt)
                branch = run_query("SELECT branch_name FROM branches")['branch_name'].tolist()
                st.subheader("Select Branch")
                selected_branch = st.selectbox("Branch Name", branch)
                loan_amount = st.number_input("Loan Amount", min_value=0)
                interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, format="%.2f")
                loan_type = st.selectbox("loan_type", ["Personal", "Auto", "Home", "Business", "Loan Against Property", "Education"])
                loan_status = st.selectbox("loan_status", ["Active", "Inactive","Closed", "Defaulted"])
                loan_duration_months = st.number_input("Loan Duration (Months)", min_value=1)
                start_date = datetime.date.today().strftime('%Y-%m-%d')
                submit_button = st.form_submit_button("Add Loan")

            if submit_button:
                if not customer_id:
                    st.error("Customer ID is required!")
                else:
                    try:
                        with sqlite3.connect("Database/BankSight.db") as conn_local:
                            conn_local.execute(
                               """ UPDATE loans SET customer_id = ?, branch = ?, loan_amount = ?, account_id = ?, interest_rate = ?, loan_type = ?, loan_status = ?, loan_term_months = ?, start_date = ? WHERE loan_id = ? """, ( customer_id, selected_branch, loan_amount, selected_account, interest_rate, loan_type, loan_status, loan_duration_months, start_date, loan_id ) # <-- important: specify which loan to update
                            )
                            conn_local.commit()
                        st.success(f"Loan for Customer ID {customer_id} added successfully!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Failed to add loan: {e}")

        elif table_name == "creditcards":   
            pass
        
            
                        
    def handle_delete(self, table_name):
        st.subheader(f"🗑️ Permanent Removal from {table_name}")
        if table_name == "branches":
            id_col = "branch_id"
            T_branch= run_query("SELECT branch_name FROM branches")['branch_name'].tolist()
            st.subheader("Select Branch")
            selected_name = st.selectbox("Branch Name", T_branch)
        elif table_name == "accounts":
            id_col = "account_id"
            T_branch= run_query("SELECT name FROM customers ")['name'].tolist()
            st.subheader("Select Customer")
            selected_name = st.selectbox("Customer Name", T_branch)
        elif table_name == "transactions":
            id_col = "txn_id"
            T_branch= run_query("SELECT name FROM customers ")['name'].tolist()
            st.subheader("Select Customer")
            selected_name = st.selectbox("Customer Name", T_branch)
        elif table_name == "loans":
            id_col = "loan_id"
            T_branch= run_query("SELECT name FROM customers ")['name'].tolist()
            st.subheader("Select Customer")
            selected_name = st.selectbox("Customer Name", T_branch)
        else: # customers
            id_col = "customer_id"
            T_branch= run_query("SELECT name FROM customers ")['name'].tolist()
            st.subheader("Select Customer")
            selected_name = st.selectbox("Customer Name", T_branch)
            # 1. Fetch the record to delete based on selection
        target_id = None
        if table_name == "branches":
            # Branch Logic
            res = run_query("SELECT branch_id FROM branches WHERE branch_name = ?", (selected_name,))
            target_id = int(res.iloc[0, 0]) if not res.empty else None
        elif table_name == "accounts":
            # Account Logic: You need the account_id, not just the customer_id
            cust_id = run_query("SELECT customer_id FROM customers WHERE name = ?", (selected_name,)).iloc[0,0]
            # Let the user select which SPECIFIC account to delete
            acc_list = run_query("SELECT account_id FROM accounts WHERE customer_id = ?", (cust_id,))['account_id'].tolist()
            target_id = st.selectbox("Select Specific Account ID", acc_list)
        elif table_name == "transactions":
            # Transaction Logic: You need the txn_id
            cust_id = run_query("SELECT customer_id FROM customers WHERE name = ?", (selected_name,)).iloc[0,0]
            txn_list = run_query("SELECT txn_id FROM transactions WHERE customer_id = ?", (cust_id,))['txn_id'].tolist()
            target_id = st.selectbox("Select Specific Transaction ID", txn_list)
        elif table_name == "loans":
            # Loans Logic: You need the loan_id
            cust_id = run_query("SELECT customer_id FROM customers WHERE name = ?", (selected_name,)).iloc[0,0]
            loan_list = run_query("SELECT loan_id FROM loans WHERE customer_id = ?", (cust_id,))['loan_id'].tolist()
            target_id = st.selectbox("Select Specific Loan ID", loan_list)
        else: # Customers
            res = run_query("SELECT customer_id FROM customers WHERE name = ?", (selected_name,))
            target_id = str(res.iloc[0, 0]) if not res.empty else None
            print(f"Target Customer ID for Deletion: {res}")

        if target_id:
            # 2. Verify and show the record
                

                print(f"Attempting to delete {table_name} record with {id_col}: {target_id}")
                check_df = run_query(f"SELECT * FROM {table_name} WHERE {id_col} = ?", (target_id,))
                print(f"Record fetched for deletion confirmation: {check_df}")
                if not check_df.empty:
                    st.warning(f"CRITICAL: You are about to delete {table_name} record: {target_id}")
                    st.dataframe(check_df)
                    
                # 3. KEEP THE BUTTON INSIDE THE SAME SCOPE AS THE CHECKBOX
                    confirm = st.checkbox(f"Confirm permanent deletion of {target_id}")
                    
                    if st.button("Confirm Delete"):
                        if confirm:
                            try:
                                # Use your execute_action method
                                print(f"data testing DELETE FROM {table_name} WHERE {id_col} = ?", (target_id,))
                                execute_action(f"DELETE FROM {table_name} WHERE {id_col} = ?", (target_id,))
                                st.success(f"Record {target_id} has been wiped from the database.")
                                st.balloons()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Integrity Error: {e}. You cannot delete this because other data depends on it.")
                        else:
                            st.error("Action blocked: Please check the confirmation box first.")
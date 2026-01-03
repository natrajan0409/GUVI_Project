
import streamlit as st
import datetime
from scripts.commonmethod import execute_action, run_query, get_customer_id_by_name, get_connection, to_float

def create_transaction():
    customer_names = run_query("SELECT name FROM customers")['name'].tolist()

    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", customer_names)

    # Fetch dependent data
    customer_id = get_customer_id_by_name(selected_name)
    if not customer_id:
        return
        
    select_account = run_query("SELECT account_id FROM accounts WHERE customer_id = ?", (customer_id,))['account_id'].tolist()
    if not select_account:
        st.error("No accounts found for this customer.")
        return
        
    account = st.selectbox("Select Account", select_account)
    
    res = run_query("SELECT account_balance FROM accounts WHERE account_id = ?", (account,))
    bankbalance = res.iloc[0,0] if not res.empty else 0
    st.info(f"Current Account Balance: ₹{bankbalance}")

    # Transaction types and extra info logic
    txn_type = st.selectbox("Transaction Type", ["Deposit", "Withdrawal", "Transfer", "loan Payment", "Debit", "Credit payment"])
    
    Loanoutstanding = 0
    creditcard_due = 0
    
    if txn_type == "loan Payment":
        try:
            loan_res = run_query("SELECT loan_amount FROM loans WHERE customer_id = ?", (customer_id,))
            Loanoutstanding = loan_res.iloc[0, 0] if not loan_res.empty else 0
        except Exception:
            Loanoutstanding = 0
            
        if Loanoutstanding == 0:
            st.warning("No loan found for this customer.")
        else:
            st.info(f"Current Loan Outstanding: ₹{Loanoutstanding}")
            st.info("Note: Transaction status will be set to 'Pending' for loan payments. Staff will verify and update accordingly.")
            
    elif txn_type == "Credit payment":
         try:
            cc_res = run_query("SELECT current_balance FROM creditcards WHERE customer_id = ?", (customer_id,))
            creditcard_due = cc_res.iloc[0, 0] if not cc_res.empty else 0
         except Exception:
            creditcard_due = 0
            
         if creditcard_due == 0:
             st.warning("No credit card found for this customer.")
         else:
             st.info(f"Current Credit Card Due: ₹{creditcard_due}")
             st.info("Note: Transaction status will be set to 'Pending' for credit payments. Staff will verify and update accordingly.")

    # Status handling
    if txn_type in ["loan Payment", "Credit payment"]:
        status = st.selectbox("Transaction Status", ["Pending"], disabled=True)
    else:
        status = st.selectbox("Transaction Status", ["Success", "Failed", "Pending"])
        
    amount = st.number_input("Transaction Amount", min_value=1)

    if st.button("Add Transaction"):
        if not account:
            st.error("Account ID not found.")
            return

        current_balance = float(bankbalance)
        cust_id = customer_id
        
        is_valid = True
        new_balance = current_balance
        
        # Balance Calculation and Validation Logic
        if txn_type == "Debit":
             if (current_balance - amount) < 1000:
                 st.error(f"Transaction Denied! Minimum balance of ₹1,000 required. Current: ₹{current_balance}")
                 is_valid = False
             else:
                 new_balance = current_balance - amount
                 
        elif txn_type == "Withdrawal" or txn_type == "Transfer":
             if (current_balance - amount) < 1000:
                 st.error(f"Transaction Denied! Minimum balance of ₹1,000 required. Current: ₹{current_balance}")
                 is_valid = False
             else:
                 new_balance = current_balance - amount
                 
        elif txn_type == "loan Payment" or txn_type == "Credit payment":
             # Original logic: new_balance = current_balance + amount (Wait, this logic in original code was weird implementation of deposit to another internal account maybe?)
             # BUT critically, looking at original code:
             # For Loan/Credit payments, it did NOT update account balance in the main block.
             # It only logged transaction.
             # So we will KEEP account balance UNCHANGED for the customer account in this step.
             new_balance = current_balance # No change to customer saving account for now, as it is pending verification.
             
        else: # Deposit
             new_balance = current_balance + amount

        if is_valid:
            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Update Account Balance logic
                    # Only update if NOT Loan/Credit Payment (which are pending) AND status is Success
                    if txn_type not in ["loan Payment", "Credit payment"] and status == "Success":
                        cursor.execute("UPDATE accounts SET account_balance = ? WHERE account_id = ?", (new_balance, account))
                    
                    # Log Transaction
                    new_txn_id = f"T{int(datetime.datetime.now().timestamp())}"
                    
                    # Ensure status logic matches
                    final_status = status if status else 'Success'
                    
                    cursor.execute("""
                        INSERT INTO transactions (txn_id, customer_id, txn_type, amount, txn_time, status) 
                        VALUES (?, ?, ?, ?, ?, ?)""", 
                        (new_txn_id, cust_id, txn_type, amount, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), final_status))
                    
                    conn.commit()
                
                if txn_type in ["loan Payment", "Credit payment"]:
                     st.success(f"Transaction logged with status {final_status}. No balance update yet.")
                
                elif status == "Success":
                     st.success(f"Success! New Balance: ₹{new_balance:.2f}")
                else:
                     st.success(f"Transaction logged with status {final_status}. No balance update yet.")
                
                st.balloons()
            except Exception as e:
                st.error(f"Database Error: {e}")

def update_transaction():
    st.info("Only 'Failed' and 'Pending' transactions can be updated.")
    T_customer = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", T_customer)
    
    result = run_query("SELECT * FROM transactions WHERE customer_id = (SELECT customer_id FROM customers WHERE name = ?) AND status IN ('Failed', 'Pending')",
             (selected_name,))
             
    if result.empty:
        st.write("No Failed/Pending transactions found.")
        return

    Tran_id = result['txn_id'].tolist()
    selected_txn = st.selectbox("Select Transaction ID", Tran_id)
    
    # We need to fetch details of the selected txn
    row = result[result['txn_id'] == selected_txn].iloc[0]
    trx_type = row['txn_type']
    old_status = row['status']
    old_amount = row['amount']
    customer_id = row['customer_id']
    
    st.write(f"Editing Transaction: {selected_txn} ({trx_type})")
    
    with st.form("transaction_update_form"):
        new_status = st.selectbox("Update Status", ["Success", "Failed", "Pending"], 
                                index=["Success", "Failed", "Pending"].index(old_status) if old_status in ["Success", "Failed", "Pending"] else 0)
        st.text(f"Transaction amount: {old_amount} (Unchangeable)")
        new_amount = st.number_input("Adjust Amount", min_value=1.0, value=float(old_amount))
        submit_button = st.form_submit_button(" Update Changes")

    if submit_button:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # For Loan Payments, we update Loan table? Original code had complex logic for this in update.
            # Step 31 line 509: if trx_type=="loan Payment": update loans table.
            
            if trx_type == "loan Payment":
                loan_res = run_query("SELECT loan_id, loan_amount FROM loans WHERE customer_id = ?", (customer_id,))
                if not loan_res.empty:
                    loan_id = loan_res.iloc[0]['loan_id']
                    current_loan_bal = float(loan_res.iloc[0]['loan_amount'])
                    
                    # New loan balance = old - amount
                    new_loan_bal = current_loan_bal - float(new_amount)
                    
                    try:
                        cursor.execute("UPDATE loans SET loan_amount = ? WHERE loan_id = ?", (new_loan_bal, loan_id))
                        cursor.execute(
                            "UPDATE transactions SET status = ?, amount = ?, txn_time = ? WHERE txn_id = ?",
                            (new_status, new_amount, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), selected_txn))
                        conn.commit()
                        st.success("Database synchronized successfully! Loan balance updated.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Database Error: {e}")
                else:
                    st.error("No active loan found to update.")

            else:
                # Normal Account Logic
                cursor.execute("SELECT account_id, account_balance FROM accounts WHERE customer_id = ?", (customer_id,))
                res = cursor.fetchone()
                if not res:
                    st.error("No account found for customer.")
                    return
                account_id, current_balance = res
                
                temp_balance = float(current_balance)
                final_balance = temp_balance
                is_valid = True
                
                if new_status == "Success":
                    if trx_type in ["Withdrawal", "Transfer", "Debit"]:
                        if (temp_balance - new_amount) < 1000:
                             st.error(f"Denied! Balance would fall below ₹1,000. Available: ₹{temp_balance}")
                             is_valid = False
                        else:
                            final_balance = temp_balance - new_amount
                    elif trx_type in ["Deposit"]:
                        final_balance = temp_balance + new_amount
                
                if is_valid:
                    try:
                        cursor.execute("UPDATE accounts SET account_balance = ? WHERE account_id = ?", (final_balance, account_id))
                        cursor.execute(
                            "UPDATE transactions SET status = ?, amount = ?, txn_time = ? WHERE txn_id = ?",
                            (new_status, new_amount, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), selected_txn))
                        conn.commit()
                        st.success("Database synchronized successfully!")
                        st.balloons()
                    except Exception as e:
                         st.error(f"Database Error: {e}")

def delete_transaction():
    T_branch = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", T_branch)
    
    cust_id_res = run_query("SELECT customer_id FROM customers WHERE name = ?", (selected_name,))
    if cust_id_res.empty: return
    cust_id = cust_id_res.iloc[0,0]
    
    txn_list = run_query("SELECT txn_id FROM transactions WHERE customer_id = ? and status in('Pending', 'Failed')", (cust_id,))['txn_id'].tolist()
    if not txn_list:
        st.warning("No transactions found.")
        return
        
    target_id = st.selectbox("Select Specific Transaction ID", txn_list)

    if target_id:
        check_df = run_query("SELECT * FROM transactions WHERE txn_id = ?", (target_id,))
        if not check_df.empty:
            st.warning(f"CRITICAL: You are about to delete transaction: {target_id}")
            st.dataframe(check_df)
            
            confirm = st.checkbox(f"Confirm permanent deletion of {target_id}")
            
            if st.button("Confirm Delete"):
                if confirm:
                    try:
                        execute_action("DELETE FROM transactions WHERE txn_id = ?", (target_id,))
                        st.success(f"Record {target_id} has been wiped from the database.")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Integrity Error: {e}.")
                else:
                    st.error("Action blocked: Please check the confirmation box first.")

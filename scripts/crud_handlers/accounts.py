
import streamlit as st
import datetime
from scripts.commonmethod import execute_action, run_query, get_customer_id_by_name

def create_account():
    customer = run_query("SELECT name FROM customers")['name'].tolist()
    with st.form("account_form"):
        st.subheader("Select Customer") 
        selected_name = st.selectbox("Customer Name", customer)
        # customer_id will be fetched after form submission or we need to fetch it outside form?
        # Form submission is safer
        
        account_balance = st.number_input("Account Balance", min_value=0)
        open_date = datetime.date.today().strftime('%Y-%m-%d')
        submit_button = st.form_submit_button("Add Account")

    if submit_button:
        customer_id = get_customer_id_by_name(selected_name)
        if not customer_id:
            st.error("Customer ID is required!")
        else:
            try:
                execute_action(
                    "INSERT INTO accounts (customer_id, account_balance, last_updated) VALUES (?, ?, ?)", 
                    (customer_id, account_balance, open_date)
                )
                st.success(f"Account for Customer ID {customer_id} added successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Failed to add account: {e}") 

def update_account():
    # 1. Selection happens OUTSIDE the form to fetch current data
    accounts_df = run_query("SELECT customer_id FROM accounts")
    if accounts_df.empty:
        st.warning("No accounts found.")
        return
        
    accounts_list = accounts_df['customer_id'].tolist()
    selected_account = st.selectbox("Select Account Customer ID to Update", accounts_list)
    
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
                execute_action("""UPDATE accounts 
                    SET account_balance=?, last_updated=? 
                    WHERE account_id=?""",
                    (float(new_balance), new_date, int(account_id)))
                st.success(f"Account for Customer ID '{selected_account}' updated successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Failed to update record: {e}")
    else:
        st.warning("Account details could not be retrieved.")

def delete_account():
    T_branch = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", T_branch)
    
    cust_id_res = run_query("SELECT customer_id FROM customers WHERE name = ?", (selected_name,))
    if cust_id_res.empty:
        return
    cust_id = cust_id_res.iloc[0,0]
    
    # Let the user select which SPECIFIC account to delete
    acc_res = run_query("SELECT account_id FROM accounts WHERE customer_id = ?", (cust_id,))
    if acc_res.empty:
        st.warning("No accounts found for this customer.")
        return
        
    acc_list = acc_res['account_id'].tolist()
    target_id = st.selectbox("Select Specific Account ID", acc_list)
    
    if target_id:
        check_df = run_query("SELECT * FROM accounts WHERE account_id = ?", (target_id,))
        if not check_df.empty:
            st.warning(f"CRITICAL: You are about to delete account record: {target_id}")
            st.dataframe(check_df)
            
            confirm = st.checkbox(f"Confirm permanent deletion of {target_id}")
            
            if st.button("Confirm Delete"):
                if confirm:
                    try:
                        execute_action("DELETE FROM accounts WHERE account_id = ?", (target_id,))
                        st.success(f"Record {target_id} has been wiped from the database.")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Integrity Error: {e}. You cannot delete this because other data depends on it.")
                else:
                    st.error("Action blocked: Please check the confirmation box first.")

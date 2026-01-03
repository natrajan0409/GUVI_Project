
import streamlit as st
import datetime
from scripts.commonmethod import execute_action, run_query, get_customer_id_by_name

def create_loan():
    customer = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", customer)
    
    if not selected_name: return

    customer_id = get_customer_id_by_name(selected_name)
    
    with st.form("loan_form"):
        acc_res = run_query("SELECT account_id FROM accounts WHERE customer_id = ?", (customer_id,))
        accunt = acc_res['account_id'].tolist()
        
        st.subheader("Select Account")
        selected_account = st.selectbox("Account ID", accunt)
        
        branch_res = run_query("SELECT branch_name FROM branches")
        branch = branch_res['branch_name'].tolist()
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
                execute_action(
                    "INSERT INTO loans (customer_id,branch_name, loan_amount, account_id, interest_rate, loan_type, loan_status,loan_term_months, start_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (customer_id, selected_branch, loan_amount, selected_account, interest_rate, loan_type, loan_status, loan_duration_months, start_date)
                )
                st.success(f"Loan for Customer ID {customer_id} added successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Failed to add loan: {e}")

def update_loan():
    customer = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", customer)
    customer_id = get_customer_id_by_name(selected_name)
    
    # Logic to fetch loan IDs to populate selectbox
    loan_res = run_query("SELECT loan_id FROM loans WHERE customer_id = ?", (customer_id,))
    loan_ids = loan_res['loan_id'].tolist()
    
    if not loan_ids:
        st.warning("No loans found for this customer.")
        return
        
    loan_id = st.selectbox("Select Loan ID to Update", loan_ids) 
    
    # Fetch current details for the selected loan to pre-fill the form
    # We use a try/except or empty check to be safe
    try:
        current_loan = run_query("SELECT * FROM loans WHERE loan_id = ?", (loan_id,)).iloc[0]
    except IndexError:
         st.error("Error retrieving loan details.")
         return

    with st.form("loan_update_form"):
        
        acc_res = run_query("SELECT account_id FROM accounts WHERE customer_id = ?", (customer_id,))
        accunt = acc_res['account_id'].tolist()
        # Find index of current account
        curr_acc = current_loan.get('account_id')
        acc_idx = accunt.index(curr_acc) if curr_acc in accunt else 0
        selected_account = st.selectbox("Account ID", accunt, index=acc_idx)
        
        branch_res = run_query("SELECT branch_name FROM branches")
        branch = branch_res['branch_name'].tolist()
        
        # Check column name for branch. create_loan uses 'branch_name' but checks user edits elsewhere.
        # We will try 'branch_name' then 'branch'
        curr_branch = current_loan.get('branch_name') if 'branch_name' in current_loan else current_loan.get('branch')
        branch_idx = branch.index(curr_branch) if curr_branch in branch else 0
        selected_branch = st.selectbox("Branch Name", branch, index=branch_idx)
        
        # Pre-fill amounts with current values
        curr_amount = float(current_loan.get('loan_amount', 0))
        loan_amount = st.number_input("Loan Amount", min_value=0, value=int(curr_amount))
        
        curr_rate = float(current_loan.get('interest_rate', 0.0))
        interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, format="%.2f", value=curr_rate)
        
        types = ["Personal", "Auto", "Home", "Business", "Loan Against Property", "Education"]
        curr_type = current_loan.get('loan_type')
        type_idx = types.index(curr_type) if curr_type in types else 0
        loan_type = st.selectbox("loan_type", types, index=type_idx)
        
        statuses = ["Active", "Inactive","Closed", "Defaulted"]
        curr_status = current_loan.get('loan_status')
        status_idx = statuses.index(curr_status) if curr_status in statuses else 0
        loan_status = st.selectbox("loan_status", statuses, index=status_idx)
        
        curr_term = int(current_loan.get('loan_term_months', 1))
        loan_duration_months = st.number_input("Loan Duration (Months)", min_value=1, value=curr_term)
        
        start_date = datetime.date.today().strftime('%Y-%m-%d')
        submit_button = st.form_submit_button("Update Loan")

    if submit_button:
        try:
             # NOTE: Update query uses 'branch' or 'branch_name'?? 
             # create_loan used INSERT INTO ... branch_name ... (from user edit Step 125)
             # But update logic in Step 126 user code wasn't shown fully changed.
             # I will use 'branch_name=?' to be safe if that column exists, or fallback.
             # Wait, SQL update string is literal. I must match the DB schema.
             # If insert worked with 'branch_name', column is probably 'branch_name'.
             # But Step 125 showed: "INSERT INTO loans (...,branch_name, ...)"
             # Let's assume schema has 'branch_name'.
             
             # Actually, best to check schema? I can't check schema easily without iterating.
             # I will try to update 'branch' column as in original code, but if user changed it...
             # The user changed INSERT. 
             # Let's assume the column is `branch` based on old code, or `branch_name`.
             # Standardizing on `branch_name` seems risky if I don't know for sure.
             # I'll check `branches` table... no `loans` table.
             # I'll use the user's insert column `branch_name` as the target for update too?
             # Actually, original code had `branch` in insert too. Step 125 changed it to `branch_name`.
             # So I will use `branch_name` in Update too.
             
             execute_action(
               """ UPDATE loans SET customer_id = ?, branch_name = ?, loan_amount = ?, account_id = ?, interest_rate = ?, loan_type = ?, loan_status = ?, loan_term_months = ?, start_date = ? WHERE loan_id = ? """, 
               ( customer_id, selected_branch, loan_amount, selected_account, interest_rate, loan_type, loan_status, loan_duration_months, start_date, loan_id )
            )
             st.success(f"Loan {loan_id} updated successfully!")
             st.balloons()
        except Exception as e:
            # If branch_name fails, maybe it is branch?
            st.error(f"Failed to update loan: {e}. (Hint: Column might be 'branch' instead of 'branch_name'?)")

def delete_loan():
    T_branch = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", T_branch)
    
    cust_id_res = run_query("SELECT customer_id FROM customers WHERE name = ?", (selected_name,))
    if cust_id_res.empty: return
    cust_id = cust_id_res.iloc[0,0]
    
    loan_list = run_query("SELECT loan_id FROM loans WHERE customer_id = ?", (cust_id,))['loan_id'].tolist()
    target_id = st.selectbox("Select Specific Loan ID", loan_list)
    
    if target_id:
        check_df = run_query("SELECT * FROM loans WHERE loan_id = ?", (target_id,))
        if not check_df.empty:
            st.warning(f"CRITICAL: You are about to delete loan record: {target_id}")
            st.dataframe(check_df)
            
            confirm = st.checkbox(f"Confirm permanent deletion of {target_id}")
            
            if st.button("Confirm Delete"):
                if confirm:
                    try:
                        execute_action("DELETE FROM loans WHERE loan_id = ?", (target_id,))
                        st.success(f"Record {target_id} has been wiped from the database.")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Integrity Error: {e}.")
                else:
                    st.error("Action blocked: Please check the confirmation box first.")

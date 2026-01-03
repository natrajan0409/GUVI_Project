
import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
from scripts.commonmethod import execute_action, run_query, get_customer_id_by_name, get_branch_names, generate_card_number

def create_creditcard():
    customer = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Create New Credit Card")
    selected_name = st.selectbox("Select Customer", customer)
    
    if not selected_name:
        return

    customer_id = get_customer_id_by_name(selected_name)
    
    # Check for accounts first
    acc_res = run_query("SELECT account_id FROM accounts WHERE customer_id = ?", (customer_id,))
    if acc_res.empty:
        st.error(f"Customer {selected_name} does not have an account! Please create an account first.")
        return
    accounts = acc_res['account_id'].tolist()

    # Get Existing Active Cards
    # Rule: Can only create a card type if no active (unexpired) card of that type exists.
    existing_cards = run_query("""
        SELECT card_type, expiry_date, status 
        FROM creditcards 
        WHERE customer_id = ?
    """, (customer_id,))
    
    blocked_types = []
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    
    if not existing_cards.empty:
        st.info("Existing Cards:")
        st.dataframe(existing_cards)
        
        for _, row in existing_cards.iterrows():
            # If card is NOT Expired/Blocked AND Expiry Date is in the future
            if row['status'] not in ['Expired', 'Blocked'] and row['expiry_date'] > today_str:
                blocked_types.append(row['card_type'])
    
    all_types = ["Business", "Platinum", "Gold", "Silver", "Bronze"]
    allowed_types = [t for t in all_types if t not in blocked_types]
    
    if not allowed_types:
        st.warning("Customer already has all card types Active and Valid. Cannot issue new cards.")
        return

    with st.form("creditcard_form"):
        branch_names = get_branch_names()
        branch_name = st.selectbox("Select Branch", branch_names)
        selected_account = st.selectbox("Select Linked Account", accounts)
        
        if 'temp_card_number' not in st.session_state:
             st.session_state.temp_card_number = generate_card_number()
        
        card_number = st.text_input("Credit Card Number", st.session_state.temp_card_number, disabled=True)
        
        card_type = st.selectbox("Card Type", allowed_types)
        
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
        try:
            execute_action(
                """INSERT INTO creditcards 
                (branch_name, customer_id, account_id, card_number, card_type, card_network, 
                    credit_limit, current_balance, issued_date, expiry_date, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (branch_name, customer_id, selected_account, card_number, card_type, card_network,
                credit_limit, current_balance, issue_date, expiry_date, status)
            )
            st.success(f"Credit Card ({card_type}) for {selected_name} added successfully!")
            st.session_state.temp_card_number = generate_card_number() # Reset
            st.balloons()
        except Exception as e:
            st.error(f"Failed to add credit card: {e}")

def update_creditcard():
    customer = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", customer)
    customer_id = get_customer_id_by_name(selected_name)
    
    # Logic to fetch Card IDs to populate selectbox
    cc_res = run_query("SELECT card_id, card_number FROM creditcards WHERE customer_id = ?", (customer_id,))
    
    if cc_res.empty:
        st.warning("No credit cards found for this customer.")
        return
        
    # Create a display list (ID - Number)
    cc_res['display'] = cc_res['card_id'].astype(str) + " - " + cc_res['card_number']
    cc_list = cc_res['display'].tolist()
    
    selected_cc_display = st.selectbox("Select Credit Card to Update", cc_list)
    selected_cc_id = selected_cc_display.split(" - ")[0]
    
    # Fetch current details
    try:
        current_cc = run_query("SELECT * FROM creditcards WHERE card_id = ?", (selected_cc_id,)).iloc[0]
    except IndexError:
         st.error("Error retrieving credit card details.")
         return

    with st.form("cc_update_form"):
        st.write(f"Updating Card: {current_cc['card_number']}")
        
        # Branch
        branch_names = get_branch_names()
        current_branch = current_cc.get('branch_name')
        b_idx = branch_names.index(current_branch) if current_branch in branch_names else 0
        new_branch = st.selectbox("Branch Name", branch_names, index=b_idx)
        
        # Account
        acc_res = run_query("SELECT account_id FROM accounts WHERE customer_id = ?", (customer_id,))
        accounts = acc_res['account_id'].tolist()
        curr_acc = current_cc.get('account_id')
        a_idx = accounts.index(curr_acc) if curr_acc in accounts else 0
        new_account = st.selectbox("Linked Account", accounts, index=a_idx)
        
        # Fields
        types = ["Business", "Platinum", "Gold", "Silver", "Bronze"]
        current_type = current_cc.get('card_type')
        t_idx = types.index(current_type) if current_type in types else 0
        new_type = st.selectbox("Card Type", types, index=t_idx)
        
        networks = ["Visa", "MasterCard", "American Express", "Discover"]
        current_net = current_cc.get('card_network')
        n_idx = networks.index(current_net) if current_net in networks else 0
        new_network = st.selectbox("Card Network", networks, index=n_idx)
        
        curr_limit = float(current_cc.get('credit_limit', 0))
        new_limit = st.number_input("Credit Limit", min_value=0.0, value=curr_limit)
        
        curr_statuses = ["Active", "Inactive", "Blocked"]
        current_status = current_cc.get('status')
        s_idx = curr_statuses.index(current_status) if current_status in curr_statuses else 0
        new_status = st.selectbox("Card Status", curr_statuses, index=s_idx)

        submit_button = st.form_submit_button("Update Credit Card")
        
    if submit_button:
        try:
             execute_action(
               """ UPDATE creditcards SET branch_name = ?, account_id = ?, card_type = ?, card_network = ?, credit_limit = ?, status = ? WHERE card_id = ? """, 
               (new_branch, new_account, new_type, new_network, new_limit, new_status, selected_cc_id)
            )
             st.success(f"Credit Card {selected_cc_id} updated successfully!")
             st.balloons()
        except Exception as e:
            st.error(f"Failed to update credit card: {e}")

def delete_creditcard():
    customer = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", customer)
    
    customer_id = get_customer_id_by_name(selected_name)
    
    cc_res = run_query("SELECT card_id, card_number FROM creditcards WHERE customer_id = ?", (customer_id,))
    
    if cc_res.empty:
        st.warning("No credit cards found for this customer.")
        return

    cc_res['display'] = cc_res['card_id'].astype(str) + " - " + cc_res['card_number']
    cc_list = cc_res['display'].tolist()
    
    selected_cc_display = st.selectbox("Select Credit Card to Delete", cc_list)
    target_id = selected_cc_display.split(" - ")[0]
    
    if target_id:
        check_df = run_query("SELECT * FROM creditcards WHERE card_id = ?", (target_id,))
        if not check_df.empty:
            st.warning(f"CRITICAL: You are about to delete credit card record: {target_id}")
            st.dataframe(check_df)
            
            confirm = st.checkbox(f"Confirm permanent deletion of {target_id}")
            
            if st.button("Confirm Delete"):
                if confirm:
                    try:
                        execute_action("DELETE FROM creditcards WHERE card_id = ?", (target_id,))
                        st.success(f"Record {target_id} has been wiped from the database.")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Integrity Error: {e}.")
                else:
                    st.error("Action blocked: Please check the confirmation box first.")

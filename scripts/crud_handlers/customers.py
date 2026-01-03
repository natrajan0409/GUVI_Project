
import streamlit as st
import datetime
from scripts.commonmethod import execute_action, run_query, get_next_customer_id

def create_customer():
    custom_id = get_next_customer_id()
    
    with st.form("customer_form"):
        st.info(f"New Customer ID: {custom_id}")
        name = st.text_input("Name")
        gender = st.selectbox("Gender", ["M", "F", "O"])
        age = st.number_input("Age", min_value=18)
        city = st.text_input("City")
        PhNo = st.number_input("Phone Number", min_value=1000000000, max_value=9999999999)
        account_type = st.selectbox("Account Type", ["Savings", "Current", "Premium"])
        join_date = datetime.date.today().strftime('%Y-%m-%d')
        submit_button = st.form_submit_button("Add Customer")

    if submit_button:
        if not name:
            st.error("Name is required!")
        else:
            try:
                # Check if name + phone already exists
                exists_df = run_query(
                    "SELECT 1 FROM customers WHERE name = ? AND Phnumber = ? AND account_type = ?",
                    (name, PhNo, account_type)
                )
                
                if not exists_df.empty:
                    st.error("This name + phone + account_type combination already exists!")
                else:
                    execute_action(
                        "INSERT INTO customers (customer_id, name, Phnumber, gender, age, city, account_type, join_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (custom_id, name, PhNo, gender, age, city, account_type, join_date)
                    )
                    st.success(f"Customer {name} added successfully!")
                    st.balloons()
            except Exception as e:
                st.error(f"Failed to add customer: {e}")

def update_customer():
    T_customer = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", T_customer)
    
    record = run_query("SELECT * FROM customers WHERE name = ?", (selected_name,))
    if record.empty:
        st.error("Customer not found!")
        return
    
    record_id = record.iloc[0]['customer_id']
    # Pre-fill logic could be improved, but keeping simple for now matched to original
    gender = st.selectbox("Gender", ["M", "F", "O"])
    age = st.number_input("Age", min_value=18)
    city = st.text_input("City")
    account_type = st.selectbox("Account Type", ["Savings", "Current", "Premium"])
    join_date = datetime.date.today().strftime('%Y-%m-%d')
    
    if st.button("Update customers Record"):
        try:
            execute_action(
                "UPDATE customers SET name = ?, gender = ?, age = ?, city = ?, account_type = ?, join_date = ? WHERE customer_id = ?", 
                (selected_name, gender, age, city, account_type, join_date, record_id)
            )
            st.success("Record updated successfully!")
        except Exception as e:
            st.error(f"Failed to update record: {e}")

def delete_customer():
    T_customer = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", T_customer)
    
    res = run_query("SELECT customer_id FROM customers WHERE name = ?", (selected_name,))
    target_id = str(res.iloc[0, 0]) if not res.empty else None
    
    if target_id:
        check_df = run_query("SELECT * FROM customers WHERE customer_id = ?", (target_id,))
        if not check_df.empty:
            st.warning(f"CRITICAL: You are about to delete customer record: {target_id}")
            st.dataframe(check_df)
            
            confirm = st.checkbox(f"Confirm permanent deletion of {target_id}")
            
            if st.button("Confirm Delete"):
                if confirm:
                    try:
                        execute_action("DELETE FROM customers WHERE customer_id = ?", (target_id,))
                        st.success(f"Record {target_id} has been wiped from the database.")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Integrity Error: {e}. You cannot delete this because other data depends on it.")
                else:
                    st.error("Action blocked: Please check the confirmation box first.")

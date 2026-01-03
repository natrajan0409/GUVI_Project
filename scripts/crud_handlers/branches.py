
import streamlit as st
import datetime
from scripts.commonmethod import execute_action, run_query

def create_branch():
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
                execute_action(
                    "INSERT INTO branches (branch_name, city, manager_name, total_employees, branch_revenue, opening_date, performance_rating) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                    (branch_name, city, manager_name, total_employees, branch_revenue, opening_date, performance_rating)
                )
                st.success(f"Branch {branch_name} added successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Failed to add branch: {e}")

def update_branch():
    branch_names = run_query("SELECT branch_name FROM branches")['branch_name'].tolist()
    selected_branch_name = st.selectbox("Select Branch to Update", branch_names)
    
    record = run_query("SELECT * FROM branches WHERE branch_name = ?", (selected_branch_name,))
    
    if not record.empty:
        row = record.iloc[0]
        branch_id = row['branch_id']

        with st.form("update_branch_form"):
            st.subheader(f"Editing Branch: {selected_branch_name} (ID: {branch_id})")
            
            new_name = st.text_input("Branch Name", value=row['branch_name'])
            new_city = st.text_input("City", value=row['city'])
            new_manager = st.text_input("Manager Name", value=row['manager_name'])
            new_emp = st.number_input("Total Employees", min_value=1, value=int(row['total_employees']))
            new_rev = st.number_input("Branch Revenue", min_value=0.0, value=float(row['branch_revenue']))
            try:
                current_date_obj = datetime.datetime.strptime(row['opening_date'], '%Y-%m-%d').date()
            except:
                current_date_obj = datetime.date.today()
            new_date_val = st.date_input("Opening Date", value=current_date_obj)
            new_date = new_date_val.strftime('%Y-%m-%d')
            new_rating = st.slider("Performance Rating", 1, 5, value=int(row['performance_rating']))
            
            submit_update = st.form_submit_button("Update Branch Details")

        if submit_update:
            try:
                execute_action("""UPDATE branches 
                    SET branch_name=?, city=?, manager_name=?, total_employees=?, 
                    branch_revenue=?, opening_date=?, performance_rating=? 
                    WHERE branch_id=?""",
                    (new_name, new_city, new_manager, int(new_emp), float(new_rev), new_date, int(new_rating), int(branch_id)))
                st.success(f"Branch '{new_name}' updated successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Failed to update record: {e}")   
    else:
        st.warning("Branch details could not be retrieved.")

def delete_branch():
    T_branch = run_query("SELECT branch_name FROM branches")['branch_name'].tolist()
    st.subheader("Select Branch")
    selected_name = st.selectbox("Branch Name", T_branch)
    
    res = run_query("SELECT branch_id FROM branches WHERE branch_name = ?", (selected_name,))
    target_id = int(res.iloc[0, 0]) if not res.empty else None

    if target_id:
        check_df = run_query("SELECT * FROM branches WHERE branch_id = ?", (target_id,))
        if not check_df.empty:
            st.warning(f"CRITICAL: You are about to delete branch record: {target_id}")
            st.dataframe(check_df)
            
            confirm = st.checkbox(f"Confirm permanent deletion of {target_id}")
            
            if st.button("Confirm Delete"):
                if confirm:
                    try:
                        execute_action("DELETE FROM branches WHERE branch_id = ?", (target_id,))
                        st.success(f"Record {target_id} has been wiped from the database.")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Integrity Error: {e}. You cannot delete this because other data depends on it.")
                else:
                    st.error("Action blocked: Please check the confirmation box first.")

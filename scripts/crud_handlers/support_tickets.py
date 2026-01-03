
import streamlit as st
import datetime
from scripts.commonmethod import execute_action, run_query, get_customer_id_by_name, get_branch_names

def create_ticket():
    customer = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Select Customer")
    selected_name = st.selectbox("Customer Name", customer)
    
    if not selected_name: return
    customer_id = get_customer_id_by_name(selected_name)
    
    # 1. Fetch Accounts for this customer
    acc_df = run_query("SELECT account_id FROM accounts WHERE customer_id = ?", (customer_id,))
    account_options = acc_df['account_id'].tolist() if not acc_df.empty else []
    
    # 2. Fetch Loans for this customer
    loan_df = run_query("SELECT loan_id FROM loans WHERE customer_id = ?", (customer_id,))
    loan_options = loan_df['loan_id'].tolist() if not loan_df.empty else []
    
    with st.form("ticket_form"):
        # Allow selecting specific Account/Loan if multiple, or default to None
        selected_account_id = st.selectbox("Related Account ID", [None] + account_options, disabled=not account_options)
        selected_loan_id = st.selectbox("Related Loan ID", [None] + loan_options, disabled=not loan_options)

        # Branch
        branches = get_branch_names()
        branch_name = st.selectbox("Branch Name", branches)
        
        issue_category = st.selectbox("Issue Category", ["Loan Payment Delay", "Account Access", "Transaction Dispute", "Fraud Alert", "Other"])
        description = st.text_area("Description")
        priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"], index=0)
        support_agent = st.text_input("Support Agent Name")
        channel = st.selectbox("Channel", ["Email", "Phone", "In-Person", "Chat"])
        
        date_opened = datetime.date.today().strftime('%Y-%m-%d')
        
        submit_button = st.form_submit_button("Create Ticket")

    if submit_button:
        try:
            execute_action(
                """INSERT INTO SupportTickets 
                (Customer_ID, Account_ID, Loan_ID, Branch_Name, Issue_Category, Description, Date_Opened, Priority, Status, Support_Agent, Channel) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (customer_id, selected_account_id, selected_loan_id, branch_name, issue_category, description, date_opened, priority, status, support_agent, channel)
            )
            st.success(f"Support Ticket created for {selected_name}!")
            st.balloons()
        except Exception as e:
            st.error(f"Failed to create ticket: {e}")

def update_ticket():
    # Select ticket by ID or Customer
    customer = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Filter by Customer")
    selected_name = st.selectbox("Customer Name", customer)
    customer_id = get_customer_id_by_name(selected_name)
    
    tickets = run_query("SELECT Ticket_ID, Issue_Category, Status FROM SupportTickets WHERE Customer_ID = ?", (customer_id,))
    
    if tickets.empty:
        st.warning("No tickets found for this customer.")
        return
        
    tickets['display'] = tickets['Ticket_ID'].astype(str) + " - " + tickets['Issue_Category'] + " (" + tickets['Status'] + ")"
    ticket_list = tickets['display'].tolist()
    selected_ticket_display = st.selectbox("Select Ticket to Update", ticket_list)
    selected_ticket_id = selected_ticket_display.split(" - ")[0]
    
    current_ticket = run_query("SELECT * FROM SupportTickets WHERE Ticket_ID = ?", (selected_ticket_id,)).iloc[0]
    
    with st.form("update_ticket_form"):
        st.write(f"Updating Ticket: {selected_ticket_id}")
        st.write(f"Opened: {current_ticket['Date_Opened']}")
        
        # Display current links
        st.write(f"Linked Account: {current_ticket['Account_ID']}")
        st.write(f"Linked Loan: {current_ticket['Loan_ID']}")
        
        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"], 
                                  index=["Open", "In Progress", "Resolved", "Closed"].index(current_ticket['Status']) if current_ticket['Status'] in ["Open", "In Progress", "Resolved", "Closed"] else 0)
        
        resolution_remarks = st.text_area("Resolution Remarks", value=current_ticket['Resolution_Remarks'] if current_ticket['Resolution_Remarks'] else "")
        
        date_closed_val = current_ticket['Date_Closed']
        
        close_ticket = st.checkbox("Close Ticket Now?")
        if close_ticket:
            date_closed_val = datetime.date.today().strftime('%Y-%m-%d')
            
        update_submit = st.form_submit_button("Update Ticket")
        
    if update_submit:
        try:
            execute_action(
                "UPDATE SupportTickets SET Status = ?, Resolution_Remarks = ?, Date_Closed = ? WHERE Ticket_ID = ?",
                (new_status, resolution_remarks, date_closed_val, selected_ticket_id)
            )
            st.success("Ticket updated successfully!")
            st.balloons()
        except Exception as e:
            st.error(f"Failed to update ticket: {e}")

def delete_ticket():
    customer = run_query("SELECT name FROM customers")['name'].tolist()
    st.subheader("Filter by Customer")
    selected_name = st.selectbox("Customer Name", customer)
    customer_id = get_customer_id_by_name(selected_name)
    
    tickets = run_query("SELECT Ticket_ID, Issue_Category, Status FROM SupportTickets WHERE Customer_ID = ?", (customer_id,))
    
    if tickets.empty:
        st.warning("No tickets found.")
        return
        
    tickets['display'] = tickets['Ticket_ID'].astype(str) + " - " + tickets['Issue_Category']
    ticket_list = tickets['display'].tolist()
    selected_ticket_display = st.selectbox("Select Ticket to Delete", ticket_list)
    target_id = selected_ticket_display.split(" - ")[0]
    
    if target_id:
        check_df = run_query("SELECT * FROM SupportTickets WHERE Ticket_ID = ?", (target_id,))
        if not check_df.empty:
            st.warning(f"CRITICAL: Deleting ticket {target_id}")
            st.dataframe(check_df)
            confirm = st.checkbox(f"Confirm deletion of {target_id}")
            
            if st.button("Confirm Delete"):
                if confirm:
                    try:
                        execute_action("DELETE FROM SupportTickets WHERE Ticket_ID = ?", (target_id,))
                        st.success(f"Ticket {target_id} deleted.")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

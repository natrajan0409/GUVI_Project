
import streamlit as st
import pandas as pd
from scripts.commonmethod import run_query

# Page Config
st.set_page_config(page_title="BankSight Dashboard", layout="wide")


class DataExplorer:
    def render(self, conn):
        st.title("Raw Data Viewer & Filter")
        
        try:
            tables = run_query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")['name'].tolist()
        except Exception:
            tables = ["customers", "branches", "accounts", "transactions", "loans", "creditcards", "SupportTickets"]

        table_name = st.selectbox("Select Table", tables)

        if table_name:
            if table_name not in tables:
                st.error("Invalid table selected.")
            else:
                try:
                    # Load all data (or a larger subset) for filtering
                    # Warning: production apps should filter in SQL. For this project size, pandas processing is fine.
                    df = run_query(f"SELECT * FROM {table_name}")
                    
                    st.write(f"Total Records: {len(df)}")
                    
                    # Filtering UI
                    with st.expander("Filter Data"):
                        columns = df.columns.tolist()
                        selected_column = st.selectbox("Select Column to Filter By", ["None"] + columns)
                        
                        if selected_column != "None":
                            unique_vals = df[selected_column].unique()
                            # Decide on filter type based on dtype
                            if len(unique_vals) < 50:
                                selected_vals = st.multiselect(f"Select values for {selected_column}", unique_vals)
                                if selected_vals:
                                    df = df[df[selected_column].isin(selected_vals)]
                            else:
                                # Text search or range?
                                filter_val = st.text_input(f"Search in {selected_column}")
                                if filter_val:
                                    df = df[df[selected_column].astype(str).str.contains(filter_val, case=False)]
                                    
                    st.dataframe(df, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Failed to load table {table_name}: {e}")
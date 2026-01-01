import streamlit as st
import sqlite3
import pandas as pd
import datetime
import pandas as pd
from scripts.commonmethod import run_query

# Page Config
st.set_page_config(page_title="BankSight Dashboard", layout="wide")


class DataExplorer:
    def render(self, conn):
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
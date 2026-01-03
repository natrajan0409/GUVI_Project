"""Home page for the BankSight Streamlit app.

Formatting only — no logic changes.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from scripts.commonmethod import  run_query 

# Page Config
st.set_page_config(page_title="BankSight Dashboard", layout="wide")


# Function to generate custom_id for new entries
class HomePage:
    def render(self, conn) -> None:
        st.title("Welcome to BankSight")
        st.write("Data successfully loaded. Use the sidebar to explore.")
        st.write("### Database Row Counts")
        for table in ["customers", "branches", "accounts", "transactions"]:
            try:
                count = run_query(f"SELECT COUNT(*) FROM {table}").iloc[0, 0]
            except Exception:
                count = 0
            st.metric(label=table.capitalize(), value=count)
        
        st.markdown("---")
        st.subheader("About Application")
        st.info(
            "BankSight Transaction Intelligence Dashboard is a comprehensive tool developed for banking analysts. "
            "It facilitates data operations (CRUD), analytical insights, and operational simulations."
        )
        st.markdown("Created by: Natrajan") # Placeholder for now

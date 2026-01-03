import streamlit as st
import sqlite3
import pandas as pd
import datetime
import pandas as pd
from scripts.home import HomePage
from scripts.export import DataExplorer
from scripts.Insights import InsightsPage
from scripts.crud import CRUDOperationsPage
from scripts.about import AboutPage

# Page Config
def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Home", "Explorer", "Insights", "CRUD", "About"])
    
    # Persistent Connection
    conn = sqlite3.connect("Database/BankSight.db", check_same_thread=False)

    # Dictionary mapping selection to Class instances
    pages = {
        "Home": HomePage(),
        "Explorer": DataExplorer(),
        "Insights": InsightsPage(),
        "CRUD": CRUDOperationsPage(),
        "About": AboutPage()  
    }

    # Execute the render method of the selected page
    pages[selection].render(conn)

if __name__ == "__main__":
    main()
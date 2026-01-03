# BankSight Transaction Intelligence Dashboard

**BankSight** is a comprehensive banking analytics and operations dashboard built with **Streamlit** and **Python**. It is designed for banking analysts to perform data operations (CRUD), visualize key insights, and simulate operational flows in a secure and modular environment.

---

## 🚀 Features

### 1. 📊 Interactive Insights
- **15+ Analytical Queries**: Visualize critical business metrics across multiple categories:
    - Customer & Account Analysis
    - Transaction Behavior (High-value, Fraud detection)
    - Loan Insights & Performance
    - Branch Performance
    - Support Ticket Resolution

### 2. 🛠️ CRUD Operations (Data Management)
Full management capability for the banking ecosystem.
- **Customers**: Add, Update, Delete customer profiles.
- **Accounts**:
    - **One-Account Rule**: Enforces single account per customer.
    - Real-time balance checks.
- **Transactions**:
    - Simulate Deposits, Withdrawals, Transfers.
    - **Logic Enforcement**: Prevents withdrawals if balance < ₹1,000.
    - **Types**: Loan Payments, Credit Card Payments, Debits.
- **Credit Cards**:
    - **Validation**: Prevents duplicate active card types.
    - **Unique Numbers**: Auto-generates globally unique card numbers.
- **Loans & Support Tickets**: fully integrated management.

### 3. 🔍 Data Explorer
- **Raw Data Viewer**: View underlying database tables.
- **Advanced Filtering**: Filter data by City, Amount, Date, Gender, etc., without writing SQL.
- **Security**: Protected against SQL Injection via strict table whitelisting.

---

## 🛠️ Technology Stack
- **Frontend/App**: Streamlit
- **Logic**: Python 3.x (Pandas, NumPy)
- **Database**: SQLite


---

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-repo/banksight.git
    cd banksight
    ```

2.  **Install Dependencies**
    Ensure you have Python installed. Then run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    streamlit run main.py
    ```

---

## 📂 Project Structure

```
GUVI_Project/
├── main.py                 # Application Entry Point
├── scripts/
│   ├── home.py             # Home Page
│   ├── about.py            # About Page
│   ├── export.py           # Data Explorer & Filtering
│   ├── Insights.py         # Analytical Queries
│   ├── crud.py             # CRUD Dispatcher
│   ├── commonmethod.py     # Database Utilities (Connection, Query execution)
│   └── crud_handlers/      # Modular Business Logic
│       ├── customers.py
│       ├── accounts.py
│       ├── transactions.py
│       ├── ...
├── Database/
│   └── BankSight.db        # SQLite Database
└── Data/                   # Raw Data Sources (CSVs, JSONs)
```

---

## 👨‍💻 Creator

**K. Natrajan** | Lead Automation Engineer

Specializing in robust automation frameworks and data integrity systems.
- **GitHub**: [Link](https://github.com/)
- **Expertise**: Selenium, API Automation, SQL Validation, Banking Domain.

---
*Built for the GUVI Project Capstone.*

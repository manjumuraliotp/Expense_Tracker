import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class PersonalExpenseTracker:
    """
    A robust Personal Expense Tracker and Financial Analytics Engine
    built using Pandas, NumPy, and Matplotlib.
    """
    def __init__(self, filename="personal_expenses.csv"):
        self.filename = filename
        self.valid_expense_categories = ['Food & Dining', 'Rent & Bills', 'Transportation',
                                         'Entertainment', 'Healthcare', 'Shopping', 'Miscellaneous']
        self.valid_income_categories = ['Salary', 'Freelance', 'Investments', 'Bonus', 'Other Income']
        self._initialize_storage()

    def _initialize_storage(self):
        """Create the CSV file with schema if it doesn't already exist."""
        if not os.path.exists(self.filename):
            df = pd.DataFrame(columns=[
                'transaction_id', 'date', 'type', 'category', 'amount', 'description'
            ])
            df.to_csv(self.filename, index=False)
            print(f"[INFO] Storage initialized: '{self.filename}' created.")

    def load_data(self):
        """Load and parse transactions using Pandas."""
        try:
            df = pd.read_csv(self.filename)
            if not df.empty:
                # Use format='mixed' for robustness, and then ensure consistency by normalizing to midnight
                df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce').dt.normalize()
                df['amount'] = pd.to_numeric(df['amount'])
                df = df.sort_values(by='date').reset_index(drop=True)
            return df
        except Exception as e:
            print(f"[ERROR] Failed to load data: {e}")
            return pd.DataFrame()

    def add_transaction(self, trans_type, category, amount, description="", date=None):
        """Add a single income or expense record."""
        trans_type = trans_type.capitalize()
        if trans_type not in ['Income', 'Expense']:
            raise ValueError("Transaction type must be 'Income' or 'Expense'.")

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if date is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        else:
            date_str = pd.to_datetime(date).strftime('%Y-%m-%d')

        df = self.load_data()
        next_id = 1001 if df.empty else df['transaction_id'].max() + 1

        new_record = pd.DataFrame([{
            'transaction_id': next_id,
            'date': date_str,
            'type': trans_type,
            'category': category,
            'amount': round(amount, 2),
            'description': description
        }])

        updated_df = pd.concat([df, new_record], ignore_index=True)
        # Convert the 'date' column to YYYY-MM-DD string format before saving to ensure consistent format in CSV
        updated_df['date'] = pd.to_datetime(updated_df['date'], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d')
        updated_df.to_csv(self.filename, index=False)
        print(f"[SUCCESS] Recorded: {trans_type} of ₹{amount:,.2f} under '{category}'.")

    def populate_sample_data(self, months=3):
        """Populate realistic test data for immediate analytics and portfolio demonstration."""
        np.random.seed(42)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        sample_records = []
        current_date = start_date
        t_id = 1001

        while current_date <= end_date:
            # 1. Monthly recurring salary on the 1st of each month
            if current_date.day == 1:
                sample_records.append({
                    'transaction_id': t_id,
                    'date': current_date.strftime('%Y-%m-%d'),
                    'type': 'Income',
                    'category': 'Salary',
                    'amount': 85000.0,
                    'description': 'Monthly Corporate Salary'
                })
                t_id += 1

                # Rent and major utility bills on the 2nd
                sample_records.append({
                    'transaction_id': t_id,
                    'date': (current_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'type': 'Expense',
                    'category': 'Rent & Bills',
                    'amount': 26000.0,
                    'description': 'Apartment Rent & Electricity'
                })
                t_id += 1

            # 2. Daily variable transactions (Food, Travel, Shopping)
            daily_events = np.random.poisson(lam=1.2)
            for _ in range(daily_events):
                cat = np.random.choice(self.valid_expense_categories, p=[0.35, 0.05, 0.25, 0.15, 0.05, 0.10, 0.05])
                if cat == 'Food & Dining':
                    amt = np.random.uniform(150, 1400)
                elif cat == 'Transportation':
                    amt = np.random.uniform(80, 650)
                elif cat == 'Shopping':
                    amt = np.random.uniform(800, 4500)
                elif cat == 'Entertainment':
                    amt = np.random.uniform(300, 1800)
                else:
                    amt = np.random.uniform(200, 1500)

                sample_records.append({
                    'transaction_id': t_id,
                    'date': current_date.strftime('%Y-%m-%d'),
                    'type': 'Expense',
                    'category': cat,
                    'amount': round(amt, 2),
                    'description': f'Daily {cat}'
                })
                t_id += 1

            # 3. Occasional freelance income (10% chance per week)
            if np.random.rand() < 0.04:
                sample_records.append({
                    'transaction_id': t_id,
                    'date': current_date.strftime('%Y-%m-%d'),
                    'type': 'Income',
                    'category': 'Freelance',
                    'amount': round(np.random.uniform(8000, 22000), 2),
                    'description': 'Consulting Project Payout'
                })
                t_id += 1

            current_date += timedelta(days=1)

        pd.DataFrame(sample_records).to_csv(self.filename, index=False)
        print(f"[SUCCESS] Test database populated with {len(sample_records)} realistic transactions!")

    def generate_summary(self):
        """Compute key financial KPIs: Total Inflow, Outflow, Net Savings, and Savings Rate."""
        df = self.load_data()
        if df.empty:
            print("[INFO] No transaction records available to summarize.")
            return

        total_income = df[df['type'] == 'Income']['amount'].sum()
        total_expense = df[df['type'] == 'Expense']['amount'].sum()
        net_savings = total_income - total_expense
        savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0

        # Category Breakdown
        expense_df = df[df['type'] == 'Expense']
        category_breakdown = expense_df.groupby('category')['amount'].agg(
            Total_Spent='sum',
            Transaction_Count='count',
            Avg_Per_Transaction='mean'
        ).sort_values(by='Total_Spent', ascending=False)

        category_breakdown['Share_%'] = (category_breakdown['Total_Spent'] / total_expense * 100).round(1)

        print("\n" + "="*55)
        print("          EXECUTIVE FINANCIAL HEALTH REPORT          ")
        print("="*55)
        print(f" Total Inflow (Income)    : ₹{total_income:,.2f}")
        print(f" Total Outflow (Expenses) : ₹{total_expense:,.2f}")
        print(f" Net Savings              : ₹{net_savings:,.2f}")
        print(f" Savings Rate             : {savings_rate:.1f}%")
        print("-" * 55)
        print("Top Expense Categories by Volume:")
        print(category_breakdown[['Total_Spent', 'Share_%', 'Transaction_Count']])
        print("="*55 + "\n")
        return category_breakdown

    def visualize_dashboard(self, save_path="personal_financial_dashboard.png"):
        """
        Generate a 3-panel visual dashboard displaying:
        1. Expense Category Breakdown (Donut Chart)
        2. Monthly Income vs. Expense Comparison (Grouped Bar Chart)
        3. Cumulative Net Cash Flow (Line / Area Chart)
        """
        df = self.load_data()
        if df.empty:
            print("[WARNING] Insufficient data to render visual dashboard.")
            return

        df['year_month'] = df['date'].dt.to_period('M').astype(str)

        # Matplotlib Styling
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
        fig = plt.figure(figsize=(16, 10))

        # ---------------------------------------------------------
        # Subplot 1: Expense Category Donut Chart
        # ---------------------------------------------------------
        ax1 = plt.subplot2grid((2, 2), (0, 0))
        expense_df = df[df['type'] == 'Expense']
        cat_data = expense_df.groupby('category')['amount'].sum().sort_values(ascending=False)

        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(cat_data)))
        wedges, texts, autotexts = ax1.pie(
            cat_data, labels=cat_data.index, autopct='%1.1f%%',
            startangle=140, colors=colors, pctdistance=0.75,
            wedgeprops=dict(width=0.45, edgecolor='w', linewidth=2)
        )
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_weight('bold')
        ax1.set_title('Expense Distribution by Category (%)', fontsize=12, fontweight='bold', pad=15)

        # ---------------------------------------------------------
        # Subplot 2: Monthly Inflow vs. Outflow (Grouped Bars)
        # ---------------------------------------------------------
        ax2 = plt.subplot2grid((2, 2), (0, 1))
        monthly_summary = df.pivot_table(index='year_month', columns='type', values='amount', aggfunc='sum', fill_value=0)

        # Ensure both columns exist
        if 'Income' not in monthly_summary: monthly_summary['Income'] = 0
        if 'Expense' not in monthly_summary: monthly_summary['Expense'] = 0

        bar_width = 0.35
        x = np.arange(len(monthly_summary.index))

        ax2.bar(x - bar_width/2, monthly_summary['Income'], width=bar_width, label='Income (Inflow)', color='#2a9d8f')
        ax2.bar(x + bar_width/2, monthly_summary['Expense'], width=bar_width, label='Expense (Outflow)', color='#e76f51')

        ax2.set_title('Monthly Inflow vs. Outflow Comparison', fontsize=12, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(monthly_summary.index, rotation=25)
        ax2.set_ylabel('Amount (₹)')
        ax2.legend()

        # ---------------------------------------------------------
        # Subplot 3: Cumulative Net Cash Balance Over Time
        # ---------------------------------------------------------
        ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)

        # Signed amounts for cash flow tracking
        df['signed_amount'] = np.where(df['type'] == 'Income', df['amount'], -df['amount'])
        daily_cashflow = df.groupby('date')['signed_amount'].sum().reset_index()
        daily_cashflow['cumulative_balance'] = daily_cashflow['signed_amount'].cumsum()

        ax3.plot(daily_cashflow['date'], daily_cashflow['cumulative_balance'],
                 color='#1d3557', linewidth=2.5, label='Net Available Savings')
        ax3.fill_between(daily_cashflow['date'], daily_cashflow['cumulative_balance'],
                         color='#457b9d', alpha=0.25)

        ax3.set_title('Cumulative Net Savings Trajectory Over Time', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Cumulative Surplus (₹)')
        ax3.set_xlabel('Timeline')
        ax3.legend(loc='upper left')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.show()
        print(f"[SUCCESS] Financial Dashboard successfully rendered and saved to '{save_path}'!")


# =========================================================
# Execution Entry Point
# =========================================================
if __name__ == "__main__":
    tracker = PersonalExpenseTracker("personal_expenses.csv")

    # 1. Populate realistic demonstration data (90 days of transactions)
    tracker.populate_sample_data(months=3)

    # 2. Add an ad-hoc live transaction to test user input
    tracker.add_transaction("Expense", "Food & Dining", 1250.0, "Weekend Team Dinner")
    tracker.add_transaction("Income", "Investments", 4500.0, "Dividend Credit")

    # 3. Compute Financial KPIs
    tracker.generate_summary()

    # 4. Generate Visual Dashboard
    tracker.visualize_dashboard("personal_financial_dashboard.png")
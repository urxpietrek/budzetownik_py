import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns

import pandas as pd

import base64
from io import BytesIO

def create_charts(expenses):
    category_totals = {}

    def _create_pie():
        for expense in expenses:
            category_totals[expense.category] = category_totals.get(expense.category, 0) + expense.amount

        categories = list(category_totals.keys())
        amounts = list(category_totals.values())

        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        wedges, texts, autotexts = ax.pie(
            amounts, 
            labels=categories, 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=plt.cm.Pastel2.colors,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1}
        )

        plt.setp(texts, size=10, weight="bold")
        plt.setp(autotexts, size=10, weight="bold", color="white")

        ax.set_title(
            'Expenses by Category',
            fontsize=14,
            weight='bold',
            color='#333'
        )

        fig.patch.set_facecolor('#f8f9fa')
        ax.axis('equal')

        tmpfile = BytesIO()
        fig.savefig(tmpfile, format='png', transparent=True)

        plt.close(fig)
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
        
        return encoded

    def _create_bar():
        data = [{'date': expense.date, 'amount': expense.amount} for expense in expenses]
        df = pd.DataFrame(data)
        
        if df.empty:
            return None

        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
        df['year_month'] = df['date'].dt.to_period('M').astype(str)

        grouped = df.groupby('year_month')['amount'].sum().reset_index()

        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        sns.barplot(
            data=grouped,
            x='year_month', 
            y='amount', 
            palette='coolwarm', 
            ax=ax
        )

        ax.set_title('Monthly Expenses', fontsize=14, weight='bold')
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Total Expenses (PLN)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)

        fig.patch.set_facecolor('#f8f9fa')
        sns.despine()

        tmpfile = BytesIO()
        fig.savefig(tmpfile, format='png', transparent=True)

        plt.close(fig)
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
        
        return encoded

    return _create_pie(), _create_bar()

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Connect to SQLite database
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

# Create the expenses table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL
                  )''')
conn.commit()

max_budget = None  # Global variable to store the maximum budget
budget_start_date = None  # Global variable to store the budget start date
budget_end_date = None    # Global variable to store the budget end date

def set_budget():
    global max_budget, budget_start_date, budget_end_date
    try:
        max_budget = float(budget_entry.get())
        budget_start_date = start_date_entry.get()
        budget_end_date = end_date_entry.get()
        validate_date(budget_start_date)
        validate_date(budget_end_date)
        budget_label.config(text=f"Maximum Budget: {max_budget:.2f} from {budget_start_date} to {budget_end_date}")
        check_budget()
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for the budget.")
    except ValueError as ve:
        messagebox.showerror("Invalid Date", str(ve))

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Date {date_str} is not in the correct format (YYYY-MM-DD)")

def add_expense():
    date = date_entry.get()
    category = category_entry.get()
    amount = amount_entry.get()

    if date and category and amount:
        try:
            amount = float(amount)
            validate_date(date)
            cursor.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)", (date, category, amount))
            conn.commit()
            status_label.config(text="Expense added successfully!", fg="green")
            date_entry.delete(0, tk.END)
            category_entry.delete(0, tk.END)
            amount_entry.delete(0, tk.END)
            view_expenses()
            check_budget()
        except ValueError:
            status_label.config(text="Please enter a valid amount and date!", fg="red")
    else:
        status_label.config(text="Please fill all the fields!", fg="red")

def delete_expense():
    selected_item = expenses_tree.selection()
    if selected_item:
        item_text = expenses_tree.item(selected_item, "values")
        date, category, amount = item_text
        cursor.execute("DELETE FROM expenses WHERE date = ? AND category = ? AND amount = ?", (date, category, amount))
        conn.commit()
        status_label.config(text="Expense deleted successfully!", fg="green")
        view_expenses()
        check_budget()
    else:
        status_label.config(text="Please select an expense to delete!", fg="red")

def view_expenses():
    global expenses_tree
    expenses_tree.delete(*expenses_tree.get_children())
    cursor.execute("SELECT date, category, amount FROM expenses")
    total_expense = 0
    for row in cursor.fetchall():
        expenses_tree.insert("", tk.END, values=row)
        total_expense += row[2]  # row[2] is the amount
    total_label.config(text=f"Total Expense: {total_expense:.2f}")

def check_budget():
    global max_budget, budget_start_date, budget_end_date
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?", (budget_start_date, budget_end_date))
    total_expense = cursor.fetchone()[0] or 0  # Fetch the sum, handle None with 0
    if max_budget is not None:
        remaining_budget = max_budget - total_expense
        if remaining_budget < 0:
            budget_status_label.config(text=f"Warning: You've exceeded your budget by {abs(remaining_budget):.2f}!", fg="red")
        else:
            budget_status_label.config(text=f"Remaining Budget: {remaining_budget:.2f}", fg="green")

def plot_expenses():
    cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE date BETWEEN ? AND ? GROUP BY category", (budget_start_date, budget_end_date))
    data = cursor.fetchall()

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    # Create a figure and axis
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    # Create the bar chart
    ax.bar(categories, amounts)

    # Set chart title and labels
    ax.set_title(f'Total Expenses by Category ({budget_start_date} to {budget_end_date})')
    ax.set_ylabel('Amount')
    ax.set_xlabel('Category')

    return fig

def show_graph():
    # Create a new window for the graph
    graph_window = tk.Toplevel(root)
    graph_window.title("Expense Graph")

    # Get the figure from plot_expenses
    fig = plot_expenses()

    # Create the canvas to display the graph in the new window
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Create the main application window
root = tk.Tk()
root.title("Expense Tracker")

# Create labels and entries for adding expenses
date_label = tk.Label(root, text="Date (YYYY-MM-DD):")
date_label.grid(row=0, column=0, padx=5, pady=5)
date_entry = tk.Entry(root)
date_entry.grid(row=0, column=1, padx=5, pady=5)

category_label = tk.Label(root, text="Category:")
category_label.grid(row=1, column=0, padx=5, pady=5)
category_entry = tk.Entry(root)
category_entry.grid(row=1, column=1, padx=5, pady=5)

amount_label = tk.Label(root, text="Amount:")
amount_label.grid(row=2, column=0, padx=5, pady=5)
amount_entry = tk.Entry(root)
amount_entry.grid(row=2, column=1, padx=5, pady=5)

add_button = tk.Button(root, text="Add Expense", command=add_expense)
add_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

# Budget section
budget_label = tk.Label(root, text="Set Maximum Budget:")
budget_label.grid(row=4, column=0, padx=5, pady=5, columnspan=2)

budget_entry = tk.Entry(root)
budget_entry.grid(row=4, column=2, padx=5, pady=5)

start_date_label = tk.Label(root, text="Start Date (YYYY-MM-DD):")
start_date_label.grid(row=5, column=0, padx=5, pady=5)

start_date_entry = tk.Entry(root)
start_date_entry.grid(row=5, column=1, padx=5, pady=5)

end_date_label = tk.Label(root, text="End Date (YYYY-MM-DD):")
end_date_label.grid(row=5, column=2, padx=5, pady=5)

end_date_entry = tk.Entry(root)
end_date_entry.grid(row=5, column=3, padx=5, pady=5)

set_budget_button = tk.Button(root, text="Set Budget", command=set_budget)
set_budget_button.grid(row=4, column=4, padx=5, pady=5, rowspan=2)

# Create a treeview to display expenses 
columns = ("Date", "Category", "Amount")
expenses_tree = ttk.Treeview(root, columns=columns, show="headings")
expenses_tree.heading("Date", text="Date")
expenses_tree.heading("Category", text="Category")
expenses_tree.heading("Amount", text="Amount")
expenses_tree.grid(row=6, column=0, columnspan=5, padx=5, pady=5)

# Create a label to display the total expense
total_label = tk.Label(root, text="")
total_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

# Create a label to show the status of expense addition and deletion
status_label = tk.Label(root, text="", fg="green")
status_label.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

# Create a label to display the remaining budget or warning
budget_status_label = tk.Label(root, text="", fg="green")
budget_status_label.grid(row=9, column=0, columnspan=5, padx=5, pady=5)

# Create buttons to view and delete expenses
view_button = tk.Button(root, text="View Expenses", command=view_expenses)
view_button.grid(row=10, column=0, padx=5, pady=10)

delete_button = tk.Button(root, text="Delete Expense", command=delete_expense)
delete_button.grid(row=10, column=1, padx=5, pady=10)

# Add button to show graph
graph_button = tk.Button(root, text="Show Graph", command=show_graph)
graph_button.grid(row=10, column=2, columnspan=2, padx=5, pady=10)

# Display existing expenses on application start
view_expenses()

root.mainloop()

# Close the database connection when the application closes
conn.close()

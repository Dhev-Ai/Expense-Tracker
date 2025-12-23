"""
Expense View
Add, edit, and manage expenses
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, date
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import COLORS, FONTS, DIMENSIONS
from utils.helpers import format_currency, PAYMENT_METHODS
from controllers.expense_controller import ExpenseController


class ExpenseListView(tk.Frame):
    """View for listing and managing expenses"""
    
    def __init__(self, parent, user, on_navigate):
        super().__init__(parent, bg=COLORS['bg_secondary'])
        self.parent = parent
        self.user = user
        self.on_navigate = on_navigate
        self.expenses = []
        self.categories = []
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create expense list widgets"""
        # Header
        header = tk.Frame(self, bg=COLORS['bg_secondary'])
        header.pack(fill=tk.X, padx=30, pady=20)
        
        tk.Label(
            header,
            text="💳 My Expenses",
            font=FONTS['heading'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        # Add button
        add_btn = tk.Button(
            header,
            text="➕ Add New",
            font=FONTS['button'],
            bg=COLORS['primary'],
            fg=COLORS['text_white'],
            activebackground=COLORS['primary_dark'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=8,
            command=lambda: self.on_navigate('add_expense')
        )
        add_btn.pack(side=tk.RIGHT)
        
        # Filters section
        filter_frame = tk.Frame(self, bg=COLORS['card_bg'])
        filter_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        
        filter_inner = tk.Frame(filter_frame, bg=COLORS['card_bg'])
        filter_inner.pack(fill=tk.X, padx=20, pady=15)
        
        # Search
        search_frame = tk.Frame(filter_inner, bg=COLORS['card_bg'])
        search_frame.pack(side=tk.LEFT)
        
        tk.Label(
            search_frame,
            text="🔍",
            font=FONTS['body'],
            bg=COLORS['card_bg']
        ).pack(side=tk.LEFT)
        
        self.search_entry = tk.Entry(
            search_frame,
            font=FONTS['body'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            width=25
        )
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0), ipady=8)
        self.search_entry.insert(0, "Search expenses...")
        self.search_entry.bind('<FocusIn>', lambda e: self.search_entry.delete(0, tk.END) if self.search_entry.get() == "Search expenses..." else None)
        self.search_entry.bind('<FocusOut>', lambda e: self.search_entry.insert(0, "Search expenses...") if not self.search_entry.get() else None)
        self.search_entry.bind('<Return>', lambda e: self.search_expenses())
        
        # Category filter
        cat_frame = tk.Frame(filter_inner, bg=COLORS['card_bg'])
        cat_frame.pack(side=tk.LEFT, padx=(30, 0))
        
        tk.Label(
            cat_frame,
            text="Category:",
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.LEFT)
        
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(
            cat_frame,
            textvariable=self.category_var,
            state='readonly',
            width=20
        )
        self.category_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_expenses())
        
        # Date range
        date_frame = tk.Frame(filter_inner, bg=COLORS['card_bg'])
        date_frame.pack(side=tk.LEFT, padx=(30, 0))
        
        tk.Label(
            date_frame,
            text="From:",
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.LEFT)
        
        self.start_date = DateEntry(
            date_frame,
            width=12,
            background=COLORS['primary'],
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.start_date.pack(side=tk.LEFT, padx=(5, 10))
        self.start_date.set_date(datetime.now().replace(day=1))
        
        tk.Label(
            date_frame,
            text="To:",
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.LEFT)
        
        self.end_date = DateEntry(
            date_frame,
            width=12,
            background=COLORS['primary'],
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.end_date.pack(side=tk.LEFT, padx=(5, 0))
        
        # Filter button
        filter_btn = tk.Button(
            filter_inner,
            text="Apply Filter",
            font=FONTS['body'],
            bg=COLORS['secondary'],
            fg=COLORS['text_white'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.filter_expenses
        )
        filter_btn.pack(side=tk.RIGHT)
        
        # Expenses list container
        list_container = tk.Frame(self, bg=COLORS['card_bg'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))
        
        # Create Treeview
        columns = ('date', 'category', 'description', 'amount', 'payment')
        self.tree = ttk.Treeview(list_container, columns=columns, show='headings', height=15)
        
        # Define headings
        self.tree.heading('date', text='Date')
        self.tree.heading('category', text='Category')
        self.tree.heading('description', text='Description')
        self.tree.heading('amount', text='Amount')
        self.tree.heading('payment', text='Payment Method')
        
        # Define columns
        self.tree.column('date', width=100, anchor='center')
        self.tree.column('category', width=150, anchor='w')
        self.tree.column('description', width=250, anchor='w')
        self.tree.column('amount', width=120, anchor='e')
        self.tree.column('payment', width=120, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=20, padx=(0, 20))
        
        # Bind double-click for edit
        self.tree.bind('<Double-1>', self.on_edit)
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="✏️ Edit", command=self.edit_selected)
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_selected)
        
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Bottom action buttons
        action_frame = tk.Frame(list_container, bg=COLORS['card_bg'])
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Total display
        self.total_label = tk.Label(
            action_frame,
            text="Total: ₹0.00",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['primary']
        )
        self.total_label.pack(side=tk.LEFT)
        
        # Delete button
        delete_btn = tk.Button(
            action_frame,
            text="🗑️ Delete Selected",
            font=FONTS['body'],
            bg=COLORS['error'],
            fg=COLORS['text_white'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.delete_selected
        )
        delete_btn.pack(side=tk.RIGHT)
        
        # Edit button
        edit_btn = tk.Button(
            action_frame,
            text="✏️ Edit Selected",
            font=FONTS['body'],
            bg=COLORS['accent'],
            fg=COLORS['text_white'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.edit_selected
        )
        edit_btn.pack(side=tk.RIGHT, padx=(0, 10))
    
    def load_data(self):
        """Load expenses and categories"""
        # Load categories
        self.categories = ExpenseController.get_categories()
        cat_names = ["All"] + [c.category_name for c in self.categories]
        self.category_combo['values'] = cat_names
        
        # Load expenses
        self.load_expenses()
    
    def load_expenses(self, start_date=None, end_date=None, category_id=None):
        """Load expenses with optional filters"""
        self.expenses = ExpenseController.get_expenses(
            self.user.user_id,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id
        )
        self.populate_tree()
    
    def populate_tree(self):
        """Populate treeview with expenses"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add expenses
        total = 0
        for expense in self.expenses:
            self.tree.insert('', tk.END, iid=expense.expense_id, values=(
                expense.expense_date,
                f"{expense.category_icon} {expense.category_name.split(' ', 1)[-1] if expense.category_name else ''}",
                expense.description or '',
                format_currency(expense.amount),
                expense.payment_method or ''
            ))
            total += float(expense.amount) if expense.amount else 0
        
        # Update total
        self.total_label.config(text=f"Total: {format_currency(total)}")
    
    def filter_expenses(self):
        """Apply filters to expense list"""
        start = self.start_date.get_date()
        end = self.end_date.get_date()
        
        category_id = None
        cat_name = self.category_var.get()
        if cat_name != "All":
            for cat in self.categories:
                if cat.category_name == cat_name:
                    category_id = cat.category_id
                    break
        
        self.load_expenses(start, end, category_id)
    
    def search_expenses(self):
        """Search expenses"""
        search_term = self.search_entry.get().strip()
        if search_term and search_term != "Search expenses...":
            self.expenses = ExpenseController.search_expenses(self.user.user_id, search_term)
            self.populate_tree()
        else:
            self.load_expenses()
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_edit(self, event):
        """Handle double-click to edit"""
        self.edit_selected()
    
    def edit_selected(self):
        """Edit selected expense"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an expense to edit")
            return
        
        expense_id = selection[0]
        self.show_edit_dialog(expense_id)
    
    def delete_selected(self):
        """Delete selected expense"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            expense_id = selection[0]
            success, message = ExpenseController.delete_expense(expense_id, self.user.user_id)
            
            if success:
                messagebox.showinfo("Success", message)
                self.load_expenses()
            else:
                messagebox.showerror("Error", message)
    
    def show_edit_dialog(self, expense_id):
        """Show edit dialog"""
        expense = ExpenseController.get_expense_by_id(expense_id, self.user.user_id)
        if not expense:
            messagebox.showerror("Error", "Expense not found")
            return
        
        # Create edit dialog
        dialog = tk.Toplevel(self)
        dialog.title("Edit Expense")
        dialog.geometry("450x500")
        dialog.configure(bg=COLORS['bg_primary'])
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 450) // 2
        y = (dialog.winfo_screenheight() - 500) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        tk.Label(
            dialog,
            text="✏️ Edit Expense",
            font=FONTS['heading_small'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(pady=(20, 20))
        
        # Form
        form = tk.Frame(dialog, bg=COLORS['bg_primary'])
        form.pack(fill=tk.X, padx=30)
        
        # Category
        tk.Label(
            form,
            text="Category",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        ).pack(anchor='w')
        
        cat_var = tk.StringVar(value=expense.category_name)
        cat_combo = ttk.Combobox(
            form,
            textvariable=cat_var,
            values=[c.category_name for c in self.categories],
            state='readonly',
            width=35
        )
        cat_combo.pack(fill=tk.X, pady=(5, 15))
        
        # Amount
        tk.Label(
            form,
            text="Amount (₹)",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        ).pack(anchor='w')
        
        amount_entry = tk.Entry(
            form,
            font=FONTS['body_large'],
            bg=COLORS['bg_tertiary'],
            relief=tk.FLAT
        )
        amount_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        amount_entry.insert(0, str(expense.amount))
        
        # Description
        tk.Label(
            form,
            text="Description",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        ).pack(anchor='w')
        
        desc_entry = tk.Entry(
            form,
            font=FONTS['body_large'],
            bg=COLORS['bg_tertiary'],
            relief=tk.FLAT
        )
        desc_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        desc_entry.insert(0, expense.description or '')
        
        # Date
        tk.Label(
            form,
            text="Date",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        ).pack(anchor='w')
        
        date_entry = DateEntry(
            form,
            width=35,
            background=COLORS['primary'],
            foreground='white',
            date_pattern='yyyy-mm-dd'
        )
        date_entry.pack(fill=tk.X, pady=(5, 15))
        date_entry.set_date(expense.expense_date)
        
        # Payment method
        tk.Label(
            form,
            text="Payment Method",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        ).pack(anchor='w')
        
        payment_var = tk.StringVar(value=expense.payment_method or 'Cash')
        payment_combo = ttk.Combobox(
            form,
            textvariable=payment_var,
            values=PAYMENT_METHODS,
            state='readonly',
            width=35
        )
        payment_combo.pack(fill=tk.X, pady=(5, 20))
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=COLORS['bg_primary'])
        btn_frame.pack(fill=tk.X, padx=30, pady=20)
        
        def save_changes():
            # Get category ID
            cat_id = None
            for cat in self.categories:
                if cat.category_name == cat_var.get():
                    cat_id = cat.category_id
                    break
            
            success, message = ExpenseController.update_expense(
                expense_id,
                self.user.user_id,
                category_id=cat_id,
                amount=amount_entry.get(),
                description=desc_entry.get(),
                expense_date=date_entry.get_date(),
                payment_method=payment_var.get()
            )
            
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
                self.load_expenses()
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=FONTS['button'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            width=15,
            command=dialog.destroy
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="Save Changes",
            font=FONTS['button'],
            bg=COLORS['primary'],
            fg=COLORS['text_white'],
            relief=tk.FLAT,
            width=15,
            command=save_changes
        ).pack(side=tk.RIGHT)
    
    def refresh(self):
        """Refresh expense list"""
        self.load_expenses()


class AddExpenseView(tk.Frame):
    """View for adding new expense"""
    
    def __init__(self, parent, user, on_navigate, on_success=None):
        super().__init__(parent, bg=COLORS['bg_secondary'])
        self.parent = parent
        self.user = user
        self.on_navigate = on_navigate
        self.on_success = on_success
        self.categories = []
        
        self.create_widgets()
        self.load_categories()
    
    def create_widgets(self):
        """Create add expense form"""
        # Header
        header = tk.Frame(self, bg=COLORS['bg_secondary'])
        header.pack(fill=tk.X, padx=30, pady=20)
        
        tk.Label(
            header,
            text="➕ Add New Expense",
            font=FONTS['heading'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        # Form card
        card = tk.Frame(self, bg=COLORS['card_bg'])
        card.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # Form container
        form = tk.Frame(card, bg=COLORS['card_bg'])
        form.pack(padx=40, pady=40)
        
        # Two column layout
        left_col = tk.Frame(form, bg=COLORS['card_bg'])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 30))
        
        right_col = tk.Frame(form, bg=COLORS['card_bg'])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH)
        
        # === LEFT COLUMN ===
        
        # Amount (prominent)
        tk.Label(
            left_col,
            text="💰 Amount *",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(anchor='w')
        
        amount_frame = tk.Frame(left_col, bg=COLORS['card_bg'])
        amount_frame.pack(fill=tk.X, pady=(10, 20))
        
        tk.Label(
            amount_frame,
            text="₹",
            font=FONTS['heading'],
            bg=COLORS['card_bg'],
            fg=COLORS['primary']
        ).pack(side=tk.LEFT)
        
        self.amount_entry = tk.Entry(
            amount_frame,
            font=FONTS['heading'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            width=15
        )
        self.amount_entry.pack(side=tk.LEFT, padx=(10, 0), ipady=10)
        self.amount_entry.focus()
        
        # Category
        tk.Label(
            left_col,
            text="📁 Category *",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(anchor='w', pady=(10, 0))
        
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            left_col,
            textvariable=self.category_var,
            state='readonly',
            font=FONTS['body_large'],
            width=30
        )
        self.category_combo.pack(fill=tk.X, pady=(10, 20))
        
        # Description
        tk.Label(
            left_col,
            text="📝 Description *",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(anchor='w', pady=(10, 0))
        
        self.desc_entry = tk.Entry(
            left_col,
            font=FONTS['body_large'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            width=35
        )
        self.desc_entry.pack(fill=tk.X, pady=(10, 20), ipady=10)
        
        # === RIGHT COLUMN ===
        
        # Date
        tk.Label(
            right_col,
            text="📅 Date *",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(anchor='w')
        
        self.date_entry = DateEntry(
            right_col,
            font=FONTS['body_large'],
            background=COLORS['primary'],
            foreground='white',
            date_pattern='yyyy-mm-dd',
            width=28
        )
        self.date_entry.pack(fill=tk.X, pady=(10, 20))
        
        # Payment method
        tk.Label(
            right_col,
            text="💳 Payment Method",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(anchor='w', pady=(10, 0))
        
        self.payment_var = tk.StringVar(value='Cash')
        self.payment_combo = ttk.Combobox(
            right_col,
            textvariable=self.payment_var,
            values=PAYMENT_METHODS,
            state='readonly',
            font=FONTS['body_large'],
            width=28
        )
        self.payment_combo.pack(fill=tk.X, pady=(10, 20))
        
        # Notes
        tk.Label(
            right_col,
            text="📋 Notes (Optional)",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(anchor='w', pady=(10, 0))
        
        self.notes_text = tk.Text(
            right_col,
            font=FONTS['body'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            width=30,
            height=4
        )
        self.notes_text.pack(fill=tk.X, pady=(10, 20))
        
        # Buttons
        btn_frame = tk.Frame(card, bg=COLORS['card_bg'])
        btn_frame.pack(fill=tk.X, padx=40, pady=(0, 40))
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=FONTS['button'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            width=15,
            height=2,
            cursor='hand2',
            command=lambda: self.on_navigate('expenses')
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="Save & Add Another",
            font=FONTS['button'],
            bg=COLORS['secondary'],
            fg=COLORS['text_white'],
            relief=tk.FLAT,
            width=18,
            height=2,
            cursor='hand2',
            command=lambda: self.save_expense(add_another=True)
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(
            btn_frame,
            text="Save Expense",
            font=FONTS['button'],
            bg=COLORS['primary'],
            fg=COLORS['text_white'],
            relief=tk.FLAT,
            width=15,
            height=2,
            cursor='hand2',
            command=self.save_expense
        ).pack(side=tk.RIGHT)
    
    def load_categories(self):
        """Load expense categories"""
        self.categories = ExpenseController.get_categories()
        cat_display = []
        for c in self.categories:
            name = c.category_name if c.category_name else 'Unknown'
            # Category name already includes emoji (e.g., '🍔 Food & Dining')
            # Just use the name directly without adding icon again
            cat_display.append(name)
        self.category_combo['values'] = cat_display
        if cat_display:
            self.category_combo.current(0)
    
    def save_expense(self, add_another=False):
        """Save the expense"""
        # Get category ID
        cat_index = self.category_combo.current()
        if cat_index < 0:
            messagebox.showerror("Error", "Please select a category")
            return
        
        category_id = self.categories[cat_index].category_id
        
        # Get other values
        amount = self.amount_entry.get().strip()
        description = self.desc_entry.get().strip()
        expense_date = self.date_entry.get_date()
        payment_method = self.payment_var.get()
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        # Validate
        if not amount:
            messagebox.showerror("Error", "Please enter an amount")
            self.amount_entry.focus()
            return
        
        if not description:
            messagebox.showerror("Error", "Please enter a description")
            self.desc_entry.focus()
            return
        
        # Save
        success, message, expense = ExpenseController.add_expense(
            user_id=self.user.user_id,
            category_id=category_id,
            amount=amount,
            description=description,
            expense_date=expense_date,
            payment_method=payment_method,
            notes=notes if notes else None
        )
        
        if success:
            messagebox.showinfo("Success", message)
            
            if add_another:
                # Clear form for next entry
                self.amount_entry.delete(0, tk.END)
                self.desc_entry.delete(0, tk.END)
                self.notes_text.delete("1.0", tk.END)
                self.amount_entry.focus()
            else:
                self.on_navigate('expenses')
            
            if self.on_success:
                self.on_success()
        else:
            messagebox.showerror("Error", message)

"""
Budget View
Comprehensive budget management with category budgets, tracking, and alerts
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import COLORS, FONTS, CHART_COLORS
from utils.helpers import format_currency
from controllers.expense_controller import ExpenseController

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class BudgetView(tk.Frame):
    """Budget management and tracking view"""
    
    def __init__(self, parent, user, on_navigate):
        super().__init__(parent, bg=COLORS['bg_secondary'])
        self.parent = parent
        self.user = user
        self.on_navigate = on_navigate
        self.budgets = {}  # category_id: budget_amount
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create budget widgets"""
        # Main scrollable container
        canvas = tk.Canvas(self, bg=COLORS['bg_secondary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_secondary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Content
        content = tk.Frame(self.scrollable_frame, bg=COLORS['bg_secondary'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Header
        self.create_header(content)
        
        # Overall budget card
        self.overall_frame = tk.Frame(content, bg=COLORS['card_bg'])
        self.overall_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Budget chart
        self.chart_frame = tk.Frame(content, bg=COLORS['card_bg'])
        self.chart_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Category budgets grid
        self.categories_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        self.categories_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Quick tips
        self.tips_frame = tk.Frame(content, bg=COLORS['card_bg'])
        self.tips_frame.pack(fill=tk.X, pady=(20, 0))
    
    def create_header(self, parent):
        """Create header with title and actions"""
        header = tk.Frame(parent, bg=COLORS['bg_secondary'])
        header.pack(fill=tk.X)
        
        # Left - Title
        left = tk.Frame(header, bg=COLORS['bg_secondary'])
        left.pack(side=tk.LEFT)
        
        tk.Label(
            left,
            text="🎯 Budget Management",
            font=FONTS['heading'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        ).pack(anchor='w')
        
        tk.Label(
            left,
            text=f"Track and manage your spending limits • {datetime.now().strftime('%B %Y')}",
            font=FONTS['body'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary']
        ).pack(anchor='w')
        
        # Right - Actions
        right = tk.Frame(header, bg=COLORS['bg_secondary'])
        right.pack(side=tk.RIGHT)
        
        # Save button
        save_btn = tk.Button(
            right,
            text="💾 Save Budgets",
            font=FONTS['button'],
            bg=COLORS['primary'],
            fg=COLORS['text_white'],
            activebackground=COLORS['primary_dark'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10,
            command=self.save_all_budgets
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        save_btn.bind('<Enter>', lambda e: save_btn.config(bg=COLORS['primary_dark']))
        save_btn.bind('<Leave>', lambda e: save_btn.config(bg=COLORS['primary']))
        
        # Reset button
        reset_btn = tk.Button(
            right,
            text="🔄 Reset",
            font=FONTS['button'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['border'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10,
            command=self.reset_budgets
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    def create_overall_budget_card(self, data):
        """Create overall budget summary card"""
        # Clear existing
        for widget in self.overall_frame.winfo_children():
            widget.destroy()
        
        inner = tk.Frame(self.overall_frame, bg=COLORS['card_bg'])
        inner.pack(fill=tk.X, padx=25, pady=20)
        
        # Title
        title_frame = tk.Frame(inner, bg=COLORS['card_bg'])
        title_frame.pack(fill=tk.X)
        
        tk.Label(
            title_frame,
            text="💰 Monthly Budget Overview",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        # Set overall budget
        set_frame = tk.Frame(title_frame, bg=COLORS['card_bg'])
        set_frame.pack(side=tk.RIGHT)
        
        tk.Label(
            set_frame,
            text="Total Budget: ₹",
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.LEFT)
        
        self.total_budget_var = tk.StringVar(value=str(data.get('total_budget', 15000)))
        total_entry = tk.Entry(
            set_frame,
            textvariable=self.total_budget_var,
            font=FONTS['body_medium'],
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT,
            width=12
        )
        total_entry.pack(side=tk.LEFT, padx=(5, 0), ipady=5)
        
        # Stats row
        stats_frame = tk.Frame(inner, bg=COLORS['card_bg'])
        stats_frame.pack(fill=tk.X, pady=(25, 0))
        
        total_budget = float(self.total_budget_var.get() or 0)
        total_spent = data.get('total_spent', 0)
        remaining = max(total_budget - total_spent, 0)
        percentage = min((total_spent / total_budget) * 100, 100) if total_budget > 0 else 0
        
        stats = [
            ("Budget Set", format_currency(total_budget), COLORS['primary'], "🎯"),
            ("Total Spent", format_currency(total_spent), COLORS['error'], "💸"),
            ("Remaining", format_currency(remaining), COLORS['success'] if remaining > 0 else COLORS['error'], "💰"),
            ("Used", f"{percentage:.1f}%", COLORS['warning'] if percentage > 80 else COLORS['info'], "📊")
        ]
        
        for i, (label, value, color, icon) in enumerate(stats):
            stat_card = tk.Frame(stats_frame, bg=COLORS['bg_secondary'])
            stat_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            stat_inner = tk.Frame(stat_card, bg=COLORS['bg_secondary'])
            stat_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            tk.Label(
                stat_inner,
                text=f"{icon} {label}",
                font=FONTS['caption'],
                bg=COLORS['bg_secondary'],
                fg=COLORS['text_secondary']
            ).pack(anchor='w')
            
            tk.Label(
                stat_inner,
                text=value,
                font=FONTS['heading_small'],
                bg=COLORS['bg_secondary'],
                fg=color
            ).pack(anchor='w', pady=(5, 0))
        
        # Progress bar
        progress_frame = tk.Frame(inner, bg=COLORS['card_bg'])
        progress_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(
            progress_frame,
            text="Budget Progress",
            font=FONTS['body_medium'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 10))
        
        progress_container = tk.Frame(progress_frame, bg=COLORS['bg_tertiary'], height=24)
        progress_container.pack(fill=tk.X)
        progress_container.pack_propagate(False)
        
        # Determine color
        if percentage < 50:
            bar_color = COLORS['success']
        elif percentage < 80:
            bar_color = COLORS['warning']
        else:
            bar_color = COLORS['error']
        
        progress_bar = tk.Frame(progress_container, bg=bar_color, height=24)
        progress_bar.place(relwidth=percentage/100, relheight=1)
        
        # Percentage text
        if percentage > 8:
            tk.Label(
                progress_bar,
                text=f"{percentage:.0f}% used",
                font=FONTS['body_small'],
                bg=bar_color,
                fg=COLORS['text_white']
            ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Status message
        status_frame = tk.Frame(inner, bg=COLORS['card_bg'])
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        if percentage >= 100:
            status = "⚠️ Budget exceeded! Consider reducing expenses."
            status_color = COLORS['error']
        elif percentage >= 80:
            status = "⏰ Approaching budget limit. Spend carefully."
            status_color = COLORS['warning']
        elif percentage >= 50:
            status = "📊 You're on track. Keep monitoring your spending."
            status_color = COLORS['info']
        else:
            status = "✅ Great job! You're well within budget."
            status_color = COLORS['success']
        
        tk.Label(
            status_frame,
            text=status,
            font=FONTS['body_medium'],
            bg=COLORS['card_bg'],
            fg=status_color
        ).pack(side=tk.LEFT)
        
        days_left = 30 - datetime.now().day + 1
        tk.Label(
            status_frame,
            text=f"{days_left} days left in month",
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.RIGHT)
    
    def create_budget_chart(self, categories):
        """Create budget vs spent chart"""
        # Clear existing
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        inner = tk.Frame(self.chart_frame, bg=COLORS['card_bg'])
        inner.pack(fill=tk.X, padx=25, pady=20)
        
        tk.Label(
            inner,
            text="📊 Budget vs Actual by Category",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 15))
        
        if MATPLOTLIB_AVAILABLE and categories:
            fig = Figure(figsize=(10, 4), dpi=100, facecolor=COLORS['card_bg'])
            ax = fig.add_subplot(111)
            
            cat_names = [c['name'][:10] for c in categories[:8]]
            budgets_vals = [float(c.get('budget', 0)) for c in categories[:8]]
            spent_vals = [float(c.get('spent', 0)) for c in categories[:8]]
            
            x = range(len(cat_names))
            width = 0.35
            
            bars1 = ax.bar([i - width/2 for i in x], budgets_vals, width, label='Budget', color=COLORS['primary'], alpha=0.8)
            bars2 = ax.bar([i + width/2 for i in x], spent_vals, width, label='Spent', color=COLORS['secondary'], alpha=0.8)
            
            ax.set_xticks(x)
            ax.set_xticklabels(cat_names, fontsize=9)
            ax.set_facecolor(COLORS['card_bg'])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(COLORS['border'])
            ax.spines['bottom'].set_color(COLORS['border'])
            ax.tick_params(colors=COLORS['text_secondary'])
            ax.legend(loc='upper right', fontsize=9)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(
                lambda x, p: f'₹{x/1000:.0f}k' if x >= 1000 else f'₹{x:.0f}'))
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, inner)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.X)
        else:
            # Fallback text display
            self.create_text_comparison(inner, categories)
    
    def create_text_comparison(self, parent, categories):
        """Text-based budget comparison"""
        for cat in categories[:6]:
            row = tk.Frame(parent, bg=COLORS['card_bg'])
            row.pack(fill=tk.X, pady=8)
            
            budget = float(cat.get('budget', 0))
            spent = float(cat.get('spent', 0))
            percentage = (spent / budget * 100) if budget > 0 else 0
            
            tk.Label(
                row,
                text=f"{cat.get('icon', '📦')} {cat['name'][:15]}",
                font=FONTS['body_medium'],
                bg=COLORS['card_bg'],
                fg=COLORS['text_primary'],
                width=18,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            # Progress bar
            bar_frame = tk.Frame(row, bg=COLORS['bg_tertiary'], height=12, width=300)
            bar_frame.pack(side=tk.LEFT, padx=10)
            bar_frame.pack_propagate(False)
            
            bar_color = COLORS['success'] if percentage < 80 else (COLORS['warning'] if percentage < 100 else COLORS['error'])
            bar = tk.Frame(bar_frame, bg=bar_color, height=12)
            bar.place(relwidth=min(percentage, 100)/100, relheight=1)
            
            tk.Label(
                row,
                text=f"{format_currency(spent)} / {format_currency(budget)}",
                font=FONTS['body'],
                bg=COLORS['card_bg'],
                fg=COLORS['text_secondary']
            ).pack(side=tk.RIGHT)
    
    def create_category_budgets(self, categories):
        """Create category budget cards"""
        # Clear existing
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        
        # Title
        tk.Label(
            self.categories_frame,
            text="📂 Set Category Budgets",
            font=FONTS['subheading'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 15))
        
        # Grid container
        grid = tk.Frame(self.categories_frame, bg=COLORS['bg_secondary'])
        grid.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid columns
        for i in range(3):
            grid.columnconfigure(i, weight=1, uniform='col')
        
        self.budget_entries = {}
        
        for i, cat in enumerate(categories):
            self.create_category_budget_card(grid, cat, i)
    
    def create_category_budget_card(self, parent, category, index):
        """Create individual category budget card"""
        row = index // 3
        col = index % 3
        
        card = tk.Frame(parent, bg=COLORS['card_bg'], cursor='hand2')
        card.grid(row=row, column=col, sticky='nsew', padx=8, pady=8)
        
        inner = tk.Frame(card, bg=COLORS['card_bg'])
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Header with icon and name
        header = tk.Frame(inner, bg=COLORS['card_bg'])
        header.pack(fill=tk.X)
        
        icon_frame = tk.Frame(header, bg=category.get('color', COLORS['primary']), width=40, height=40)
        icon_frame.pack(side=tk.LEFT)
        icon_frame.pack_propagate(False)
        
        tk.Label(
            icon_frame,
            text=category.get('icon', '📦'),
            font=FONTS['body_large'],
            bg=category.get('color', COLORS['primary']),
            fg=COLORS['text_white']
        ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(
            header,
            text=category['name'],
            font=FONTS['body_medium'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(12, 0))
        
        # Spent info
        spent = float(category.get('spent', 0))
        budget = float(category.get('budget', 0))
        
        info_frame = tk.Frame(inner, bg=COLORS['card_bg'])
        info_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Label(
            info_frame,
            text="Spent this month:",
            font=FONTS['caption'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            info_frame,
            text=format_currency(spent),
            font=FONTS['body_medium'],
            bg=COLORS['card_bg'],
            fg=COLORS['error'] if spent > budget and budget > 0 else COLORS['text_primary']
        ).pack(side=tk.RIGHT)
        
        # Budget input
        budget_frame = tk.Frame(inner, bg=COLORS['card_bg'])
        budget_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            budget_frame,
            text="Budget: ₹",
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.LEFT)
        
        budget_var = tk.StringVar(value=str(int(budget)) if budget > 0 else "")
        budget_entry = tk.Entry(
            budget_frame,
            textvariable=budget_var,
            font=FONTS['body'],
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT,
            width=10
        )
        budget_entry.pack(side=tk.RIGHT, ipady=5)
        
        self.budget_entries[category['id']] = budget_var
        
        # Progress bar
        percentage = (spent / budget * 100) if budget > 0 else 0
        
        progress_frame = tk.Frame(inner, bg=COLORS['bg_tertiary'], height=8)
        progress_frame.pack(fill=tk.X, pady=(12, 0))
        
        if budget > 0:
            bar_color = COLORS['success'] if percentage < 80 else (COLORS['warning'] if percentage < 100 else COLORS['error'])
            progress = tk.Frame(progress_frame, bg=bar_color, height=8)
            progress.place(relwidth=min(percentage, 100)/100, relheight=1)
        
        # Status
        if budget > 0:
            if percentage >= 100:
                status = f"⚠️ Over by {format_currency(spent - budget)}"
                status_color = COLORS['error']
            elif percentage >= 80:
                status = f"⏰ {100 - percentage:.0f}% remaining"
                status_color = COLORS['warning']
            else:
                status = f"✅ {format_currency(budget - spent)} left"
                status_color = COLORS['success']
            
            tk.Label(
                inner,
                text=status,
                font=FONTS['caption'],
                bg=COLORS['card_bg'],
                fg=status_color
            ).pack(anchor='w', pady=(8, 0))
    
    def create_tips(self):
        """Create budget tips section"""
        # Clear existing
        for widget in self.tips_frame.winfo_children():
            widget.destroy()
        
        inner = tk.Frame(self.tips_frame, bg=COLORS['card_bg'])
        inner.pack(fill=tk.X, padx=25, pady=20)
        
        tk.Label(
            inner,
            text="💡 Smart Budgeting Tips",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 15))
        
        tips = [
            ("50/30/20 Rule", "Allocate 50% for needs, 30% for wants, 20% for savings"),
            ("Track Daily", "Review your expenses daily to stay on top of spending"),
            ("Set Alerts", "Create alerts when you reach 80% of category budgets"),
            ("Review Monthly", "Analyze your spending patterns at the end of each month")
        ]
        
        tips_grid = tk.Frame(inner, bg=COLORS['card_bg'])
        tips_grid.pack(fill=tk.X)
        
        for i, (title, desc) in enumerate(tips):
            tip_frame = tk.Frame(tips_grid, bg=COLORS['bg_secondary'])
            tip_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            tip_inner = tk.Frame(tip_frame, bg=COLORS['bg_secondary'])
            tip_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
            
            tk.Label(
                tip_inner,
                text=f"#{i+1} {title}",
                font=FONTS['body_medium'],
                bg=COLORS['bg_secondary'],
                fg=COLORS['primary']
            ).pack(anchor='w')
            
            tk.Label(
                tip_inner,
                text=desc,
                font=FONTS['caption'],
                bg=COLORS['bg_secondary'],
                fg=COLORS['text_secondary'],
                wraplength=200,
                justify='left'
            ).pack(anchor='w', pady=(5, 0))
    
    def save_all_budgets(self):
        """Save all budget settings"""
        try:
            # Save total budget
            total_budget = float(self.total_budget_var.get() or 0)
            
            # Save category budgets
            for cat_id, var in self.budget_entries.items():
                budget_value = float(var.get() or 0)
                self.budgets[cat_id] = budget_value
                
                # Save to database
                ExpenseController.set_category_budget(
                    self.user.user_id,
                    cat_id,
                    budget_value
                )
            
            messagebox.showinfo("Success", "Budgets saved successfully! 🎉")
            self.load_data()  # Refresh
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for budgets")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save budgets: {str(e)}")
    
    def reset_budgets(self):
        """Reset all budgets"""
        if messagebox.askyesno("Reset Budgets", "Are you sure you want to reset all budgets to 0?"):
            for var in self.budget_entries.values():
                var.set("")
            self.total_budget_var.set("15000")
            messagebox.showinfo("Reset", "All budgets have been reset")
    
    def load_data(self):
        """Load budget data"""
        # Get category data with spending
        data = ExpenseController.get_dashboard_data(self.user.user_id)
        category_totals = data.get('category_totals', [])
        
        # Get all categories
        categories = ExpenseController.get_categories()
        
        # Merge data
        category_data = []
        total_spent = 0
        
        for cat in categories:
            cat_total = next(
                (c for c in category_totals if c['category_id'] == cat.category_id),
                {'total': 0}
            )
            spent = float(cat_total.get('total', 0))
            total_spent += spent
            
            # Get saved budget (from DB or default)
            budget = ExpenseController.get_category_budget(self.user.user_id, cat.category_id)
            
            category_data.append({
                'id': cat.category_id,
                'name': cat.name,
                'icon': cat.icon,
                'color': cat.color or CHART_COLORS[len(category_data) % len(CHART_COLORS)],
                'spent': spent,
                'budget': budget or 0
            })
        
        # Create UI
        self.create_overall_budget_card({
            'total_budget': 15000,
            'total_spent': total_spent
        })
        
        self.create_budget_chart(category_data)
        self.create_category_budgets(category_data)
        self.create_tips()
    
    def refresh(self):
        """Refresh budget view"""
        self.load_data()

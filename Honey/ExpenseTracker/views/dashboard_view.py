"""
Enhanced Dashboard View
Interactive dashboard with real-time stats, charts, and budget tracking
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import COLORS, FONTS, DIMENSIONS, CHART_COLORS
from utils.helpers import format_currency, get_greeting, get_month_short_name
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


class DashboardView(tk.Frame):
    """Enhanced Dashboard with interactive elements"""
    
    def __init__(self, parent, user, on_navigate):
        super().__init__(parent, bg=COLORS['bg_secondary'])
        self.parent = parent
        self.user = user
        self.on_navigate = on_navigate
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create dashboard widgets"""
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
        
        # Header with greeting and quick actions
        self.create_header(content)
        
        # Quick stats row
        self.stats_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        self.stats_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Budget overview section
        self.budget_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        self.budget_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Charts section
        charts_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        charts_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Pie chart (left)
        self.pie_frame = tk.Frame(charts_frame, bg=COLORS['card_bg'])
        self.pie_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Line chart (right)
        self.line_frame = tk.Frame(charts_frame, bg=COLORS['card_bg'])
        self.line_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Bottom section
        bottom_frame = tk.Frame(content, bg=COLORS['bg_secondary'])
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Recent expenses (left)
        self.recent_frame = tk.Frame(bottom_frame, bg=COLORS['card_bg'])
        self.recent_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Top categories (right)
        self.top_cat_frame = tk.Frame(bottom_frame, bg=COLORS['card_bg'])
        self.top_cat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    def create_header(self, parent):
        """Create header with greeting and quick actions"""
        header = tk.Frame(parent, bg=COLORS['bg_secondary'])
        header.pack(fill=tk.X)
        
        # Left side - Greeting
        left = tk.Frame(header, bg=COLORS['bg_secondary'])
        left.pack(side=tk.LEFT)
        
        greeting = f"{get_greeting()}! 👋"
        greeting_label = tk.Label(
            left,
            text=greeting,
            font=FONTS['heading'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        )
        greeting_label.pack(anchor='w')
        
        name_label = tk.Label(
            left,
            text=self.user.full_name,
            font=FONTS['heading_small'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['primary']
        )
        name_label.pack(anchor='w')
        
        date_label = tk.Label(
            left,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=FONTS['body'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary']
        )
        date_label.pack(anchor='w', pady=(5, 0))
        
        # Right side - Quick actions
        right = tk.Frame(header, bg=COLORS['bg_secondary'])
        right.pack(side=tk.RIGHT)
        
        # Quick add expense button
        add_btn = tk.Button(
            right,
            text="➕ Add Expense",
            font=FONTS['button'],
            bg=COLORS['primary'],
            fg=COLORS['text_white'],
            activebackground=COLORS['primary_dark'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10,
            command=lambda: self.on_navigate('add_expense')
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        add_btn.bind('<Enter>', lambda e: add_btn.config(bg=COLORS['primary_dark']))
        add_btn.bind('<Leave>', lambda e: add_btn.config(bg=COLORS['primary']))
        
        # Set budget button
        budget_btn = tk.Button(
            right,
            text="🎯 Set Budget",
            font=FONTS['button'],
            bg=COLORS['secondary'],
            fg=COLORS['text_white'],
            activebackground=COLORS['secondary_dark'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10,
            command=lambda: self.on_navigate('budget')
        )
        budget_btn.pack(side=tk.LEFT, padx=5)
        budget_btn.bind('<Enter>', lambda e: budget_btn.config(bg=COLORS['secondary_dark']))
        budget_btn.bind('<Leave>', lambda e: budget_btn.config(bg=COLORS['secondary']))
        
        # View reports button
        reports_btn = tk.Button(
            right,
            text="📊 Reports",
            font=FONTS['button'],
            bg=COLORS['accent'],
            fg=COLORS['text_white'],
            activebackground=COLORS['accent_dark'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10,
            command=lambda: self.on_navigate('reports')
        )
        reports_btn.pack(side=tk.LEFT, padx=5)
        reports_btn.bind('<Enter>', lambda e: reports_btn.config(bg=COLORS['accent_dark']))
        reports_btn.bind('<Leave>', lambda e: reports_btn.config(bg=COLORS['accent']))
    
    def create_stat_card(self, parent, title, value, icon, color, trend=None, trend_positive=True, col=0):
        """Create an interactive statistics card"""
        card = tk.Frame(parent, bg=COLORS['card_bg'], cursor='hand2')
        card.grid(row=0, column=col, sticky='nsew', padx=8, pady=5)
        
        # Hover effect
        def on_enter(e):
            card.config(bg=COLORS['card_hover'])
            for widget in card.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.config(bg=COLORS['card_hover'])
                    for child in widget.winfo_children():
                        try:
                            child.config(bg=COLORS['card_hover'])
                        except:
                            pass
        
        def on_leave(e):
            card.config(bg=COLORS['card_bg'])
            for widget in card.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.config(bg=COLORS['card_bg'])
                    for child in widget.winfo_children():
                        try:
                            child.config(bg=COLORS['card_bg'])
                        except:
                            pass
        
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
        
        # Content
        inner = tk.Frame(card, bg=COLORS['card_bg'])
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icon with colored background
        icon_frame = tk.Frame(inner, bg=color, width=50, height=50)
        icon_frame.pack(anchor='w')
        icon_frame.pack_propagate(False)
        
        icon_label = tk.Label(
            icon_frame,
            text=icon,
            font=('Segoe UI', 20),
            bg=color,
            fg=COLORS['text_white']
        )
        icon_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        title_label = tk.Label(
            inner,
            text=title,
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        )
        title_label.pack(anchor='w', pady=(15, 5))
        
        # Value
        value_label = tk.Label(
            inner,
            text=value,
            font=FONTS['heading_small'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        )
        value_label.pack(anchor='w')
        
        # Trend indicator
        if trend:
            trend_frame = tk.Frame(inner, bg=COLORS['card_bg'])
            trend_frame.pack(anchor='w', pady=(5, 0))
            
            trend_color = COLORS['success'] if trend_positive else COLORS['error']
            trend_icon = "↑" if trend_positive else "↓"
            
            tk.Label(
                trend_frame,
                text=f"{trend_icon} {trend}",
                font=FONTS['body_small'],
                bg=COLORS['card_bg'],
                fg=trend_color
            ).pack(side=tk.LEFT)
            
            tk.Label(
                trend_frame,
                text=" vs last month",
                font=FONTS['caption'],
                bg=COLORS['card_bg'],
                fg=COLORS['text_light']
            ).pack(side=tk.LEFT)
        
        return card
    
    def create_budget_overview(self, data):
        """Create budget overview section"""
        # Clear existing
        for widget in self.budget_frame.winfo_children():
            widget.destroy()
        
        # Main card
        card = tk.Frame(self.budget_frame, bg=COLORS['card_bg'])
        card.pack(fill=tk.X)
        
        inner = tk.Frame(card, bg=COLORS['card_bg'])
        inner.pack(fill=tk.X, padx=25, pady=20)
        
        # Header
        header = tk.Frame(inner, bg=COLORS['card_bg'])
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="🎯 Monthly Budget Overview",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        # Set budget link
        set_budget = tk.Label(
            header,
            text="Manage →",
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['primary'],
            cursor='hand2'
        )
        set_budget.pack(side=tk.RIGHT)
        set_budget.bind('<Button-1>', lambda e: self.on_navigate('budget'))
        
        # Budget progress
        budget_total = data.get('budget_total', 10000)  # Default budget
        spent = data['monthly_total']
        remaining = max(budget_total - spent, 0)
        percentage = min((spent / budget_total) * 100, 100) if budget_total > 0 else 0
        
        # Progress info
        info_frame = tk.Frame(inner, bg=COLORS['card_bg'])
        info_frame.pack(fill=tk.X, pady=(20, 10))
        
        tk.Label(
            info_frame,
            text=f"Spent: {format_currency(spent)}",
            font=FONTS['body_medium'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            info_frame,
            text=f"Budget: {format_currency(budget_total)}",
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.RIGHT)
        
        # Progress bar
        progress_container = tk.Frame(inner, bg=COLORS['bg_tertiary'], height=20)
        progress_container.pack(fill=tk.X, pady=(0, 10))
        progress_container.pack_propagate(False)
        
        # Determine color based on percentage
        if percentage < 50:
            bar_color = COLORS['success']
        elif percentage < 80:
            bar_color = COLORS['warning']
        else:
            bar_color = COLORS['error']
        
        progress_bar = tk.Frame(progress_container, bg=bar_color, height=20)
        progress_bar.place(relwidth=percentage/100, relheight=1)
        
        # Percentage label on bar
        if percentage > 10:
            tk.Label(
                progress_bar,
                text=f"{percentage:.0f}%",
                font=FONTS['body_small'],
                bg=bar_color,
                fg=COLORS['text_white']
            ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Remaining info
        remaining_frame = tk.Frame(inner, bg=COLORS['card_bg'])
        remaining_frame.pack(fill=tk.X)
        
        status_text = f"✅ {format_currency(remaining)} remaining" if remaining > 0 else "⚠️ Budget exceeded!"
        status_color = COLORS['success'] if remaining > 0 else COLORS['error']
        
        tk.Label(
            remaining_frame,
            text=status_text,
            font=FONTS['body_medium'],
            bg=COLORS['card_bg'],
            fg=status_color
        ).pack(side=tk.LEFT)
        
        days_left = (datetime.now().replace(month=datetime.now().month % 12 + 1, day=1) - datetime.now()).days
        tk.Label(
            remaining_frame,
            text=f"{days_left} days left in month",
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.RIGHT)
    
    def create_pie_chart(self, category_data):
        """Create interactive pie chart"""
        # Clear existing
        for widget in self.pie_frame.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.pie_frame, bg=COLORS['card_bg'])
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(
            header,
            text="🥧 Spending by Category",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        if MATPLOTLIB_AVAILABLE:
            # Filter categories with expenses
            data = [(c['category_name'].split(' ')[-1][:12], float(c['total']), c.get('color', CHART_COLORS[0])) 
                    for c in category_data if float(c['total']) > 0][:8]
            
            if data:
                fig = Figure(figsize=(4.5, 3.5), dpi=100, facecolor=COLORS['card_bg'])
                ax = fig.add_subplot(111)
                
                labels = [d[0] for d in data]
                sizes = [d[1] for d in data]
                colors = [d[2] for d in data]
                
                # Create pie with explode effect
                explode = [0.02] * len(data)
                
                wedges, texts, autotexts = ax.pie(
                    sizes, 
                    labels=labels, 
                    colors=colors, 
                    autopct='%1.1f%%',
                    startangle=90,
                    explode=explode,
                    textprops={'fontsize': 8},
                    pctdistance=0.75
                )
                
                # Style percentage text
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontsize(7)
                
                ax.axis('equal')
                fig.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, self.pie_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(padx=10, pady=(0, 20))
            else:
                self.show_no_data(self.pie_frame, "No expenses to display")
        else:
            self.create_text_pie_chart(category_data)
    
    def create_text_pie_chart(self, category_data):
        """Fallback text-based pie chart"""
        total = sum(float(c['total']) for c in category_data)
        
        for cat in category_data[:6]:
            if float(cat['total']) > 0:
                row = tk.Frame(self.pie_frame, bg=COLORS['card_bg'])
                row.pack(fill=tk.X, padx=20, pady=5)
                
                percentage = (float(cat['total']) / total * 100) if total > 0 else 0
                
                # Color dot
                dot = tk.Frame(row, bg=cat.get('color', COLORS['primary']), width=12, height=12)
                dot.pack(side=tk.LEFT)
                
                tk.Label(
                    row,
                    text=f" {cat['category_name'].split(' ', 1)[-1][:15]}",
                    font=FONTS['body'],
                    bg=COLORS['card_bg'],
                    fg=COLORS['text_primary'],
                    anchor='w'
                ).pack(side=tk.LEFT, padx=(5, 0))
                
                tk.Label(
                    row,
                    text=f"{percentage:.1f}%",
                    font=FONTS['body_medium'],
                    bg=COLORS['card_bg'],
                    fg=COLORS['text_secondary']
                ).pack(side=tk.RIGHT)
        
        tk.Frame(self.pie_frame, bg=COLORS['card_bg'], height=20).pack()
    
    def create_line_chart(self, monthly_data):
        """Create line chart for spending trend"""
        # Clear existing
        for widget in self.line_frame.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.line_frame, bg=COLORS['card_bg'])
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(
            header,
            text="📈 Spending Trend",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        if MATPLOTLIB_AVAILABLE:
            fig = Figure(figsize=(4.5, 3.5), dpi=100, facecolor=COLORS['card_bg'])
            ax = fig.add_subplot(111)
            
            months = [get_month_short_name(d['month']) for d in monthly_data]
            values = [float(d['total']) for d in monthly_data]
            
            # Create gradient fill under line
            ax.fill_between(range(len(months)), values, alpha=0.3, color=COLORS['primary'])
            ax.plot(range(len(months)), values, color=COLORS['primary'], linewidth=2, marker='o', markersize=5)
            
            ax.set_xticks(range(len(months)))
            ax.set_xticklabels(months, fontsize=7)
            ax.set_facecolor(COLORS['card_bg'])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(COLORS['border'])
            ax.spines['bottom'].set_color(COLORS['border'])
            ax.tick_params(colors=COLORS['text_secondary'], labelsize=8)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x/1000:.0f}k' if x >= 1000 else f'₹{x:.0f}'))
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.line_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=10, pady=(0, 20))
        else:
            self.create_text_trend(monthly_data)
    
    def create_text_trend(self, monthly_data):
        """Fallback text-based trend display"""
        max_val = max([float(d['total']) for d in monthly_data] + [1])
        
        for d in monthly_data:
            row = tk.Frame(self.line_frame, bg=COLORS['card_bg'])
            row.pack(fill=tk.X, padx=20, pady=3)
            
            tk.Label(
                row,
                text=get_month_short_name(d['month']),
                font=FONTS['caption'],
                bg=COLORS['card_bg'],
                fg=COLORS['text_secondary'],
                width=4,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            bar_width = (float(d['total']) / max_val * 150) if max_val > 0 else 0
            
            bar_frame = tk.Frame(row, bg=COLORS['bg_tertiary'], height=10, width=150)
            bar_frame.pack(side=tk.LEFT, padx=5)
            bar_frame.pack_propagate(False)
            
            if bar_width > 0:
                bar = tk.Frame(bar_frame, bg=COLORS['primary'], height=10, width=int(bar_width))
                bar.pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=format_currency(d['total']),
                font=FONTS['caption'],
                bg=COLORS['card_bg'],
                fg=COLORS['text_secondary']
            ).pack(side=tk.RIGHT)
    
    def create_recent_expenses(self, expenses):
        """Create recent expenses list"""
        # Clear existing
        for widget in self.recent_frame.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.recent_frame, bg=COLORS['card_bg'])
        header.pack(fill=tk.X, padx=20, pady=(20, 15))
        
        tk.Label(
            header,
            text="📝 Recent Expenses",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        view_all = tk.Label(
            header,
            text="View All →",
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['primary'],
            cursor='hand2'
        )
        view_all.pack(side=tk.RIGHT)
        view_all.bind('<Button-1>', lambda e: self.on_navigate('expenses'))
        
        if expenses:
            for expense in expenses[:5]:
                self.create_expense_row(expense)
        else:
            self.show_no_data(self.recent_frame, "No expenses yet", "Add your first expense to get started!")
        
        tk.Frame(self.recent_frame, bg=COLORS['card_bg'], height=20).pack()
    
    def create_expense_row(self, expense):
        """Create expense row with hover effect"""
        row = tk.Frame(self.recent_frame, bg=COLORS['card_bg'], cursor='hand2')
        row.pack(fill=tk.X, padx=20, pady=8)
        
        # Hover effect
        def on_enter(e):
            row.config(bg=COLORS['card_hover'])
            for child in row.winfo_children():
                try:
                    child.config(bg=COLORS['card_hover'])
                except:
                    pass
        
        def on_leave(e):
            row.config(bg=COLORS['card_bg'])
            for child in row.winfo_children():
                try:
                    child.config(bg=COLORS['card_bg'])
                except:
                    pass
        
        row.bind('<Enter>', on_enter)
        row.bind('<Leave>', on_leave)
        
        # Icon with colored background
        icon_frame = tk.Frame(row, bg=expense.category_color or COLORS['primary'], width=40, height=40)
        icon_frame.pack(side=tk.LEFT)
        icon_frame.pack_propagate(False)
        
        tk.Label(
            icon_frame,
            text=expense.category_icon or '📦',
            font=FONTS['body_large'],
            bg=expense.category_color or COLORS['primary'],
            fg=COLORS['text_white']
        ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Details
        details = tk.Frame(row, bg=COLORS['card_bg'])
        details.pack(side=tk.LEFT, padx=(12, 0), fill=tk.X, expand=True)
        
        tk.Label(
            details,
            text=expense.description[:30] + ('...' if len(expense.description or '') > 30 else ''),
            font=FONTS['body_medium'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(anchor='w')
        
        tk.Label(
            details,
            text=f"{expense.category_name.split(' ', 1)[-1] if expense.category_name else ''} • {expense.expense_date}",
            font=FONTS['caption'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_light'],
            anchor='w'
        ).pack(anchor='w')
        
        # Amount
        tk.Label(
            row,
            text=format_currency(expense.amount),
            font=FONTS['body_medium'],
            bg=COLORS['card_bg'],
            fg=COLORS['error']
        ).pack(side=tk.RIGHT)
    
    def create_top_categories(self, category_data):
        """Create top spending categories"""
        # Clear existing
        for widget in self.top_cat_frame.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.top_cat_frame, bg=COLORS['card_bg'])
        header.pack(fill=tk.X, padx=20, pady=(20, 15))
        
        tk.Label(
            header,
            text="🏆 Top Categories",
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        total = sum(float(c['total']) for c in category_data)
        
        for i, cat in enumerate(category_data[:5]):
            if float(cat['total']) > 0:
                self.create_category_row(cat, i + 1, total)
        
        tk.Frame(self.top_cat_frame, bg=COLORS['card_bg'], height=20).pack()
    
    def create_category_row(self, category, rank, total):
        """Create category row with progress"""
        row = tk.Frame(self.top_cat_frame, bg=COLORS['card_bg'])
        row.pack(fill=tk.X, padx=20, pady=8)
        
        # Rank badge
        rank_colors = ['#FFD700', '#C0C0C0', '#CD7F32', COLORS['text_light'], COLORS['text_light']]
        rank_frame = tk.Frame(row, bg=rank_colors[rank-1], width=28, height=28)
        rank_frame.pack(side=tk.LEFT)
        rank_frame.pack_propagate(False)
        
        tk.Label(
            rank_frame,
            text=str(rank),
            font=FONTS['body_medium'],
            bg=rank_colors[rank-1],
            fg=COLORS['text_white'] if rank <= 3 else COLORS['text_primary']
        ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Category info
        info = tk.Frame(row, bg=COLORS['card_bg'])
        info.pack(side=tk.LEFT, padx=(12, 0), fill=tk.X, expand=True)
        
        name_row = tk.Frame(info, bg=COLORS['card_bg'])
        name_row.pack(fill=tk.X)
        
        tk.Label(
            name_row,
            text=f"{category.get('icon', '📦')} {category['category_name'].split(' ', 1)[-1][:15]}",
            font=FONTS['body_medium'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        percentage = (float(category['total']) / total * 100) if total > 0 else 0
        tk.Label(
            name_row,
            text=f"{percentage:.1f}%",
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.RIGHT)
        
        # Progress bar
        progress = tk.Frame(info, bg=COLORS['bg_tertiary'], height=6)
        progress.pack(fill=tk.X, pady=(5, 0))
        
        bar = tk.Frame(progress, bg=category.get('color', COLORS['primary']), height=6)
        bar.place(relwidth=percentage/100, relheight=1)
        
        # Amount
        tk.Label(
            row,
            text=format_currency(category['total']),
            font=FONTS['body_medium'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        ).pack(side=tk.RIGHT)
    
    def show_no_data(self, parent, title, subtitle=""):
        """Show no data message"""
        container = tk.Frame(parent, bg=COLORS['card_bg'])
        container.pack(fill=tk.BOTH, expand=True, pady=30)
        
        tk.Label(
            container,
            text="📭",
            font=('Segoe UI', 36),
            bg=COLORS['card_bg']
        ).pack()
        
        tk.Label(
            container,
            text=title,
            font=FONTS['body_medium'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        ).pack(pady=(10, 0))
        
        if subtitle:
            tk.Label(
                container,
                text=subtitle,
                font=FONTS['body'],
                bg=COLORS['card_bg'],
                fg=COLORS['text_light']
            ).pack()
    
    def load_data(self):
        """Load dashboard data"""
        data = ExpenseController.get_dashboard_data(self.user.user_id)
        
        # Store data
        self.category_data = data['category_totals']
        
        # Configure grid for stats
        for i in range(4):
            self.stats_frame.columnconfigure(i, weight=1)
        
        # Create stat cards
        self.create_stat_card(
            self.stats_frame,
            "Today's Spending",
            format_currency(data['today_total']),
            "📅",
            COLORS['primary'],
            trend="12%",
            trend_positive=False,
            col=0
        )
        
        self.create_stat_card(
            self.stats_frame,
            "This Month",
            format_currency(data['monthly_total']),
            "📊",
            COLORS['secondary'],
            trend="8%",
            trend_positive=True,
            col=1
        )
        
        self.create_stat_card(
            self.stats_frame,
            "This Year",
            format_currency(data['yearly_total']),
            "📈",
            COLORS['accent'],
            col=2
        )
        
        self.create_stat_card(
            self.stats_frame,
            "Transactions",
            str(data['monthly_count']),
            "🧾",
            COLORS['info'],
            col=3
        )
        
        # Create sections
        data['budget_total'] = 15000  # Default budget
        self.create_budget_overview(data)
        self.create_pie_chart(data['category_totals'])
        self.create_line_chart(data['monthly_trend'])
        self.create_recent_expenses(data['recent_expenses'])
        self.create_top_categories(data['category_totals'])
    
    def refresh(self):
        """Refresh dashboard"""
        self.load_data()

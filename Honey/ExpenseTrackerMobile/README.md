# 💰 Expense Tracker System

A comprehensive expense tracking application built with Python and MySQL, featuring a modern and clean user interface.

## 📋 Features

- **User Authentication**: Secure login and registration system
- **Dashboard**: Overview of expenses with visual statistics
- **Expense Management**: Add, edit, delete, and view expenses
- **Categories**: Organize expenses by categories (Food, Transport, Entertainment, etc.)
- **Reports**: Generate monthly/yearly expense reports with charts
- **Search & Filter**: Find expenses by date, category, or amount
- **Export**: Export data to CSV format

## 🛠️ Technologies Used

- **Python 3.x**: Core programming language
- **Tkinter**: GUI framework for clean UI/UX
- **MySQL**: Database management
- **Matplotlib**: Charts and visualizations
- **Pillow**: Image handling

## 📦 Installation

### Prerequisites

1. Python 3.8 or higher
2. MySQL Server 5.7 or higher
3. pip (Python package manager)

### Setup Steps

1. **Clone or download the project**

2. **Install required packages**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Setup MySQL Database**:

   - Open MySQL and create the database by running the SQL script:

   ```bash
   mysql -u root -p < database/setup.sql
   ```

   - Or manually run the SQL commands in `database/setup.sql`

4. **Configure Database Connection**:

   - Open `config/database_config.py`
   - Update the MySQL credentials (host, user, password)

5. **Run the Application**:
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
ExpenseTracker/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── config/
│   └── database_config.py # Database configuration
├── database/
│   ├── setup.sql          # Database schema
│   └── db_connection.py   # Database connection handler
├── models/
│   ├── user.py            # User model
│   └── expense.py         # Expense model
├── views/
│   ├── login_view.py      # Login/Register UI
│   ├── dashboard_view.py  # Main dashboard
│   ├── expense_view.py    # Expense management
│   └── report_view.py     # Reports and charts
├── controllers/
│   ├── auth_controller.py # Authentication logic
│   └── expense_controller.py # Expense operations
└── utils/
    ├── helpers.py         # Utility functions
    └── styles.py          # UI styling constants
```

## 🎨 Screenshots

The application features a modern, clean interface with:

- Color-coded categories
- Interactive charts
- Responsive design

## 👤 Default Login

For testing, you can register a new account or use the application after setup.

## 📝 License

This project is created for educational purposes.

---

**Made with ❤️ for School Project**

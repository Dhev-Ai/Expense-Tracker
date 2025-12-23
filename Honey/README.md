# 📱 Expense Tracker - Mobile & Web Applications

This folder contains **two versions** of the Expense Tracker application:

## 1. 🌐 Web Application (Flask)

Location: `ExpenseTrackerWeb/`

A responsive web application that works on any device (mobile, tablet, desktop).

### Features:

- ✅ Responsive design (mobile-first)
- ✅ Dashboard with charts
- ✅ Add/View/Delete expenses
- ✅ Category reports with pie charts
- ✅ Budget management
- ✅ User authentication

### How to Run:

```bash
cd ExpenseTrackerWeb
pip install -r requirements.txt
python app.py
```

Then open: **http://localhost:5000** in your browser

---

## 2. 📱 Mobile Application (Kivy)

Location: `ExpenseTrackerMobile/`

A native mobile app that can be compiled to Android APK.

### Features:

- ✅ Native mobile UI
- ✅ Dashboard with stats
- ✅ Add expenses quickly
- ✅ View expense history
- ✅ Reports by category
- ✅ Remember me login

### How to Run (Desktop Testing):

```bash
cd ExpenseTrackerMobile
pip install -r requirements.txt
python main.py
```

### How to Build Android APK:

```bash
# On Linux/WSL (required for Android build)
pip install buildozer
cd ExpenseTrackerMobile
buildozer android debug
```

The APK will be in: `bin/expensetracker-1.0.0-debug.apk`

---

## 🗄️ Database

Both apps use the same MySQL database from the original ExpenseTracker project.

Make sure MySQL is running with:

- **Host:** localhost
- **User:** root
- **Password:** 12345
- **Database:** expense_tracker

---

## 📁 Project Structure

```
Honey/
├── ExpenseTracker/          # Original Desktop App (Tkinter)
├── ExpenseTrackerWeb/       # Web Application (Flask)
│   ├── app.py              # Main Flask application
│   ├── requirements.txt
│   └── templates/          # HTML templates
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── expenses.html
│       ├── add_expense.html
│       ├── reports.html
│       └── budget.html
└── ExpenseTrackerMobile/    # Mobile Application (Kivy)
    ├── main.py             # Main Kivy application
    ├── buildozer.spec      # Android build config
    └── requirements.txt
```

---

## 🚀 Quick Start

### For Web (Recommended for school project):

```bash
cd e:\Honey\ExpenseTrackerWeb
pip install flask flask-login mysql-connector-python
python app.py
```

### For Mobile Testing:

```bash
cd e:\Honey\ExpenseTrackerMobile
pip install kivy mysql-connector-python
python main.py
```

---

## 👨‍💻 GPS

School Project - Expense Tracker System

-- =============================================
-- EXPENSE TRACKER DATABASE SETUP
-- =============================================

-- Create Database
CREATE DATABASE IF NOT EXISTS expense_tracker;
USE expense_tracker;

-- =============================================
-- USERS TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- =============================================
-- CATEGORIES TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    icon VARCHAR(50) DEFAULT '📦',
    color VARCHAR(20) DEFAULT '#6366F1',
    description VARCHAR(200),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- EXPENSES TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS expenses (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    description VARCHAR(255),
    expense_date DATE NOT NULL,
    payment_method ENUM('Cash', 'Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Other') DEFAULT 'Cash',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT
);

-- =============================================
-- BUDGET TABLE (Optional Feature)
-- =============================================
CREATE TABLE IF NOT EXISTS budgets (
    budget_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT,
    budget_amount DECIMAL(10, 2) NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    UNIQUE KEY unique_budget (user_id, category_id, month, year)
);

-- =============================================
-- INSERT DEFAULT CATEGORIES
-- =============================================
INSERT INTO categories (category_name, icon, color, description, is_default) VALUES
('🍔 Food & Dining', '🍔', '#EF4444', 'Restaurant, groceries, snacks', TRUE),
('🚗 Transportation', '🚗', '#F59E0B', 'Fuel, public transport, taxi', TRUE),
('🛒 Shopping', '🛒', '#10B981', 'Clothes, electronics, accessories', TRUE),
('🎬 Entertainment', '🎬', '#8B5CF6', 'Movies, games, subscriptions', TRUE),
('💊 Healthcare', '💊', '#EC4899', 'Medicine, doctor visits, gym', TRUE),
('📚 Education', '📚', '#3B82F6', 'Books, courses, tuition', TRUE),
('🏠 Housing', '🏠', '#6366F1', 'Rent, utilities, maintenance', TRUE),
('💡 Utilities', '💡', '#14B8A6', 'Electricity, water, internet', TRUE),
('✈️ Travel', '✈️', '#F97316', 'Trips, hotels, vacation', TRUE),
('🎁 Gifts', '🎁', '#D946EF', 'Presents, donations', TRUE),
('📱 Phone & Internet', '📱', '#0EA5E9', 'Mobile bills, internet', TRUE),
('💼 Other', '💼', '#64748B', 'Miscellaneous expenses', TRUE);

-- =============================================
-- CREATE INDEXES FOR BETTER PERFORMANCE
-- =============================================
CREATE INDEX idx_expenses_user ON expenses(user_id);
CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_expenses_category ON expenses(category_id);
CREATE INDEX idx_budgets_user ON budgets(user_id);

-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- Monthly Expense Summary View
CREATE OR REPLACE VIEW monthly_expense_summary AS
SELECT 
    e.user_id,
    YEAR(e.expense_date) as year,
    MONTH(e.expense_date) as month,
    c.category_name,
    c.color,
    SUM(e.amount) as total_amount,
    COUNT(*) as transaction_count
FROM expenses e
JOIN categories c ON e.category_id = c.category_id
GROUP BY e.user_id, YEAR(e.expense_date), MONTH(e.expense_date), c.category_id;

-- Daily Expense Summary View
CREATE OR REPLACE VIEW daily_expense_summary AS
SELECT 
    e.user_id,
    e.expense_date,
    SUM(e.amount) as total_amount,
    COUNT(*) as transaction_count
FROM expenses e
GROUP BY e.user_id, e.expense_date;

-- =============================================
-- STORED PROCEDURES
-- =============================================

DELIMITER //

-- Procedure to get expense statistics for a user
CREATE PROCEDURE GetExpenseStats(IN p_user_id INT, IN p_month INT, IN p_year INT)
BEGIN
    SELECT 
        COALESCE(SUM(amount), 0) as total_expenses,
        COALESCE(AVG(amount), 0) as avg_expense,
        COALESCE(MAX(amount), 0) as max_expense,
        COALESCE(MIN(amount), 0) as min_expense,
        COUNT(*) as total_transactions
    FROM expenses
    WHERE user_id = p_user_id 
    AND MONTH(expense_date) = p_month 
    AND YEAR(expense_date) = p_year;
END //

-- Procedure to get category-wise expenses
CREATE PROCEDURE GetCategoryExpenses(IN p_user_id INT, IN p_month INT, IN p_year INT)
BEGIN
    SELECT 
        c.category_name,
        c.icon,
        c.color,
        COALESCE(SUM(e.amount), 0) as total_amount,
        COUNT(e.expense_id) as transaction_count
    FROM categories c
    LEFT JOIN expenses e ON c.category_id = e.category_id 
        AND e.user_id = p_user_id
        AND MONTH(e.expense_date) = p_month 
        AND YEAR(e.expense_date) = p_year
    GROUP BY c.category_id
    ORDER BY total_amount DESC;
END //

DELIMITER ;

-- =============================================
-- SAMPLE DATA (Optional - for testing)
-- =============================================

-- Uncomment below lines to add a test user (password: test123)
-- INSERT INTO users (username, email, password, full_name) VALUES
-- ('testuser', 'test@example.com', 'pbkdf2:sha256:600000$test$hashedpassword', 'Test User');

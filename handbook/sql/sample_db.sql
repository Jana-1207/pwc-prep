-- =====================================================================
-- Sample database used by every runnable SQL example in the handbook.
-- PostgreSQL 13+ compatible. The build script loads this file fresh
-- before each chapter, so every chapter starts from the same data.
--
-- Themes:  HR (departments, employees)
--          E-commerce (customers, products, orders, order_items)
--          Banking (accounts)            -> transactions / ACID
--          Marketing leads (leads)       -> duplicate handling
--          Daily sales (daily_sales)     -> window functions
--          App logins (user_logins)      -> latest record, date analysis
-- =====================================================================

DROP TABLE IF EXISTS order_items, orders, products, customers,
                     employees, departments, accounts, leads,
                     daily_sales, user_logins CASCADE;

-- ---------------------------------------------------------------------
-- HR
-- ---------------------------------------------------------------------
CREATE TABLE departments (
    dept_id    INT PRIMARY KEY,
    dept_name  VARCHAR(50) NOT NULL UNIQUE,
    location   VARCHAR(50) NOT NULL
);

INSERT INTO departments (dept_id, dept_name, location) VALUES
    (1, 'Engineering', 'Bengaluru'),
    (2, 'Finance',     'Mumbai'),
    (3, 'HR',          'Kolkata'),
    (4, 'Marketing',   'Delhi'),
    (5, 'Legal',       'Hyderabad');      -- has no employees yet

CREATE TABLE employees (
    emp_id      INT PRIMARY KEY,
    emp_name    VARCHAR(60) NOT NULL,
    email       VARCHAR(80) UNIQUE,                      -- may be NULL
    dept_id     INT REFERENCES departments(dept_id),     -- may be NULL
    manager_id  INT REFERENCES employees(emp_id),        -- self reference
    salary      NUMERIC(10,2) NOT NULL CHECK (salary > 0),
    hire_date   DATE NOT NULL,
    city        VARCHAR(40) NOT NULL
);

INSERT INTO employees VALUES
    ( 1, 'Arjun Mehta',    'arjun.mehta@company.com',    1, NULL, 150000, '2015-04-01', 'Bengaluru'),
    ( 2, 'Priya Sharma',   'priya.sharma@company.com',   1,    1, 120000, '2017-06-15', 'Bengaluru'),
    ( 3, 'Rahul Verma',    'rahul.verma@company.com',    1,    2,  95000, '2019-01-10', 'Pune'),
    ( 4, 'Sneha Iyer',     'sneha.iyer@company.com',     1,    2,  95000, '2020-03-23', 'Bengaluru'),
    ( 5, 'Vikram Rao',     'vikram.rao@company.com',     1,    2,  80000, '2021-07-01', 'Hyderabad'),
    ( 6, 'Ananya Das',     'ananya.das@company.com',     2,    1, 110000, '2016-09-12', 'Mumbai'),
    ( 7, 'Karan Malhotra', 'karan.malhotra@company.com', 2,    6,  70000, '2020-11-02', 'Mumbai'),
    ( 8, 'Meera Nair',     'meera.nair@company.com',     2,    6,  70000, '2022-02-14', 'Kochi'),
    ( 9, 'Rohan Gupta',    'rohan.gupta@company.com',    3,    1,  65000, '2018-05-21', 'Kolkata'),
    (10, 'Divya Menon',    'divya.menon@company.com',    3,    9,  52000, '2023-01-09', 'Kolkata'),
    (11, 'Aditya Singh',   'aditya.singh@company.com',   4,    1,  90000, '2019-08-19', 'Delhi'),
    (12, 'Neha Kapoor',    'neha.kapoor@company.com',    4,   11,  60000, '2021-12-06', 'Delhi'),
    (13, 'Farhan Ali',     NULL,                      NULL,    1,  55000, '2024-06-03', 'Pune'),
    (14, 'Pooja Reddy',    'pooja.reddy@company.com',    1,    3,  72000, '2024-02-12', 'Hyderabad');

-- ---------------------------------------------------------------------
-- E-commerce
-- ---------------------------------------------------------------------
CREATE TABLE customers (
    customer_id    INT PRIMARY KEY,
    customer_name  VARCHAR(60) NOT NULL,
    email          VARCHAR(80) UNIQUE,
    city           VARCHAR(40) NOT NULL,
    signup_date    DATE NOT NULL
);

INSERT INTO customers VALUES
    (1, 'Aarav Patel',   'aarav@mail.com',  'Mumbai',    '2023-11-05'),
    (2, 'Isha Kulkarni', 'isha@mail.com',   'Pune',      '2023-12-12'),
    (3, 'Kabir Khan',    'kabir@mail.com',  'Delhi',     '2024-01-03'),
    (4, 'Diya Joshi',    'diya@mail.com',   'Bengaluru', '2024-01-20'),
    (5, 'Vivaan Shah',   'vivaan@mail.com', 'Ahmedabad', '2024-02-08'),
    (6, 'Saanvi Rao',    'saanvi@mail.com', 'Chennai',   '2024-02-25'),  -- no orders
    (7, 'Reyansh Bose',  NULL,              'Kolkata',   '2024-03-15');  -- no orders

CREATE TABLE products (
    product_id    INT PRIMARY KEY,
    product_name  VARCHAR(60) NOT NULL,
    category      VARCHAR(30) NOT NULL,
    price         NUMERIC(10,2) NOT NULL CHECK (price >= 0)
);

INSERT INTO products VALUES
    (1, 'Wireless Mouse',      'Electronics',   799.00),
    (2, 'Mechanical Keyboard', 'Electronics',  3499.00),
    (3, 'USB-C Hub',           'Electronics',  1999.00),
    (4, 'Office Chair',        'Furniture',    8999.00),
    (5, 'Standing Desk',       'Furniture',   15999.00),
    (6, 'Notebook Pack',       'Stationery',    249.00),
    (7, 'Gel Pen Set',         'Stationery',    149.00),
    (8, 'Monitor Arm',         'Furniture',    2499.00);   -- never ordered

CREATE TABLE orders (
    order_id      INT PRIMARY KEY,
    customer_id   INT NOT NULL REFERENCES customers(customer_id),
    order_date    DATE NOT NULL,
    status        VARCHAR(12) NOT NULL
                  CHECK (status IN ('PENDING','SHIPPED','DELIVERED','CANCELLED','RETURNED')),
    total_amount  NUMERIC(10,2) NOT NULL DEFAULT 0
);

-- Note: order ids 107 and 112 are intentionally missing (deleted orders).
INSERT INTO orders (order_id, customer_id, order_date, status) VALUES
    (101, 1, '2024-01-05', 'DELIVERED'),
    (102, 2, '2024-01-12', 'DELIVERED'),
    (103, 1, '2024-01-28', 'DELIVERED'),
    (104, 3, '2024-02-02', 'CANCELLED'),
    (105, 4, '2024-02-14', 'DELIVERED'),
    (106, 2, '2024-02-20', 'DELIVERED'),
    (108, 5, '2024-03-03', 'SHIPPED'),
    (109, 1, '2024-03-10', 'DELIVERED'),
    (110, 3, '2024-03-18', 'DELIVERED'),
    (111, 4, '2024-03-29', 'RETURNED'),
    (113, 2, '2024-04-04', 'SHIPPED'),
    (114, 5, '2024-04-11', 'PENDING'),
    (115, 1, '2024-04-19', 'PENDING'),
    (116, 3, '2024-04-19', 'DELIVERED');

CREATE TABLE order_items (
    order_id    INT NOT NULL REFERENCES orders(order_id),
    product_id  INT NOT NULL REFERENCES products(product_id),
    quantity    INT NOT NULL CHECK (quantity > 0),
    unit_price  NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

INSERT INTO order_items VALUES
    (101, 1,  2,   799.00), (101, 6,  5,   249.00),
    (102, 2,  1,  3499.00),
    (103, 4,  1,  8999.00),
    (104, 5,  1, 15999.00),
    (105, 3,  1,  1999.00), (105, 1,  1,   799.00),
    (106, 7, 10,   149.00), (106, 6,  4,   249.00),
    (108, 2,  2,  3499.00),
    (109, 5,  1, 15999.00), (109, 4,  1,  8999.00),
    (110, 1,  3,   799.00),
    (111, 3,  2,  1999.00),
    (113, 4,  2,  8999.00),
    (114, 6, 10,   249.00), (114, 7,  5,   149.00),
    (115, 2,  1,  3499.00), (115, 3,  1,  1999.00),
    (116, 5,  1, 15999.00);

-- keep the order header total consistent with its line items
UPDATE orders o
SET    total_amount = (SELECT SUM(i.quantity * i.unit_price)
                       FROM   order_items i
                       WHERE  i.order_id = o.order_id);

-- ---------------------------------------------------------------------
-- Banking (used for transactions / ACID)
-- ---------------------------------------------------------------------
CREATE TABLE accounts (
    account_id   INT PRIMARY KEY,
    holder_name  VARCHAR(60) NOT NULL,
    balance      NUMERIC(12,2) NOT NULL CHECK (balance >= 0)
);

INSERT INTO accounts VALUES
    (1, 'Aarav Patel',   50000.00),
    (2, 'Isha Kulkarni', 20000.00),
    (3, 'Kabir Khan',     5000.00);

-- ---------------------------------------------------------------------
-- Marketing leads (contains duplicates on purpose)
-- ---------------------------------------------------------------------
CREATE TABLE leads (
    lead_id     INT PRIMARY KEY,
    full_name   VARCHAR(60) NOT NULL,
    email       VARCHAR(80) NOT NULL,
    created_at  DATE NOT NULL
);

INSERT INTO leads VALUES
    (1, 'Amit Kumar',  'amit@mail.com', '2024-01-02'),
    (2, 'Sara Thomas', 'sara@mail.com', '2024-01-03'),
    (3, 'Amit Kumar',  'amit@mail.com', '2024-01-05'),
    (4, 'John Dsouza', 'john@mail.com', '2024-01-06'),
    (5, 'Sara Thomas', 'sara@mail.com', '2024-01-09'),
    (6, 'Amit K.',     'amit@mail.com', '2024-01-11'),
    (7, 'Lina George', 'lina@mail.com', '2024-01-12');

-- ---------------------------------------------------------------------
-- Daily sales by region (window-function playground)
-- ---------------------------------------------------------------------
CREATE TABLE daily_sales (
    sale_date  DATE NOT NULL,
    region     VARCHAR(10) NOT NULL,
    amount     NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (sale_date, region)
);

INSERT INTO daily_sales VALUES
    ('2024-03-01', 'North', 12000), ('2024-03-01', 'South',  9000),
    ('2024-03-02', 'North', 15000), ('2024-03-02', 'South',  9500),
    ('2024-03-03', 'North', 11000), ('2024-03-03', 'South', 14000),
    ('2024-03-04', 'North', 18000), ('2024-03-04', 'South',  8000),
    ('2024-03-05', 'North', 21000), ('2024-03-05', 'South', 16000),
    ('2024-03-06', 'North', 17000), ('2024-03-06', 'South', 15500),
    ('2024-03-07', 'North', 23000), ('2024-03-07', 'South', 19000);

-- ---------------------------------------------------------------------
-- App logins (user_id = customer_id)
-- ---------------------------------------------------------------------
CREATE TABLE user_logins (
    login_id    INT PRIMARY KEY,
    user_id     INT NOT NULL REFERENCES customers(customer_id),
    login_time  TIMESTAMP NOT NULL,
    device      VARCHAR(10) NOT NULL
);

INSERT INTO user_logins VALUES
    ( 1, 1, '2024-04-01 09:15', 'mobile'),
    ( 2, 2, '2024-04-01 10:02', 'web'),
    ( 3, 1, '2024-04-02 20:45', 'web'),
    ( 4, 3, '2024-04-02 11:30', 'mobile'),
    ( 5, 1, '2024-04-03 08:05', 'mobile'),
    ( 6, 2, '2024-04-04 18:20', 'mobile'),
    ( 7, 4, '2024-04-04 21:10', 'web'),
    ( 8, 3, '2024-04-05 07:55', 'web'),
    ( 9, 1, '2024-04-05 22:40', 'mobile'),
    (10, 5, '2024-04-06 12:00', 'web');

ANALYZE;

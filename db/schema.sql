PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS PurchaseItem;
DROP TABLE IF EXISTS Purchase;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS CreditCard;
DROP TABLE IF EXISTS Staff;
DROP TABLE IF EXISTS Customer;

-- ----------------------------------------------------------------------------
-- 1. Strong Entity: Customer
-- ----------------------------------------------------------------------------
CREATE TABLE Customer (
    customer_id   INTEGER PRIMARY KEY,
    first_name    TEXT NOT NULL,
    last_name     TEXT NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    phone_number  TEXT,
    date_joined   TEXT NOT NULL
);

-- ----------------------------------------------------------------------------
-- 2. Strong Entity: Staff
-- ----------------------------------------------------------------------------
CREATE TABLE Staff (
    staff_id   INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    email      TEXT UNIQUE NOT NULL,
    job_title  TEXT,
    hire_date  TEXT NOT NULL
);

-- ----------------------------------------------------------------------------
-- 3. Weak Entity: CreditCard  (identifying parent: Customer)
--    card_id is a PARTIAL key -- unique only within one customer.
-- ----------------------------------------------------------------------------
CREATE TABLE CreditCard (
    card_id         INTEGER,
    customer_id     INTEGER,
    card_number     TEXT NOT NULL,
    expiration_date TEXT NOT NULL,
    cardholder_name TEXT NOT NULL,
    billing_street  TEXT NOT NULL,
    billing_city    TEXT NOT NULL,
    billing_state   TEXT NOT NULL,
    billing_zip     TEXT NOT NULL,
    PRIMARY KEY (card_id, customer_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 4. Strong Entity: Product 
-- ----------------------------------------------------------------------------
CREATE TABLE Product (
    product_id     INTEGER PRIMARY KEY,
    staff_id       INTEGER NOT NULL,
    product_name   TEXT NOT NULL,
    description    TEXT,
    price          REAL NOT NULL CHECK (price > 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    category       TEXT,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
);

-- ----------------------------------------------------------------------------
-- 5. Strong Entity: Purchase
--    Composite FK (card_id, customer_id) guarantees a customer can only pay
--    with a card that belongs to THEM -- not just any card in the table.
-- ----------------------------------------------------------------------------
CREATE TABLE Purchase (
    purchase_id   INTEGER PRIMARY KEY,
    customer_id   INTEGER NOT NULL,
    card_id       INTEGER NOT NULL,
    purchase_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount  REAL NOT NULL CHECK (total_amount >= 0),
    status        TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (card_id, customer_id) REFERENCES CreditCard(card_id, customer_id)
);

-- ----------------------------------------------------------------------------
-- 6. Weak Entity: PurchaseItem  (identifying parents: Purchase + Product)
--    unit_price is snapshotted at purchase time so later price changes on
--    Product do not rewrite order history.
-- ----------------------------------------------------------------------------
CREATE TABLE PurchaseItem (
    purchase_id INTEGER,
    product_id  INTEGER,
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    unit_price  REAL NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (purchase_id, product_id),
    FOREIGN KEY (purchase_id) REFERENCES Purchase(purchase_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id)  REFERENCES Product(product_id)
);

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Customers ------------------------------------------------------------------
INSERT INTO Customer (customer_id, first_name, last_name, email, password_hash, phone_number, date_joined) VALUES
    (1, 'Ada',   'Lovelace', 'ada.lovelace@example.com', 'sha256$8f2a1c...', '555-0101', '2024-01-15'),
    (2, 'Alan',  'Turing',   'alan.turing@example.com',  'sha256$b71e93...', '555-0102', '2024-03-02'),
    (3, 'Grace', 'Hopper',   'grace.hopper@example.com', 'sha256$44c0de...', '555-0103', '2024-06-20'),
    (4, 'Katherine', 'Johnson', 'k.johnson@example.com', 'sha256$19ff70...', NULL,       '2025-02-11');

-- Staff ----------------------------------------------------------------------
INSERT INTO Staff (staff_id, first_name, last_name, email, job_title, hire_date) VALUES
    (1, 'Marcus', 'Ellis',  'marcus.ellis@shop.com',  'Inventory Manager', '2023-05-01'),
    (2, 'Priya',  'Raman',  'priya.raman@shop.com',   'Catalog Admin',     '2023-09-12'),
    (3, 'Sofia',  'Nowak',  'sofia.nowak@shop.com',   'Fulfillment Lead',  '2024-02-19');

-- Credit cards ---------------------------------------------------------------
INSERT INTO CreditCard (card_id, customer_id, card_number, expiration_date, cardholder_name, billing_street, billing_city, billing_state, billing_zip) VALUES
    (1, 1, '4111111111111111', '2027-05-31', 'Ada Lovelace',      '12 Analytical Ave', 'Newark',    'NJ', '07102'),
    (2, 1, '5500005555555559', '2028-01-31', 'Ada Lovelace',      '12 Analytical Ave', 'Newark',    'NJ', '07102'),
    (1, 2, '4222222222222220', '2026-11-30', 'Alan M Turing',     '4 Enigma Road',     'Princeton', 'NJ', '08540'),
    (1, 3, '6011000990139424', '2027-09-30', 'Grace B Hopper',    '88 Compiler Ct',    'Arlington', 'VA', '22201'),
    (1, 4, '378282246310005',  '2029-03-31', 'Katherine Johnson', '1 Orbit Way',       'Hampton',   'VA', '23666');

-- Products -------------------------------------------------------------------
INSERT INTO Product (product_id, staff_id, product_name, description, price, stock_quantity, category) VALUES
    (1, 1, '27" 4K Monitor',        'IPS panel, 60Hz, USB-C 90W passthrough',   329.99,  18, 'Electronics'),
    (2, 1, 'Mechanical Keyboard',   'Hot-swappable, tactile brown switches',     89.99,  42, 'Electronics'),
    (3, 1, 'Noise-Cancelling Headphones', 'Over-ear, 30h battery, ANC',         249.00,  12, 'Electronics'),
    (4, 1, 'USB-C Cable 2m',        'Braided, 100W PD, 10Gbps',                  12.50, 240, 'Electronics'),
    (5, 2, 'Ergonomic Desk Chair',  'Mesh back, adjustable lumbar support',     419.00,   7, 'Furniture'),
    (6, 2, 'Standing Desk 48"',     'Electric, dual motor, memory presets',     549.00,   4, 'Furniture'),
    (7, 2, 'LED Desk Lamp',         'Dimmable, 5 color temperatures',            34.00,  63, 'Home'),
    (8, 3, 'A5 Dotted Notebook',    '160gsm paper, 192 pages',                    6.75, 150, 'Stationery'),
    (9, 3, 'Gel Pen 12-Pack',       '0.5mm, assorted colors',                     9.25,  88, 'Stationery'),
    (10, 3, 'Laptop Backpack',      'Water resistant, fits 16" laptop',          74.50,  31, 'Accessories');

-- Purchases ------------------------------------------------------------------
INSERT INTO Purchase (purchase_id, customer_id, card_id, purchase_date, total_amount, status) VALUES
    (1, 1, 1, '2025-03-04 10:12:00', 419.98, 'Delivered'),
    (2, 2, 1, '2025-03-18 14:37:00', 249.00, 'Shipped'),
    (3, 1, 2, '2025-04-02 09:05:00',  53.25, 'Delivered'),
    (4, 3, 1, '2025-05-21 16:48:00', 968.00, 'Processing'),
    (5, 4, 1, '2025-06-09 11:30:00',  74.50, 'Shipped'),
    (6, 2, 1, '2025-07-01 08:20:00',  41.00, 'Processing');

-- Purchase line items --------------------------------------------------------
INSERT INTO PurchaseItem (purchase_id, product_id, quantity, unit_price) VALUES
    -- Purchase 1: monitor + keyboard = 329.99 + 89.99 = 419.98
    (1, 1, 1, 329.99),
    (1, 2, 1,  89.99),
    -- Purchase 2: headphones = 249.00
    (2, 3, 1, 249.00),
    -- Purchase 3: lamp + cable + notebook = 34.00 + 12.50 + 6.75 = 53.25
    (3, 7, 1,  34.00),
    (3, 4, 1,  12.50),
    (3, 8, 1,   6.75),
    -- Purchase 4: standing desk + chair   = 549.00 + 419.00 = 968.00
    (4, 6, 1, 549.00),
    (4, 5, 1, 419.00),
    -- Purchase 5: backpack = 74.50
    (5, 10, 1, 74.50),
    -- Purchase 6: cable x2 + notebook + pens = 25.00 + 6.75 + 9.25 = 41.00
    (6, 4, 2,  12.50),
    (6, 8, 1,   6.75),
    (6, 9, 1,   9.25);

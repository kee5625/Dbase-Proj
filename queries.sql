-- ----------------------------------------------------------------------------
-- Query 1 — Product catalog with the staff member managing each item.
-- Tables: Product, Staff
-- ----------------------------------------------------------------------------
SELECT p.product_id,
       p.product_name,
       p.category,
       p.price,
       p.stock_quantity,
       s.first_name || ' ' || s.last_name AS managed_by
FROM Product p
JOIN Staff s ON s.staff_id = p.staff_id
ORDER BY p.product_name;


-- ----------------------------------------------------------------------------
-- Query 2 — Product search. Customer browsing by category and price ceiling.
-- Tables: Product, Staff       (parameterized in code; literals shown here)
-- ----------------------------------------------------------------------------
SELECT p.product_id,
       p.product_name,
       p.category,
       p.price,
       p.stock_quantity,
       s.first_name || ' ' || s.last_name AS managed_by
FROM Product p
JOIN Staff s ON s.staff_id = p.staff_id
WHERE p.category = 'Electronics'
  AND p.price <= 300.00
ORDER BY p.price;


-- ----------------------------------------------------------------------------
-- Query 3 — Low stock report with the staff member to contact for restock.
-- Tables: Product, Staff
-- ----------------------------------------------------------------------------
SELECT p.product_id,
       p.product_name,
       p.stock_quantity,
       s.first_name || ' ' || s.last_name AS managed_by,
       s.email AS contact
FROM Product p
JOIN Staff s ON s.staff_id = p.staff_id
WHERE p.stock_quantity < 20
ORDER BY p.stock_quantity;


-- ----------------------------------------------------------------------------
-- Query 4 — Customer overview: saved cards, order count, lifetime spend.
-- Tables: Customer, CreditCard, Purchase
-- ----------------------------------------------------------------------------
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS name,
       c.email,
       (SELECT COUNT(*) FROM CreditCard cc WHERE cc.customer_id = c.customer_id) AS card_count,
       (SELECT COUNT(*) FROM Purchase p WHERE p.customer_id = c.customer_id) AS order_count,
       COALESCE((SELECT SUM(total_amount) FROM Purchase p WHERE p.customer_id = c.customer_id), 0.0) AS lifetime_spend
FROM Customer c
ORDER BY c.last_name, c.first_name;


-- ----------------------------------------------------------------------------
-- Query 5 — Order list with buyer name and item count.
-- Tables: Purchase, Customer, PurchaseItem
-- ----------------------------------------------------------------------------
SELECT p.purchase_id,
       c.first_name || ' ' || c.last_name AS customer,
       p.purchase_date,
       p.total_amount,
       p.status,
       SUM(pi.quantity) AS item_count
FROM Purchase p
JOIN Customer c ON p.customer_id = c.customer_id
JOIN PurchaseItem pi ON p.purchase_id = pi.purchase_id
GROUP BY p.purchase_id, customer, p.purchase_date, p.total_amount, p.status
ORDER BY p.purchase_date DESC;


-- ----------------------------------------------------------------------------
-- Query 6 — Itemized breakdown of a single order.
-- Tables: PurchaseItem, Product
-- ----------------------------------------------------------------------------
SELECT pr.product_name,
       pr.category,
       pi.quantity,
       pi.unit_price,
       (pi.quantity * pi.unit_price) AS line_total
FROM PurchaseItem pi
JOIN Product pr ON pi.product_id = pr.product_id
WHERE pi.purchase_id = 1
ORDER BY pr.product_name;


-- ----------------------------------------------------------------------------
-- Query 7 — Customers alongside the products they bought costing over $100.
--           (The example query given in the assignment brief.)
-- Tables: Customer, Purchase, PurchaseItem, Product   -- four-table join
-- TODO(teammate): mirror customers_buying_over() from db/queries.py
-- ----------------------------------------------------------------------------

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
-- TODO(teammate): mirror customers_overview() from db/queries.py
-- ----------------------------------------------------------------------------


-- ----------------------------------------------------------------------------
-- Query 5 — Order list with buyer name and item count.
-- Tables: Purchase, Customer, PurchaseItem
-- TODO(teammate): mirror purchases_with_customer() from db/queries.py
-- ----------------------------------------------------------------------------


-- ----------------------------------------------------------------------------
-- Query 6 — Itemized breakdown of a single order.
-- Tables: PurchaseItem, Product
-- TODO(teammate): mirror order_line_items() from db/queries.py
-- ----------------------------------------------------------------------------


-- ----------------------------------------------------------------------------
-- Query 7 — Customers alongside the products they bought costing over $100.
--           (The example query given in the assignment brief.)
-- Tables: Customer, Purchase, PurchaseItem, Product   -- four-table join
-- TODO(teammate): mirror customers_buying_over() from db/queries.py
-- ----------------------------------------------------------------------------

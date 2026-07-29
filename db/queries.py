from __future__ import annotations

import sqlite3

from .connection import query

# ============================================================================
# READ QUERIES — Karthik
# ============================================================================


def products_with_staff(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Catalog with the staff member managing each item."""
    sql = """
        SELECT p.product_id,
               p.product_name,
               p.category,
               p.price,
               p.stock_quantity,
               s.first_name || ' ' || s.last_name AS managed_by
        FROM Product p
        JOIN Staff s ON s.staff_id = p.staff_id
        ORDER BY p.product_name
    """
    return query(conn, sql)


def search_products(
    conn: sqlite3.Connection,
    name: str | None = None,
    category: str | None = None,
    max_price: float | None = None,
) -> list[sqlite3.Row]:
    """Search Product"""
    sql = """
        SELECT p.product_id,
               p.product_name,
               p.category,
               p.price,
               p.stock_quantity,
               s.first_name || ' ' || s.last_name AS managed_by
        FROM Product p
        JOIN Staff s ON s.staff_id = p.staff_id
    """
    conditions: list[str] = []
    params: list = []

    if name:
        conditions.append("p.product_name LIKE ?")
        params.append(f"%{name}%")
    if category:
        conditions.append("p.category = ?")
        params.append(category)
    if max_price is not None:
        conditions.append("p.price <= ?")
        params.append(max_price)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY p.price"

    return query(conn, sql, tuple(params))


def low_stock(conn: sqlite3.Connection, threshold: int = 10) -> list[sqlite3.Row]:
    """Restock report."""
    sql = """
        SELECT p.product_id,
               p.product_name,
               p.stock_quantity,
               s.first_name || ' ' || s.last_name AS managed_by,
               s.email AS contact
        FROM Product p
        JOIN Staff s ON s.staff_id = p.staff_id
        WHERE p.stock_quantity < ?
        ORDER BY p.stock_quantity
    """
    return query(conn, sql, (threshold,))


def product_by_id(conn: sqlite3.Connection, product_id: int) -> sqlite3.Row | None:
    """Single product"""
    rows = query(conn, "SELECT * FROM Product WHERE product_id = ?", (product_id,))
    return rows[0] if rows else None


def list_customers(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Customer picker for the Checkout tab."""
    sql = """
        SELECT customer_id,
               first_name || ' ' || last_name AS name,
               email
        FROM Customer
        ORDER BY last_name, first_name
    """
    return query(conn, sql)


def cards_for_customer(conn: sqlite3.Connection, customer_id: int) -> list[sqlite3.Row]:
    """Cards belonging to one customer. Used by Checkout and the Customers tab."""
    sql = """
        SELECT card_id,
               customer_id,
               card_number,
               cardholder_name,
               expiration_date,
               billing_city || ', ' || billing_state AS billing
        FROM CreditCard
        WHERE customer_id = ?
        ORDER BY card_id
    """
    return query(conn, sql, (customer_id,))


def mask_card(card_number: str) -> str:
    """Show only the last 4 digits: 4111111111111111 -> **** **** **** 1111."""
    last4 = card_number[-4:]
    return f"**** **** **** {last4}"

def customers_overview(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Query 4 — every customer with how many cards they saved and how many
    orders they placed, plus lifetime spend.

    Required columns:
        customer_id, name, email, card_count, order_count, lifetime_spend

    """
    raise NotImplementedError("Teammate: see docs/TEAMMATE_TASKS.md")


def purchases_with_customer(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Query 5 — order list with the buyer's name resolved.

    Required columns:
        purchase_id, customer, purchase_date, total_amount, status, item_count

    Hints:
      - Purchase JOIN Customer for the name.
      - item_count comes from PurchaseItem; group by purchase.
      - Newest orders first.
    """
    raise NotImplementedError("Teammate: see docs/TEAMMATE_TASKS.md")


def order_line_items(conn: sqlite3.Connection, purchase_id: int) -> list[sqlite3.Row]:
    """Query 6 — itemized breakdown of one order.

    Required columns:
        product_name, category, quantity, unit_price, line_total

    """
    raise NotImplementedError("Teammate: see docs/TEAMMATE_TASKS.md")


def customers_buying_over(conn: sqlite3.Connection, min_price: float = 100.0) -> list[sqlite3.Row]:
    """Query 7 — the assignment's example query: customer names alongside the
    names of products they purchased where the product price exceeded a value.

    Required columns:
        customer, product_name, price, quantity, purchase_date
    """
    raise NotImplementedError("Teammate: see docs/TEAMMATE_TASKS.md")

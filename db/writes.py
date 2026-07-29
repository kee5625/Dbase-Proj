from __future__ import annotations

import sqlite3


class WriteError(Exception):
    """Raised for rule violations the UI should show as a message, not a crash."""


# ============================================================================
# Product CRUD
# ============================================================================


def add_product(
    conn: sqlite3.Connection,
    staff_id: int,
    product_name: str,
    price: float,
    stock_quantity: int,
    category: str | None = None,
    description: str | None = None,
) -> int:
    """INSERT a product. Returns the new product_id."""
    if not product_name.strip():
        raise WriteError("Product name is required.")
    if price <= 0:
        raise WriteError("Price must be greater than 0.")
    if stock_quantity < 0:
        raise WriteError("Stock quantity cannot be negative.")

    sql = """
        INSERT INTO Product (staff_id, product_name, description, price, stock_quantity, category)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        cur = conn.execute(
            sql, (staff_id, product_name.strip(), description, price, stock_quantity, category)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise WriteError(f"Could not add product: {e}") from e

    return cur.lastrowid


def update_product(
    conn: sqlite3.Connection,
    product_id: int,
    price: float | None = None,
    stock_quantity: int | None = None,
) -> int:
    """UPDATE price and/or stock on one product. Returns rows affected."""
    fields: list[str] = []
    params: list = []

    if price is not None:
        if price <= 0:
            raise WriteError("Price must be greater than 0.")
        fields.append("price = ?")
        params.append(price)
    if stock_quantity is not None:
        if stock_quantity < 0:
            raise WriteError("Stock quantity cannot be negative.")
        fields.append("stock_quantity = ?")
        params.append(stock_quantity)

    if not fields:
        raise WriteError("Nothing to update.")

    params.append(product_id)
    sql = f"UPDATE Product SET {', '.join(fields)} WHERE product_id = ?"
    try:
        cur = conn.execute(sql, tuple(params))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise WriteError(f"Could not update product: {e}") from e

    if cur.rowcount == 0:
        raise WriteError(f"No product with id {product_id}.")
    return cur.rowcount


def delete_product(conn: sqlite3.Connection, product_id: int) -> int:
    """DELETE a product."""
    in_orders = conn.execute(
        "SELECT COUNT(*) FROM PurchaseItem WHERE product_id = ?", (product_id,)
    ).fetchone()[0]
    if in_orders:
        raise WriteError(
            f"Cannot delete: product appears in {in_orders} past order(s). "
            "Set stock to 0 instead."
        )

    cur = conn.execute("DELETE FROM Product WHERE product_id = ?", (product_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise WriteError(f"No product with id {product_id}.")
    return cur.rowcount


# ============================================================================
# Credit cards
# ============================================================================


def next_card_id(conn: sqlite3.Connection, customer_id: int) -> int:
    """card_id is a partial key"""
    row = conn.execute(
        "SELECT COALESCE(MAX(card_id), 0) + 1 FROM CreditCard WHERE customer_id = ?",
        (customer_id,),
    ).fetchone()
    return row[0]


def add_card(
    conn: sqlite3.Connection,
    customer_id: int,
    card_number: str,
    expiration_date: str,
    cardholder_name: str,
    billing_street: str,
    billing_city: str,
    billing_state: str,
    billing_zip: str,
) -> int:
    """Attach a card to a customer"""
    card_id = next_card_id(conn, customer_id)
    sql = """
        INSERT INTO CreditCard (card_id, customer_id, card_number, expiration_date,
                                cardholder_name, billing_street, billing_city,
                                billing_state, billing_zip)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        conn.execute(
            sql,
            (card_id, customer_id, card_number, expiration_date, cardholder_name,
             billing_street, billing_city, billing_state, billing_zip),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise WriteError(f"Could not add card: {e}") from e
    return card_id


# ============================================================================
# Checkout
# ============================================================================


def place_order(
    conn: sqlite3.Connection,
    customer_id: int,
    card_id: int,
    items: list[tuple[int, int]],
    status: str = "Processing",
) -> int:
    """Place an order."""
    if not items:
        raise WriteError("Order must contain at least one item.")

    merged: dict[int, int] = {}
    for product_id, qty in items:
        if qty <= 0:
            raise WriteError("Quantity must be greater than 0.")
        merged[product_id] = merged.get(product_id, 0) + qty

    card = conn.execute(
        "SELECT 1 FROM CreditCard WHERE card_id = ? AND customer_id = ?",
        (card_id, customer_id),
    ).fetchone()
    if card is None:
        raise WriteError(f"Card {card_id} does not belong to customer {customer_id}.")

    # Price from the database
    lines: list[tuple[int, int, float]] = []
    total = 0.0
    for product_id, qty in merged.items():
        product = conn.execute(
            "SELECT product_name, price, stock_quantity FROM Product WHERE product_id = ?",
            (product_id,),
        ).fetchone()
        if product is None:
            raise WriteError(f"No product with id {product_id}.")
        if product["stock_quantity"] < qty:
            raise WriteError(
                f"Insufficient stock for {product['product_name']}: "
                f"{product['stock_quantity']} left, {qty} requested."
            )
        lines.append((product_id, qty, product["price"]))
        total += qty * product["price"]

    total = round(total, 2)

    try:
        cur = conn.execute(
            """
            INSERT INTO Purchase (customer_id, card_id, total_amount, status)
            VALUES (?, ?, ?, ?)
            """,
            (customer_id, card_id, total, status),
        )
        purchase_id = cur.lastrowid

        for product_id, qty, unit_price in lines:
            conn.execute(
                """
                INSERT INTO PurchaseItem (purchase_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
                """,
                (purchase_id, product_id, qty, unit_price),
            )
            upd = conn.execute(
                """
                UPDATE Product SET stock_quantity = stock_quantity - ?
                WHERE product_id = ? AND stock_quantity >= ?
                """,
                (qty, product_id, qty),
            )
            if upd.rowcount == 0:
                raise WriteError(f"Stock changed during checkout for product {product_id}.")

        conn.commit()
    except (sqlite3.IntegrityError, WriteError):
        conn.rollback()
        raise

    return purchase_id


def cancel_order(conn: sqlite3.Connection, purchase_id: int) -> int:
    """Delete an order and return its stock"""
    items = conn.execute(
        "SELECT product_id, quantity FROM PurchaseItem WHERE purchase_id = ?",
        (purchase_id,),
    ).fetchall()
    if not items:
        exists = conn.execute(
            "SELECT 1 FROM Purchase WHERE purchase_id = ?", (purchase_id,)
        ).fetchone()
        if exists is None:
            raise WriteError(f"No order with id {purchase_id}.")

    try:
        for item in items:
            conn.execute(
                "UPDATE Product SET stock_quantity = stock_quantity + ? WHERE product_id = ?",
                (item["quantity"], item["product_id"]),
            )
        cur = conn.execute("DELETE FROM Purchase WHERE purchase_id = ?", (purchase_id,))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise WriteError(f"Could not cancel order: {e}") from e

    return cur.rowcount

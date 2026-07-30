"""Checkout tab - build a cart and place an order as one transaction."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, DataTable, Input, Select, Static

from db.queries import cards_for_customer, list_customers, mask_card, products_with_staff
from db.writes import WriteError, place_order

from .base import TabBody, format_cell


class CheckoutTab(TabBody):
    def compose(self) -> ComposeResult:
        with Horizontal(classes="row"):
            yield Select([], prompt="Customer", id="customer")
            yield Select([], prompt="Card", id="card")

        with Horizontal(classes="row"):
            yield Select([], prompt="Product", id="product")
            yield Input(placeholder="qty", value="1", id="qty")
            yield Button("Add to cart", id="add", variant="primary")

        yield DataTable(id="cart", cursor_type="row", zebra_stripes=True)

        with Horizontal(classes="row"):
            yield Static("Total: 0.00", id="total")
            yield Button("Place order", id="place", variant="success")
            yield Button("Clear cart", id="clear", variant="error")

        yield Static("", classes="status")

    def on_mount(self) -> None:
        # cart entries: product_id -> [name, qty, unit_price]
        self.cart: dict[int, list] = {}
        self.query_one("#cart", DataTable).add_columns("Product", "Qty", "Unit price", "Line total")
        self.load_customers()
        self.load_products()
        self.status("Pick a customer, then a card, then add products.")

    # -- data ----------------------------------------------------------------

    def load_customers(self) -> None:
        rows = list_customers(self.conn)
        options = [(f"{r['name']} ({r['email']})", r["customer_id"]) for r in rows]
        self.query_one("#customer", Select).set_options(options)

    def load_products(self) -> None:
        rows = products_with_staff(self.conn)
        options = [
            (f"{r['product_name']} — {r['price']:,.2f} ({r['stock_quantity']} in stock)",
             r["product_id"])
            for r in rows
        ]
        self.query_one("#product", Select).set_options(options)
        self.products = {r["product_id"]: r for r in rows}

    def load_cards(self, customer_id: int) -> None:
        rows = cards_for_customer(self.conn, customer_id)
        options = [
            (f"#{r['card_id']}  {mask_card(r['card_number'])}  exp {r['expiration_date']}",
             r["card_id"])
            for r in rows
        ]
        self.query_one("#card", Select).set_options(options)

    def selection(self, widget_id: str, label: str) -> int:
        value = self.query_one(f"#{widget_id}", Select).value
        if value is Select.BLANK:
            raise WriteError(f"Select a {label} first.")
        return int(value)

    def redraw_cart(self) -> None:
        table = self.query_one("#cart", DataTable)
        table.clear()
        total = 0.0
        for product_id, (name, qty, unit_price) in self.cart.items():
            line = qty * unit_price
            total += line
            table.add_row(name, str(qty), format_cell(unit_price), format_cell(line))
        self.query_one("#total", Static).update(f"Total: {total:,.2f}")

    # -- events --------------------------------------------------------------

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "customer" and event.value is not Select.BLANK:
            self.load_cards(int(event.value))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        try:
            handler = {
                "add": self.do_add,
                "place": self.do_place,
                "clear": self.do_clear,
            }[event.button.id]
        except KeyError:
            return

        try:
            handler()
        except WriteError as e:
            self.status(str(e), error=True)

    def do_add(self) -> None:
        product_id = self.selection("product", "product")
        raw = self.query_one("#qty", Input).value.strip()
        try:
            qty = int(raw)
        except ValueError:
            raise WriteError(f"{raw!r} is not a whole number.") from None
        if qty <= 0:
            raise WriteError("Quantity must be greater than 0.")

        product = self.products[product_id]
        entry = self.cart.setdefault(product_id, [product["product_name"], 0, product["price"]])
        entry[1] += qty

        if entry[1] > product["stock_quantity"]:
            entry[1] -= qty
            if entry[1] == 0:
                del self.cart[product_id]
            raise WriteError(
                f"Only {product['stock_quantity']} of {product['product_name']} in stock."
            )

        self.redraw_cart()
        self.status(f"Added {qty} x {product['product_name']}.")

    def do_place(self) -> None:
        customer_id = self.selection("customer", "customer")
        card_id = self.selection("card", "card")
        if not self.cart:
            raise WriteError("Cart is empty.")

        items = [(product_id, entry[1]) for product_id, entry in self.cart.items()]
        purchase_id = place_order(self.conn, customer_id, card_id, items)

        self.cart.clear()
        self.redraw_cart()
        self.load_products()  # stock changed
        self.status(f"Order {purchase_id} placed. Stock updated.")

    def do_clear(self) -> None:
        self.cart.clear()
        self.redraw_cart()
        self.status("Cart cleared.")

"""Products tab - staff-facing catalog with search and full CRUD."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, DataTable, Input, Static

from db.queries import products_with_staff, search_products
from db.writes import WriteError, add_product, delete_product, update_product

from .base import TabBody, fill_table


def _to_float(raw: str) -> float | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        raise WriteError(f"{raw!r} is not a valid number.") from None


def _to_int(raw: str) -> int | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        raise WriteError(f"{raw!r} is not a whole number.") from None


class ProductsTab(TabBody):
    def compose(self) -> ComposeResult:
        with Horizontal(classes="row"):
            yield Input(placeholder="name contains", id="f_name")
            yield Input(placeholder="category", id="f_category")
            yield Input(placeholder="max price", id="f_max_price")
            yield Button("Search", id="search", variant="primary")
            yield Button("Show all", id="show_all")

        yield DataTable(id="table", cursor_type="row", zebra_stripes=True)

        with Horizontal(classes="row"):
            yield Input(placeholder="new price", id="e_price")
            yield Input(placeholder="new stock", id="e_stock")
            yield Button("Update selected", id="update")
            yield Button("Delete selected", id="delete", variant="error")

        with Horizontal(classes="row"):
            yield Input(placeholder="name", id="a_name")
            yield Input(placeholder="category", id="a_category")
            yield Input(placeholder="price", id="a_price")
            yield Input(placeholder="stock", id="a_stock")
            yield Input(placeholder="staff id", id="a_staff")
            yield Button("Add product", id="add", variant="success")

        yield Static("", classes="status")

    def on_mount(self) -> None:
        self._ids: list[int] = []
        self.refresh_table()

    # -- data ----------------------------------------------------------------

    def refresh_table(self, rows=None, label: str = "All products") -> None:
        if rows is None:
            rows = products_with_staff(self.conn)
        self._ids = [row["product_id"] for row in rows]
        fill_table(self.query_one("#table", DataTable), rows)
        self.status(f"{label} — {len(rows)} rows")

    def selected_product_id(self) -> int:
        table = self.query_one("#table", DataTable)
        if not self._ids or table.cursor_row is None or table.cursor_row >= len(self._ids):
            raise WriteError("Select a row in the table first.")
        return self._ids[table.cursor_row]

    def value(self, widget_id: str) -> str:
        return self.query_one(f"#{widget_id}", Input).value

    def clear_inputs(self, *widget_ids: str) -> None:
        for widget_id in widget_ids:
            self.query_one(f"#{widget_id}", Input).value = ""

    # -- events --------------------------------------------------------------

    def on_button_pressed(self, event: Button.Pressed) -> None:
        try:
            handler = {
                "search": self.do_search,
                "show_all": self.do_show_all,
                "update": self.do_update,
                "delete": self.do_delete,
                "add": self.do_add,
            }[event.button.id]
        except KeyError:
            return

        try:
            handler()
        except WriteError as e:
            self.status(str(e), error=True)

    def do_search(self) -> None:
        name = self.value("f_name").strip() or None
        category = self.value("f_category").strip() or None
        max_price = _to_float(self.value("f_max_price"))
        rows = search_products(self.conn, name=name, category=category, max_price=max_price)
        self.refresh_table(rows, "Search results")

    def do_show_all(self) -> None:
        self.clear_inputs("f_name", "f_category", "f_max_price")
        self.refresh_table()

    def do_update(self) -> None:
        product_id = self.selected_product_id()
        update_product(
            self.conn,
            product_id,
            price=_to_float(self.value("e_price")),
            stock_quantity=_to_int(self.value("e_stock")),
        )
        self.clear_inputs("e_price", "e_stock")
        self.refresh_table()
        self.status(f"Updated product {product_id}.")

    def do_delete(self) -> None:
        product_id = self.selected_product_id()
        delete_product(self.conn, product_id)
        self.refresh_table()
        self.status(f"Deleted product {product_id}.")

    def do_add(self) -> None:
        price = _to_float(self.value("a_price"))
        stock = _to_int(self.value("a_stock"))
        staff_id = _to_int(self.value("a_staff"))
        if price is None:
            raise WriteError("Price is required.")
        if staff_id is None:
            raise WriteError("Staff id is required.")

        product_id = add_product(
            self.conn,
            staff_id=staff_id,
            product_name=self.value("a_name"),
            price=price,
            stock_quantity=stock or 0,
            category=self.value("a_category").strip() or None,
        )
        self.clear_inputs("a_name", "a_category", "a_price", "a_stock", "a_staff")
        self.refresh_table()
        self.status(f"Added product {product_id}.")

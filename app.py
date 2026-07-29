from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from db import get_connection, init_db
from db.connection import DB_PATH
from db.queries import (products_by_category, purchases_with_customer, sales_totals_by_customer)


class EcommerceApp(App):
    CSS = """
    #status { height: 1; color: $text-muted; }
    #controls { height: auto; padding: 1 0; }
    Input { width: 30; }
    DataTable { height: 1fr; }
    """

    BINDINGS = [
        ("1", "show_purchases", "Purchases (JOIN)"),
        ("2", "show_sales", "Sales totals"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("", id="status")
        with Horizontal(id="controls"):
            yield Input(placeholder="category e.g. Electronics", id="category")
            yield Button("Filter products", id="filter", variant="primary")
        yield DataTable(id="table")
        yield Footer()

    def on_mount(self) -> None:
        self.conn = get_connection()
        self.action_show_purchases()

    # helpers

    def _render(self, rows, title: str) -> None:
        """Load sqlite3.Row list into the DataTable. Columns come from row.keys()."""
        table = self.query_one("#table", DataTable)
        table.clear(columns=True)
        if not rows:
            self.query_one("#status", Static).update(f"{title} — 0 rows")
            return
        table.add_columns(*rows[0].keys())
        for row in rows:
            table.add_row(*[str(row[k]) for k in row.keys()])
        self.query_one("#status", Static).update(f"{title} — {len(rows)} rows")

    # actions (keyboard)

    def action_show_purchases(self) -> None:
        self._render(purchases_with_customer(self.conn), "Purchases JOIN Customer")

    def action_show_sales(self) -> None:
        self._render(sales_totals_by_customer(self.conn), "Sales totals by customer")

    # events

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "filter":
            category = self.query_one("#category", Input).value.strip() or "Electronics"
            self._render(products_by_category(self.conn, category), f"Products in {category!r}")

    def on_unmount(self) -> None:
        if getattr(self, "conn", None):
            self.conn.close()


def main() -> None:
    if not DB_PATH.exists():
        init_db()
    EcommerceApp().run()


if __name__ == "__main__":
    main()

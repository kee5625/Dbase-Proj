from __future__ import annotations

import sys

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane

from db.connection import DB_PATH, get_connection, init_db
from screens.base import TabBody
from screens.checkout import CheckoutTab
from screens.customers import CustomersTab
from screens.orders import OrdersTab
from screens.products import ProductsTab


class EcommerceApp(App):
    TITLE = "E-Commerce Database"
    SUB_TITLE = "SQLite + Textual"

    CSS = """
    .row {
        height: auto;
        padding: 0 1;
    }
    .row > Input { width: 1fr; }
    .row > Select { width: 1fr; }
    .row > Button { width: auto; margin-left: 1; }
    .status {
        height: auto;
        padding: 0 1;
        color: $text-muted;
    }
    .status.error { color: $error; }
    DataTable { height: 1fr; }
    #detail { height: auto; padding: 0 1; }
    #items { height: 40%; }
    #total { width: 1fr; content-align: left middle; }
    """

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        if not DB_PATH.exists():
            init_db()
        # One connection for the whole app
        self.conn = get_connection()

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="tab-products"):
            with TabPane("Products", id="tab-products"):
                yield ProductsTab()
            with TabPane("Checkout", id="tab-checkout"):
                yield CheckoutTab()
            with TabPane("Customers", id="tab-customers"):
                yield CustomersTab()
            with TabPane("Orders", id="tab-orders"):
                yield OrdersTab()
        yield Footer()

    def action_refresh(self) -> None:
        """Re-run the query behind every tab that has one."""
        for tab in self.query(TabBody):
            if hasattr(tab, "refresh_table"):
                tab.refresh_table()

    def on_unmount(self) -> None:
        self.conn.close()


if __name__ == "__main__":
    # --reset wipes the database and reloads schema.sql before starting.
    if "--reset" in sys.argv:
        init_db()
        print(f"Rebuilt {DB_PATH}")
    EcommerceApp().run()

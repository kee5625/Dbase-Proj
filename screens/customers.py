"""Customers tab - customer list with a drilldown to their saved cards.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import DataTable, Static

from db.queries import customers_overview

from .base import TabBody, fill_table


class CustomersTab(TabBody):
    def compose(self) -> ComposeResult:
        yield DataTable(id="table", cursor_type="row", zebra_stripes=True)
        yield DataTable(id="detail", cursor_type="row", zebra_stripes=True)
        yield Static("", classes="status")

    def on_mount(self) -> None:
        self.refresh_table()

    def refresh_table(self) -> None:
        try:
            rows = customers_overview(self.conn)
        except NotImplementedError:
            self.status("customers_overview() is not implemented yet.", error=True)
            return
        self._ids = [row["customer_id"] for row in rows]
        fill_table(self.query_one("#table", DataTable), rows)
        self.status(f"Customers — {len(rows)} rows")

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.control.id == "table":
            customer_id = self._ids[event.cursor_row]
            from db.queries import cards_for_customer
            cards = cards_for_customer(self.conn, customer_id)
            fill_table(self.query_one("#detail", DataTable), cards)

"""Orders tab - order list with a drilldown to line items."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import DataTable, Static

from db.queries import purchases_with_customer

from .base import Tab, fill_table


class OrdersTab(Tab):
    def compose(self) -> ComposeResult:
        yield DataTable(id="table", cursor_type="row", zebra_stripes=True)
        yield DataTable(id="items", cursor_type="row", zebra_stripes=True)
        yield Static("", classes="status")

    def on_mount(self) -> None:
        self.refresh_table()

    def refresh_table(self) -> None:
        try:
            rows = purchases_with_customer(self.conn)
        except NotImplementedError:
            self.status("purchases_with_customer() is not implemented yet.", error=True)
            return
        self._ids = [row["purchase_id"] for row in rows]
        fill_table(self.query_one("#table", DataTable), rows)
        self.status(f"Orders — {len(rows)} rows")

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        
        pass

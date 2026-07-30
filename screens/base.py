"""Shared helpers for the tab widgets."""

from __future__ import annotations

import sqlite3

from textual.containers import Vertical
from textual.widgets import DataTable


def fill_table(table: DataTable, rows: list[sqlite3.Row]) -> None:
    """Replace a DataTable's contents. Columns are taken from the row keys."""
    table.clear(columns=True)
    if not rows:
        return
    table.add_columns(*rows[0].keys())
    for row in rows:
        table.add_row(*[format_cell(row[k]) for k in row.keys()])


def format_cell(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


class TabBody(Vertical):
    """Base for every tab. Shares the app's single database connection."""

    @property
    def conn(self) -> sqlite3.Connection:
        return self.app.conn

    def status(self, message: str, error: bool = False) -> None:
        widget = self.query_one(".status")
        widget.update(message)
        widget.set_class(error, "error")

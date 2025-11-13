#!/usr/bin/env python3
"""
WSYS Terminal Editor – minimal, works with Textual 6.5+
"""

from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Footer, Header, Static
from textual.containers import Container


class MetaPanel(Static):
    """Live cursor + clock."""
    def update_meta(self, line: int, col: int):
        self.update(
            f"Cursor: ({line+1}, {col+1}) | {datetime.now():%H:%M:%S}"
        )


class WSYSEditor(App):
    CSS = """
    Screen { layout: vertical; }
    #editor { border: round white; height: 1fr; }
    #meta   { background: $accent-darken-1; color: $text; padding: 1 2; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        self.text_area = TextArea(id="editor")
        self.meta = MetaPanel(id="meta")
        yield Container(self.text_area)
        yield self.meta
        yield Footer()

    def on_mount(self) -> None:
        self.text_area.focus()
        self.set_interval(1, self.update_meta_info)

    def update_meta_info(self) -> None:
        try:
            line, col = self.text_area.cursor_location
            self.meta.update_meta(line, col)
        except Exception as e:
            self.meta.update(f"[Error reading cursor: {e}]")


if __name__ == "__main__":
    WSYSEditor().run()

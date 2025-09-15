from textual.app import ComposeResult
from textual.widgets import Label
from textual.screen import ModalScreen
from textual.events import Key


class Entry(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Label("This is the entry editor")
        yield Label("Press 'b' to go back (Journal Entries)")

    def on_key(self, event: Key):
        if event.key == "b":
            self.dismiss()

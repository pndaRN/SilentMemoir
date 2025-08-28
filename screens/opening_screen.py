from textual.app import ComposeResult
from textual.widgets import Label
from textual.screen import Screen
from textual.events import Key
from textual.containers import Vertical


class OpeningScreen(Screen):
    def on_key(self, event: Key) -> None:
        if event.key == "e":
            self.enter()

    def compose(self) -> ComposeResult:
        with Vertical(id="os_center"):
            yield Label("Silent Memoir")
            yield Label("Press 'e' to Enter")

    def enter(self) -> None:
        self.app.push_screen("View Journals")

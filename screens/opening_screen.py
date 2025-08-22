from textual.app import App, ComposeResult 
from textual.widgets import Label
from textual.screen import Screen
from textual.events import Key

class OpeningScreen(Screen):

    def on_key(self, event=Key):
        if event.key == "e":
            self.enter()

    def compose(self) -> ComposeResult:
        yield Label("This is the opening screen")
        yield Label("Press 'e' to Enter")

    def enter(self) -> None:
        self.app.push_screen("View Journals")




from textual.app import ComposeResult
from textual.widgets import Label
from textual.screen import Screen
from textual.containers import Horizontal
from textual.events import Key

from pyfiglet import Figlet
from data.quotes import QUOTES

import random


class OpeningScreen(Screen):
    def on_key(self, event: Key) -> None:
        if event.key == "e" or event.key == "E":
            self.enter()

    def compose(self) -> ComposeResult:
        f = Figlet(font="shadow")
        # Fonts I like: Slant, Big,
        title = f.renderText("Silent Memoir")

        with Horizontal(id="os_title"):
            yield Label(title, classes="titleText")
        with Horizontal(id="os_quote"):
            yield Label(random.choice(QUOTES), id="quoteLabel")
        with Horizontal(id="os_enter"):
            yield Label("Press 'e' to Enter")

    def enter(self):
        self.app.push_screen("View Journals")

    def on_mount(self):
        self.set_interval(10, self.update_quote)

    async def update_quote(self):
        quote = random.choice(QUOTES)
        self.query_one("#quoteLabel", Label).update(quote)
